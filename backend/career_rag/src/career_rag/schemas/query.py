from typing import Literal

from pydantic import BaseModel, Field


class QueryPlan(BaseModel):
    """LLM 为检索生成的结构化计划。

    fact：具体事实，例如技术、证书、公司、时间。
    summary：需要汇总多段经历，例如“做过哪些项目”。
    out_of_scope：与候选人履历无关。
    """

    intent: Literal[
        "fact",
        "summary",
        "out_of_scope",
    ] = Field(description="问题类型")

    rewritten_question: str = Field(
        description="面向 HR 展示的自然语言改写问题"
    )

    search_query: str = Field(
        description="用于检索履历的关键词或改写查询"
    )

    top_k: int = Field(
        description="需要召回的候选 Chunk 数量",
        ge=1,
        le=20,
    )
