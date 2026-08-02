from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# backend/career_rag 目录
PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    """应用配置，环境变量会自动覆盖这里的默认值。"""

    app_name: str = "个人简历 RAG"
    app_description: str = "个人简历 Q&A"
    max_upload_size_mb: int = 20
    upload_dir: Path = PROJECT_ROOT / "data" / "uploads"
    parsed_dir: Path = PROJECT_ROOT / "data" / "parsed"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()