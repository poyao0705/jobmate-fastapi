from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    AUTH0_DOMAIN: str
    AUTH0_AUDIENCE: str
    
    class Config:
        env_file = ".env"

settings = Settings()