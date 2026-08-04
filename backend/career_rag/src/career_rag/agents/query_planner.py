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
            return result

        # 防止某些兼容服务返回普通 dict
        return QueryPlan.model_validate(result)

    except QueryPlannerError:
        raise
    except Exception as exc:
        raise QueryPlannerError(
            f"查询规划失败：{question}"
        ) from exc