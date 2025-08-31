#!/usr/bin/env python3
"""
Basic test for the Agentic Community Assistant

This test verifies that the core modules can be imported and basic functionality works.
Run this to check if the installation is correct.
"""

import sys
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing module imports...")
    
    try:
        # Test core imports
        from app.models import Intake, Journey, Person, Baby, Address
        print("✅ Core models imported successfully")
        
        from app.orchestrator import JourneyOrchestrator
        print("✅ Orchestrator imported successfully")
        
        from app.utils.storage import save_artifact, get_vault_path
        print("✅ Storage utilities imported successfully")
        
        from app.utils.audit import log_event, log_consent
        print("✅ Audit utilities imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_basic_models():
    """Test that basic models can be instantiated"""
    print("\nTesting basic model instantiation...")
    
    try:
        from app.models import Intake, Person, Baby, Address
        
        # Create test data
        address = Address(
            line1="123 Test Street",
            suburb="Test Suburb",
            state="NSW",
            postcode="2000"
        )
        
        person = Person(
            full_name="Test Person",
            dob="1990-01-01",
            address=address
        )
        
        baby = Baby(
            name="Test Baby",
            dob="2025-01-01",
            parents=[person]
        )
        
        intake = Intake(
            parent1=person,
            baby=baby,
            address=address
        )
        
        print("✅ Basic models instantiated successfully")
        print(f"   - Address: {address.line1}, {address.suburb}")
        print(f"   - Person: {person.full_name}")
        print(f"   - Baby: {baby.name}")
        print(f"   - Intake created with ID pattern: {type(intake).__name__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Model instantiation failed: {e}")
        return False

def test_orchestrator():
    """Test that orchestrator can be instantiated"""
    print("\nTesting orchestrator...")
    
    try:
        from app.orchestrator import JourneyOrchestrator
        
        orchestrator = JourneyOrchestrator()
        print("✅ Orchestrator instantiated successfully")
        
        # Test that forms directory exists
        forms_dir = orchestrator.forms_dir
        if forms_dir.exists():
            print(f"✅ Forms directory found: {forms_dir}")
            
            # Check for form files
            form_files = list(forms_dir.glob("*.yml"))
            print(f"✅ Found {len(form_files)} form schema files:")
            for form_file in form_files:
                print(f"   - {form_file.name}")
        else:
            print("⚠️  Forms directory not found")
            
        return True
        
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_utilities():
    """Test that utility functions work"""
    print("\nTesting utility functions...")
    
    try:
        from app.utils.storage import get_vault_path
        from app.utils.audit import log_event
        
        # Test storage
        test_journey_id = "test_journey_123"
        vault_path = get_vault_path(test_journey_id)
        print(f"✅ Vault path generated: {vault_path}")
        
        # Test audit logging
        event_hash = log_event(
            actor="test",
            action="test_action",
            why="Testing audit functionality",
            metadata={"test": True}
        )
        print(f"✅ Audit event logged with hash: {event_hash[:8]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Utility test failed: {e}")
        return False

def test_knowledge_base():
    """Test that knowledge base is accessible"""
    print("\nTesting knowledge base...")
    
    try:
        knowledge_path = "app/rag/knowledge.md"
        
        if os.path.exists(knowledge_path):
            with open(knowledge_path, 'r') as f:
                content = f.read()
                
            print(f"✅ Knowledge base found: {knowledge_path}")
            print(f"   - Size: {len(content)} characters")
            print(f"   - Contains NSW BDM info: {'NSW' in content}")
            print(f"   - Contains Medicare info: {'Medicare' in content}")
            print(f"   - Contains URLs: {content.count('http')} links found")
            
            return True
        else:
            print(f"❌ Knowledge base not found: {knowledge_path}")
            return False
            
    except Exception as e:
        print(f"❌ Knowledge base test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 AGENTIC COMMUNITY ASSISTANT - BASIC TESTS")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_basic_models,
        test_orchestrator,
        test_utilities,
        test_knowledge_base
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The system is ready to use.")
        print("\nNext steps:")
        print("1. Start the server: python3 -m uvicorn app.main:app --reload")
        print("2. Run the demo: python3 demo.py")
        print("3. View API docs: http://localhost:8000/docs")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("\nTroubleshooting:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check that you're in the correct directory")
        print("3. Verify Python version (3.8+ required)")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
