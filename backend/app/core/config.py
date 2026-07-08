import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

# Locate the root project dir containing the .env file
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.join(ROOT_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True
    )

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True

    # Security
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 120

    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "sentinel_ai"

    # Gemini LLM Config
    GEMINI_API_KEY: str

    # Storage Paths (One folder in the main project folder)
    UPLOAD_DIR: str = "uploads"

    # CORS Allowed Hosts (Comma-separated string to prevent parsing errors)
    ALLOWED_HOSTS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    @property
    def allowed_hosts_list(self) -> List[str]:
        """Convert comma-separated hosts to a list of strings for CORSMiddleware."""
        return [i.strip() for i in self.ALLOWED_HOSTS.split(",") if i.strip()]

    @property
    def upload_path(self) -> Path:
        """Point directly to 'uploads' in the root project workspace."""
        path = ROOT_DIR / self.UPLOAD_DIR
        return path

    def create_directories(self) -> None:
        """Create a single uploads directory in the main project folder."""
        os.makedirs(self.upload_path, exist_ok=True)

settings = Settings()
# Ensure directories are created on launch
settings.create_directories()
