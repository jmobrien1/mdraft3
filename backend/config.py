from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def from_env(cls):
        # Try with VITE_ prefix first (for local dev), then without (for Render)
        return cls(
            supabase_url=os.getenv("VITE_SUPABASE_URL") or os.getenv("SUPABASE_URL"),
            supabase_key=os.getenv("VITE_SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")
        )

@lru_cache()
def get_settings():
    return Settings.from_env()
