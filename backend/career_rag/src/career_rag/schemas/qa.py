from pydantic import BaseModel, Field, field_validator


class AskQuestionRequest(BaseModel):
    """HR 的履历问题。"""

    question: str = Field(
        min_length=1,
        max_length=500,
        description="需要询问的候选人履历问题",
    )

    @field_validator("question")
    @classmethod
    def validate_question(cls, value: str) -> str:
        question = value.strip()

        if not question:
            raise ValueError("问题不能为空")

        return question


class Citation(BaseModel):
    """回答引用的一段履历原文。"""

    citation_id: int
    chunk_id: str
    source_name: str
    page_numbers: list[int]
    headings: list[str]
    content: str


class RAGAnswer(BaseModel):
    """一次履历问答的完整结果。"""

    question: str
    answer: str
    citations: list[Citation]
    # 题外问题不经过检索，因此没有改写问题
    rewritten_question: str | None = None
