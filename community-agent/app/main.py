from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import hashlib
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from .models import (
    Intake, Journey, PrefillResponse, ConsentRequest, 
    SubmissionResponse, IntakeResponse
)
from .orchestrator import JourneyOrchestrator
from .utils.audit import log_consent, verify_consent, get_audit_trail, get_consent_summary
from .utils.storage import list_artifacts, get_artifact_stats, cleanup_expired_artifacts, save_artifact
from .agent import agent

app = FastAPI(
    title="Agentic Community Assistant",
    description="AI-powered assistant for guiding users through life events with automated form completion",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = JourneyOrchestrator()

# In-memory storage for demo (in production, use proper database)
journey_store: Dict[str, Journey] = {}
intake_store: Dict[str, Intake] = {}

# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main web interface"""
    static_dir = Path(__file__).parent / "static"
    index_path = static_dir / "index.html"
    
    if index_path.exists():
        return FileResponse(str(index_path))
    else:
        return {
            "service": "Agentic Community Assistant",
            "version": "1.0.0",
            "description": "AI-powered life event guidance with automated form completion",
            "endpoints": {
                "intake": "POST /intake - Start a new journey",
                "plan": "GET /plan/{journey_id} - Get journey plan",
                "prefill": "POST /prefill/{journey_id}/{step} - Prefill form",
                "consent": "POST /consent/{journey_id} - Grant consent",
                "submit": "POST /submit/{journey_id}/{step} - Submit form",
                "artifacts": "GET /artifacts - List artifacts",
                "audit": "GET /audit - Get audit trail"
            }
        }


@app.post("/intake", response_model=IntakeResponse)
async def create_intake(intake: Intake):
    """
    Create a new intake and journey plan for baby just born life event
    
    This endpoint:
    1. Creates a unique journey ID
    2. Plans the journey steps (birth registration, Medicare enrolment)
    3. Saves intake data to secure vault
    4. Returns journey plan
    """
    try:
        # Plan the journey
        journey = orchestrator.plan_journey(intake)
        
        # Store in memory for demo (in production, use database)
        journey_store[journey.id] = journey
        intake_store[journey.id] = intake
        
        # Log intake creation
        user_hash = hashlib.sha256(intake.parent1.full_name.encode()).hexdigest()[:8]
        
        return IntakeResponse(
            journey_id=journey.id,
            plan=journey
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create intake: {str(e)}")


@app.get("/plan/{journey_id}", response_model=Journey)
async def get_journey_plan(journey_id: str):
    """
    Get the journey plan for a specific journey ID
    
    Returns the complete journey with all steps and their current status.
    """
    if journey_id not in journey_store:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    return journey_store[journey_id]


@app.post("/prefill/{journey_id}/{step}", response_model=PrefillResponse)
async def prefill_form(journey_id: str, step: str):
    """
    Prefill a form for a specific journey step
    
    This endpoint:
    1. Loads the form schema for the step
    2. Maps intake data to form fields
    3. Returns prefill data and review information
    4. Saves prefill artifact
    """
    if journey_id not in journey_store:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    if journey_id not in intake_store:
        raise HTTPException(status_code=404, detail="Intake data not found")
    
    try:
        # Get intake data
        intake = intake_store[journey_id]
        
        # Prefill the form
        prefill_response = orchestrator.prefill_form(journey_id, step, intake)
        
        return prefill_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to prefill form: {str(e)}")


@app.post("/consent/{journey_id}")
async def grant_consent(journey_id: str, consent_request: ConsentRequest):
    """
    Grant consent for a specific journey
    
    This endpoint:
    1. Records user consent with scope and signature
    2. Creates audit trail entry
    3. Returns consent ID for future verification
    """
    if journey_id not in journey_store:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    try:
        # Create user identifier hash (privacy-preserving)
        user_hash = hashlib.sha256(consent_request.consent.scope[0].encode()).hexdigest()[:8]
        
        # Log consent
        consent_id = log_consent(
            journey_id=journey_id,
            consent_scope=consent_request.consent.scope,
            user_identifier=user_hash,
            signature=consent_request.consent.signature
        )
        
        return {
            "consent_id": consent_id,
            "status": "granted",
            "scope": consent_request.consent.scope,
            "granted_at": consent_request.consent.granted_at.isoformat(),
            "message": "Consent granted successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to grant consent: {str(e)}")


@app.post("/submit/{journey_id}/{step}", response_model=SubmissionResponse)
async def submit_form(journey_id: str, step: str, form_data: Dict[str, Any]):
    """
    Submit a form for a specific journey step
    
    This endpoint:
    1. Processes form submission
    2. Generates receipt and reference number
    3. Saves submission artifact
    4. Updates journey step status
    """
    if journey_id not in journey_store:
        raise HTTPException(status_code=404, detail="Journey not found")
    
    try:
        # Submit the form
        submission_response = orchestrator.submit_form(journey_id, step, form_data)
        
        # Update journey step status
        journey = journey_store[journey_id]
        for journey_step in journey.steps:
            if journey_step.id == step:
                journey_step.status = "completed"
                break
        
        return submission_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to submit form: {str(e)}")


@app.get("/artifacts")
async def list_journey_artifacts(journey_id: str = None):
    """
    List artifacts for a specific journey or all artifacts
    
    Returns metadata about stored artifacts without exposing PII.
    """
    try:
        artifacts = list_artifacts(journey_id)
        stats = get_artifact_stats()
        
        return {
            "artifacts": artifacts,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list artifacts: {str(e)}")


@app.get("/audit")
async def get_audit_information(
    journey_id: str = None,
    action: str = None,
    limit: int = 50
):
    """
    Get audit trail information
    
    Returns filtered audit events and consent summary.
    """
    try:
        # Get audit trail
        audit_events = get_audit_trail(journey_id, action)
        
        # Limit results
        if limit:
            audit_events = audit_events[:limit]
        
        # Get consent summary
        consent_summary = get_consent_summary()
        
        return {
            "audit_events": audit_events,
            "consent_summary": consent_summary,
            "total_events": len(audit_events)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get audit information: {str(e)}")


# Agentic AI Endpoints
@app.post("/agent/start")
async def agent_start(request: Dict[str, Any]):
    """Start a conversation with the agentic AI assistant"""
    try:
        user_message = request.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Start conversation with agent
        response = agent.start_conversation(user_message)
        
        # Save conversation artifact
        conversation_artifact = {
            "conversation_id": response.get("journey_id"),
            "user_message": user_message,
            "agent_response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        save_artifact(
            f"conversations/{response.get('journey_id')}/start.json",
            conversation_artifact,
            "conversation_start"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agent/continue")
async def agent_continue(request: Dict[str, Any]):
    """Continue an existing conversation with the agentic AI assistant"""
    try:
        journey_id = request.get("journey_id")
        user_input = request.get("user_input")
        
        if not journey_id:
            raise HTTPException(status_code=400, detail="Journey ID is required")
        
        # Continue conversation with agent
        response = agent.continue_conversation(journey_id, user_input)
        
        # Save continuation artifact
        continuation_artifact = {
            "journey_id": journey_id,
            "user_input": user_input,
            "agent_response": response,
            "timestamp": datetime.now().isoformat()
        }
        
        save_artifact(
            f"conversations/{journey_id}/continue.json",
            continuation_artifact,
            "conversation_continue"
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agent/status/{journey_id}")
async def agent_status(journey_id: str):
    """Get the current status of an agent conversation"""
    try:
        if not agent.current_journey or agent.current_journey.id != journey_id:
            return {"error": "Journey not found or not active"}
        
        # Get current journey status
        current_step = None
        for step in agent.current_journey.steps:
            if step.status != 'completed':
                current_step = step
                break
        
        return {
            "journey_id": journey_id,
            "current_step": current_step.dict() if current_step else None,
            "total_steps": len(agent.current_journey.steps),
            "completed_steps": len([s for s in agent.current_journey.steps if s.status == 'completed']),
            "status": "active" if current_step else "completed"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup")
async def cleanup_expired_data():
    """
    Clean up expired artifacts and data
    
    This endpoint removes data that has exceeded its TTL.
    """
    try:
        cleanup_expired_artifacts(ttl_days=30)
        
        return {
            "status": "success",
            "message": "Cleanup completed",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cleanup: {str(e)}")


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Agentic Community Assistant"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
