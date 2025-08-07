"""Configuration management for Splunk Agentic AI."""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Splunk Configuration
    SPLUNK_HOST: str = os.getenv("SPLUNK_HOST", "localhost")
    SPLUNK_PORT: int = int(os.getenv("SPLUNK_PORT", "8089"))
    SPLUNK_USERNAME: str = os.getenv("SPLUNK_USERNAME", "admin")
    SPLUNK_PASSWORD: str = os.getenv("SPLUNK_PASSWORD", "")
    SPLUNK_TOKEN: Optional[str] = os.getenv("SPLUNK_TOKEN")
    SPLUNK_SCHEME: str = os.getenv("SPLUNK_SCHEME", "https")
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Application Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API Configuration
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Streamlit Configuration
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        required_fields = [
            "SPLUNK_HOST",
            "OPENAI_API_KEY"
        ]
        
        missing_fields = []
        for field in required_fields:
            if not getattr(cls, field):
                missing_fields.append(field)
        
        if missing_fields:
            raise ValueError(f"Missing required configuration: {', '.join(missing_fields)}")
        
        # Validate Splunk auth
        if not cls.SPLUNK_TOKEN and not (cls.SPLUNK_USERNAME and cls.SPLUNK_PASSWORD):
            raise ValueError("Either SPLUNK_TOKEN or SPLUNK_USERNAME/SPLUNK_PASSWORD must be provided")
        
        return True

# Global config instance
config = Config()
