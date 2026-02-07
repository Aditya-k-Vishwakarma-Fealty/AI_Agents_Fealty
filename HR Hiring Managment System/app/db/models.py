"""
Database models for HR Hiring Management System.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Float, 
    ForeignKey, Enum, JSON, Boolean
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


Base = declarative_base()


class CandidateStage(str, enum.Enum):
    """Candidate application stages."""
    SUBMITTED = "submitted"
    PARSED = "parsed"
    SCORED = "scored"
    SHORTLISTED = "shortlisted"
    INTERVIEWED = "interviewed"
    FINAL = "final"


class CandidateStatus(str, enum.Enum):
    """Candidate final status."""
    ACTIVE = "active"
    REJECTED = "rejected"
    WAITLISTED = "waitlisted"
    SELECTED = "selected"


class EmailType(str, enum.Enum):
    """Email communication types."""
    SHORTLIST = "shortlist"
    INTERVIEW_INVITE = "interview_invite"
    REJECTION = "rejection"
    SELECTION = "selection"


class FinalDecision(str, enum.Enum):
    """Final hiring decision."""
    SELECTED = "selected"
    WAITLISTED = "waitlisted"
    REJECTED = "rejected"


class Candidate(Base):
    """Candidate model - stores candidate profile information."""
    __tablename__ = "candidates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(20), nullable=True)
    resume_path = Column(String(500), nullable=False)
    application_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    current_stage = Column(
        Enum(CandidateStage),
        default=CandidateStage.SUBMITTED,
        nullable=False
    )
    status = Column(
        Enum(CandidateStatus),
        default=CandidateStatus.ACTIVE,
        nullable=False
    )
    
    # Relationships
    scores = relationship("CandidateScore", back_populates="candidate", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="candidate", cascade="all, delete-orphan")
    email_logs = relationship("EmailLog", back_populates="candidate", cascade="all, delete-orphan")
    rankings = relationship("FinalRanking", back_populates="candidate", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Candidate(id={self.id}, name='{self.name}', email='{self.email}')>"


class Role(Base):
    """Role model - stores job descriptions and requirements."""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    required_skills = Column(JSON, nullable=False)  # List of skills
    experience_required = Column(Integer, nullable=True)  # Years of experience
    jd_embedding_id = Column(String(255), nullable=True)  # ChromaDB reference
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    scores = relationship("CandidateScore", back_populates="role", cascade="all, delete-orphan")
    interviews = relationship("Interview", back_populates="role", cascade="all, delete-orphan")
    rankings = relationship("FinalRanking", back_populates="role", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Role(id={self.id}, title='{self.title}')>"


class CandidateScore(Base):
    """CandidateScore model - stores resume matching scores."""
    __tablename__ = "candidate_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    resume_score = Column(Float, nullable=False)  # 0-100
    match_percentage = Column(Float, nullable=False)  # 0-100
    strengths = Column(JSON, nullable=True)  # List of strengths
    gaps = Column(JSON, nullable=True)  # List of gaps
    ai_reasoning = Column(Text, nullable=True)  # Explainable AI reasoning
    scored_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="scores")
    role = relationship("Role", back_populates="scores")
    
    def __repr__(self):
        return f"<CandidateScore(candidate_id={self.candidate_id}, role_id={self.role_id}, score={self.resume_score})>"


class Interview(Base):
    """Interview model - stores interview feedback and scores."""
    __tablename__ = "interviews"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    interview_date = Column(DateTime, nullable=True)
    interviewer_name = Column(String(255), nullable=True)
    communication_score = Column(Float, nullable=False)  # 0-10
    knowledge_score = Column(Float, nullable=False)  # 0-10
    confidence_score = Column(Float, nullable=False)  # 0-10
    overall_score = Column(Float, nullable=False)  # 0-10
    feedback = Column(Text, nullable=True)
    ai_evaluation = Column(JSON, nullable=True)  # AI-generated evaluation
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="interviews")
    role = relationship("Role", back_populates="interviews")
    
    def __repr__(self):
        return f"<Interview(id={self.id}, candidate_id={self.candidate_id}, overall_score={self.overall_score})>"


class EmailLog(Base):
    """EmailLog model - tracks email communications."""
    __tablename__ = "email_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    email_type = Column(Enum(EmailType), nullable=False)
    sent_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    reply_received = Column(Boolean, default=False, nullable=False)
    reply_content = Column(Text, nullable=True)
    reply_date = Column(DateTime, nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="email_logs")
    
    def __repr__(self):
        return f"<EmailLog(id={self.id}, candidate_id={self.candidate_id}, type={self.email_type})>"


class FinalRanking(Base):
    """FinalRanking model - stores combined rankings and final decisions."""
    __tablename__ = "final_rankings"
    
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    combined_score = Column(Float, nullable=False)  # Weighted score
    rank = Column(Integer, nullable=False)  # Position in ranking
    final_decision = Column(Enum(FinalDecision), nullable=True)
    decision_date = Column(DateTime, nullable=True)
    decision_notes = Column(Text, nullable=True)
    
    # Relationships
    candidate = relationship("Candidate", back_populates="rankings")
    role = relationship("Role", back_populates="rankings")
    
    def __repr__(self):
        return f"<FinalRanking(candidate_id={self.candidate_id}, role_id={self.role_id}, rank={self.rank})>"
