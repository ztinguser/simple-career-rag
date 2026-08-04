import logging

from fastapi import APIRouter, HTTPException, status
from starlette.concurrency import run_in_threadpool

from career_rag.graph.workflow import (
    CareerRAGGraphError,
    run_career_rag_graph,
)
from career_rag.schemas.qa import (
    AskQuestionRequest,
    RAGAnswer,
)


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/chat",
    tags=["履历 Q&A"],
)


@router.post(
    "/ask",
    response_model=RAGAnswer,
)
async def ask_question(
    request: AskQuestionRequest,
) -> RAGAnswer:
    """回答 HR 提出的候选人履历问题。"""

    try:
        # Graph、Embedding 和 LLM 都是同步调用，
        # 放入线程池，避免阻塞 FastAPI 事件循环
        result = await run_in_threadpool(
            run_career_rag_graph,
            request.question,
        )

        return result

    except CareerRAGGraphError as exc:
        logger.exception("履历问答执行失败")

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="问答服务暂时不可用，请稍后重试",
        ) from exc