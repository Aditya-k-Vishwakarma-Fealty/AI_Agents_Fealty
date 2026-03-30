"""
Main FastAPI Application - HR Hiring Management System.
"""
from app.config.settings import settings
from app.utils.rich_setup import (
    configure_rich_logging,
    get_console,
    print_banner,
    print_shutdown_banner,
)

# Rich logging first so all subsequent log lines are styled
configure_rich_logging(settings.log_level)

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.db.session import init_db, close_db, get_db
from app.db.models import Candidate, Role, Interview
from app.api import candidates, roles, interviews, insights
from app.utils.scheduler import start_scheduler, shutdown_scheduler

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown tasks with visible phases in the terminal.
    """
    console = get_console()
    print_banner(
        settings.app_name,
        "AI-Powered Agentic HR Hiring Management System",
        settings.app_version,
    )

    try:
        with console.status(
            "[bold cyan]Phase 1/3[/bold cyan]  [dim]—[/dim]  Initializing database schema…",
            spinner="dots12",
            spinner_style="cyan",
        ):
            init_db()
        console.print(
            "  [green]✓[/green]  [bold]Database[/bold]  [dim]tables ready[/dim]"
        )

        with console.status(
            "[bold cyan]Phase 2/3[/bold cyan]  [dim]—[/dim]  Verifying storage directories…",
            spinner="dots12",
            spinner_style="cyan",
        ):
            settings.ensure_directories()
        console.print(
            "  [green]✓[/green]  [bold]Storage[/bold]   [dim]resumes & vector paths OK[/dim]"
        )

        with console.status(
            "[bold cyan]Phase 3/3[/bold cyan]  [dim]—[/dim]  Starting background scheduler…",
            spinner="dots12",
            spinner_style="cyan",
        ):
            start_scheduler()
        console.print(
            "  [green]✓[/green]  [bold]Scheduler[/bold] [dim]voice interview checks armed[/dim]"
        )

        logger.info(
            "[bold green]Startup complete[/bold green] — API ready at [link=http://0.0.0.0:8000/docs]OpenAPI docs[/link]"
        )
    except Exception:
        logger.exception("[red]Startup failed[/red]")
        raise

    yield

    console.print("\n[yellow]Shutdown sequence[/yellow]")
    logger.info("Stopping scheduler & closing database pool…")
    shutdown_scheduler()
    close_db()
    logger.info("Goodbye.")
    print_shutdown_banner("All services stopped cleanly.")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Agentic HR Hiring Management System",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(candidates.router)
app.include_router(roles.router)
app.include_router(interviews.router)
app.include_router(insights.router)


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version,
    }


@app.get("/stats")
async def dashboard_stats(db: Session = Depends(get_db)):
    """
    Lightweight aggregate counts and recent activity for the admin dashboard.
    Uses SQL COUNT — avoids loading full candidate/role lists.
    """
    candidates_count = db.query(func.count(Candidate.id)).scalar() or 0
    roles_count = (
        db.query(func.count(Role.id)).filter(Role.is_active.is_(True)).scalar() or 0
    )
    interviews_count = db.query(func.count(Interview.id)).scalar() or 0

    recent_candidates = (
        db.query(Candidate)
        .order_by(Candidate.application_date.desc())
        .limit(8)
        .all()
    )
    recent_activity = [
        {
            "id": c.id,
            "name": c.name,
            "stage": c.current_stage.value,
            "status": c.status.value,
            "application_date": c.application_date.isoformat() if c.application_date else None,
        }
        for c in recent_candidates
    ]

    stage_rows = (
        db.query(Candidate.current_stage, func.count(Candidate.id))
        .group_by(Candidate.current_stage)
        .all()
    )
    stage_counts = {}
    for stage_val, count in stage_rows:
        key = stage_val.value if hasattr(stage_val, "value") else str(stage_val)
        stage_counts[key] = int(count or 0)

    recent_interview_rows = (
        db.query(Interview)
        .options(joinedload(Interview.candidate), joinedload(Interview.role))
        .order_by(Interview.created_date.desc())
        .limit(5)
        .all()
    )
    recent_interviews = []
    for iv in recent_interview_rows:
        cand = iv.candidate
        role = iv.role
        recent_interviews.append(
            {
                "id": iv.id,
                "candidate_id": iv.candidate_id,
                "candidate_name": cand.name if cand else "",
                "role_title": role.title if role else "",
                "interviewer_name": iv.interviewer_name,
                "overall_score": iv.overall_score,
                "communication_score": iv.communication_score,
                "knowledge_score": iv.knowledge_score,
                "confidence_score": iv.confidence_score,
                "created_date": iv.created_date.isoformat() if iv.created_date else None,
                "is_voice_interview": bool(iv.is_voice_interview),
                "feedback_present": bool(iv.feedback),
            }
        )

    return {
        "candidates": candidates_count,
        "roles": roles_count,
        "interviews": interviews_count,
        "recent_activity": recent_activity,
        "stage_counts": stage_counts,
        "recent_interviews": recent_interviews,
    }


@app.get("/api/info")
async def api_info():
    """API information and available endpoints."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "stats": {
                "dashboard": "GET /stats",
            },
            "insights": {
                "recruiter": "GET /insights",
            },
            "candidates": {
                "submit": "POST /candidates/submit",
                "get": "GET /candidates/{id}",
                "list": "GET /candidates",
                "evaluate": "POST /candidates/{id}/evaluate",
                "update_stage": "PUT /candidates/{id}/stage",
                "scores": "GET /candidates/{id}/scores",
            },
            "roles": {
                "create": "POST /roles/create",
                "get": "GET /roles/{id}",
                "list": "GET /roles",
                "shortlist": "POST /roles/{id}/shortlist",
                "candidates": "GET /roles/{id}/candidates",
                "rankings": "GET /roles/{id}/rankings",
            },
            "interviews": {
                "submit": "POST /interviews/submit",
                "get": "GET /interviews/{id}",
                "evaluation": "GET /interviews/{id}/evaluation",
                "candidate_interviews": "GET /interviews/candidate/{id}",
                "schedule": "POST /interviews/schedule",
                "generate_ranking": "POST /interviews/role/{id}/generate-ranking",
                "final_decision": "POST /interviews/role/{id}/final-decision",
            },
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
