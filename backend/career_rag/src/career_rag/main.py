from fastapi import FastAPI

from career_rag.api.chat import router as chat_router
from career_rag.api.documents import router as documents_router
from career_rag.config.settings import settings

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version="0.1.0",
)

# 将文件接口加入 FastAPI 应用
app.include_router(documents_router)
app.include_router(chat_router)

@app.get("/api/health", tags=["Career Rag"])
async def health_check() -> dict[str, str]:
    """检查后端服务是否正常运行。"""
    return {
        "status": "ok",
        "message": "个人履历 RAG 服务运行正常",
    }