from pathlib import Path

from pydantic import Field
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

    qdrant_url: str = "http://localhost:6333"
    qdrant_collection_name: str = "career_chunks"

    # Embedding 使用 OpenAI 兼容接口，方便以后更换服务商
    embedding_api_key: str | None = None
    embedding_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    embedding_model: str = "text-embedding-v4"
    embedding_dimension: int = 1024

    # 默认召回 5 条，可通过 .env 的 RETRIEVAL_TOP_K 调整
    retrieval_top_k: int = Field(default=5, ge=1, le=20)

    # 生成模型同样使用 OpenAI 兼容接口
    llm_api_key: str | None = None
    llm_base_url: str = (
        "https://dashscope.aliyuncs.com/compatible-mode/v1"
    )
    llm_model: str = "qwen-plus"
    llm_temperature: float = Field(
        default=0.1,
        ge=0,
        le=2,
    )

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
