from career_rag.config.settings import settings
from career_rag.embeddings.openai_compatible import (
    OpenAICompatibleEmbedding,
)
from career_rag.schemas.document import RetrievedChunk
from career_rag.vectorstores.qdrant_store import search_chunks


class DenseRetrieverError(RuntimeError):
    """稠密向量检索失败。"""


def dense_retrieve(
    question: str,
    top_k: int = settings.retrieval_top_k,
) -> list[RetrievedChunk]:
    """使用 Embedding 和 Qdrant 检索相关原文。"""

    if not question.strip():
        raise DenseRetrieverError("检索失败：问题不能为空")

    try:
        embedding = OpenAICompatibleEmbedding()

        # 查询和文档必须使用相同的 Embedding 模型
        query_vector = embedding.embed_query(question)

        return search_chunks(
            query_vector=query_vector,
            top_k=top_k,
        )

    except DenseRetrieverError:
        raise
    except Exception as exc:
        raise DenseRetrieverError(
            f"稠密向量检索失败：{question}"
        ) from exc
