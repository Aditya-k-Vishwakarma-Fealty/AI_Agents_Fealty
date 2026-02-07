"""
Candidates API Router - Endpoints for candidate management.
"""
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import logging

from app.db.session import get_db
from app.db.models import Candidate, CandidateScore, CandidateStage, CandidateStatus
from app.services.candidate_service import CandidateService
from app.utils.file_utils import validate_file_type

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/candidates", tags=["candidates"])


# Pydantic models for request/response
class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    current_stage: str
    status: str
    
    class Config:
        from_attributes = True


class EvaluateRequest(BaseModel):
    role_id: int


class UpdateStageRequest(BaseModel):
    stage: str


@router.post("/submit")
async def submit_candidate(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: Optional[str] = Form(None),
    resume: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Submit a new candidate with resume.
    
    Args:
        name: Candidate name
        email: Candidate email
        phone: Candidate phone (optional)
        resume: Resume file (PDF or DOCX)
        db: Database session
    
    Returns:
        Candidate ID and status
    """
    try:
        # Validate file type
        is_valid, error_msg = validate_file_type(resume.filename)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Read file content
        file_content = await resume.read()
        
        # Create service and submit candidate
        service = CandidateService(db)
        result = await service.submit_candidate(
            name=name,
            email=email,
            phone=phone,
            resume_file_content=file_content,
            resume_filename=resume.filename
        )
        
        if result["status"] == "success":
            return {
                "candidate_id": result["candidate_id"],
                "status": "success",
                "message": "Candidate submitted successfully",
                "parsed_data": result.get("parsed_data")
            }
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Submission failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in submit_candidate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{candidate_id}", response_model=CandidateResponse)
async def get_candidate(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get candidate details by ID.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
    
    Returns:
        Candidate details
    """
    candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    
    return candidate


@router.post("/{candidate_id}/evaluate")
async def evaluate_candidate(
    candidate_id: int,
    request: EvaluateRequest,
    db: Session = Depends(get_db)
):
    """
    Evaluate candidate for a specific role.
    
    Args:
        candidate_id: Candidate ID
        request: Evaluation request with role_id
        db: Database session
    
    Returns:
        Evaluation results
    """
    try:
        service = CandidateService(db)
        result = await service.evaluate_candidate(
            candidate_id=candidate_id,
            role_id=request.role_id
        )
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Evaluation failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in evaluate_candidate endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=List[CandidateResponse])
async def list_candidates(
    role_id: Optional[int] = Query(None),
    status: Optional[str] = Query(None),
    stage: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List candidates with optional filters.
    
    Args:
        role_id: Filter by role ID (optional)
        status: Filter by status (optional)
        stage: Filter by stage (optional)
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of candidates
    """
    query = db.query(Candidate)
    
    # Apply filters
    if role_id:
        # Filter candidates who have scores for this role
        query = query.join(CandidateScore).filter(CandidateScore.role_id == role_id)
    
    if status:
        try:
            query = query.filter(Candidate.status == CandidateStatus(status))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid status: {status}")
    
    if stage:
        try:
            query = query.filter(Candidate.current_stage == CandidateStage(stage))
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")
    
    candidates = query.offset(skip).limit(limit).all()
    return candidates


@router.put("/{candidate_id}/stage")
async def update_candidate_stage(
    candidate_id: int,
    request: UpdateStageRequest,
    db: Session = Depends(get_db)
):
    """
    Manually update candidate's stage.
    
    Args:
        candidate_id: Candidate ID
        request: Update request with new stage
        db: Database session
    
    Returns:
        Updated candidate
    """
    try:
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            raise HTTPException(status_code=404, detail="Candidate not found")
        
        # Validate stage
        try:
            new_stage = CandidateStage(request.stage)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid stage: {request.stage}")
        
        candidate.current_stage = new_stage
        db.commit()
        db.refresh(candidate)
        
        return {
            "status": "success",
            "candidate_id": candidate.id,
            "new_stage": candidate.current_stage.value
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating candidate stage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{candidate_id}/scores")
async def get_candidate_scores(
    candidate_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all scores for a candidate across different roles.
    
    Args:
        candidate_id: Candidate ID
        db: Database session
    
    Returns:
        List of scores
    """
    scores = db.query(CandidateScore).filter(
        CandidateScore.candidate_id == candidate_id
    ).all()
    
    result = []
    for score in scores:
        result.append({
            "role_id": score.role_id,
            "resume_score": score.resume_score,
            "match_percentage": score.match_percentage,
            "strengths": score.strengths,
            "gaps": score.gaps,
            "ai_reasoning": score.ai_reasoning,
            "scored_date": score.scored_date.isoformat()
        })
    
    return result
