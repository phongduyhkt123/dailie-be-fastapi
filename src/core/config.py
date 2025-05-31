import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # Database settings
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "dailee"
    db_user: str = "postgres"
    db_password: str = "password"
    db_sslmode: str = "prefer"
    database_url: Optional[str] = None
    
    # API settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = True
    
    # Security settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS settings
    cors_origins: list = ["*"]  # Configure properly for production
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url_complete(self) -> str:
        """Get complete database URL"""
        if self.database_url:
            return self.database_url
        return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}?sslmode={self.db_sslmode}"


# Global settings instance
settings = Settings()
