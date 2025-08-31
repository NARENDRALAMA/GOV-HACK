"""
AI Integration Module using Ollama

This module provides a simple interface to the Ollama AI model
for government service assistance without pandas dependencies.
"""

import json
import subprocess
import logging
from typing import Dict, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OllamaAI:
    """Simple AI integration using Ollama"""
    
    def __init__(self, model_name: str = "qwen2.5:0.5b"):
        self.model_name = model_name
        self.conversation_history = []
        
    def generate_response(self, user_message: str, context: str = "") -> Dict[str, Any]:
        """
        Generate AI response using Ollama
        
        Args:
            user_message: User's input message
            context: Additional context for the AI
            
        Returns:
            Dictionary containing AI response and metadata
        """
        try:
            # Prepare the prompt with context
            if context:
                full_prompt = f"Context: {context}\n\nUser: {user_message}\n\nAssistant:"
            else:
                full_prompt = f"User: {user_message}\n\nAssistant:"
            
            # Call Ollama
            result = subprocess.run(
                ["ollama", "run", self.model_name],
                input=full_prompt,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                ai_response = result.stdout.strip()
                
                # Parse the response to extract the actual AI response
                if "Assistant:" in ai_response:
                    ai_response = ai_response.split("Assistant:")[-1].strip()
                
                # LIMIT RESPONSE LENGTH to prevent overwhelming responses
                if len(ai_response) > 200:
                    # Truncate long responses and add a helpful note
                    ai_response = ai_response[:200].rsplit('.', 1)[0] + ". For more details, please ask a specific question."
                
                # Log the interaction
                self.conversation_history.append({
                    'timestamp': datetime.now().isoformat(),
                    'user_message': user_message,
                    'ai_response': ai_response,
                    'context': context
                })
                
                return {
                    'success': True,
                    'response': ai_response,
                    'model': self.model_name,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                logger.error(f"Ollama error: {result.stderr}")
                return {
                    'success': False,
                    'error': f"Ollama error: {result.stderr}",
                    'fallback_response': "I'm having trouble processing your request right now. Please try again in a moment."
                }
                
        except subprocess.TimeoutExpired:
            logger.error("Ollama request timed out")
            return {
                'success': False,
                'error': 'Request timed out',
                'fallback_response': "I'm taking longer than expected to respond. Please try again with a simpler question."
            }
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'fallback_response': "I encountered an unexpected error. Please try again."
            }
    
    def analyze_government_request(self, user_message: str) -> Dict[str, Any]:
        """
        Analyze user message to determine government service needs
        
        Args:
            user_message: User's input message
            
        Returns:
            Dictionary with analysis results
        """
        # Create a specialized prompt for government services - KEEP RESPONSES SHORT!
        context = """
        You are a helpful AI assistant for Australian government services. 
        
        IMPORTANT: Keep your responses SHORT and CONCISE (max 2-3 sentences).
        Do NOT give long explanations or overwhelming details.
        
        Your role is to:
        1. Quickly identify what government service is needed
        2. Give a brief, helpful response
        3. Suggest next steps if relevant
        
        Common services: Birth registration, Medicare, unemployment benefits, emergency assistance.
        
        Remember: SHORT and HELPFUL responses only!
        """
        
        response = self.generate_response(user_message, context)
        
        if response['success']:
            # Try to extract structured information from the response
            analysis = self._extract_service_info(response['response'], user_message)
            response.update(analysis)
        
        return response
    
    def _extract_service_info(self, ai_response: str, user_message: str) -> Dict[str, Any]:
        """
        Extract structured information from AI response
        
        Args:
            ai_response: AI's response text
            user_message: Original user message
            
        Returns:
            Dictionary with extracted information
        """
        # Simple keyword-based extraction
        user_message_lower = user_message.lower()
        ai_response_lower = ai_response.lower()
        
        # Detect life events
        life_event = None
        if any(word in user_message_lower for word in ['baby', 'born', 'birth', 'newborn']):
            life_event = "baby_just_born"
        elif any(word in user_message_lower for word in ['job', 'unemployment', 'fired', 'laid off', 'redundant']):
            life_event = "job_loss"
        elif any(word in user_message_lower for word in ['flood', 'fire', 'disaster', 'emergency', 'damage']):
            life_event = "disaster_recovery"
        elif any(word in user_message_lower for word in ['carer', 'care', 'disability']):
            life_event = "carer_support"
        
        # Detect location if mentioned
        location = None
        location_keywords = ['sydney', 'melbourne', 'brisbane', 'perth', 'adelaide', 'canberra', 'darwin', 'hobart']
        for loc in location_keywords:
            if loc in user_message_lower:
                location = loc.title()
                break
        
        # Create journey plan based on life event
        journey_steps = []
        if life_event == "baby_just_born":
            journey_steps = [
                {"id": "birth_reg", "title": "Birth Registration", "description": "Register your baby's birth with NSW Registry", "status": "pending"},
                {"id": "medicare_enrolment", "title": "Medicare Enrolment", "description": "Enrol your newborn for Medicare coverage", "status": "pending"}
            ]
        elif life_event == "job_loss":
            journey_steps = [
                {"id": "jobseeker_payment", "title": "JobSeeker Payment", "description": "Apply for unemployment benefits", "status": "pending"},
                {"id": "job_service_provider", "title": "Job Service Provider", "description": "Register with employment services", "status": "pending"}
            ]
        elif life_event == "disaster_recovery":
            journey_steps = [
                {"id": "emergency_payment", "title": "Emergency Disaster Payment", "description": "Apply for immediate financial assistance", "status": "pending"},
                {"id": "housing_assistance", "title": "Emergency Housing", "description": "Apply for emergency housing support", "status": "pending"}
            ]
        
        return {
            'life_event': life_event,
            'location': location,
            'journey_steps': journey_steps,
            'suggestions': [
                "I can help you complete the necessary forms automatically",
                "Let me guide you through each step of the process",
                "I'll prefill forms with your information to save time"
            ]
        }
    
    def get_conversation_history(self) -> list:
        """Get conversation history"""
        return self.conversation_history
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# Create a global instance
ollama_ai = OllamaAI()
