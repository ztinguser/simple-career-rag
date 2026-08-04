from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from career_rag.llm.chat_model import create_chat_model
from career_rag.prompts.planner import PLANNER_PROMPT
from career_rag.schemas.query import QueryPlan


class QueryPlannerError(RuntimeError):
    """查询规划失败。"""


def plan_query(question: str) -> QueryPlan:
    """使用 LLM 生成结构化检索计划。"""

    if not question.strip():
        raise QueryPlannerError(
            "查询规划失败：问题不能为空"
        )

    try:
        model = create_chat_model()

        # DashScope 兼容接口支持 Function Calling，
        # 使用它生成符合 QueryPlan 的结构化结果
        structured_model = model.with_structured_output(
            QueryPlan,
            method="function_calling",
        )

        result = structured_model.invoke(
            [
                SystemMessage(content=PLANNER_PROMPT),
                HumanMessage(content=question),
            ]
        )

        if isinstance(result, QueryPlan):
            plan = result
        else:
            # 防止某些兼容服务返回普通 dict
            plan = QueryPlan.model_validate(result)

        # 题外问题和明确问题都不向 HR 展示改写
        if plan.intent == "out_of_scope" or not plan.rewrite_needed:
            return plan.model_copy(
                update={
                    "rewrite_needed": False,
                    "rewritten_question": None,
                }
            )

        rewritten_question = (
            plan.rewritten_question or ""
        ).strip()

        if not rewritten_question:
            raise QueryPlannerError(
                "查询规划失败：需要改写但未返回改写问题"
            )

        original = "".join(question.split()).rstrip("？?。")
        rewritten = "".join(
            rewritten_question.split()
        ).rstrip("？?。")

        # 没有产生实质改写时，不向 HR 展示重复问题
        if rewritten == original:
            return plan.model_copy(
                update={
                    "rewrite_needed": False,
                    "rewritten_question": None,
                }
            )

        return plan

    except QueryPlannerError:
        raise
    except Exception as exc:
        raise QueryPlannerError(
            f"查询规划失败：{question}"
        ) from exc
