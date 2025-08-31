# Unemployment and Emergency Services Features

This document describes the new features added to the Community Agent project to support unemployment and emergency/disaster recovery scenarios.

## Overview

The Community Agent now supports multiple life events beyond birth registration, including:

1. **Unemployment/Job Loss** - JobSeeker Payment and Job Service Provider registration
2. **Emergency/Disaster Recovery** - Emergency Disaster Payment and Housing Assistance
3. **Carer Support** - Carer Payment and Allowance applications

These features address the core problems identified in government services:

- Too many separate offices and departments
- Repetitive forms and paperwork
- Confusing eligibility rules
- Poor timing during stressful life events
- Lack of information sharing between agencies
- Digital barriers for vulnerable populations

## New Form Definitions

### Unemployment Services

#### 1. Centrelink JobSeeker Payment (`unemployment_centrelink.v1.yml`)

- **Purpose**: Apply for unemployment benefits through Centrelink
- **Key Fields**:
  - Applicant personal information (name, DOB, contact details)
  - Employment history (last employer, last work date, reason for unemployment)
  - Banking details for payments
  - Address information
- **Processing Time**: 2-4 weeks
- **Source**: Services Australia - JobSeeker Payment

#### 2. Job Service Provider Registration (`job_service_provider.v1.yml`)

- **Purpose**: Register with a job service provider for employment assistance
- **Key Fields**:
  - Applicant personal information
  - Skills assessment requirements
  - Training interests and work preferences
  - Resume upload capability
- **Processing Time**: Varies by provider
- **Source**: Department of Employment and Workplace Relations - Jobactive

### Emergency/Disaster Recovery Services

#### 1. Emergency Disaster Payment (`emergency_disaster_payment.v1.yml`)

- **Purpose**: Apply for emergency financial assistance after a disaster
- **Key Fields**:
  - Applicant personal information
  - Disaster details (type, date, location, property damage)
  - Banking details for immediate payments
- **Processing Time**: 1-3 business days for urgent cases
- **Source**: Services Australia - Disaster Recovery Payment

#### 2. Emergency Housing Assistance (`emergency_housing_assistance.v1.yml`)

- **Purpose**: Apply for emergency housing support after a disaster
- **Key Fields**:
  - Applicant personal information
  - Disaster details
  - Housing status and damage description
  - Special needs and accessibility requirements
  - Temporary accommodation needs
- **Processing Time**: Varies based on availability and urgency
- **Source**: State Emergency Services - Emergency Housing

## New Data Models

### Employment Model

```python
class Employment(BaseModel):
    last_employer: Optional[str] = None
    last_work_date: Optional[date] = None
    reason_for_unemployment: Optional[str] = None
    preferred_provider: Optional[str] = None
    skills_assessment: Optional[bool] = None
    training_interests: Optional[List[str]] = None
    work_preferences: Optional[List[str]] = None
    resume_upload: Optional[str] = None
```

### Banking Model

```python
class Banking(BaseModel):
    bsb: Optional[str] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
```

### Disaster Model

```python
class Disaster(BaseModel):
    type: Optional[str] = None
    date: Optional[date] = None
    location: Optional[str] = None
    property_damage: Optional[str] = None
```

### Housing Model

```python
class Housing(BaseModel):
    status: Optional[str] = None
    damage_description: Optional[str] = None
    household_size: Optional[int] = None
    special_needs: Optional[List[str]] = None
    temporary_accommodation_needed: Optional[bool] = None
```

## Enhanced Orchestrator

The `JourneyOrchestrator` now automatically detects life events and creates appropriate journey plans:

### Life Event Detection

- **Baby Just Born**: Detected when `intake.baby` and `intake.parent1` are present
- **Job Loss**: Detected when `intake.employment` and `intake.applicant` are present
- **Disaster Recovery**: Detected when `intake.disaster` and `intake.applicant` are present
- **Carer Support**: Detected when `intake.applicant` and carer information are present

### Journey Planning

Each life event gets a tailored set of journey steps:

#### Unemployment Journey

1. Centrelink JobSeeker Payment application
2. Job Service Provider registration

#### Disaster Recovery Journey

1. Emergency Disaster Payment application
2. Emergency Housing Assistance application

#### Carer Support Journey

1. Carer Payment application
2. Carer Allowance application

## Automation Support

### Unemployment Automation (`unemployment_centrelink_playwright.py`)

- Automates JobSeeker Payment form filling
- Handles employment history and banking details
- Generates mock receipts for demonstration
- Saves automation artifacts for audit trail

### Emergency Disaster Automation (`emergency_disaster_playwright.py`)

- Automates Emergency Disaster Payment form filling
- Handles disaster details and property damage information
- Generates mock receipts for demonstration
- Saves automation artifacts for audit trail

## Demo Scripts

### `demo_unemployment.py`

Demonstrates the complete unemployment services workflow:

- Creates sample unemployment intake data
- Plans unemployment journey
- Prefills and submits forms
- Shows automation capabilities

### `demo_emergency.py`

Demonstrates the complete disaster recovery workflow:

- Creates sample disaster recovery intake data
- Plans disaster recovery journey
- Prefills and submits forms
- Shows automation capabilities

## Usage Examples

### Unemployment Scenario

```python
from app.models import Intake, Person, Employment, Banking
from app.orchestrator import JourneyOrchestrator

# Create unemployment intake
intake = Intake(
    applicant=Person(full_name="John Smith", dob=date(1985, 6, 15)),
    employment=Employment(
        last_employer="ABC Company",
        last_work_date=date(2025, 8, 1),
        reason_for_unemployment="Redundancy"
    ),
    banking=Banking(bsb="012-345", account_number="12345678")
)

# Plan journey
orchestrator = JourneyOrchestrator()
journey = orchestrator.plan_journey(intake, jurisdiction="NSW")

# Journey will automatically include:
# - Centrelink JobSeeker Payment step
# - Job Service Provider Registration step
```

### Disaster Recovery Scenario

```python
from app.models import Intake, Person, Disaster, Housing

# Create disaster recovery intake
intake = Intake(
    applicant=Person(full_name="Sarah Johnson", dob=date(1980, 3, 20)),
    disaster=Disaster(
        type="Flood",
        date=date(2025, 8, 15),
        location="Lismore, NSW"
    ),
    housing=Housing(
        status="Displaced",
        temporary_accommodation_needed=True
    )
)

# Plan journey
journey = orchestrator.plan_journey(intake, jurisdiction="NSW")

# Journey will automatically include:
# - Emergency Disaster Payment step
# - Emergency Housing Assistance step
```

## Benefits

### For Users

1. **Simplified Navigation**: Single intake process for multiple related services
2. **Reduced Repetition**: Information entered once, used across multiple forms
3. **Clear Guidance**: Step-by-step journey through complex government processes
4. **Faster Processing**: Automated form filling reduces manual data entry

### For Government Agencies

1. **Better User Experience**: Streamlined service delivery
2. **Reduced Errors**: Consistent data across multiple forms
3. **Improved Efficiency**: Less time spent on repetitive data collection
4. **Better Coordination**: Integrated approach to related services

## Future Enhancements

### Planned Features

1. **Real-time Status Tracking**: Monitor application progress across agencies
2. **Integrated Notifications**: Unified communication about all related services
3. **Smart Recommendations**: AI-powered suggestions for additional support
4. **Multi-language Support**: Expanded language options for diverse communities

### Integration Opportunities

1. **Centrelink APIs**: Direct integration with real government systems
2. **State Agency Systems**: Connect with state-level emergency services
3. **Local Council Services**: Integrate with community-level support
4. **Third-party Providers**: Connect with job service providers and training organizations

## Testing

### Running Demos

```bash
# Test unemployment services
python demo_unemployment.py

# Test emergency services
python demo_emergency.py
```

### Manual Testing

1. Create intake data for different life events
2. Verify journey planning creates correct steps
3. Test form prefill functionality
4. Validate form submission and receipt generation

## Security and Privacy

### Data Protection

- No sensitive data hardcoded in automation scripts
- Comprehensive audit logging of all actions
- Secure storage in vault directory structure
- Consent-based data sharing between services

### Compliance

- Follows government data handling guidelines
- Maintains audit trails for regulatory compliance
- Supports consent management and withdrawal
- Implements data retention policies

## Support and Documentation

### Getting Help

- Check the main README.md for project overview
- Review form YAML files for field definitions
- Examine automation scripts for implementation details
- Use demo scripts as working examples

### Contributing

- Follow existing code patterns and structure
- Add comprehensive documentation for new features
- Include demo scripts for new services
- Maintain backward compatibility where possible

---

This document provides a comprehensive overview of the new unemployment and emergency services features. For specific implementation details, refer to the individual source files and demo scripts.

