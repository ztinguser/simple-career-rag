from pydantic import BaseModel


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