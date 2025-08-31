# Agentic Community Assistant

An AI-powered assistant that guides users through life events with automated form completion, supporting multiple life events including birth registration, unemployment support, and emergency/disaster recovery. The system automates government form completion with a focus on autonomy, accessibility, privacy, and auditability.

## 🎯 High-Level Goals

- **Input via API**: Accept structured intake data and generate personalized journey plans
- **Automated Form Prefilling**: Map intake data to government forms using YAML schemas
- **Human Review & Consent**: Support human review with explicit consent management
- **Mock/API/RPA Submission**: Demonstrate end-to-end automation with Playwright
- **Audit Trail**: Complete logging of all actions with SHA-256 hashing
- **Privacy-First**: PII stored in secure vault with TTL, no plaintext in logs
- **Multi-Life Event Support**: Handle birth registration, unemployment, disaster recovery, and carer support

## 🏗️ Architecture

- **Frontend**: Modern, responsive web interface with Tailwind CSS
- **Backend**: FastAPI with async support
- **Agentic AI**: Intelligent agent with natural language understanding and autonomous workflow execution
- **RAG**: Government datasets integration (NSW BDM, ABS demographics, service locations)
- **Orchestration**: Multi-step workflow planning and execution with life event detection
- **Automation**: Playwright skeleton for headless form filling across multiple services
- **Data Models**: Pydantic with comprehensive validation for multiple life events
- **Privacy**: Vault-based storage with automatic TTL cleanup
- **Audit**: JSONL audit log with cryptographic hashing
- **Inclusivity**: Demographic-based accessibility and language support

## 🚀 Quick Start

### Prerequisites

- macOS (tested on macOS 13+)
- Python 3.8+
- Git

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd community-agent

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
python3 -m pip install --upgrade pip
pip install -r requirements.txt

# Install Playwright browsers
python3 -m playwright install

# Copy environment configuration
cp env.example .env
# Edit .env with your configuration
```

### Running the Application

```bash
# Start the FastAPI server
python3 -m uvicorn app.main:app --reload

# Open the beautiful web interface
open http://localhost:8000

# Or view API documentation
open http://localhost:8000/docs
```

## 📚 API Endpoints

### Core Endpoints

| Endpoint                       | Method | Description                         |
| ------------------------------ | ------ | ----------------------------------- |
| `/intake`                      | POST   | Create new journey with intake data |
| `/plan/{journey_id}`           | GET    | Get journey plan and steps          |
| `/prefill/{journey_id}/{step}` | POST   | Prefill form for specific step      |
| `/consent/{journey_id}`        | POST   | Grant consent for journey           |
| `/submit/{journey_id}/{step}`  | POST   | Submit form and get receipt         |
| `/artifacts`                   | GET    | List artifacts (metadata only)      |
| `/audit`                       | GET    | Get audit trail and consent summary |

### Health & Maintenance

| Endpoint   | Method | Description                |
| ---------- | ------ | -------------------------- |
| `/health`  | GET    | Service health check       |
| `/cleanup` | POST   | Clean up expired artifacts |

## 🧪 Demo Options

### Option 1: Beautiful Web Interface (Recommended for Users)

```bash
# Start the server
python3 -m uvicorn app.main:app --reload

# Open the web interface
```

### Option 2: Command Line Demos

```bash
# Test birth registration services
python3 demo.py

# Test unemployment services
python3 demo_unemployment.py

# Test emergency/disaster recovery services
python3 demo_emergency.py

# Test web interface
python3 demo_web.py
```

### Option 3: Agentic AI Demo

```bash
# Test the intelligent agent
python3 demo_agentic.py
```

## 🌟 Supported Life Events

### 1. Birth Registration (Original)

- **NSW Birth Registry**: Automated birth certificate registration
- **Medicare Newborn Enrolment**: Automatic Medicare coverage setup
- **Processing**: 5-10 business days for birth registration, 2-3 weeks for Medicare

### 2. Unemployment Support (New)

- **Centrelink JobSeeker Payment**: Unemployment benefits application
- **Job Service Provider Registration**: Employment assistance and training
- **Processing**: 2-4 weeks for JobSeeker, varies for job services

### 3. Emergency/Disaster Recovery (New)

- **Emergency Disaster Payment**: Immediate financial assistance
- **Emergency Housing Assistance**: Temporary accommodation support
- **Processing**: 1-3 business days for urgent payments, varies for housing

### 4. Carer Support (Planned)

- **Carer Payment**: Financial support for full-time carers
- **Carer Allowance**: Additional assistance for carers
- **Processing**: Varies based on assessment requirements

## 🔧 Life Event Detection

The system automatically detects life events based on intake data:

- **Baby Just Born**: Detected when `intake.baby` and `intake.parent1` are present
- **Job Loss**: Detected when `intake.employment` and `intake.applicant` are present
- **Disaster Recovery**: Detected when `intake.disaster` and `intake.applicant` are present
- **Carer Support**: Detected when `intake.applicant` and carer information are present

Each life event gets a tailored journey plan with appropriate government services.

### 2. Get Journey Plan

```bash
# Replace {journey_id} with the ID from step 1
curl "http://localhost:8000/plan/{journey_id}"
```

**Expected Response**: Complete journey with pending steps.

### 3. Prefill Birth Registration Form

```bash
curl -X POST "http://localhost:8000/prefill/{journey_id}/birth_reg"
```

**Expected Response**: Prefilled form data and review information.

### 4. Grant Consent

```bash
curl -X POST "http://localhost:8000/consent/{journey_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "journey_id": "{journey_id}",
    "consent": {
      "scope": ["birth_registration", "medicare_enrolment"],
      "ttl_days": 30,
      "signature": "Jane Doe"
    }
  }'
```

**Expected Response**: Consent ID and confirmation.

### 5. Submit Birth Registration

```bash
curl -X POST "http://localhost:8000/submit/{journey_id}/birth_reg" \
  -H "Content-Type: application/json" \
  -d '{
    "parent1_full_name": "Jane Doe",
    "parent1_dob": "1990-01-01",
    "baby_name": "Baby Doe",
    "baby_dob": "2025-08-28",
    "place_of_birth": "Westmead Hospital"
  }'
```

**Expected Response**: Receipt with reference number.

### 6. Repeat for Medicare Enrolment

```bash
# Prefill Medicare form
curl -X POST "http://localhost:8000/prefill/{journey_id}/medicare_enrolment"

# Submit Medicare form
curl -X POST "http://localhost:8000/submit/{journey_id}/medicare_enrolment" \
  -H "Content-Type: application/json" \
  -d '{
    "parent1_full_name": "Jane Doe",
    "parent1_dob": "1990-01-01",
    "baby_name": "Baby Doe",
    "baby_dob": "2025-08-28"
  }'
```

### 7. View Artifacts and Audit Trail

```bash
# List all artifacts
curl "http://localhost:8000/artifacts"

# Get audit trail
curl "http://localhost:8000/audit"

# Get specific journey artifacts
curl "http://localhost:8000/artifacts?journey_id={journey_id}"
```

## 🤖 Agentic AI Features

### Natural Language Understanding

- **Intent Recognition**: Automatically detects user needs (birth registration, Medicare, etc.)
- **Entity Extraction**: Identifies locations, postcodes, dates, and other key information
- **Context Awareness**: Understands complex requests like "My baby was born yesterday in Parramatta"

### Government Data Integration (RAG)

- **NSW BDM Service Locations**: Real service office data with addresses and contact details
- **Birth Registration Requirements**: Official NSW guidance with source URLs and citations
- **ABS Demographics**: Postcode-based demographic data for inclusivity logic
- **Service Proximity**: Finds nearest government service locations based on postcode

### Autonomous Workflow Execution

- **Multi-Step Planning**: Creates complete journeys from single requests
- **Intelligent Orchestration**: Chains together birth registration → Medicare enrolment
- **Form Prefilling**: Automatically populates government forms with extracted data
- **Progress Tracking**: Monitors and reports on workflow completion status

### Inclusivity & Accessibility

- **Language Support**: Offers multilingual assistance for high non-English speaking areas (>40%)
- **Age-Based Preferences**: Suggests voice/SMS updates for older demographics (median age >60)
- **Disability Considerations**: Adapts interface for areas with higher disability rates
- **Cultural Sensitivity**: Provides appropriate support for Indigenous communities

## 🔒 Privacy & Security Features

### PII Vault

- All personal information stored in `_artifacts/vault/{journey_id}/`
- Automatic TTL-based cleanup (default: 30 days)
- No PII in application logs or audit trails

### Consent Management

- Explicit consent required for each action
- Consent ledger with cryptographic hashing
- Audit trail for all consent actions
- TTL-based consent expiration

### Audit Trail

- JSONL format audit log with SHA-256 hashing
- No plaintext PII in audit entries
- Comprehensive metadata for compliance
- Immutable audit records

## 📊 Open Dataset Integration

The system integrates with government open datasets through the RAG knowledge base:

- **NSW BDM**: Birth registration requirements and processing times
- **Services Australia**: Medicare newborn enrolment information
- **ABS Data**: Birth statistics and population data
- **Health Services**: Immunisation schedules and requirements

All sources are cited with URLs in `app/rag/knowledge.md` and referenced in responses.

## 🎭 Playwright Automation

The system includes a Playwright automation skeleton for form filling:

```bash
# Test automation (demo mode)
cd app/automation
python birth_registry_playwright.py
```

**Features**:

- Headless browser automation
- Field mapping from intake data
- Error handling and logging
- Mock receipt generation
- Artifact saving for audit trail

**Safety**: Uses placeholder URLs and generates mock receipts for demonstration.

## 📁 Repository Structure

```
community-agent/
├── app/
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic data models
│   ├── orchestrator.py          # Journey orchestration logic
│   ├── forms/                   # YAML form schemas
│   ├── automation/              # Playwright automation
│   ├── utils/                   # Storage and audit utilities
│   └── rag/                     # Knowledge base
├── requirements.txt             # Python dependencies
├── env.example                  # Environment configuration
├── README.md                    # This file
└── LICENSE                      # License information
```

## 🔧 Configuration

### Environment Variables

Copy `env.example` to `.env` and configure:

- **Server settings**: Host, port, debug mode
- **Security**: Secret keys, token expiration
- **Privacy**: TTL settings, audit levels
- **Automation**: Playwright settings
- **Storage**: File paths and size limits

### Form Schemas

Form schemas are defined in YAML format in `app/forms/`:

- Field definitions with validation rules
- Source mapping to intake data
- Review text and instructions
- Receipt expectations

## 🚀 Future Enhancements

### Planned Features

- **SMS/WhatsApp Integration**: Multi-channel support
- **Voice Interface**: IVR and speech recognition
- **Real Government APIs**: Integration with actual services
- **Advanced RAG**: Vector embeddings and semantic search
- **Multi-language Support**: Internationalization
- **Mobile App**: Native iOS/Android applications

### Architecture Improvements

- **Database Integration**: PostgreSQL for production
- **Message Queue**: Redis for async processing
- **Monitoring**: Prometheus metrics and Grafana dashboards
- **CI/CD**: Automated testing and deployment
- **Containerization**: Docker and Kubernetes support

## 🧪 Testing

### Manual Testing

```bash
# Start the application
python3 -m uvicorn app.main:app --reload

# Run the demo script above
# Check artifacts directory
ls -la _artifacts/

# Verify audit trail
cat _artifacts/audit.log
```

### Automated Testing

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest
```

## 📈 Monitoring & Maintenance

### Health Checks

```bash
# Service health
curl http://localhost:8000/health

# Artifact statistics
curl http://localhost:8000/artifacts

# Audit summary
curl http://localhost:8000/audit
```

### Cleanup Operations

```bash
# Clean expired artifacts
curl -X POST http://localhost:8000/cleanup
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NSW Registry of Births, Deaths and Marriages
- Services Australia - Medicare
- Australian Bureau of Statistics
- data.gov.au for open datasets
- FastAPI and Playwright communities

## 📞 Support

For questions or issues:

- Check the API documentation at `/docs`
- Review the audit trail for debugging
- Check the artifacts directory for data verification

---

**Demo for Judges**: Run the demo script above to see the complete end-to-end workflow in action. The system demonstrates autonomy, privacy protection, and comprehensive audit trails while automating government service interactions.
