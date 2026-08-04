from typing import Literal

from career_rag.agents.query_planner import plan_query
from career_rag.graph.state import CareerRAGState
from career_rag.prompts.rag import OUT_OF_SCOPE_ANSWER
from career_rag.retriever.hybrid import hybrid_retrieve
from career_rag.schemas.qa import RAGAnswer
from career_rag.services.qa_service import generate_answer


def plan_node(
    state: CareerRAGState,
) -> dict:
    """分析问题并生成检索计划。"""

    plan = plan_query(state["question"])

    return {
        "plan": plan,
    }


def route_after_plan(
    state: CareerRAGState,
) -> Literal["retrieve", "reject"]:
    """根据问题类型选择下一节点。"""

    plan = state.get("plan")

    if plan is None:
        raise RuntimeError("条件路由失败：缺少查询计划")

    if plan.intent == "out_of_scope":
        return "reject"

    return "retrieve"


def retrieve_node(
    state: CareerRAGState,
) -> dict:
    """按照查询计划执行混合检索。"""

    plan = state.get("plan")

    if plan is None:
        raise RuntimeError("检索失败：缺少查询计划")

    chunks = hybrid_retrieve(
        # 检索使用规划器改写后的问题
        question=plan.search_query,
        top_k=plan.top_k,
    )

    return {
        "chunks": chunks,
    }


def generate_node(
    state: CareerRAGState,
) -> dict:
    """使用原始问题和检索结果生成回答。"""

    plan = state.get("plan")

    if plan is None:
        raise RuntimeError("生成回答失败：缺少查询计划")

    result = generate_answer(
        # 回答时必须使用 HR 的原始问题
        question=state["question"],
        chunks=state.get("chunks", []),
    )

    # 面向 HR 展示自然语言改写，不暴露检索关键词
    result = result.model_copy(
        update={
            "rewritten_question": (
                plan.rewritten_question
                if plan.rewrite_needed
                else None
            ),
        }
    )

    return {
        "result": result,
    }


def reject_node(
    state: CareerRAGState,
) -> dict:
    """拒绝回答与个人履历无关的问题。"""

    return {
        "result": RAGAnswer(
            question=state["question"],
            answer=OUT_OF_SCOPE_ANSWER,
            citations=[],
        )
    }
