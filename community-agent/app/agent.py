"""
Agentic AI System for Government Services

This module implements an intelligent agent that can:
1. Understand natural language requests
2. Plan multi-step workflows
3. Retrieve government data and requirements
4. Execute tasks autonomously
5. Apply inclusivity logic based on demographics
"""

import re
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from .rag.retrieve import (
    search_services, load_howto, load_abs_profile, 
    get_inclusivity_adjustments, search_knowledge_base
)
from .orchestrator import JourneyOrchestrator
from .models import Journey, JourneyStep, Intake, Consent
from .utils.audit import log_event, log_consent
from .utils.storage import save_artifact

class AgenticAssistant:
    """
    Intelligent agent that autonomously handles government service requests
    """
    
    def __init__(self):
        self.orchestrator = JourneyOrchestrator()
        self.conversation_history = []
        self.current_journey = None
        
    def start_conversation(self, user_message: str) -> Dict:
        """
        Start a new conversation with the agent
        
        Args:
            user_message: Natural language request from user
            
        Returns:
            Agent response with plan and next steps
        """
        # Log the conversation start
        conversation_id = self._generate_id("conv")
        self.conversation_history.append({
            'id': conversation_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'agent_response': None
        })
        
        # Extract intent and entities
        intent = self._extract_intent(user_message)
        entities = self._extract_entities(user_message)
        
        # Generate response plan
        response = self._generate_response(intent, entities, user_message)
        
        # Update conversation history
        self.conversation_history[-1]['agent_response'] = response
        
        # Log the event
        log_event(
            actor="agent",
            action="conversation_started",
            why=f"Agent started conversation for {intent}",
            metadata={
                'intent': intent,
                'entities': entities,
                'conversation_id': conversation_id,
                'journey_id': response.get('journey_id')
            }
        )
        
        return response
    
    def continue_conversation(self, journey_id: str, user_input: str = None) -> Dict:
        """
        Continue an existing conversation/journey
        
        Args:
            journey_id: ID of the journey to continue
            user_input: Optional user input for the next step
            
        Returns:
            Agent response with next actions
        """
        if not self.current_journey or self.current_journey.id != journey_id:
            return {
                'error': 'Journey not found or not active',
                'suggestion': 'Start a new conversation with /agent/start'
            }
        
        # Execute next step in the journey
        next_step = self._execute_next_step(journey_id, user_input)
        
        # Log the continuation
        log_event(
            actor="agent",
            action="conversation_continued",
            why="Agent continued conversation to next step",
            metadata={'next_step': next_step, 'journey_id': journey_id}
        )
        
        return next_step
    
    def _extract_intent(self, message: str) -> str:
        """Extract the user's intent from their message"""
        message_lower = message.lower()
        
        # Birth registration intent
        if any(word in message_lower for word in ['baby', 'born', 'birth', 'newborn']):
            if any(word in message_lower for word in ['register', 'registration', 'certificate']):
                return 'birth_registration'
            else:
                return 'birth_related'
        
        # Medicare intent
        if any(word in message_lower for word in ['medicare', 'health', 'medical', 'coverage']):
            return 'medicare_enrolment'
        
        # General government services
        if any(word in message_lower for word in ['government', 'service', 'help', 'assist']):
            return 'general_assistance'
        
        # Default to birth registration for baby-related queries
        if any(word in message_lower for word in ['baby', 'child', 'infant']):
            return 'birth_registration'
        
        return 'general_assistance'
    
    def _extract_entities(self, message: str) -> Dict:
        """Extract relevant entities from the user's message"""
        entities = {}
        
        # Extract postcode
        postcode_match = re.search(r'\b(\d{4})\b', message)
        if postcode_match:
            entities['postcode'] = postcode_match.group(1)
        
        # Extract location/suburb
        location_patterns = [
            r'in (\w+)',
            r'at (\w+)',
            r'(\w+) hospital',
            r'(\w+) medical centre'
        ]
        
        for pattern in location_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                entities['location'] = match.group(1)
                break
        
        # Extract time references
        time_patterns = [
            r'(\d+) days? ago',
            r'(\d+) weeks? ago',
            r'yesterday',
            r'today',
            r'last week'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                if 'ago' in pattern:
                    entities['days_ago'] = int(match.group(1))
                elif 'yesterday' in pattern:
                    entities['days_ago'] = 1
                elif 'today' in pattern:
                    entities['days_ago'] = 0
                elif 'last week' in pattern:
                    entities['days_ago'] = 7
                break
        
        return entities
    
    def _generate_response(self, intent: str, entities: Dict, original_message: str) -> Dict:
        """Generate a comprehensive response with plan and actions"""
        
        # Get postcode for inclusivity logic
        postcode = entities.get('postcode', '2150')  # Default to Parramatta
        inclusivity = get_inclusivity_adjustments(postcode)
        
        # Create journey plan
        if intent == 'birth_registration':
            journey = self._create_birth_registration_journey(entities, inclusivity)
        elif intent == 'medicare_enrolment':
            journey = self._create_medicare_journey(entities, inclusivity)
        else:
            journey = self._create_general_journey(entities, inclusivity)
        
        # Get relevant government information
        howto_info = load_howto(intent)
        service_locations = search_services(intent, postcode)
        
        # Generate response
        response = {
            'journey_id': journey.id,
            'intent': intent,
            'entities': entities,
            'plan': {
                'steps': [step.dict() for step in journey.steps],
                'estimated_duration': '2-3 business days',
                'requirements': self._get_requirements(intent)
            },
            'government_info': {
                'requirements': howto_info,
                'nearest_services': service_locations[:3],  # Top 3
                'source_urls': howto_info.get('citations', [])
            },
            'inclusivity': inclusivity,
            'next_action': 'ready_to_continue',
            'message': self._generate_natural_response(intent, entities, inclusivity)
        }
        
        # Store the journey
        self.current_journey = journey
        
        return response
    
    def _create_birth_registration_journey(self, entities: Dict, inclusivity: Dict) -> Journey:
        """Create a birth registration journey"""
        
        # Create intake data from entities
        intake_data = {
            'parent1': {
                'full_name': 'To be provided',
                'dob': '1990-01-01',  # Default date
                'email': None,
                'phone': None
            },
            'baby': {
                'name': None,
                'sex': None,
                'dob': self._calculate_baby_dob(entities.get('days_ago', 0)),
                'place_of_birth': entities.get('location', 'To be provided'),
                'parents': []
            },
            'address': {
                'line1': 'To be provided',
                'suburb': 'To be provided',
                'postcode': entities.get('postcode', '2150'),
                'state': 'NSW'
            },
            'preferred_language': 'en',
            'accessibility': inclusivity.get('accessibility_preferences', [])
        }
        
        # Create journey
        journey = self.orchestrator.plan_journey(Intake(**intake_data))
        
        return journey
    
    def _create_medicare_journey(self, entities: Dict, inclusivity: Dict) -> Journey:
        """Create a Medicare enrolment journey"""
        
        # For Medicare, we need birth registration first
        intake_data = {
            'parent1': {
                'full_name': 'To be provided',
                'dob': '1990-01-01',  # Default date
                'email': None,
                'phone': None
            },
            'baby': {
                'name': None,
                'sex': None,
                'dob': self._calculate_baby_dob(entities.get('days_ago', 0)),
                'place_of_birth': entities.get('location', 'To be provided'),
                'parents': []
            },
            'address': {
                'line1': 'To be provided',
                'suburb': 'To be provided',
                'postcode': entities.get('postcode', '2150'),
                'state': 'NSW'
            },
            'preferred_language': 'en',
            'accessibility': inclusivity.get('accessibility_preferences', [])
        }
        
        # Create journey with both steps
        journey = self.orchestrator.plan_journey(Intake(**intake_data))
        
        return journey
    
    def _create_general_journey(self, entities: Dict, inclusivity: Dict) -> Journey:
        """Create a general assistance journey"""
        
        intake_data = {
            'parent1': {
                'full_name': 'To be provided',
                'dob': '1990-01-01',  # Default date
                'email': None,
                'phone': None
            },
            'baby': {
                'name': None,
                'sex': None,
                'dob': self._calculate_baby_dob(entities.get('days_ago', 0)),
                'place_of_birth': entities.get('location', 'To be provided'),
                'parents': []
            },
            'address': {
                'line1': 'To be provided',
                'suburb': 'To be provided',
                'postcode': entities.get('postcode', '2150'),
                'state': 'NSW'
            },
            'preferred_language': 'en',
            'accessibility': inclusivity.get('accessibility_preferences', [])
        }
        
        # Create basic journey
        journey = self.orchestrator.plan_journey(Intake(**intake_data))
        
        return journey
    
    def _execute_next_step(self, journey_id: str, user_input: str = None) -> Dict:
        """Execute the next step in the journey"""
        
        if not self.current_journey:
            return {'error': 'No active journey'}
        
        # Find next incomplete step
        next_step = None
        for step in self.current_journey.steps:
            if step.status != 'completed':
                next_step = step
                break
        
        if not next_step:
            return {
                'status': 'journey_complete',
                'message': 'All steps completed successfully!',
                'summary': self._generate_journey_summary()
            }
        
        # Execute the step
        try:
            if next_step.id == 'birth_reg':
                result = self._execute_birth_registration_step(next_step, user_input)
            elif next_step.id == 'medicare_enrolment':
                result = self._execute_medicare_step(next_step, user_input)
            else:
                result = {'status': 'unknown_step', 'step_id': next_step.id}
            
            # Mark step as completed
            next_step.status = 'completed'
            
            return result
            
        except Exception as e:
            log_event(
                actor="agent",
                action="step_execution_error",
                why=f"Error executing step {next_step.id}",
                metadata={'step_id': next_step.id, 'error': str(e), 'journey_id': journey_id}
            )
            return {
                'error': f'Error executing step: {str(e)}',
                'step_id': next_step.id
            }
    
    def _execute_birth_registration_step(self, step: JourneyStep, user_input: str) -> Dict:
        """Execute birth registration step"""
        
        # Prefill the form
        prefill_data = self.orchestrator.prefill_form(
            self.current_journey.journey_id, 
            step.id
        )
        
        # Get service locations
        services = search_services('birth registration', 
                                 self.current_journey.intake.address.postcode)
        
        return {
            'status': 'step_completed',
            'step_id': step.id,
            'step_title': step.title,
            'prefill_data': prefill_data.data,
            'nearest_services': services[:2],
            'next_action': 'ready_for_medicare',
            'message': f'Birth registration form prepared. Nearest service: {services[0]["name"] if services else "None"}'
        }
    
    def _execute_medicare_step(self, step: JourneyStep, user_input: str) -> Dict:
        """Execute Medicare enrolment step"""
        
        # Prefill the form
        prefill_data = self.orchestrator.prefill_form(
            self.current_journey.journey_id, 
            step.id
        )
        
        return {
            'status': 'step_completed',
            'step_id': step.id,
            'step_title': step.title,
            'prefill_data': prefill_data.data,
            'next_action': 'journey_complete',
            'message': 'Medicare enrolment form prepared. Your baby will be automatically covered for 12 months.'
        }
    
    def _calculate_baby_dob(self, days_ago: int) -> str:
        """Calculate baby's date of birth"""
        if days_ago == 0:
            return datetime.now().strftime('%Y-%m-%d')
        else:
            return (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
    
    def _get_requirements(self, intent: str) -> List[str]:
        """Get requirements for the given intent"""
        if intent == 'birth_registration':
            return [
                'Birth registration statement from hospital',
                'Parent identification documents',
                'Proof of address',
                'Marriage certificate (if applicable)'
            ]
        elif intent == 'medicare_enrolment':
            return [
                'Completed birth registration',
                'Parent Medicare card details',
                'Baby\'s birth certificate'
            ]
        else:
            return ['Basic identification documents']
    
    def _generate_natural_response(self, intent: str, entities: Dict, inclusivity: Dict) -> str:
        """Generate a natural language response"""
        
        postcode = entities.get('postcode', '2150')
        location = entities.get('location', 'your area')
        
        response = f"I understand you need help with {intent.replace('_', ' ')} for your baby born in {location} (postcode {postcode}). "
        
        if intent == 'birth_registration':
            response += "I'll help you register the birth with NSW Registry and enrol for Medicare. "
            response += "Birth registration is required within 60 days and is free of charge. "
        elif intent == 'medicare_enrolment':
            response += "I'll help you enrol your newborn for Medicare coverage. "
            response += "Newborns are automatically covered under their parent's Medicare card for 12 months. "
        
        # Add inclusivity adjustments
        if inclusivity.get('language_support'):
            response += "I notice your area has a high percentage of non-English speakers. Would you like to continue in another language? "
        
        if 'voice_updates' in inclusivity.get('communication_preferences', []):
            response += "I can also provide updates via voice or SMS if you prefer. "
        
        response += "Let me start preparing the necessary forms and find the nearest service locations for you."
        
        return response
    
    def _generate_journey_summary(self) -> Dict:
        """Generate a summary of the completed journey"""
        if not self.current_journey:
            return {}
        
        completed_steps = [step for step in self.current_journey.steps if step.status == 'completed']
        
        return {
            'journey_id': self.current_journey.id,
            'total_steps': len(self.current_journey.steps),
            'completed_steps': len(completed_steps),
            'completion_date': datetime.now().isoformat(),
            'next_reminders': [
                'Immunisation schedule starts at 6 weeks',
                'Birth certificate available for purchase',
                'Consider Centrelink family assistance'
            ]
        }
    
    def _generate_id(self, prefix: str) -> str:
        """Generate a unique ID"""
        timestamp = datetime.now().isoformat()
        hash_input = f"{prefix}_{timestamp}_{len(self.conversation_history)}"
        return f"{prefix}_{hashlib.md5(hash_input.encode()).hexdigest()[:8]}"

# Global instance
agent = AgenticAssistant()
