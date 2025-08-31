from datetime import datetime, date
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class Sex(str, Enum):
    MALE = "M"
    FEMALE = "F"
    OTHER = "X"


class Address(BaseModel):
    line1: str
    suburb: str
    state: str
    postcode: str


class Person(BaseModel):
    full_name: str
    dob: date
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None


class Baby(BaseModel):
    name: Optional[str] = None
    sex: Optional[Sex] = None
    dob: date
    place_of_birth: Optional[str] = None
    parents: List[Person]


class Employment(BaseModel):
    last_employer: Optional[str] = None
    last_work_date: Optional[date] = None
    reason_for_unemployment: Optional[str] = None
    preferred_provider: Optional[str] = None
    skills_assessment: Optional[bool] = None
    training_interests: Optional[List[str]] = None
    work_preferences: Optional[List[str]] = None
    resume_upload: Optional[str] = None


class Banking(BaseModel):
    bsb: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None


class Disaster(BaseModel):
    type: Optional[str] = None
    date: Optional[date] = None
    location: Optional[str] = None
    property_damage: Optional[str] = None


class Housing(BaseModel):
    status: Optional[str] = None
    damage_description: Optional[str] = None
    household_size: Optional[int] = None
    special_needs: Optional[List[str]] = None
    temporary_accommodation_needed: Optional[bool] = None


class Consent(BaseModel):
    scope: List[str] = Field(description="List of consent scopes (e.g., ['birth_registration', 'medicare_enrolment', 'jobseeker_payment', 'disaster_payment'])")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    ttl_days: int = Field(default=30, description="Time to live in days")
    signature: Optional[str] = None


class Artifact(BaseModel):
    type: str = Field(description="Type of artifact (intake, submission, consent, etc.)")
    path: str = Field(description="File path to the artifact")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    step_id: Optional[str] = None


class JourneyStep(BaseModel):
    id: str
    title: str
    status: str = Field(default="pending", description="pending, in_progress, completed, failed")
    artifacts: List[Artifact] = Field(default_factory=list)


class Journey(BaseModel):
    id: str
    life_event: str = Field(default="baby_just_born", description="baby_just_born, job_loss, disaster_recovery, carer_support")
    jurisdiction: str = Field(default="NSW")
    steps: List[JourneyStep] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Intake(BaseModel):
    # Birth-related fields
    parent1: Optional[Person] = None
    parent2: Optional[Person] = None
    baby: Optional[Baby] = None
    
    # Unemployment-related fields
    applicant: Optional[Person] = None
    employment: Optional[Employment] = None
    banking: Optional[Banking] = None
    
    # Emergency/Disaster-related fields
    disaster: Optional[Disaster] = None
    housing: Optional[Housing] = None
    
    # Common fields
    preferred_language: str = Field(default="en")
    accessibility: List[str] = Field(default_factory=list, description="List of accessibility needs")
    address: Optional[Address] = None


class FormField(BaseModel):
    id: str
    label: str
    required: bool
    source: str = Field(description="Dotted path to intake data (e.g., 'parent1.full_name')")


class FormSchema(BaseModel):
    id: str
    title: str
    description: str
    fields: List[FormField]
    review_text: str
    receipt_expected: bool = True


class PrefillResponse(BaseModel):
    form_id: str
    data: Dict[str, Any]
    review: Dict[str, Any]
    review_text: str


class ConsentRequest(BaseModel):
    journey_id: str
    consent: Consent


class SubmissionResponse(BaseModel):
    reference: str
    form_id: str
    submitted_at: datetime
    receipt_url: Optional[str] = None


class IntakeResponse(BaseModel):
    journey_id: str
    plan: Journey
