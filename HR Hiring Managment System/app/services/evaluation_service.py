"""
Evaluation Service - Handles scoring, ranking, and final decisions.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.db.models import (
    Candidate, Role, CandidateScore, Interview, FinalRanking,
    FinalDecision, CandidateStage
)
from app.agents.interview_agent import interview_agent
from app.config.settings import settings

logger = logging.getLogger(__name__)


class EvaluationService:
    """Service for evaluation, scoring, and ranking operations."""
    
    def __init__(self, db: Session):
        """
        Initialize evaluation service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def evaluate_interview(
        self,
        candidate_id: int,
        role_id: int,
        interviewer_name: str,
        communication_score: float,
        knowledge_score: float,
        confidence_score: float,
        feedback: str
    ) -> Dict[str, Any]:
        """
        Evaluate interview performance.
        
        Args:
            candidate_id: Candidate ID
            role_id: Role ID
            interviewer_name: Interviewer's name
            communication_score: Communication score (0-10)
            knowledge_score: Knowledge score (0-10)
            confidence_score: Confidence score (0-10)
            feedback: Interviewer feedback
        
        Returns:
            Dict with evaluation results
        """
        try:
            # Get candidate and role data
            candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
            role = self.db.query(Role).filter(Role.id == role_id).first()
            
            if not candidate or not role:
                return {"status": "error", "message": "Candidate or role not found"}
            
            # Calculate overall score
            overall_score = interview_agent.calculate_overall_score(
                communication_score, knowledge_score, confidence_score
            )
            
            # Get AI evaluation
            from app.agents.resume_agent import resume_agent
            parse_result = resume_agent.parse_resume(candidate.resume_path)
            candidate_data = parse_result.get("data", {}) if parse_result["status"] == "success" else {}
            
            role_data = {
                "title": role.title,
                "experience_required": role.experience_required
            }
            
            eval_result = interview_agent.evaluate_interview(
                communication_score=communication_score,
                knowledge_score=knowledge_score,
                confidence_score=confidence_score,
                feedback=feedback,
                candidate_data=candidate_data,
                role_data=role_data
            )
            
            if eval_result["status"] == "success":
                # Save interview record
                interview = Interview(
                    candidate_id=candidate_id,
                    role_id=role_id,
                    interviewer_name=interviewer_name,
                    communication_score=communication_score,
                    knowledge_score=knowledge_score,
                    confidence_score=confidence_score,
                    overall_score=overall_score,
                    feedback=feedback,
                    ai_evaluation=eval_result["data"],
                    interview_date=datetime.utcnow()
                )
                self.db.add(interview)
                
                # Update candidate stage
                candidate.current_stage = CandidateStage.INTERVIEWED
                self.db.commit()
                self.db.refresh(interview)
                
                logger.info(f"Evaluated interview for candidate {candidate_id}")
                return {
                    "status": "success",
                    "interview_id": interview.id,
                    "overall_score": overall_score,
                    "ai_evaluation": eval_result["data"]
                }
            else:
                return eval_result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error evaluating interview: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def generate_final_ranking(
        self,
        role_id: int,
        resume_weight: Optional[float] = None,
        interview_weight: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate final ranking for all candidates for a role.
        
        Args:
            role_id: Role ID
            resume_weight: Weight for resume score (default from settings)
            interview_weight: Weight for interview score (default from settings)
        
        Returns:
            Dict with ranked candidates
        """
        try:
            # Use default weights if not provided
            resume_w = resume_weight if resume_weight is not None else settings.resume_score_weight
            interview_w = interview_weight if interview_weight is not None else settings.interview_score_weight
            
            # Get all candidates with both scores and interviews
            candidates_data = []
            
            # Query candidates who have been interviewed
            interviews = self.db.query(Interview).filter(Interview.role_id == role_id).all()
            
            for interview in interviews:
                # Get resume score
                score = self.db.query(CandidateScore).filter(
                    CandidateScore.candidate_id == interview.candidate_id,
                    CandidateScore.role_id == role_id
                ).first()
                
                if score:
                    # Calculate combined score
                    # Normalize interview score (0-10) to (0-100)
                    normalized_interview_score = interview.overall_score * 10
                    
                    combined_score = (
                        score.resume_score * resume_w +
                        normalized_interview_score * interview_w
                    )
                    
                    candidates_data.append({
                        "candidate_id": interview.candidate_id,
                        "resume_score": score.resume_score,
                        "interview_score": interview.overall_score,
                        "combined_score": combined_score
                    })
            
            # Sort by combined score (descending)
            candidates_data.sort(key=lambda x: x["combined_score"], reverse=True)
            
            # Assign ranks and save to database
            for rank, candidate_data in enumerate(candidates_data, start=1):
                # Check if ranking already exists
                existing_ranking = self.db.query(FinalRanking).filter(
                    FinalRanking.candidate_id == candidate_data["candidate_id"],
                    FinalRanking.role_id == role_id
                ).first()
                
                if existing_ranking:
                    # Update existing ranking
                    existing_ranking.combined_score = candidate_data["combined_score"]
                    existing_ranking.rank = rank
                else:
                    # Create new ranking
                    ranking = FinalRanking(
                        candidate_id=candidate_data["candidate_id"],
                        role_id=role_id,
                        combined_score=candidate_data["combined_score"],
                        rank=rank
                    )
                    self.db.add(ranking)
                
                # Update candidate stage
                candidate = self.db.query(Candidate).filter(
                    Candidate.id == candidate_data["candidate_id"]
                ).first()
                if candidate:
                    candidate.current_stage = CandidateStage.FINAL
            
            self.db.commit()
            
            logger.info(f"Generated final ranking for role {role_id}")
            return {
                "status": "success",
                "total_candidates": len(candidates_data),
                "rankings": candidates_data
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error generating final ranking: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def make_final_decision(
        self,
        role_id: int,
        selections: int,
        waitlist: int = 0
    ) -> Dict[str, Any]:
        """
        Make final hiring decisions based on rankings.
        
        Args:
            role_id: Role ID
            selections: Number of candidates to select
            waitlist: Number of candidates to waitlist
        
        Returns:
            Dict with decision results
        """
        try:
            # Get rankings for this role
            rankings = self.db.query(FinalRanking).filter(
                FinalRanking.role_id == role_id
            ).order_by(FinalRanking.rank).all()
            
            if not rankings:
                return {
                    "status": "error",
                    "message": "No rankings found for this role"
                }
            
            selected = []
            waitlisted = []
            rejected = []
            
            for i, ranking in enumerate(rankings):
                candidate = self.db.query(Candidate).filter(
                    Candidate.id == ranking.candidate_id
                ).first()
                
                if i < selections:
                    # Select
                    ranking.final_decision = FinalDecision.SELECTED
                    ranking.decision_date = datetime.utcnow()
                    if candidate:
                        from app.db.models import CandidateStatus
                        candidate.status = CandidateStatus.SELECTED
                    selected.append(ranking.candidate_id)
                elif i < selections + waitlist:
                    # Waitlist
                    ranking.final_decision = FinalDecision.WAITLISTED
                    ranking.decision_date = datetime.utcnow()
                    if candidate:
                        from app.db.models import CandidateStatus
                        candidate.status = CandidateStatus.WAITLISTED
                    waitlisted.append(ranking.candidate_id)
                else:
                    # Reject
                    ranking.final_decision = FinalDecision.REJECTED
                    ranking.decision_date = datetime.utcnow()
                    if candidate:
                        from app.db.models import CandidateStatus
                        candidate.status = CandidateStatus.REJECTED
                    rejected.append(ranking.candidate_id)
            
            self.db.commit()
            
            logger.info(f"Made final decisions for role {role_id}")
            return {
                "status": "success",
                "selected": selected,
                "waitlisted": waitlisted,
                "rejected": rejected,
                "summary": {
                    "selected_count": len(selected),
                    "waitlisted_count": len(waitlisted),
                    "rejected_count": len(rejected)
                }
            }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error making final decisions: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    def get_rankings(self, role_id: int) -> List[Dict[str, Any]]:
        """
        Get rankings for a role with candidate details.
        
        Args:
            role_id: Role ID
        
        Returns:
            List of ranked candidates with details
        """
        try:
            rankings = self.db.query(FinalRanking).filter(
                FinalRanking.role_id == role_id
            ).order_by(FinalRanking.rank).all()
            
            result = []
            for ranking in rankings:
                candidate = self.db.query(Candidate).filter(
                    Candidate.id == ranking.candidate_id
                ).first()
                
                if candidate:
                    result.append({
                        "rank": ranking.rank,
                        "candidate_id": candidate.id,
                        "name": candidate.name,
                        "email": candidate.email,
                        "combined_score": ranking.combined_score,
                        "final_decision": ranking.final_decision.value if ranking.final_decision else None,
                        "decision_date": ranking.decision_date.isoformat() if ranking.decision_date else None
                    })
            
            return result
        except Exception as e:
            logger.error(f"Error getting rankings: {e}")
            return []
    async def process_voice_interview_result(
        self,
        call_id: str,
        transcript: str,
        duration: float
    ) -> Dict[str, Any]:
        """
        Process results from a completed voice interview.
        
        Args:
            call_id: Retell call/session ID
            transcript: Interview transcript
            duration: Call duration in seconds
        """
        try:
            # Find interview record
            interview = self.db.query(Interview).filter(
                Interview.voice_session_id == call_id
            ).first()
            
            if not interview:
                logger.error(f"Interview record not found for call_id: {call_id}")
                return {"status": "error", "message": "Interview record not found"}
            
            # Update interview with transcript
            interview.voice_transcript = transcript
            interview.voice_duration_seconds = int(duration)
            
            # Use AI to analyze the transcript and provide scores
            # We can repurpose the InterviewAgent but with a different prompt if needed.
            # For now, let's use the standard evaluate_interview logic but adapted for transcripts
            
            candidate = self.db.query(Candidate).filter(Candidate.id == interview.candidate_id).first()
            role = self.db.query(Role).filter(Role.id == interview.role_id).first()
            
            # Use the agent to analyze the transcript
            # We'll pass the transcript as if it was 'feedback' for now, 
            # but we should ideally have a specialized prompt.
            eval_result = interview_agent.evaluate_interview(
                communication_score=5, # Baseline, AI will revise
                knowledge_score=5,
                confidence_score=5,
                feedback=f"VOICE INTERVIEW TRANSCRIPT:\n{transcript}",
                candidate_data={"name": candidate.name},
                role_data={"title": role.title}
            )
            
            if eval_result["status"] == "success":
                data = eval_result["data"]
                interview.overall_score = data.get("overall_score", 0)
                # Attempt to extract sub-scores if available, otherwise use overall
                interview.communication_score = data.get("overall_score", 0)
                interview.knowledge_score = data.get("overall_score", 0)
                interview.confidence_score = data.get("overall_score", 0)
                interview.ai_evaluation = data
                
                # Update candidate stage
                candidate.current_stage = CandidateStage.INTERVIEWED
                self.db.commit()
                
                logger.info(f"Successfully processed voice interview for {candidate.name}")
                return {"status": "success", "candidate_id": candidate.id}
            else:
                return eval_result
                
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing voice interview result: {e}")
            return {"status": "error", "message": str(e)}
