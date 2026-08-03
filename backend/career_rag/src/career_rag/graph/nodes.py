from career_rag.config.settings import settings
from career_rag.graph.state import CareerRAGState
from career_rag.retriever.hybrid import hybrid_retrieve
from career_rag.services.qa_service import generate_answer


def retrieve_node(
    state: CareerRAGState,
) -> dict:
    """执行 Dense + BM25 混合检索。"""

    question = state["question"]
    top_k = state.get(
        "top_k",
        settings.retrieval_top_k,
    )

    chunks = hybrid_retrieve(
        question=question,
        top_k=top_k,
    )

    # 节点只返回自己新增或修改的状态
    return {
        "chunks": chunks,
    }


def generate_node(
    state: CareerRAGState,
) -> dict:
    """根据检索结果生成带引用回答。"""

    result = generate_answer(
        question=state["question"],
        chunks=state.get("chunks", []),
    )

    return {
        "result": result,
    }