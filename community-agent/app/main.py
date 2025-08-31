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
from .ai_integration import ollama_ai

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
intake_store: Dict[str, Journey] = {}

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
                "audit": "GET /audit - Get audit trail",
                "ai_chat": "POST /ai/chat - Chat with AI assistant"
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
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/plan/{journey_id}")
async def get_journey_plan(journey_id: str):
    """Get the journey plan for a specific journey ID"""
    try:
        if journey_id not in journey_store:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        return journey_store[journey_id]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/prefill/{journey_id}/{step_id}")
async def prefill_form(journey_id: str, step_id: str):
    """Prefill a form for a specific journey step"""
    try:
        if journey_id not in journey_store:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        # Get the form schema and prefill data
        prefill_data = orchestrator.prefill_form(journey_id, step_id, intake_store[journey_id])
        
        return prefill_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/consent/{journey_id}")
async def grant_consent(journey_id: str, consent_request: ConsentRequest):
    """Grant consent for a journey"""
    try:
        if journey_id not in journey_store:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        # Log consent
        log_consent(
            journey_id=journey_id,
            consent=consent_request,
            actor="user"
        )
        
        return {"status": "consent_granted", "journey_id": journey_id}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/submit/{journey_id}/{step_id}")
async def submit_form(journey_id: str, step_id: str):
    """Submit a form for a specific journey step"""
    try:
        if journey_id not in journey_store:
            raise HTTPException(status_code=404, detail="Journey not found")
        
        # Submit the form
        submission = orchestrator.submit_form(journey_id, step_id)
        
        return submission
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/artifacts")
async def list_journey_artifacts(journey_id: str = None):
    """List artifacts for journeys"""
    try:
        if journey_id:
            artifacts = list_artifacts(journey_id=journey_id)
        else:
            artifacts = list_artifacts()
        
        return artifacts
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/audit")
async def get_audit_trail():
    """Get the audit trail"""
    try:
        audit_trail = get_audit_trail()
        return audit_trail
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_artifact_stats():
    """Get artifact statistics"""
    try:
        stats = get_artifact_stats()
        return stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# New AI Chat Endpoints
@app.post("/ai/chat")
async def ai_chat(request: Dict[str, Any]):
    """Chat with the AI assistant"""
    try:
        user_message = request.get("message", "")
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Use the Ollama AI to analyze the request
        ai_response = ollama_ai.analyze_government_request(user_message)
        
        # Create a journey if one was identified
        journey_id = None
        if ai_response.get('life_event') and ai_response.get('journey_steps'):
            journey_id = f"ai_journey_{hashlib.sha256(user_message.encode()).hexdigest()[:8]}"
            
            # Create a simple journey structure
            journey = Journey(
                id=journey_id,
                life_event=ai_response['life_event'],
                jurisdiction="NSW",
                steps=ai_response['journey_steps']
            )
            
            # Store the journey
            journey_store[journey_id] = journey
            
            # Add journey info to response
            ai_response['journey_id'] = journey_id
            ai_response['plan'] = journey.dict()
        
        return ai_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ai/continue")
async def ai_continue(request: Dict[str, Any]):
    """Continue conversation with AI"""
    try:
        user_message = request.get("message", "")
        journey_id = request.get("journey_id")
        
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        # Generate AI response
        ai_response = ollama_ai.generate_response(user_message)
        
        # Add journey context if available
        if journey_id and journey_id in journey_store:
            journey = journey_store[journey_id]
            ai_response['journey_id'] = journey_id
            ai_response['current_journey'] = journey.dict()
        
        return ai_response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ai/history")
async def get_ai_history():
    """Get AI conversation history"""
    try:
        history = ollama_ai.get_conversation_history()
        return {"conversations": history}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/ai/history")
async def clear_ai_history():
    """Clear AI conversation history"""
    try:
        ollama_ai.clear_history()
        return {"status": "history_cleared"}
    
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
        "service": "Agentic Community Assistant",
        "ai_model": "Ollama (qwen2.5:0.5b)"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
