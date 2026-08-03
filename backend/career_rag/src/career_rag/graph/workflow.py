from langgraph.graph import END, START, StateGraph

from career_rag.config.settings import settings
from career_rag.graph.nodes import (
    generate_node,
    retrieve_node,
)
from career_rag.graph.state import CareerRAGState
from career_rag.schemas.qa import RAGAnswer


class CareerRAGGraphError(RuntimeError):
    """履历 RAG Graph 执行失败。"""


graph_builder = StateGraph(CareerRAGState)

graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("generate", generate_node)

graph_builder.add_edge(START, "retrieve")
graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", END)

# compile 会检查节点和边是否合法
career_rag_graph = graph_builder.compile()


def run_career_rag_graph(
    question: str,
    top_k: int = settings.retrieval_top_k,
) -> RAGAnswer:
    """执行完整的履历 RAG Graph。"""

    if not question.strip():
        raise CareerRAGGraphError(
            "执行 RAG Graph 失败：问题不能为空"
        )

    try:
        final_state = career_rag_graph.invoke(
            {
                "question": question,
                "top_k": top_k,
            }
        )

        result = final_state.get("result")

        if not isinstance(result, RAGAnswer):
            raise CareerRAGGraphError(
                "RAG Graph 没有生成有效回答"
            )

        return result

    except CareerRAGGraphError:
        raise
    except Exception as exc:
        raise CareerRAGGraphError(
            f"执行 RAG Graph 失败：{question}"
        ) from exc