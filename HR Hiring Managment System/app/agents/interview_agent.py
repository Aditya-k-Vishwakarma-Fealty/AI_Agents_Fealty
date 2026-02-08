"""
Interview Evaluation Agent - Evaluates interview performance.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


# Trigger reload for prompt update
class InterviewAgent:
    """Agent for evaluating interview performance."""
    
    def __init__(self):
        """Initialize the interview evaluation agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.3,
            openai_api_key=settings.openai_api_key
        )
        
        # Load system prompt
        with open("app/prompts/interview_prompt.txt", "r") as f:
            self.system_prompt = f.read()
        
        self.parser = JsonOutputParser()
    
    def evaluate_interview(
        self,
        communication_score: float,
        knowledge_score: float,
        confidence_score: float,
        feedback: str,
        candidate_data: Dict[str, Any] = None,
        role_data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Evaluate interview performance.
        
        Args:
            communication_score: Communication score (0-10)
            knowledge_score: Knowledge score (0-10)
            confidence_score: Confidence score (0-10)
            feedback: Interviewer's textual feedback
            candidate_data: Candidate background (optional)
            role_data: Role information (optional)
        
        Returns:
            Dict with evaluation results
        """
        try:
            # Prepare input
            input_text = f"""
INTERVIEW SCORES:
Communication: {communication_score}/10
Knowledge: {knowledge_score}/10
Confidence: {confidence_score}/10

INTERVIEWER FEEDBACK:
{feedback}
"""
            
            if candidate_data:
                input_text += f"""
CANDIDATE BACKGROUND:
Name: {candidate_data.get('name', 'N/A')}
Experience: {candidate_data.get('total_years_experience', 0)} years
Skills: {', '.join(candidate_data.get('skills', [])[:5])}
"""
            
            if role_data:
                input_text += f"""
ROLE INFORMATION:
Title: {role_data.get('title', 'N/A')}
Required Experience: {role_data.get('experience_required', 0)} years
"""
            
            input_text += "\nPlease provide a comprehensive evaluation of this interview performance."
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input_text}")
            ])
            
            # Create chain
            chain = prompt | self.llm | self.parser
            
            # Execute
            result = chain.invoke({"input_text": input_text})
            
            logger.info("Successfully evaluated interview")
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error evaluating interview: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def calculate_overall_score(
        self,
        communication_score: float,
        knowledge_score: float,
        confidence_score: float
    ) -> float:
        """
        Calculate weighted overall interview score.
        
        Weights: Communication 35%, Knowledge 40%, Confidence 25%
        
        Args:
            communication_score: Communication score (0-10)
            knowledge_score: Knowledge score (0-10)
            confidence_score: Confidence score (0-10)
        
        Returns:
            Overall score (0-10)
        """
        overall = (
            communication_score * 0.35 +
            knowledge_score * 0.40 +
            confidence_score * 0.25
        )
        return round(overall, 2)
    
    def evaluate_transcript(
        self,
        transcript: str,
        candidate_name: str,
        role_title: str
    ) -> Dict[str, Any]:
        """
        Evaluate voice interview transcript.
        
        Args:
            transcript: Full call transcript
            candidate_name: Name of candidate
            role_title: Role title
            
        Returns:
            Dict with scores and analysis
        """
        try:
            # Load voice prompt
            with open("app/prompts/voice_interview_prompt.txt", "r") as f:
                voice_prompt_template = f.read()
            
            prompt = ChatPromptTemplate.from_messages([
                ("system", voice_prompt_template),
                ("human", "{transcript}")
            ])
            
            # Create chain
            chain = prompt | self.llm | self.parser
            
            # Execute
            result = chain.invoke({
                "transcript": transcript,
                "candidate_name": candidate_name,
                "role_title": role_title
            })
            
            logger.info("Successfully evaluated voice transcript")
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error evaluating transcript: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# Global agent instance
interview_agent = InterviewAgent()
