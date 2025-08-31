#!/usr/bin/env python3
"""
Demo script for emergency/disaster recovery services

This script demonstrates how to use the community agent for disaster recovery scenarios,
including Emergency Disaster Payment and Emergency Housing Assistance.
"""

import asyncio
import json
from datetime import date
from pathlib import Path

from app.models import Intake, Person, Address, Disaster, Housing, Banking
from app.orchestrator import JourneyOrchestrator


def create_disaster_intake():
    """Create a sample disaster recovery intake"""
    
    # Create applicant
    applicant = Person(
        full_name="Sarah Johnson",
        dob=date(1980, 3, 20),
        email="sarah.johnson@email.com",
        phone="0498 765 432",
        address=Address(
            line1="456 River Road",
            suburb="Lismore",
            state="NSW",
            postcode="2480"
        )
    )
    
    # Create disaster details
    disaster = Disaster(
        type="Flood",
        date=date(2025, 8, 15),
        location="Lismore, NSW",
        property_damage="Home flooded, furniture damaged, car written off"
    )
    
    # Create housing details
    housing = Housing(
        status="Displaced",
        damage_description="Home uninhabitable due to flood damage",
        household_size=3,
        special_needs=["Wheelchair accessible", "Ground floor only"],
        temporary_accommodation_needed=True
    )
    
    # Create banking details
    banking = Banking(
        bsb="987-654",
        account_number="87654321",
        account_name="Sarah Johnson"
    )
    
    # Create intake
    intake = Intake(
        applicant=applicant,
        disaster=disaster,
        housing=housing,
        banking=banking,
        preferred_language="en",
        accessibility=["wheelchair_accessible", "large_text"]
    )
    
    return intake


def main():
    """Main demo function"""
    print("🚨 Emergency/Disaster Recovery Services Demo")
    print("=" * 60)
    
    # Create orchestrator
    orchestrator = JourneyOrchestrator()
    
    # Create disaster intake
    print("\n📝 Creating disaster recovery intake...")
    intake = create_disaster_intake()
    
    print(f"   Applicant: {intake.applicant.full_name}")
    print(f"   Disaster Type: {intake.disaster.type}")
    print(f"   Disaster Date: {intake.disaster.date}")
    print(f"   Location: {intake.disaster.location}")
    print(f"   Housing Status: {intake.housing.status}")
    
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
                "disaster_type": intake.disaster.type,
                "disaster_date": str(intake.disaster.date),
                "disaster_location": intake.disaster.location,
                "property_damage": intake.disaster.property_damage
            }
            
            submission_response = orchestrator.submit_form(journey.id, step.id, form_data)
            print(f"     Reference: {submission_response.reference}")
            print(f"     Submitted: {submission_response.submitted_at}")
            
        except Exception as e:
            print(f"     Error: {str(e)}")
    
    print("\n✅ Demo completed!")
    print(f"\n📁 Check the vault directory for artifacts: _artifacts/vault/{journey.id}/")
    
    # Show next steps
    print("\n📋 Next Steps for Disaster Recovery:")
    print("   1. Emergency Disaster Payment - Provides immediate financial assistance")
    print("   2. Emergency Housing Assistance - Helps find temporary accommodation")
    print("   3. Contact local council for additional support services")
    print("   4. Register with disaster recovery agencies for ongoing assistance")


if __name__ == "__main__":
    main()

