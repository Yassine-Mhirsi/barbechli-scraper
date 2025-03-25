import os
import sys
from typing import Any, Dict, List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, PostgresDsn, validator

# Add the parent directory to sys.path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
sys.path.append(parent_dir)

# Import the database URI from the main config
from dotenv import load_dotenv
load_dotenv()

try:
    NEON_URI = os.getenv("NEON_URI")
except ImportError:
    NEON_URI = os.getenv("NEON_URI")

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Barbechli API"
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database configuration
    SQLALCHEMY_DATABASE_URI: PostgresDsn = NEON_URI
    
    # API behavior settings
    DEFAULT_PAGE_SIZE: int = 50
    MAX_PAGE_SIZE: int = 500
    
    # Security settings (can be expanded later if needed)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev_secret_key")
    
    class Config:
        case_sensitive = True


settings = Settings() 