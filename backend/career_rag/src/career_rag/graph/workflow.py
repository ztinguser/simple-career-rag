from langgraph.graph import END, START, StateGraph

from career_rag.graph.nodes import (
    generate_node,
    plan_node,
    reject_node,
    retrieve_node,
    route_after_plan,
)
from career_rag.graph.state import CareerRAGState
from career_rag.schemas.qa import RAGAnswer


class CareerRAGGraphError(RuntimeError):
    """履历 RAG Graph 执行失败。"""


graph_builder = StateGraph(CareerRAGState)

graph_builder.add_node("plan", plan_node)
graph_builder.add_node("retrieve", retrieve_node)
graph_builder.add_node("generate", generate_node)
graph_builder.add_node("reject", reject_node)

graph_builder.add_edge(START, "plan")

graph_builder.add_conditional_edges(
    "plan",
    route_after_plan,
    {
        "retrieve": "retrieve",
        "reject": "reject",
    },
)

graph_builder.add_edge("retrieve", "generate")
graph_builder.add_edge("generate", END)
graph_builder.add_edge("reject", END)

career_rag_graph = graph_builder.compile()


def run_career_rag_graph(
    question: str,
) -> RAGAnswer:
    """执行带查询规划的履历 RAG Graph。"""

    if not question.strip():
        raise CareerRAGGraphError(
            "执行 RAG Graph 失败：问题不能为空"
        )

    try:
        final_state = career_rag_graph.invoke(
            {
                "question": question,
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