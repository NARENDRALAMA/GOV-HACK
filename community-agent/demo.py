#!/usr/bin/env python3
"""
Demo script for the Agentic Community Assistant

This script demonstrates the complete end-to-end workflow:
1. Create intake and journey
2. Prefill forms
3. Grant consent
4. Submit forms
5. View artifacts and audit trail

Run this after starting the FastAPI server with:
python3 -m uvicorn app.main:app --reload
"""

import requests
import json
import time
from datetime import datetime


class CommunityAssistantDemo:
    """Demo class for testing the Community Assistant"""
    
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.journey_id = None
        
    def print_step(self, step_num, title, description=""):
        """Print a formatted step header"""
        print(f"\n{'='*60}")
        print(f"STEP {step_num}: {title}")
        print(f"{'='*60}")
        if description:
            print(description)
        print()
    
    def print_response(self, response, title="Response"):
        """Print a formatted response"""
        print(f"{title}:")
        print("-" * 40)
        if response.status_code == 200:
            try:
                data = response.json()
                print(json.dumps(data, indent=2))
            except:
                print(response.text)
        else:
            print(f"Error {response.status_code}: {response.text}")
        print()
    
    def run_demo(self):
        """Run the complete demo workflow"""
        print("🚀 AGENTIC COMMUNITY ASSISTANT DEMO")
        print("=" * 60)
        print("This demo shows the complete workflow for a 'baby just born' life event")
        print("Make sure the FastAPI server is running on http://localhost:8000")
        print()
        
        # Step 1: Create Intake
        self.print_step(1, "Create Intake", "Creating a new journey for Jane and John Doe with Baby Doe")
        
        intake_data = {
            "parent1": {
                "full_name": "Jane Doe",
                "dob": "1990-01-01",
                "email": "jane.doe@example.com",
                "phone": "0412345678"
            },
            "parent2": {
                "full_name": "John Doe",
                "dob": "1988-05-15",
                "email": "john.doe@example.com"
            },
            "baby": {
                "name": "Baby Doe",
                "sex": "F",
                "dob": "2025-08-28",
                "place_of_birth": "Westmead Hospital",
                "parents": []
            },
            "address": {
                "line1": "123 Main Street",
                "suburb": "Parramatta",
                "state": "NSW",
                "postcode": "2150"
            },
            "preferred_language": "en",
            "accessibility": []
        }
        
        response = self.session.post(f"{self.base_url}/intake", json=intake_data)
        self.print_response(response, "Intake Response")
        
        if response.status_code == 200:
            data = response.json()
            self.journey_id = data["journey_id"]
            print(f"✅ Journey created successfully! ID: {self.journey_id}")
        else:
            print("❌ Failed to create intake. Please check if the server is running.")
            return
        
        # Step 2: Get Journey Plan
        self.print_step(2, "Get Journey Plan", f"Retrieving the journey plan for {self.journey_id}")
        
        response = self.session.get(f"{self.base_url}/plan/{self.journey_id}")
        self.print_response(response, "Journey Plan")
        
        if response.status_code == 200:
            print("✅ Journey plan retrieved successfully!")
        else:
            print("❌ Failed to retrieve journey plan.")
            return
        
        # Step 3: Prefill Birth Registration Form
        self.print_step(3, "Prefill Birth Registration Form", "Prefilling the NSW birth registration form")
        
        response = self.session.post(f"{self.base_url}/prefill/{self.journey_id}/birth_reg")
        self.print_response(response, "Birth Registration Prefill")
        
        if response.status_code == 200:
            print("✅ Birth registration form prefilled successfully!")
        else:
            print("❌ Failed to prefill birth registration form.")
            return
        
        # Step 4: Grant Consent
        self.print_step(4, "Grant Consent", "Granting consent for birth registration and Medicare enrolment")
        
        consent_data = {
            "journey_id": self.journey_id,
            "consent": {
                "scope": ["birth_registration", "medicare_enrolment"],
                "ttl_days": 30,
                "signature": "Jane Doe"
            }
        }
        
        response = self.session.post(f"{self.base_url}/consent/{self.journey_id}", json=consent_data)
        self.print_response(response, "Consent Response")
        
        if response.status_code == 200:
            print("✅ Consent granted successfully!")
        else:
            print("❌ Failed to grant consent.")
            return
        
        # Step 5: Submit Birth Registration
        self.print_step(5, "Submit Birth Registration", "Submitting the birth registration form")
        
        form_data = {
            "parent1_full_name": "Jane Doe",
            "parent1_dob": "1990-01-01",
            "baby_name": "Baby Doe",
            "baby_dob": "2025-08-28",
            "place_of_birth": "Westmead Hospital"
        }
        
        response = self.session.post(f"{self.base_url}/submit/{self.journey_id}/birth_reg", json=form_data)
        self.print_response(response, "Birth Registration Submission")
        
        if response.status_code == 200:
            print("✅ Birth registration submitted successfully!")
        else:
            print("❌ Failed to submit birth registration.")
            return
        
        # Step 6: Prefill Medicare Form
        self.print_step(6, "Prefill Medicare Form", "Prefilling the Medicare newborn enrolment form")
        
        response = self.session.post(f"{self.base_url}/prefill/{self.journey_id}/medicare_enrolment")
        self.print_response(response, "Medicare Prefill")
        
        if response.status_code == 200:
            print("✅ Medicare form prefilled successfully!")
        else:
            print("❌ Failed to prefill Medicare form.")
            return
        
        # Step 7: Submit Medicare Form
        self.print_step(7, "Submit Medicare Form", "Submitting the Medicare newborn enrolment form")
        
        medicare_form_data = {
            "parent1_full_name": "Jane Doe",
            "parent1_dob": "1990-01-01",
            "baby_name": "Baby Doe",
            "baby_dob": "2025-08-28"
        }
        
        response = self.session.post(f"{self.base_url}/submit/{self.journey_id}/medicare_enrolment", json=medicare_form_data)
        self.print_response(response, "Medicare Submission")
        
        if response.status_code == 200:
            print("✅ Medicare enrolment submitted successfully!")
        else:
            print("❌ Failed to submit Medicare enrolment.")
            return
        
        # Step 8: View Artifacts
        self.print_step(8, "View Artifacts", "Listing all artifacts created during the journey")
        
        response = self.session.get(f"{self.base_url}/artifacts")
        self.print_response(response, "All Artifacts")
        
        if response.status_code == 200:
            print("✅ Artifacts retrieved successfully!")
        else:
            print("❌ Failed to retrieve artifacts.")
        
        # Step 9: View Journey-Specific Artifacts
        self.print_step(9, "View Journey Artifacts", f"Listing artifacts for journey {self.journey_id}")
        
        response = self.session.get(f"{self.base_url}/artifacts?journey_id={self.journey_id}")
        self.print_response(response, "Journey Artifacts")
        
        if response.status_code == 200:
            print("✅ Journey artifacts retrieved successfully!")
        else:
            print("❌ Failed to retrieve journey artifacts.")
        
        # Step 10: View Audit Trail
        self.print_step(10, "View Audit Trail", "Displaying the complete audit trail")
        
        response = self.session.get(f"{self.base_url}/audit")
        self.print_response(response, "Audit Trail")
        
        if response.status_code == 200:
            print("✅ Audit trail retrieved successfully!")
        else:
            print("❌ Failed to retrieve audit trail.")
        
        # Step 11: Health Check
        self.print_step(11, "Health Check", "Checking service health and status")
        
        response = self.session.get(f"{self.base_url}/health")
        self.print_response(response, "Health Check")
        
        if response.status_code == 200:
            print("✅ Service is healthy!")
        else:
            print("❌ Service health check failed.")
        
        # Demo Summary
        print("\n" + "="*60)
        print("🎉 DEMO COMPLETED SUCCESSFULLY!")
        print("="*60)
        print(f"Journey ID: {self.journey_id}")
        print("What was demonstrated:")
        print("✅ Complete intake and journey planning")
        print("✅ Automated form prefilling")
        print("✅ Consent management with audit trail")
        print("✅ Form submission with receipts")
        print("✅ Artifact storage and retrieval")
        print("✅ Comprehensive audit logging")
        print("✅ Privacy protection (PII in vault)")
        print("✅ Government service automation")
        print()
        print("Next steps:")
        print("1. Check the _artifacts/ directory for stored data")
        print("2. Review the audit.log for complete audit trail")
        print("3. Explore the API documentation at /docs")
        print("4. Try the Playwright automation in app/automation/")
        print()
        print("The system demonstrates:")
        print("- Autonomy: Automated journey planning and form filling")
        print("- Accessibility: Channel-agnostic API design")
        print("- Privacy: PII vault with TTL and hashed audit trails")
        print("- Auditability: Complete action logging with cryptographic integrity")


def main():
    """Main function to run the demo"""
    demo = CommunityAssistantDemo()
    
    try:
        demo.run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Demo failed with error: {str(e)}")
        print("Make sure the FastAPI server is running with:")
        print("python3 -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    main()
