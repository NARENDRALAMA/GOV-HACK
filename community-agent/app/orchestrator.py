import yaml
import json
import hashlib
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

from .models import (
    Journey, JourneyStep, Intake, FormSchema, 
    PrefillResponse, SubmissionResponse, Artifact
)
from .utils.storage import save_artifact, get_vault_path
from .utils.audit import log_event


class JourneyOrchestrator:
    """Orchestrates the journey through life events with form automation"""
    
    def __init__(self):
        self.forms_dir = Path(__file__).parent / "forms"
        self.artifacts_dir = Path("_artifacts")
        self.artifacts_dir.mkdir(exist_ok=True)
    
    def plan_journey(self, intake: Intake, jurisdiction: str = "NSW") -> Journey:
        """Create a journey plan based on the life event type"""
        journey_id = self._generate_journey_id(intake)
        life_event = self._determine_life_event(intake)
        
        # Define journey steps based on life event and jurisdiction
        if life_event == "baby_just_born":
            steps = self._get_birth_journey_steps(jurisdiction)
        elif life_event == "job_loss":
            steps = self._get_unemployment_journey_steps(jurisdiction)
        elif life_event == "disaster_recovery":
            steps = self._get_disaster_journey_steps(jurisdiction)
        elif life_event == "carer_support":
            steps = self._get_carer_journey_steps(jurisdiction)
        else:
            # Default to birth journey for backward compatibility
            steps = self._get_birth_journey_steps(jurisdiction)
        
        journey = Journey(
            id=journey_id,
            life_event=life_event,
            jurisdiction=jurisdiction,
            steps=steps
        )
        
        # Save intake to vault
        self._save_intake_to_vault(journey_id, intake)
        
        # Log journey creation
        log_event(
            actor="system",
            action="journey_created",
            why=f"New {life_event} journey initiated",
            consent_id=None,
            metadata={"journey_id": journey_id, "jurisdiction": jurisdiction, "life_event": life_event}
        )
        
        return journey
    
    def _determine_life_event(self, intake: Intake) -> str:
        """Determine the life event type based on intake data"""
        if intake.baby and intake.parent1:
            return "baby_just_born"
        elif intake.employment and intake.applicant:
            return "job_loss"
        elif intake.disaster and intake.applicant:
            return "disaster_recovery"
        elif intake.applicant and hasattr(intake, 'carer_info') and intake.carer_info:
            return "carer_support"
        else:
            # Default to birth event for backward compatibility
            return "baby_just_born"
    
    def _get_birth_journey_steps(self, jurisdiction: str) -> List[JourneyStep]:
        """Get journey steps for birth of a baby"""
        if jurisdiction == "NSW":
            return [
                JourneyStep(
                    id="birth_reg",
                    title="Birth Registration (NSW)",
                    status="pending"
                ),
                JourneyStep(
                    id="medicare_enrolment",
                    title="Medicare Newborn Enrolment",
                    status="pending"
                )
            ]
        else:
            return [
                JourneyStep(
                    id="birth_reg",
                    title="Birth Registration",
                    status="pending"
                ),
                JourneyStep(
                    id="medicare_enrolment",
                    title="Medicare Newborn Enrolment",
                    status="pending"
                )
            ]
    
    def _get_unemployment_journey_steps(self, jurisdiction: str) -> List[JourneyStep]:
        """Get journey steps for unemployment/job loss"""
        return [
            JourneyStep(
                id="unemployment_centrelink",
                title="Centrelink JobSeeker Payment",
                status="pending"
            ),
            JourneyStep(
                id="job_service_provider",
                title="Job Service Provider Registration",
                status="pending"
            )
        ]
    
    def _get_disaster_journey_steps(self, jurisdiction: str) -> List[JourneyStep]:
        """Get journey steps for disaster recovery"""
        return [
            JourneyStep(
                id="emergency_disaster_payment",
                title="Emergency Disaster Payment",
                status="pending"
            ),
            JourneyStep(
                id="emergency_housing_assistance",
                title="Emergency Housing Assistance",
                status="pending"
            )
        ]
    
    def _get_carer_journey_steps(self, jurisdiction: str) -> List[JourneyStep]:
        """Get journey steps for carer support"""
        return [
            JourneyStep(
                id="carer_payment",
                title="Carer Payment Application",
                status="pending"
            ),
            JourneyStep(
                id="carer_allowance",
                title="Carer Allowance Application",
                status="pending"
            )
        ]
    
    def prefill_form(self, journey_id: str, step_id: str, intake: Intake) -> PrefillResponse:
        """Prefill a form based on the step and intake data"""
        # Load form schema
        form_schema = self._load_form_schema(step_id)
        
        # Map intake data to form fields
        form_data = {}
        for field in form_schema.fields:
            value = self._get_value_from_path(intake, field.source)
            if value is not None:
                form_data[field.id] = value
        
        # Create review payload
        review = {
            "form_id": form_schema.id,
            "step_id": step_id,
            "fields": form_data,
            "review_text": form_schema.review_text
        }
        
        # Save prefill artifact
        prefill_artifact = Artifact(
            type="prefill",
            path=f"vault/{journey_id}/prefill/{step_id}_prefill.json",
            step_id=step_id
        )
        
        prefill_data = {
            "journey_id": journey_id,
            "step_id": step_id,
            "form_data": form_data,
            "created_at": datetime.utcnow().isoformat()
        }
        
        save_artifact(
            prefill_artifact.path,
            prefill_data,
            "prefill"
        )
        
        return PrefillResponse(
            form_id=form_schema.id,
            data=form_data,
            review=review,
            review_text=form_schema.review_text
        )
    
    def submit_form(self, journey_id: str, step_id: str, form_data: Dict[str, Any]) -> SubmissionResponse:
        """Submit a form and generate receipt"""
        # Generate reference number
        reference = self._generate_reference(step_id, journey_id)
        
        # Create submission response
        submission_response = SubmissionResponse(
            reference=reference,
            form_id=step_id,
            submitted_at=datetime.utcnow()
        )
        
        # Save submission artifact
        submission_artifact = Artifact(
            type="submission",
            path=f"vault/{journey_id}/submissions/{step_id}_submission.json",
            step_id=step_id
        )
        
        submission_data = {
            "journey_id": journey_id,
            "step_id": step_id,
            "form_data": form_data,
            "reference": reference,
            "submitted_at": datetime.utcnow().isoformat(),
            "status": "submitted"
        }
        
        save_artifact(
            str(submission_artifact.path),
            submission_data,
            "submission"
        )
        
        # Log submission
        log_event(
            actor="user",
            action="form_submitted",
            why=f"Form {step_id} submitted for journey {journey_id}",
            consent_id=None,
            metadata={
                "journey_id": journey_id,
                "step_id": step_id,
                "reference": reference
            }
        )
        
        return submission_response
    
    def _generate_journey_id(self, intake: Intake) -> str:
        """Generate a unique journey ID based on intake data and life event"""
        life_event = self._determine_life_event(intake)
        
        if life_event == "baby_just_born" and intake.baby and intake.parent1:
            # Create a hash from baby's DOB and parent names
            hash_input = f"{intake.baby.dob}{intake.parent1.full_name}"
            if intake.parent2:
                hash_input += intake.parent2.full_name
        elif life_event == "job_loss" and intake.applicant:
            # Create a hash from applicant's DOB and name
            hash_input = f"{intake.applicant.dob}{intake.applicant.full_name}"
            if intake.employment and intake.employment.last_work_date:
                hash_input += str(intake.employment.last_work_date)
        elif life_event == "disaster_recovery" and intake.applicant:
            # Create a hash from applicant's DOB and disaster details
            hash_input = f"{intake.applicant.dob}{intake.applicant.full_name}"
            if intake.disaster and intake.disaster.date:
                hash_input += str(intake.disaster.date)
        elif life_event == "carer_support" and intake.applicant:
            # Create a hash from applicant's DOB and name
            hash_input = f"{intake.applicant.dob}{intake.applicant.full_name}"
        else:
            # Fallback hash from timestamp and random data
            hash_input = f"{datetime.utcnow().isoformat()}{life_event}"
        
        hash_obj = hashlib.sha256(hash_input.encode())
        return f"journey_{hash_obj.hexdigest()[:12]}"
    
    def _generate_reference(self, step_id: str, journey_id: str) -> str:
        """Generate a reference number for form submission"""
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        hash_obj = hashlib.sha256(f"{step_id}{journey_id}{timestamp}".encode())
        return f"{step_id.upper()[:2]}-{hash_obj.hexdigest()[:8]}"
    
    def _save_intake_to_vault(self, journey_id: str, intake: Intake):
        """Save intake data to the vault directory"""
        vault_path = get_vault_path(journey_id)
        intake_path = vault_path / "intake" / "intake.json"
        intake_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert to dict for JSON serialization
        intake_dict = intake.dict()
        intake_dict["created_at"] = datetime.utcnow().isoformat()
        
        save_artifact(
            str(intake_path),
            intake_dict,
            "intake"
        )
    
    def _load_form_schema(self, step_id: str) -> FormSchema:
        """Load form schema from YAML file"""
        form_file = self.forms_dir / f"{step_id}.yml"
        
        if not form_file.exists():
            # Fallback to default schema
            return self._get_default_schema(step_id)
        
        with open(form_file, 'r') as f:
            form_data = yaml.safe_load(f)
        
        return FormSchema(**form_data)
    
    def _get_default_schema(self, step_id: str) -> FormSchema:
        """Get default form schema if YAML file doesn't exist"""
        if step_id == "birth_reg":
            return FormSchema(
                id="birth_registry_nsw",
                title="Birth Registration (NSW)",
                description="Register the birth of your baby with NSW Registry of Births, Deaths and Marriages",
                fields=[
                    {"id": "parent1_full_name", "label": "Parent 1 Full Name", "required": True, "source": "parent1.full_name"},
                    {"id": "parent1_dob", "label": "Parent 1 Date of Birth", "required": True, "source": "parent1.dob"},
                    {"id": "baby_name", "label": "Baby's Name", "required": False, "source": "baby.name"},
                    {"id": "baby_dob", "label": "Baby's Date of Birth", "required": True, "source": "baby.dob"},
                    {"id": "place_of_birth", "label": "Place of Birth", "required": False, "source": "baby.place_of_birth"}
                ],
                review_text="Please review the birth registration details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        elif step_id == "medicare_enrolment":
            return FormSchema(
                id="medicare_newborn",
                title="Medicare Newborn Enrolment",
                description="Enrol your newborn baby for Medicare coverage",
                fields=[
                    {"id": "parent1_full_name", "label": "Parent 1 Full Name", "required": True, "source": "parent1.full_name"},
                    {"id": "baby_name", "label": "Baby's Name", "required": False, "source": "baby.name"},
                    {"id": "baby_dob", "label": "Baby's Date of Birth", "required": True, "source": "baby.dob"}
                ],
                review_text="Please review the Medicare enrolment details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        elif step_id == "unemployment_centrelink":
            return FormSchema(
                id="unemployment_centrelink",
                title="Centrelink JobSeeker Payment",
                description="Apply for unemployment benefits through Centrelink",
                fields=[
                    {"id": "applicant_full_name", "label": "Full Name", "required": True, "source": "applicant.full_name"},
                    {"id": "applicant_dob", "label": "Date of Birth", "required": True, "source": "applicant.dob"},
                    {"id": "last_employer", "label": "Last Employer Name", "required": False, "source": "employment.last_employer"},
                    {"id": "last_work_date", "label": "Last Day of Work", "required": False, "source": "employment.last_work_date"}
                ],
                review_text="Please review your JobSeeker Payment application details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        elif step_id == "job_service_provider":
            return FormSchema(
                id="job_service_provider",
                title="Job Service Provider Registration",
                description="Register with a job service provider for employment assistance",
                fields=[
                    {"id": "applicant_full_name", "label": "Full Name", "required": True, "source": "applicant.full_name"},
                    {"id": "applicant_dob", "label": "Date of Birth", "required": True, "source": "applicant.dob"},
                    {"id": "skills_assessment", "label": "Skills Assessment Required", "required": False, "source": "employment.skills_assessment"}
                ],
                review_text="Please review your Job Service Provider registration details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        elif step_id == "emergency_disaster_payment":
            return FormSchema(
                id="emergency_disaster_payment",
                title="Emergency Disaster Payment",
                description="Apply for emergency financial assistance after a disaster",
                fields=[
                    {"id": "applicant_full_name", "label": "Full Name", "required": True, "source": "applicant.full_name"},
                    {"id": "applicant_dob", "label": "Date of Birth", "required": True, "source": "applicant.dob"},
                    {"id": "disaster_type", "label": "Type of Disaster", "required": False, "source": "disaster.type"},
                    {"id": "disaster_date", "label": "Date of Disaster", "required": False, "source": "disaster.date"}
                ],
                review_text="Please review your Emergency Disaster Payment application details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        elif step_id == "emergency_housing_assistance":
            return FormSchema(
                id="emergency_housing_assistance",
                title="Emergency Housing Assistance",
                description="Apply for emergency housing support after a disaster",
                fields=[
                    {"id": "applicant_full_name", "label": "Full Name", "required": True, "source": "applicant.full_name"},
                    {"id": "applicant_dob", "label": "Date of Birth", "required": True, "source": "applicant.dob"},
                    {"id": "disaster_type", "label": "Type of Disaster", "required": False, "source": "disaster.type"},
                    {"id": "housing_status", "label": "Current Housing Status", "required": False, "source": "housing.status"}
                ],
                review_text="Please review your Emergency Housing Assistance application details above. All required fields have been completed based on your intake information.",
                receipt_expected=True
            )
        else:
            raise ValueError(f"Unknown step_id: {step_id}")
    
    def _get_value_from_path(self, obj: Any, path: str) -> Any:
        """Get value from object using dotted path notation"""
        try:
            for key in path.split('.'):
                if hasattr(obj, key):
                    obj = getattr(obj, key)
                elif isinstance(obj, dict):
                    obj = obj[key]
                else:
                    return None
            return obj
        except (AttributeError, KeyError, TypeError):
            return None
