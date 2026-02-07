"""
Resume Parsing Agent - Extracts structured data from resumes.
"""
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from typing import Dict, Any
import logging
import json

from app.config.settings import settings
from app.utils.file_utils import extract_text_from_resume

logger = logging.getLogger(__name__)


class ResumeParsingAgent:
    """Agent for parsing resumes and extracting structured information."""
    
    def __init__(self):
        """Initialize the resume parsing agent."""
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0,
            openai_api_key=settings.openai_api_key
        )
        
        # Load system prompt
        with open("app/prompts/resume_prompt.txt", "r") as f:
            self.system_prompt = f.read()
        
        self.parser = JsonOutputParser()
    
    def parse_resume(self, resume_path: str) -> Dict[str, Any]:
        """
        Parse resume and extract structured information.
        
        Args:
            resume_path: Path to resume file
        
        Returns:
            Dict with parsed resume data
        """
        try:
            # Extract text from resume
            resume_text = extract_text_from_resume(resume_path)
            
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "Resume text:\n\n{resume_text}")
            ])
            
            # Create chain
            chain = prompt | self.llm | self.parser
            
            # Execute
            result = chain.invoke({"resume_text": resume_text})
            
            logger.info(f"Successfully parsed resume: {resume_path}")
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error parsing resume: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def parse_resume_text(self, resume_text: str) -> Dict[str, Any]:
        """
        Parse resume from text directly.
        
        Args:
            resume_text: Resume text content
        
        Returns:
            Dict with parsed resume data
        """
        try:
            # Create prompt
            prompt = ChatPromptTemplate.from_messages([
                ("system", self.system_prompt),
                ("human", "Resume text:\n\n{resume_text}")
            ])
            
            # Create chain
            chain = prompt | self.llm | self.parser
            
            # Execute
            result = chain.invoke({"resume_text": resume_text})
            
            logger.info("Successfully parsed resume from text")
            return {
                "status": "success",
                "data": result
            }
        except Exception as e:
            logger.error(f"Error parsing resume text: {e}")
            return {
                "status": "error",
                "message": str(e)
            }


# Global agent instance
resume_agent = ResumeParsingAgent()
