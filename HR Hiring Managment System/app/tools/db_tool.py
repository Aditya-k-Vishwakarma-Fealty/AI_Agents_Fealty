"""
Database tool for LangChain agents.
Provides database operations as tools that agents can use.
"""
from langchain.tools import Tool
from sqlalchemy.orm import Session
from typing import Dict, Any, List
import json
import logging

from app.db.models import (
    Candidate, Role, CandidateScore, Interview, 
    EmailLog, FinalRanking, CandidateStage, CandidateStatus
)

logger = logging.getLogger(__name__)


class DatabaseTool:
    """Database operations wrapper for LangChain agents."""
    
    def __init__(self, db: Session):
        """
        Initialize database tool with session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
    
    def create_candidate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new candidate record.
        
        Args:
            data: Candidate data (name, email, phone, resume_path)
        
        Returns:
            Dict with candidate_id and status
        """
        try:
            candidate = Candidate(
                name=data["name"],
                email=data["email"],
                phone=data.get("phone"),
                resume_path=data["resume_path"]
            )
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            
            logger.info(f"Created candidate: {candidate.id}")
            return {"candidate_id": candidate.id, "status": "success"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating candidate: {e}")
            return {"status": "error", "message": str(e)}
    
    def update_candidate_stage(self, candidate_id: int, stage: str) -> Dict[str, Any]:
        """
        Update candidate's current stage.
        
        Args:
            candidate_id: Candidate ID
            stage: New stage (submitted, parsed, scored, shortlisted, interviewed, final)
        
        Returns:
            Dict with status
        """
        try:
            candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                return {"status": "error", "message": "Candidate not found"}
            
            candidate.current_stage = CandidateStage(stage)
            self.db.commit()
            
            logger.info(f"Updated candidate {candidate_id} stage to {stage}")
            return {"status": "success", "stage": stage}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating candidate stage: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_candidate(self, candidate_id: int) -> Dict[str, Any]:
        """
        Retrieve candidate information.
        
        Args:
            candidate_id: Candidate ID
        
        Returns:
            Dict with candidate data
        """
        try:
            candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                return {"status": "error", "message": "Candidate not found"}
            
            return {
                "status": "success",
                "candidate": {
                    "id": candidate.id,
                    "name": candidate.name,
                    "email": candidate.email,
                    "phone": candidate.phone,
                    "resume_path": candidate.resume_path,
                    "current_stage": candidate.current_stage.value,
                    "status": candidate.status.value
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving candidate: {e}")
            return {"status": "error", "message": str(e)}
    
    def save_score(self, candidate_id: int, role_id: int, score_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save candidate scoring results.
        
        Args:
            candidate_id: Candidate ID
            role_id: Role ID
            score_data: Score data (resume_score, match_percentage, strengths, gaps, ai_reasoning)
        
        Returns:
            Dict with status
        """
        try:
            score = CandidateScore(
                candidate_id=candidate_id,
                role_id=role_id,
                resume_score=score_data["resume_score"],
                match_percentage=score_data["match_percentage"],
                strengths=score_data.get("strengths", []),
                gaps=score_data.get("gaps", []),
                ai_reasoning=score_data.get("ai_reasoning", "")
            )
            self.db.add(score)
            self.db.commit()
            
            logger.info(f"Saved score for candidate {candidate_id}, role {role_id}")
            return {"status": "success", "score_id": score.id}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving score: {e}")
            return {"status": "error", "message": str(e)}
    
    def save_interview(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Save interview feedback and scores.
        
        Args:
            data: Interview data (candidate_id, role_id, scores, feedback, ai_evaluation)
        
        Returns:
            Dict with status and interview_id
        """
        try:
            interview = Interview(
                candidate_id=data["candidate_id"],
                role_id=data["role_id"],
                interviewer_name=data.get("interviewer_name"),
                communication_score=data["communication_score"],
                knowledge_score=data["knowledge_score"],
                confidence_score=data["confidence_score"],
                overall_score=data["overall_score"],
                feedback=data.get("feedback"),
                ai_evaluation=data.get("ai_evaluation")
            )
            self.db.add(interview)
            self.db.commit()
            self.db.refresh(interview)
            
            logger.info(f"Saved interview for candidate {data['candidate_id']}")
            return {"status": "success", "interview_id": interview.id}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving interview: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_role(self, role_id: int) -> Dict[str, Any]:
        """
        Retrieve role information.
        
        Args:
            role_id: Role ID
        
        Returns:
            Dict with role data
        """
        try:
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return {"status": "error", "message": "Role not found"}
            
            return {
                "status": "success",
                "role": {
                    "id": role.id,
                    "title": role.title,
                    "description": role.description,
                    "required_skills": role.required_skills,
                    "experience_required": role.experience_required
                }
            }
        except Exception as e:
            logger.error(f"Error retrieving role: {e}")
            return {"status": "error", "message": str(e)}


def create_db_tools(db: Session) -> List[Tool]:
    """
    Create LangChain tools for database operations.
    
    Args:
        db: Database session
    
    Returns:
        List of LangChain Tool objects
    """
    db_tool = DatabaseTool(db)
    
    tools = [
        Tool(
            name="create_candidate",
            func=lambda data: db_tool.create_candidate(json.loads(data) if isinstance(data, str) else data),
            description="Create a new candidate record. Input should be JSON with: name, email, phone, resume_path"
        ),
        Tool(
            name="update_candidate_stage",
            func=lambda data: db_tool.update_candidate_stage(**json.loads(data) if isinstance(data, str) else data),
            description="Update candidate stage. Input should be JSON with: candidate_id, stage"
        ),
        Tool(
            name="get_candidate",
            func=lambda candidate_id: db_tool.get_candidate(int(candidate_id)),
            description="Get candidate information by ID. Input should be candidate_id"
        ),
        Tool(
            name="save_score",
            func=lambda data: db_tool.save_score(**json.loads(data) if isinstance(data, str) else data),
            description="Save candidate scoring results. Input should be JSON with: candidate_id, role_id, score_data"
        ),
        Tool(
            name="save_interview",
            func=lambda data: db_tool.save_interview(json.loads(data) if isinstance(data, str) else data),
            description="Save interview feedback. Input should be JSON with interview data"
        ),
        Tool(
            name="get_role",
            func=lambda role_id: db_tool.get_role(int(role_id)),
            description="Get role information by ID. Input should be role_id"
        )
    ]
    
    return tools
