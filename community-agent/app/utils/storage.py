import json
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict


def get_vault_path(journey_id: str) -> Path:
    """Get the vault path for a specific journey"""
    artifacts_dir = Path("_artifacts")
    vault_dir = artifacts_dir / "vault" / journey_id
    vault_dir.mkdir(parents=True, exist_ok=True)
    return vault_dir


def save_artifact(path: str, data: Any, artifact_type: str):
    """Save an artifact to the specified path"""
    file_path = Path(path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Add metadata to the artifact
    artifact_data = {
        "type": artifact_type,
        "created_at": datetime.utcnow().isoformat(),
        "data": data
    }
    
    with open(file_path, 'w') as f:
        json.dump(artifact_data, f, indent=2, default=str)
    
    print(f"Artifact saved: {file_path}")


def load_artifact(path: str) -> Dict[str, Any]:
    """Load an artifact from the specified path"""
    file_path = Path(path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Artifact not found: {path}")
    
    with open(file_path, 'r') as f:
        return json.load(f)


def cleanup_expired_artifacts(ttl_days: int = 30):
    """Clean up expired artifacts based on TTL"""
    artifacts_dir = Path("_artifacts")
    vault_dir = artifacts_dir / "vault"
    
    if not vault_dir.exists():
        return
    
    cutoff_date = datetime.utcnow() - timedelta(days=ttl_days)
    
    for journey_dir in vault_dir.iterdir():
        if not journey_dir.is_dir():
            continue
        
        # Check if journey directory is expired
        journey_created_file = journey_dir / "intake" / "intake.json"
        if journey_created_file.exists():
            try:
                with open(journey_created_file, 'r') as f:
                    journey_data = json.load(f)
                    created_at_str = journey_data.get("created_at")
                    if created_at_str:
                        created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                        if created_at < cutoff_date:
                            # Remove expired journey
                            shutil.rmtree(journey_dir)
                            print(f"Removed expired journey: {journey_dir}")
            except (json.JSONDecodeError, ValueError) as e:
                print(f"Error processing journey {journey_dir}: {e}")
                continue


def list_artifacts(journey_id: str = None) -> Dict[str, Any]:
    """List all artifacts or artifacts for a specific journey"""
    artifacts_dir = Path("_artifacts")
    
    if not artifacts_dir.exists():
        return {"artifacts": [], "total": 0}
    
    artifacts = []
    
    if journey_id:
        # List artifacts for specific journey
        vault_dir = artifacts_dir / "vault" / journey_id
        if vault_dir.exists():
            for file_path in vault_dir.rglob("*.json"):
                relative_path = file_path.relative_to(artifacts_dir)
                artifacts.append({
                    "path": str(relative_path),
                    "size": file_path.stat().st_size,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
    else:
        # List all artifacts
        for file_path in artifacts_dir.rglob("*.json"):
            relative_path = file_path.relative_to(artifacts_dir)
            artifacts.append({
                "path": str(relative_path),
                "size": file_path.stat().st_size,
                "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            })
    
    return {
        "artifacts": artifacts,
        "total": len(artifacts)
    }


def get_artifact_stats() -> Dict[str, Any]:
    """Get statistics about stored artifacts"""
    artifacts_dir = Path("_artifacts")
    
    if not artifacts_dir.exists():
        return {
            "total_journeys": 0,
            "total_artifacts": 0,
            "total_size_bytes": 0,
            "oldest_artifact": None,
            "newest_artifact": None
        }
    
    total_size = 0
    total_artifacts = 0
    dates = []
    
    for file_path in artifacts_dir.rglob("*.json"):
        total_size += file_path.stat().st_size
        total_artifacts += 1
        dates.append(file_path.stat().st_mtime)
    
    # Count unique journeys
    vault_dir = artifacts_dir / "vault"
    total_journeys = 0
    if vault_dir.exists():
        total_journeys = len([d for d in vault_dir.iterdir() if d.is_dir()])
    
    return {
        "total_journeys": total_journeys,
        "total_artifacts": total_artifacts,
        "total_size_bytes": total_size,
        "oldest_artifact": datetime.fromtimestamp(min(dates)).isoformat() if dates else None,
        "newest_artifact": datetime.fromtimestamp(max(dates)).isoformat() if dates else None
    }
