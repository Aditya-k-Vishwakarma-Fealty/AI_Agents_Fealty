"""
Main FastAPI Application - HR Hiring Management System.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from contextlib import asynccontextmanager

from app.config.settings import settings
from app.db.session import init_db, close_db
from app.api import candidates, roles, interviews

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown tasks.
    """
    # Startup
    logger.info("Starting HR Hiring Management System...")
    
    # Initialize database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise
    
    # Ensure directories exist
    try:
        settings.ensure_directories()
        logger.info("Directories created/verified")
    except Exception as e:
        logger.error(f"Failed to create directories: {e}")
        raise
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown
    logger.info("Shutting down HR Hiring Management System...")
    close_db()
    logger.info("Application shutdown complete")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-Powered Agentic HR Hiring Management System",
    lifespan=lifespan
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


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


@app.get("/api/info")
async def api_info():
    """API information and available endpoints."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "endpoints": {
            "candidates": {
                "submit": "POST /candidates/submit",
                "get": "GET /candidates/{id}",
                "list": "GET /candidates",
                "evaluate": "POST /candidates/{id}/evaluate",
                "update_stage": "PUT /candidates/{id}/stage",
                "scores": "GET /candidates/{id}/scores"
            },
            "roles": {
                "create": "POST /roles/create",
                "get": "GET /roles/{id}",
                "list": "GET /roles",
                "shortlist": "POST /roles/{id}/shortlist",
                "candidates": "GET /roles/{id}/candidates",
                "rankings": "GET /roles/{id}/rankings"
            },
            "interviews": {
                "submit": "POST /interviews/submit",
                "get": "GET /interviews/{id}",
                "evaluation": "GET /interviews/{id}/evaluation",
                "candidate_interviews": "GET /interviews/candidate/{id}",
                "schedule": "POST /interviews/schedule",
                "generate_ranking": "POST /interviews/role/{id}/generate-ranking",
                "final_decision": "POST /interviews/role/{id}/final-decision"
            }
        },
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
