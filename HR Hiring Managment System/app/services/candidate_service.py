"""
Candidate Service - Orchestrates candidate workflow.
"""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
from datetime import datetime

from app.db.models import Candidate, CandidateScore, CandidateStage, CandidateStatus, EmailLog, EmailType
from app.agents.resume_agent import resume_agent
from app.agents.scoring_agent import scoring_agent
from app.agents.shortlist_agent import shortlist_agent
from app.vectorstore.chroma_client import chroma_client
from app.utils.file_utils import save_resume_file, extract_text_from_resume
from app.tools.email_tool import EmailTool

logger = logging.getLogger(__name__)


class CandidateService:
    """Service for managing candidate workflow."""
    
    def __init__(self, db: Session):
        """
        Initialize candidate service.
        
        Args:
            db: Database session
        """
        self.db = db
        self.email_tool = EmailTool()
    
    async def submit_candidate(
        self,
        name: str,
        email: str,
        phone: Optional[str],
        resume_file_content: bytes,
        resume_filename: str
    ) -> Dict[str, Any]:
        """
        Handle new candidate submission.
        
        Args:
            name: Candidate name
            email: Candidate email
            phone: Candidate phone
            resume_file_content: Resume file bytes
            resume_filename: Original filename
        
        Returns:
            Dict with candidate_id and status
        """
        try:
            # Check if candidate already exists
            existing_candidate = self.db.query(Candidate).filter(Candidate.email == email).first()
            if existing_candidate:
                return {
                    "status": "error",
                    "message": f"Candidate with email {email} already exists."
                }

            # Create candidate record
            candidate = Candidate(
                name=name,
                email=email,
                phone=phone,
                resume_path="",  # Will be updated after file save
                current_stage=CandidateStage.SUBMITTED
            )
            self.db.add(candidate)
            self.db.commit()
            self.db.refresh(candidate)
            
            # Save resume file
            resume_path = save_resume_file(resume_file_content, resume_filename, candidate.id)
            candidate.resume_path = resume_path
            self.db.commit()
            
            # Parse resume
            parse_result = resume_agent.parse_resume(resume_path)
            
            if parse_result["status"] == "success":
                # Update stage to parsed
                candidate.current_stage = CandidateStage.PARSED
                self.db.commit()
                
                # Generate and store embedding
                resume_text = extract_text_from_resume(resume_path)
                chroma_client.add_resume_embedding(
                    candidate_id=candidate.id,
                    text=resume_text,
                    metadata={
                        "name": name,
                        "email": email,
                        "skills": ", ".join(parse_result["data"].get("skills", []))
                    }
                )
                
                logger.info(f"Successfully submitted candidate {candidate.id}")
                
                # Check for cached role_id if available (e.g. from form data)
                # For now, we return success and let the frontend trigger evaluation or handle it separately
                # But to fix the "No candidates scored" issue, we should ensure evaluation happens.
                # Since submit_candidate doesn't take role_id currently, we rely on the frontend calling /evaluate
                # OR we update submit_candidate to take role_id.
                
                return {
                    "status": "success",
                    "candidate_id": candidate.id,
                    "parsed_data": parse_result["data"]
                }
            else:
                logger.error(f"Resume parsing failed for candidate {candidate.id}")
                return {
                    "status": "error",
                    "message": "Resume parsing failed",
                    "candidate_id": candidate.id
                }
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error submitting candidate: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def evaluate_candidate(
        self,
        candidate_id: int,
        role_id: int
    ) -> Dict[str, Any]:
        """
        Evaluate candidate for a specific role.
        
        Args:
            candidate_id: Candidate ID
            role_id: Role ID
        
        Returns:
            Dict with evaluation results
        """
        try:
            # Get candidate
            candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                return {"status": "error", "message": "Candidate not found"}
            
            # Get role
            from app.db.models import Role
            role = self.db.query(Role).filter(Role.id == role_id).first()
            if not role:
                return {"status": "error", "message": "Role not found"}
            
            # Parse resume if not already parsed
            if candidate.current_stage == CandidateStage.SUBMITTED:
                parse_result = resume_agent.parse_resume(candidate.resume_path)
                if parse_result["status"] != "success":
                    return {"status": "error", "message": "Resume parsing failed"}
                candidate_data = parse_result["data"]
                candidate.current_stage = CandidateStage.PARSED
                self.db.commit()
            else:
                # Re-parse for evaluation
                parse_result = resume_agent.parse_resume(candidate.resume_path)
                candidate_data = parse_result["data"]
            
            # Get similarity score
            similarity_score = chroma_client.get_similarity_score(candidate_id, role_id)
            
            # Score candidate
            role_data = {
                "title": role.title,
                "description": role.description,
                "required_skills": role.required_skills,
                "experience_required": role.experience_required
            }
            
            score_result = scoring_agent.score_candidate(
                candidate_data=candidate_data,
                role_data=role_data,
                similarity_score=similarity_score
            )
            
            if score_result["status"] == "success":
                # Save score to database
                score_data = score_result["data"]
                candidate_score = CandidateScore(
                    candidate_id=candidate_id,
                    role_id=role_id,
                    resume_score=score_data["resume_score"],
                    match_percentage=score_data["match_percentage"],
                    strengths=score_data["strengths"],
                    gaps=score_data["gaps"],
                    ai_reasoning=score_data["ai_reasoning"]
                )
                self.db.add(candidate_score)
                candidate.current_stage = CandidateStage.SCORED
                self.db.commit()
                
                # Evaluate for shortlisting
                shortlist_result = shortlist_agent.evaluate_candidate(
                    candidate_score=score_data["resume_score"],
                    match_percentage=score_data["match_percentage"]
                )
                
                logger.info(f"Evaluated candidate {candidate_id} for role {role_id}")
                return {
                    "status": "success",
                    "score_data": score_data,
                    "shortlist_decision": shortlist_result
                }
            else:
                return score_result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error evaluating candidate: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def process_shortlist(
        self,
        role_id: int,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Process shortlisting for all candidates for a role.
        
        Args:
            role_id: Role ID
            threshold: Custom threshold (optional)
        
        Returns:
            Dict with shortlisting results
        """
        try:
            # Get all scores for this role
            scores = self.db.query(CandidateScore).filter(
                CandidateScore.role_id == role_id
            ).all()
            
            if not scores:
                return {
                    "status": "error",
                    "message": "No candidates scored for this role"
                }
            
            # Prepare candidate data for batch evaluation
            candidates_data = []
            for score in scores:
                candidates_data.append({
                    "candidate_id": score.candidate_id,
                    "resume_score": score.resume_score,
                    "match_percentage": score.match_percentage
                })
            
            # Batch evaluate
            shortlist_result = shortlist_agent.batch_evaluate(candidates_data, threshold)
            
            if shortlist_result["status"] == "success":
                # Send emails to shortlisted candidates
                from app.db.models import Role
                role = self.db.query(Role).filter(Role.id == role_id).first()
                
                for shortlisted in shortlist_result["shortlisted"]:
                    candidate = self.db.query(Candidate).filter(
                        Candidate.id == shortlisted["candidate_id"]
                    ).first()
                    
                    if candidate:
                        # Send shortlist email
                        self.email_tool.send_shortlist_email(
                            candidate_name=candidate.name,
                            candidate_email=candidate.email,
                            role_title=role.title
                        )
                        
                        # Log email
                        email_log = EmailLog(
                            candidate_id=candidate.id,
                            email_type=EmailType.SHORTLIST,
                            sent_date=datetime.utcnow()
                        )
                        self.db.add(email_log)
                        
                        # Update candidate stage
                        candidate.current_stage = CandidateStage.SHORTLISTED
                
                # Send rejection emails
                for rejected in shortlist_result["rejected"]:
                    candidate = self.db.query(Candidate).filter(
                        Candidate.id == rejected["candidate_id"]
                    ).first()
                    
                    if candidate:
                        self.email_tool.send_rejection_email(
                            candidate_name=candidate.name,
                            candidate_email=candidate.email,
                            role_title=role.title
                        )
                        
                        email_log = EmailLog(
                            candidate_id=candidate.id,
                            email_type=EmailType.REJECTION,
                            sent_date=datetime.utcnow()
                        )
                        self.db.add(email_log)
                        
                        candidate.status = CandidateStatus.REJECTED
                
                self.db.commit()
                
                logger.info(f"Processed shortlist for role {role_id}")
                return shortlist_result
            else:
                return shortlist_result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error processing shortlist: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                "status": "error",
                "message": str(e)
            }

    async def update_preferred_time(self, candidate_id: int, preferred_time: datetime) -> Dict[str, Any]:
        """Update candidate's preferred interview time."""
        try:
            candidate = self.db.query(Candidate).filter(Candidate.id == candidate_id).first()
            if not candidate:
                return {"status": "error", "message": "Candidate not found"}
            
            candidate.preferred_interview_time = preferred_time
            self.db.commit()
            logger.info(f"Updated preferred interview time for candidate {candidate_id} to {preferred_time}")
            return {"status": "success", "message": "Preferred time updated"}
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating preferred time: {e}")
            return {"status": "error", "message": str(e)}
