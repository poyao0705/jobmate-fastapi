from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AUTH0_DOMAIN: Optional[str] = None
    AUTH0_AUDIENCE: Optional[str] = None
    DATABASE_URL: str
    
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()