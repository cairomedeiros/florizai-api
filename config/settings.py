from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_PUBLISHABLE_KEY: str
    SUPABASE_SECRET_KEY: str
    DATABASE_URL: str
    GROQ_API_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()