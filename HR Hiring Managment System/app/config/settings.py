"""
Application settings and configuration management.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database Configuration
    database_url: str | None = Field(default=None, alias="DATABASE_URL")
    database_host: str | None = Field(default="localhost", alias="DATABASE_HOST")
    database_port: int | str = Field(default=3306, alias="DATABASE_PORT")
    database_user: str | None = Field(default="root", alias="DATABASE_USER")
    database_password: str | None = Field(default="", alias="DATABASE_PASSWORD")
    database_name: str | None = Field(default="hr_hiring_db", alias="DATABASE_NAME")
    
    # OpenAI API
    openai_api_key: str = Field(..., alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", alias="OPENAI_MODEL")
    
    # Gmail API Configuration
    gmail_credentials_file: str = Field(default="./credentials.json", alias="GMAIL_CREDENTIALS_FILE")
    gmail_token_file: str = Field(default="./token.json", alias="GMAIL_TOKEN_FILE")
    sender_email: str = Field(default="example@gmail.com", alias="SENDER_EMAIL")
    
    # ChromaDB Configuration
    chroma_persist_directory: str = Field(
        default="./data/chroma",
        alias="CHROMA_PERSIST_DIRECTORY"
    )
    chroma_collection_resumes: str = Field(
        default="resumes",
        alias="CHROMA_COLLECTION_RESUMES"
    )
    chroma_collection_roles: str = Field(
        default="roles",
        alias="CHROMA_COLLECTION_ROLES"
    )
    
    # File Storage
    resume_upload_dir: str = Field(
        default="./data/resumes",
        alias="RESUME_UPLOAD_DIR"
    )
    max_resume_size_mb: int = Field(default=5, alias="MAX_RESUME_SIZE_MB")
    allowed_resume_extensions: str = Field(
        default="pdf,docx",
        alias="ALLOWED_RESUME_EXTENSIONS"
    )
    
    # Scoring Configuration
    resume_score_weight: float = Field(default=0.6, alias="RESUME_SCORE_WEIGHT")
    interview_score_weight: float = Field(default=0.4, alias="INTERVIEW_SCORE_WEIGHT")
    shortlist_threshold: int = Field(default=70, alias="SHORTLIST_THRESHOLD")
    min_match_percentage: int = Field(default=60, alias="MIN_MATCH_PERCENTAGE")
    
    # Application Settings
    app_name: str = Field(default="HR Hiring Management System", alias="APP_NAME")
    app_version: str = Field(default="1.0.0", alias="APP_VERSION")
    debug: bool = Field(default=False, alias="DEBUG")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    
    # Email Templates
    email_shortlist_subject: str = Field(
        default="Congratulations! You've been shortlisted",
        alias="EMAIL_SHORTLIST_SUBJECT"
    )
    email_rejection_subject: str = Field(
        default="Thank you for your application",
        alias="EMAIL_REJECTION_SUBJECT"
    )
    email_interview_subject: str = Field(
        default="Interview Invitation",
        alias="EMAIL_INTERVIEW_SUBJECT"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        populate_by_name = True
        extra = "ignore"

    def model_post_init(self, __context):
        import urllib.parse
        if not self.database_url:
            if self.database_host and self.database_user and self.database_name:
                # Construct URL
                encoded_password = urllib.parse.quote_plus(self.database_password) if self.database_password else ""
                encoded_user = urllib.parse.quote_plus(self.database_user) if self.database_user else ""
                
                password_part = f":{encoded_password}" if encoded_password else ""
                self.database_url = f"mysql+pymysql://{encoded_user}{password_part}@{self.database_host}:{self.database_port}/{self.database_name}"
            else:
                 # Provide a default valid URL or fail, but better to fail at runtime if needed
                 # Default to sqlite for testing if no DB config
                pass
        
    @property
    def allowed_extensions_list(self) -> List[str]:
        """Get list of allowed file extensions."""
        return [ext.strip() for ext in self.allowed_resume_extensions.split(",")]
    
    @property
    def max_resume_size_bytes(self) -> int:
        """Get max resume size in bytes."""
        return self.max_resume_size_mb * 1024 * 1024
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.resume_upload_dir, exist_ok=True)
        os.makedirs(self.chroma_persist_directory, exist_ok=True)


# Global settings instance
settings = Settings()
