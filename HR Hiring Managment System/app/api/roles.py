"""
Roles API Router - Endpoints for role/job description management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
import logging
from datetime import datetime

from app.db.session import get_db
from app.db.models import Role
from app.vectorstore.chroma_client import chroma_client
from app.services.candidate_service import CandidateService
from app.services.evaluation_service import EvaluationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["roles"])


# Pydantic models
class CreateRoleRequest(BaseModel):
    title: str
    description: str
    required_skills: List[str]
    experience_required: Optional[int] = None


class RoleResponse(BaseModel):
    id: int
    title: str
    description: str
    required_skills: List[str]
    experience_required: Optional[int]
    created_date: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class ShortlistRequest(BaseModel):
    threshold: Optional[float] = None


@router.post("/create")
async def create_role(
    request: CreateRoleRequest,
    db: Session = Depends(get_db)
):
    """
    Create a new role/job description.
    
    Args:
        request: Role creation request
        db: Database session
    
    Returns:
        Created role details
    """
    try:
        # Create role
        role = Role(
            title=request.title,
            description=request.description,
            required_skills=request.required_skills,
            experience_required=request.experience_required,
            created_date=datetime.utcnow(),
            is_active=True
        )
        db.add(role)
        db.commit()
        db.refresh(role)
        
        # Generate JD text for embedding
        jd_text = f"""
Title: {request.title}

Description:
{request.description}

Required Skills:
{', '.join(request.required_skills)}

Experience Required: {request.experience_required or 0} years
"""
        
        # Store embedding in ChromaDB
        doc_id = chroma_client.add_role_embedding(
            role_id=role.id,
            jd_text=jd_text,
            metadata={
                "title": request.title,
                "required_skills": ", ".join(request.required_skills),
                "experience_required": request.experience_required
            }
        )
        
        # Update role with embedding ID
        role.jd_embedding_id = doc_id
        db.commit()
        
        logger.info(f"Created role {role.id}")
        return {
            "status": "success",
            "role_id": role.id,
            "role": role
        }
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating role: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Get role details by ID.
    
    Args:
        role_id: Role ID
        db: Database session
    
    Returns:
        Role details
    """
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    return role


@router.get("", response_model=List[RoleResponse])
async def list_roles(
    active_only: bool = Query(True),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db)
):
    """
    List all roles.
    
    Args:
        active_only: Filter for active roles only
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
    
    Returns:
        List of roles
    """
    query = db.query(Role)
    
    if active_only:
        query = query.filter(Role.is_active == True)
    
    roles = query.offset(skip).limit(limit).all()
    return roles


@router.post("/{role_id}/shortlist")
async def run_shortlist(
    role_id: int,
    request: ShortlistRequest = ShortlistRequest(),
    db: Session = Depends(get_db)
):
    """
    Run shortlisting process for a role.
    
    This will:
    1. Score all candidates for the role
    2. Apply shortlisting threshold
    3. Send emails to shortlisted and rejected candidates
    
    Args:
        role_id: Role ID
        request: Shortlist request with optional threshold
        db: Database session
    
    Returns:
        Shortlisting results
    """
    try:
        # Verify role exists
        role = db.query(Role).filter(Role.id == role_id).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")
        
        # Run shortlist process
        service = CandidateService(db)
        result = await service.process_shortlist(
            role_id=role_id,
            threshold=request.threshold
        )
        
        if result["status"] == "success":
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get("message", "Shortlisting failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in shortlist endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{role_id}/candidates")
async def get_role_candidates(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Get all candidates who have applied/been scored for a role.
    
    Args:
        role_id: Role ID
        db: Database session
    
    Returns:
        List of candidates with their scores
    """
    from app.db.models import CandidateScore, Candidate
    
    scores = db.query(CandidateScore).filter(
        CandidateScore.role_id == role_id
    ).all()
    
    result = []
    for score in scores:
        candidate = db.query(Candidate).filter(Candidate.id == score.candidate_id).first()
        if candidate:
            result.append({
                "candidate_id": candidate.id,
                "name": candidate.name,
                "email": candidate.email,
                "resume_score": score.resume_score,
                "match_percentage": score.match_percentage,
                "current_stage": candidate.current_stage.value,
                "status": candidate.status.value
            })
    
    return result


@router.get("/{role_id}/rankings")
async def get_role_rankings(
    role_id: int,
    db: Session = Depends(get_db)
):
    """
    Get final rankings for a role.
    
    Args:
        role_id: Role ID
        db: Database session
    
    Returns:
        Ranked list of candidates
    """
    service = EvaluationService(db)
    rankings = service.get_rankings(role_id)
    
    return {
        "role_id": role_id,
        "total_candidates": len(rankings),
        "rankings": rankings
    }
