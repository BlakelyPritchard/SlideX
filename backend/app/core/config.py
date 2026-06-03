"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/slidex"
    
    # AI API Keys (use one)
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    ROO_API_KEY: str = ""  # Roo (Bob) API
    ROO_API_URL: str = "https://api.roo.ai/v1"  # Default Roo API endpoint
    WATSONX_API_KEY: str = ""  # IBM WatsonX.ai
    WATSONX_PROJECT_ID: str = ""  # IBM WatsonX project ID
    WATSONX_URL: str = "https://us-south.ml.cloud.ibm.com"  # Default WatsonX endpoint
    
    # Application
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str = "change-this-secret-key-in-production"
    
    # File Upload
    MAX_UPLOAD_SIZE: int = 50000000  # 50MB
    UPLOAD_DIR: str = "./uploads"
    SLIDES_DIR: str = "./slides"
    THUMBNAILS_DIR: str = "./thumbnails"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS string into list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Made with Bob
