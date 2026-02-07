"""
Matching and Scoring Agent - Evaluates candidate-role fit.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import logging

from app.config.settings import settings

logger = logging.getLogger(__name__)


# Trigger reload for prompt update
class ScoringAgent:
    """Agent for scoring candidates against role requirements."""
    
    def __init__(self):
        """Initialize the scoring agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.3,  # Slightly higher for nuanced evaluation
            openai_api_key=settings.openai_api_key
        )
        
        # Load system prompt
        with open("app/prompts/scoring_prompt.txt", "r") as f:
            self.system_prompt = f.read()
        
        self.parser = JsonOutputParser()
    
    def score_candidate(
        self,
        candidate_data: Dict[str, Any],
        role_data: Dict[str, Any],
        similarity_score: float
    ) -> Dict[str, Any]:
        """
        Score candidate against role requirements.
        
        Args:
            candidate_data: Parsed resume data
            role_data: Role requirements
            similarity_score: Vector similarity score (0-1)
        
        Returns:
            Dict with scoring results
        """
        try:
            # Prepare input
            input_text = f"""
CANDIDATE INFORMATION:
Name: {candidate_data.get('name', 'N/A')}
Skills: {', '.join(candidate_data.get('skills', []))}
Total Experience: {candidate_data.get('total_years_experience', 0)} years
Education: {candidate_data.get('education', [])}
Certifications: {', '.join(candidate_data.get('certifications', []))}

Work Experience:
{self._format_experience(candidate_data.get('experience', []))}

ROLE REQUIREMENTS:
Title: {role_data.get('title', 'N/A')}
Description: {role_data.get('description', 'N/A')}
Required Skills: {', '.join(role_data.get('required_skills', []))}
Experience Required: {role_data.get('experience_required', 0)} years

VECTOR SIMILARITY SCORE: {similarity_score:.2f} (0-1 scale)

Please evaluate this candidate for the role and provide your assessment.
"""
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "{input_text}")
            ])
            
            # Create chain
            chain = prompt | self.llm | self.parser
            
            # Execute
            result = chain.invoke({"input_text": input_text})
            
            logger.info(f"Successfully scored candidate for role")
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error scoring candidate: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def _format_experience(self, experiences: list) -> str:
        """Format experience list for prompt."""
        if not experiences:
            return "No experience listed"
        
        formatted = []
        for exp in experiences:
            formatted.append(
                f"- {exp.get('role', 'N/A')} at {exp.get('company', 'N/A')} "
                f"({exp.get('duration', 'N/A')}): {exp.get('description', 'N/A')}"
            )
        return "\n".join(formatted)


# Global agent instance
scoring_agent = ScoringAgent()
