"""
Scheduler - Handles background tasks like triggering voice interviews.
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models import Candidate, CandidateStage, Role, Interview
from app.services.voice_service import voice_ai_service
from app.config.settings import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()

async def check_and_trigger_voice_interviews():
    """
    Check for candidates who have a preferred interview time now 
    and trigger the voice AI call.
    """
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        # Look for candidates scheduled for the next 2 minutes (to avoid missing window)
        # and who are in the SHORTLISTED stage (or whatever stage indicates ready for voice)
        window_start = now - timedelta(minutes=1)
        window_end = now + timedelta(minutes=1)
        
        candidates = db.query(Candidate).filter(
            Candidate.preferred_interview_time >= window_start,
            Candidate.preferred_interview_time <= window_end,
            Candidate.current_stage == CandidateStage.SHORTLISTED
        ).all()
        
        for candidate in candidates:
            # For which role? 
            # Assuming there's a recent role they were shortlisted for.
            # In a multi-role system, we'd need a more specific mapping.
            # For now, we take their most recent score's role.
            from app.db.models import CandidateScore
            latest_score = db.query(CandidateScore).filter(
                CandidateScore.candidate_id == candidate.id
            ).order_by(CandidateScore.scored_date.desc()).first()
            
            if not latest_score:
                continue
                
            role = db.query(Role).filter(Role.id == latest_score.role_id).first()
            if not role:
                continue
            
            # Check if an interview already exists for this candidate/role to avoid double calling
            existing_interview = db.query(Interview).filter(
                Interview.candidate_id == candidate.id,
                Interview.role_id == role.id,
                Interview.is_voice_interview == True
            ).first()
            
            if existing_interview:
                continue

            logger.info(f"Triggering scheduled voice interview for {candidate.name}")
            
            # Prepare skills string
            skills = ", ".join(role.required_skills) if isinstance(role.required_skills, list) else str(role.required_skills)
            
            # Initiate call
            result = voice_ai_service.create_phone_call(
                to_number=candidate.phone,
                candidate_name=candidate.name,
                role_title=role.title,
                key_skills=skills
            )
            
            if result["status"] == "success":
                # Create interview record
                interview = Interview(
                    candidate_id=candidate.id,
                    role_id=role.id,
                    is_voice_interview=True,
                    voice_session_id=result["call_id"],
                    interview_date=now,
                    overall_score=0, # Will be updated after call
                    communication_score=0,
                    knowledge_score=0,
                    confidence_score=0,
                    feedback="Voice AI screening initiated."
                )
                db.add(interview)
                # candidate.current_stage = CandidateStage.INTERVIEWED # Wait for completion?
                db.commit()
                logger.info(f"Voice interview record created for {candidate.name}")
            else:
                logger.error(f"Failed to trigger call for {candidate.name}: {result.get('message')}")
                
    except Exception as e:
        logger.error(f"Error in scheduler task: {e}")
    finally:
        db.close()

def start_scheduler():
    """Start the background scheduler."""
    if settings.scheduler_enabled:
        scheduler.add_job(
            check_and_trigger_voice_interviews, 
            'interval', 
            minutes=settings.voice_interview_check_interval_mins
        )
        scheduler.start()
        logger.info(f"Scheduler started (interval: {settings.voice_interview_check_interval_mins} mins)")

def shutdown_scheduler():
    """Shutdown the background scheduler."""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
