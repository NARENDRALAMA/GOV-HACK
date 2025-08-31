#!/usr/bin/env python3
"""
Demo script for unemployment services

This script demonstrates how to use the community agent for unemployment scenarios,
including JobSeeker Payment and Job Service Provider registration.
"""

import asyncio
import json
from datetime import date
from pathlib import Path

from app.models import Intake, Person, Address, Employment, Banking
from app.orchestrator import JourneyOrchestrator


def create_unemployment_intake():
    """Create a sample unemployment intake"""
    
    # Create applicant
    applicant = Person(
        full_name="John Smith",
        dob=date(1985, 6, 15),
        email="john.smith@email.com",
        phone="0412 345 678",
        address=Address(
            line1="123 Main Street",
            suburb="Sydney",
            state="NSW",
            postcode="2000"
        )
    )
    
    # Create employment details
    employment = Employment(
        last_employer="ABC Company Pty Ltd",
        last_work_date=date(2025, 8, 1),
        reason_for_unemployment="Redundancy",
        preferred_provider="Max Employment",
        skills_assessment=True,
        training_interests=["Digital Marketing", "Project Management"],
        work_preferences=["Remote work", "Flexible hours"]
    )
    
    # Create banking details
    banking = Banking(
        bsb="012-345",
        account_number="12345678",
        account_name="John Smith"
    )
    
    # Create intake
    intake = Intake(
        applicant=applicant,
        employment=employment,
        banking=banking,
        preferred_language="en",
        accessibility=["screen_reader_friendly"]
    )
    
    return intake


def main():
    """Main demo function"""
    print("🚀 Unemployment Services Demo")
    print("=" * 50)
    
    # Create orchestrator
    orchestrator = JourneyOrchestrator()
    
    # Create unemployment intake
    print("\n📝 Creating unemployment intake...")
    intake = create_unemployment_intake()
    
    print(f"   Applicant: {intake.applicant.full_name}")
    print(f"   Last Employer: {intake.employment.last_employer}")
    print(f"   Last Work Date: {intake.employment.last_work_date}")
    
    # Plan journey
    print("\n🗺️  Planning journey...")
    journey = orchestrator.plan_journey(intake, jurisdiction="NSW")
    
    print(f"   Journey ID: {journey.id}")
    print(f"   Life Event: {journey.life_event}")
    print(f"   Jurisdiction: {journey.jurisdiction}")
    print(f"   Steps: {len(journey.steps)}")
    
    for step in journey.steps:
        print(f"     - {step.title} ({step.status})")
    
    # Prefill forms
    print("\n📋 Prefilling forms...")
    
    for step in journey.steps:
        print(f"\n   Prefilling {step.title}...")
        try:
            prefill_response = orchestrator.prefill_form(journey.id, step.id, intake)
            print(f"     Form ID: {prefill_response.form_id}")
            print(f"     Fields filled: {len(prefill_response.data)}")
            
            # Show some sample data
            for field_id, value in list(prefill_response.data.items())[:3]:
                print(f"       {field_id}: {value}")
            
        except Exception as e:
            print(f"     Error: {str(e)}")
    
    # Submit forms
    print("\n📤 Submitting forms...")
    
    for step in journey.steps:
        print(f"\n   Submitting {step.title}...")
        try:
            # Create sample form data
            form_data = {
                "applicant_full_name": intake.applicant.full_name,
                "applicant_dob": str(intake.applicant.dob),
                "last_employer": intake.employment.last_employer,
                "last_work_date": str(intake.employment.last_work_date)
            }
            
            submission_response = orchestrator.submit_form(journey.id, step.id, form_data)
            print(f"     Reference: {submission_response.reference}")
            print(f"     Submitted: {submission_response.submitted_at}")
            
        except Exception as e:
            print(f"     Error: {str(e)}")
    
    print("\n✅ Demo completed!")
    print(f"\n📁 Check the vault directory for artifacts: _artifacts/vault/{journey.id}/")


if __name__ == "__main__":
    main()

