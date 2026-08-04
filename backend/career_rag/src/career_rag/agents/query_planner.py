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

        original = "".join(question.split()).rstrip("？?。")
        rewritten = "".join(
            plan.rewritten_question.split()
        ).rstrip("？?。")

        # 模型偶尔会原样返回问题，程序侧保证展示字段确实有改写
        if plan.intent != "out_of_scope" and rewritten == original:
            hr_question = question.strip()

            for subject in ("候选人", "她", "他"):
                hr_question = hr_question.replace(subject, "你")

            plan = plan.model_copy(
                update={
                    "rewritten_question": (
                        f"请结合你的履历资料说明：{hr_question}"
                    )
                }
            )

        return plan

    except QueryPlannerError:
        raise
    except Exception as exc:
        raise QueryPlannerError(
            f"查询规划失败：{question}"
        ) from exc
