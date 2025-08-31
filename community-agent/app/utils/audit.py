import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, Optional


def log_event(
    actor: str,
    action: str,
    why: str,
    consent_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Log an audit event with SHA-256 hash for integrity
    
    Args:
        actor: Who performed the action (user, system, admin)
        action: What action was performed
        why: Reason for the action
        consent_id: Optional consent identifier
        metadata: Additional metadata about the event
    
    Returns:
        SHA-256 hash of the logged event
    """
    # Create artifacts directory if it doesn't exist
    artifacts_dir = Path("_artifacts")
    artifacts_dir.mkdir(exist_ok=True)
    
    # Create audit log entry
    event = {
        "timestamp": datetime.utcnow().isoformat(),
        "actor": actor,
        "action": action,
        "why": why,
        "consent_id": consent_id,
        "metadata": metadata or {}
    }
    
    # Generate SHA-256 hash of the event
    event_json = json.dumps(event, sort_keys=True, default=str)
    event_hash = hashlib.sha256(event_json.encode()).hexdigest()
    
    # Add hash to the event
    event["hash"] = event_hash
    
    # Append to audit log (JSONL format)
    audit_log_path = artifacts_dir / "audit.log"
    
    with open(audit_log_path, 'a') as f:
        f.write(json.dumps(event) + '\n')
    
    print(f"Audit event logged: {action} by {actor} - Hash: {event_hash[:8]}...")
    
    return event_hash


def log_consent(
    journey_id: str,
    consent_scope: list,
    user_identifier: str,
    signature: Optional[str] = None
) -> str:
    """
    Log a consent event and return consent ID
    
    Args:
        journey_id: Journey identifier
        consent_scope: List of consent scopes
        user_identifier: User identifier (hashed)
        signature: Optional digital signature
    
    Returns:
        Consent ID (hash)
    """
    # Create consent ID from journey and timestamp
    consent_data = f"{journey_id}{datetime.utcnow().isoformat()}"
    consent_id = hashlib.sha256(consent_data.encode()).hexdigest()[:16]
    
    # Log consent event
    log_event(
        actor="user",
        action="consent_granted",
        why="User granted consent for specified scopes",
        consent_id=consent_id,
        metadata={
            "journey_id": journey_id,
            "consent_scope": consent_scope,
            "user_identifier": user_identifier,
            "has_signature": signature is not None
        }
    )
    
    # Save consent details to vault
    consent_data = {
        "consent_id": consent_id,
        "journey_id": journey_id,
        "consent_scope": consent_scope,
        "user_identifier": user_identifier,
        "signature": signature,
        "granted_at": datetime.utcnow().isoformat(),
        "ttl_days": 30
    }
    
    # Save to consent ledger
    consent_ledger_path = Path("_artifacts") / "consent_ledger.json"
    
    if consent_ledger_path.exists():
        with open(consent_ledger_path, 'r') as f:
            ledger = json.load(f)
    else:
        ledger = {"consents": []}
    
    ledger["consents"].append(consent_data)
    
    with open(consent_ledger_path, 'w') as f:
        json.dump(ledger, f, indent=2, default=str)
    
    return consent_id


def verify_consent(consent_id: str, required_scope: str) -> bool:
    """
    Verify if consent exists and covers required scope
    
    Args:
        consent_id: Consent identifier to verify
        required_scope: Required consent scope
    
    Returns:
        True if consent is valid and covers required scope
    """
    consent_ledger_path = Path("_artifacts") / "consent_ledger.json"
    
    if not consent_ledger_path.exists():
        return False
    
    try:
        with open(consent_ledger_path, 'r') as f:
            ledger = json.load(f)
        
        for consent in ledger.get("consents", []):
            if consent.get("consent_id") == consent_id:
                # Check if consent covers required scope
                consent_scope = consent.get("consent_scope", [])
                if required_scope in consent_scope:
                    # Check if consent is still valid (not expired)
                    granted_at = datetime.fromisoformat(consent["granted_at"].replace('Z', '+00:00'))
                    ttl_days = consent.get("ttl_days", 30)
                    expiry_date = granted_at + timedelta(days=ttl_days)
                    
                    if datetime.utcnow() < expiry_date:
                        return True
        
        return False
    
    except (json.JSONDecodeError, ValueError, KeyError):
        return False


def get_audit_trail(
    journey_id: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> list:
    """
    Get audit trail with optional filtering
    
    Args:
        journey_id: Filter by journey ID
        action: Filter by action type
        start_date: Filter events after this date
        end_date: Filter events before this date
    
    Returns:
        List of filtered audit events
    """
    audit_log_path = Path("_artifacts") / "audit.log"
    
    if not audit_log_path.exists():
        return []
    
    events = []
    
    with open(audit_log_path, 'r') as f:
        for line in f:
            try:
                event = json.loads(line.strip())
                
                # Apply filters
                if journey_id and event.get("metadata", {}).get("journey_id") != journey_id:
                    continue
                
                if action and event.get("action") != action:
                    continue
                
                if start_date:
                    event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
                    if event_time < start_date:
                        continue
                
                if end_date:
                    event_time = datetime.fromisoformat(event["timestamp"].replace('Z', '+00:00'))
                    if event_time > end_date:
                        continue
                
                events.append(event)
            
            except json.JSONDecodeError:
                continue
    
    # Sort by timestamp (newest first)
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return events


def get_consent_summary() -> Dict[str, Any]:
    """
    Get summary of consent activities
    
    Returns:
        Dictionary with consent statistics
    """
    consent_ledger_path = Path("_artifacts") / "consent_ledger.json"
    
    if not consent_ledger_path.exists():
        return {
            "total_consents": 0,
            "active_consents": 0,
            "expired_consents": 0,
            "scope_breakdown": {}
        }
    
    try:
        with open(consent_ledger_path, 'r') as f:
            ledger = json.load(f)
        
        total_consents = len(ledger.get("consents", []))
        active_consents = 0
        expired_consents = 0
        scope_breakdown = {}
        
        for consent in ledger.get("consents", []):
            granted_at = datetime.fromisoformat(consent["granted_at"].replace('Z', '+00:00'))
            ttl_days = consent.get("ttl_days", 30)
            expiry_date = granted_at + timedelta(days=ttl_days)
            
            if datetime.utcnow() < expiry_date:
                active_consents += 1
            else:
                expired_consents += 1
            
            # Count scope usage
            for scope in consent.get("consent_scope", []):
                scope_breakdown[scope] = scope_breakdown.get(scope, 0) + 1
        
        return {
            "total_consents": total_consents,
            "active_consents": active_consents,
            "expired_consents": expired_consents,
            "scope_breakdown": scope_breakdown
        }
    
    except (json.JSONDecodeError, ValueError, KeyError):
        return {
            "total_consents": 0,
            "active_consents": 0,
            "expired_consents": 0,
            "scope_breakdown": {}
        }
