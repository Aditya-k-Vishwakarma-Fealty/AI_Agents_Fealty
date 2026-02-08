"""
Retell AI Service - Handles voice call interactions.
"""
import logging
import json
from typing import Dict, Any, Optional
from retell import Retell
from app.config.settings import settings

logger = logging.getLogger(__name__)

class VoiceAIService:
    """Service for managing Retell AI voice calls."""
    
    def __init__(self):
        """Initialize Retell client."""
        self.client = Retell(api_key=settings.retell_api_key)
        self.agent_id = settings.retell_agent_id
        
    def create_phone_call(
        self, 
        to_number: str, 
        candidate_name: str, 
        role_title: str, 
        key_skills: str
    ) -> Dict[str, Any]:
        """
        Initiate a phone call with a dynamic prompt.
        
        Args:
            to_number: Candidate's phone number
            candidate_name: Name of the candidate
            role_title: Title of the role
            key_skills: Comma-separated list of key skills
            
        Returns:
            Retell call object or error dict
        """
        try:
            # Basic number normalization for E.164
            # If it doesn't start with +, and is 10 digits, assume +91 (India) as default for this user
            # or just add + if it looks like it might have a country code but missing +
            if not to_number.startswith('+'):
                if len(to_number) == 10:
                    to_number = f"+91{to_number}"
                else:
                    to_number = f"+{to_number}"

            logger.info(f"Initiating Retell call to {to_number} for {candidate_name}...")
            
            # Using Retell SDK to register-call and then call (or create-call directly if using their phone numbers)
            # Assuming outbound call using Retell's phone number or registered phone
            # We use their 'register-call' or 'create-phone-call' depending on version.
            # Referencing typical SDK usage:
            
            call = self.client.call.create_phone_call(
                from_number=settings.retell_phone_number,
                to_number=to_number,
                override_agent_id=self.agent_id,
                retell_llm_dynamic_variables={
                    "candidate_name": candidate_name,
                    "role_title": role_title,
                    "key_skills": key_skills
                }
            )
            # Note: The above is a placeholder for actual SDK call structure. 
            # In some versions, you might send the dynamic prompt as an override.
            
            logger.info(f"Call initiated successfully: {call.call_id}")
            return {"status": "success", "call_id": call.call_id}
            
        except Exception as e:
            logger.error(f"Error creating Retell call: {e}")
            return {"status": "error", "message": str(e)}

    def get_call_details(self, call_id: str) -> Dict[str, Any]:
        """Get details of a completed call including transcript."""
        try:
            call = self.client.call.retrieve(call_id)
            return {
                "status": "success",
                "transcript": call.transcript,
                "duration": call.duration_ms / 1000 if call.duration_ms else 0,
                "summary": call.call_analysis.call_summary if call.call_analysis else ""
            }
        except Exception as e:
            logger.error(f"Error retrieving call details: {e}")
            return {"status": "error", "message": str(e)}

# Global instance
voice_ai_service = VoiceAIService()
