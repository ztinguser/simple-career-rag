from typing import TypedDict

from career_rag.schemas.document import HybridRetrievedChunk
from career_rag.schemas.qa import RAGAnswer


class CareerRAGState(TypedDict, total=False):
    """LangGraph 节点之间共享的状态。"""

    question: str
    top_k: int
    chunks: list[HybridRetrievedChunk]
    result: RAGAnswer