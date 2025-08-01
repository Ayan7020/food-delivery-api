from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str
    RESTAURANT_SERVICE_URL: str
    AGENT_SERVICE_URL: str 
    RABBIT_MQ: str
    class Config:
        env_file = ".env"
        
settings = Settings()