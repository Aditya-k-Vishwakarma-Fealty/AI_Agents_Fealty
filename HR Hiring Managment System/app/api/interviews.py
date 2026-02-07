"""
Interviews API Router - Endpoints for interview management.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from app.db.session import get_db
from app.db.models import Interview
from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/interviews", tags=["interviews"])


# Pydantic models
class SubmitInterviewRequest(BaseModel):
    candidate_id: int
    role_id: int
    interviewer_name: str
    communication_score: float
    knowledge_score: float
    confidence_score: float
    feedback: str


class InterviewResponse(BaseModel):
    id: int
    candidate_id: int
    role_id: int
    interviewer_name: Optional[str]
    communication_score: float
    knowledge_score: float
    confidence_score: float
    overall_score: float
    feedback: Optional[str]
    interview_date: Optional[datetime]
    
    class Config:
        from_attributes = True


class ScheduleInterviewRequest(BaseModel):
    candidate_id: int
    role_id: int
    interview_datetime: str


@router.post("/submit")
async def submit_interview(
    request: SubmitInterviewRequest,
    db: Session = Depends(get_db)
):
    """
    Submit interview feedback and get AI evaluation.
    
    Args:
        request: Interview feedback data
        db: Database session
    
    Returns:
        Interview ID and AI evaluation
    """
    try:
        # Validate scores
        if not (0 <= request.communication_score <= 10):
            raise HTTPException(status_code=400, detail="Communication score must be between 0 and 10")
        if not (0 <= request.knowledge_score <= 10):
            raise HTTPException(status_code=400, detail="Knowledge score must be between 0 and 10")
        if not (0 <= request.confidence_score <= 10):
            raise HTTPException(status_code=400, detail="Confidence score must be between 0 and 10")
        
        # Evaluate interview
        service = EvaluationService(db)
        result = await service.evaluate_interview(
            candidate_id=request.candidate_id,
            role_id=request.role_id,
            interviewer_name=request.interviewer_name,
            communication_score=request.communication_score,
            knowledge_score=request.knowledge_score,
            confidence_score=request.confidence_score,
            feedback=request.feedback
        )
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Interview evaluation failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_interview endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{interview_id}", response_model=InterviewResponse)
async def get_interview(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    Get interview details by ID.
    
    Args:
        interview_id: Interview ID
        db: Database session
    
    Returns:
        Interview details
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return interview


@router.get("/{interview_id}/evaluation")
async def get_interview_evaluation(
    interview_id: int,
    db: Session = Depends(get_db)
):
    """
    Get AI evaluation for an interview.
    
    Args:
        interview_id: Interview ID
        db: Database session
    
    Returns:
        AI evaluation details
    """
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    return {
        "interview_id": interview.id,
        "candidate_id": interview.candidate_id,
        "overall_score": interview.overall_score,
        "ai_evaluation": interview.ai_evaluation
    }


@router.get("/candidate/{candidate_id}", response_model=List[InterviewResponse])
async def get_candidate_interviews(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all interviews for a candidate.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
    
    Returns:
        List of interviews
    """
    interviews = db.query(Interview).filter(
        Interview.candidate_id == candidate_id
    ).all()
    
    return interviews


@router.post("/schedule")
async def schedule_interview(
    request: ScheduleInterviewRequest,
    db: Session = Depends(get_db)
):
    """
    Schedule an interview (sends invitation email).
    
    Args:
        request: Schedule request
        db: Database session
    
    Returns:
        Confirmation
    """
    try:
        from app.db.models import Candidate, Role
        from app.tools.email_tool import EmailTool
        
        # Get candidate and role
        candidate = db.query(Candidate).filter(Candidate.id == request.candidate_id).first()
        role = db.query(Role).filter(Role.id == request.role_id).first()
        
        if not candidate or not role:
            raise HTTPException(status_code=404, detail="Candidate or role not found")
        
        # Send interview invitation
        email_tool = EmailTool()
        result = email_tool.send_interview_invite(
            candidate_name=candidate.name,
            candidate_email=candidate.email,
            role_title=role.title,
            interview_datetime=request.interview_datetime
        )
        
        if result["status"] == "success":
            return {
                "status": "success",
                "message": "Interview invitation sent",
                "candidate_email": candidate.email,
                "interview_datetime": request.interview_datetime
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send invitation")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error scheduling interview: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/role/{role_id}/generate-ranking")
async def generate_ranking(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Generate final ranking for all interviewed candidates for a role.
    
    Args:
        role_id: Role ID
        db: Database session
    
    Returns:
        Ranking results
    """
    try:
        service = EvaluationService(db)
        result = await service.generate_final_ranking(role_id=role_id)
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Ranking generation failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating ranking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/role/{role_id}/final-decision")
async def make_final_decision(
    role_id: int,
    selections: int,
    waitlist: int = 0,
    db: Session = Depends(get_db)
):
    """
    Make final hiring decisions for a role.
    
    Args:
        role_id: Role ID
        selections: Number of candidates to select
        waitlist: Number of candidates to waitlist
        db: Database session
    
    Returns:
        Decision results
    """
    try:
        service = EvaluationService(db)
        result = await service.make_final_decision(
            role_id=role_id,
            selections=selections,
            waitlist=waitlist
        )
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Decision making failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error making final decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))
