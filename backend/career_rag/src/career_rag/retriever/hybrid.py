from career_rag.config.settings import settings
from career_rag.retriever.bm25 import (
    BM25RetrieverError,
    bm25_retrieve,
)
from career_rag.retriever.dense import (
    DenseRetrieverError,
    dense_retrieve,
)
from career_rag.schemas.document import (
    HybridRetrievedChunk,
    RetrievedChunk,
)


class HybridRetrieverError(RuntimeError):
    """混合检索失败。"""


# RRF 常用平滑常数，避免第一名拥有过大的权重
RRF_K = 60


def reciprocal_rank_fusion(
    dense_results: list[RetrievedChunk],
    bm25_results: list[RetrievedChunk],
    top_k: int,
) -> list[HybridRetrievedChunk]:
    """按照 Dense 和 BM25 的排名融合结果。"""

    fused: dict[str, HybridRetrievedChunk] = {}

    for rank, result in enumerate(dense_results, start=1):
        item = fused.get(result.chunk_id)

        if item is None:
            item = HybridRetrievedChunk(
                **result.model_dump(exclude={"score"}),
                score=0.0,
            )
            fused[result.chunk_id] = item

        item.dense_rank = rank
        item.score += 1 / (RRF_K + rank)

    for rank, result in enumerate(bm25_results, start=1):
        item = fused.get(result.chunk_id)

        if item is None:
            item = HybridRetrievedChunk(
                **result.model_dump(exclude={"score"}),
                score=0.0,
            )
            fused[result.chunk_id] = item

        item.bm25_rank = rank
        item.score += 1 / (RRF_K + rank)

    return sorted(
        fused.values(),
        key=lambda item: item.score,
        reverse=True,
    )[:top_k]


def hybrid_retrieve(
    question: str,
    top_k: int = settings.retrieval_top_k,
) -> list[HybridRetrievedChunk]:
    """同时执行 Dense 和 BM25，并融合两路结果。"""

    if not question.strip():
        raise HybridRetrieverError(
            "混合检索失败：问题不能为空"
        )

    if not 1 <= top_k <= 20:
        raise HybridRetrieverError(
            "混合检索失败：top_k 必须在 1 到 20 之间"
        )

    # 先多召回一些候选，再融合得到最终 Top-K
    candidate_k = min(max(top_k * 2, 10), 20)

    try:
        dense_results = dense_retrieve(
            question=question,
            top_k=candidate_k,
        )
        bm25_results = bm25_retrieve(
            question=question,
            top_k=candidate_k,
        )

        return reciprocal_rank_fusion(
            dense_results=dense_results,
            bm25_results=bm25_results,
            top_k=top_k,
        )

    except (DenseRetrieverError, BM25RetrieverError) as exc:
        raise HybridRetrieverError(
            f"混合检索失败：{exc}"
        ) from exc
    except Exception as exc:
        raise HybridRetrieverError(
            f"混合检索失败：{question}"
        ) from exc