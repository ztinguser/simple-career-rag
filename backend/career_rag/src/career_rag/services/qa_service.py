import re

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from career_rag.config.settings import settings
from career_rag.llm.chat_model import create_chat_model
from career_rag.prompts.rag import (
    NO_EVIDENCE_ANSWER,
    NO_EVIDENCE_PREFIX,
    SYSTEM_PROMPT,
)
from career_rag.retriever.hybrid import hybrid_retrieve
from career_rag.schemas.document import HybridRetrievedChunk
from career_rag.schemas.qa import Citation, RAGAnswer


class RAGAnswerError(RuntimeError):
    """生成履历问答结果失败。"""


def format_context(
    chunks: list[HybridRetrievedChunk],
) -> str:
    """把检索结果整理成带编号的原文。"""

    sections: list[str] = []

    for index, chunk in enumerate(chunks, start=1):
        headings = " > ".join(chunk.headings) or "无标题"
        pages = ", ".join(
            str(page) for page in chunk.page_numbers
        ) or "未知"

        sections.append(
            "\n".join(
                [
                    f"[{index}]",
                    f"来源文件：{chunk.source_name}",
                    f"页码：{pages}",
                    f"标题：{headings}",
                    "原文：",
                    chunk.content,
                ]
            )
        )

    return "\n\n".join(sections)


def extract_citation_ids(
    answer: str,
    chunk_count: int,
) -> list[int]:
    """从答案中提取并校验 [1] 形式的引用编号。"""

    citation_ids = [
        int(value)
        for value in re.findall(r"\[(\d+)\]", answer)
    ]

    # 按首次出现顺序去重
    citation_ids = list(dict.fromkeys(citation_ids))

    invalid_ids = [
        citation_id
        for citation_id in citation_ids
        if citation_id < 1 or citation_id > chunk_count
    ]

    if invalid_ids:
        raise RAGAnswerError(
            f"生成模型返回了不存在的引用编号：{invalid_ids}"
        )

    return citation_ids


def renumber_citations(
    answer: str,
    citation_ids: list[int],
) -> tuple[str, dict[int, int]]:
    """把上下文编号转换为连续的前端展示编号。"""

    # 例如模型引用 [1]、[4]，最终展示为 [1]、[2]
    citation_mapping = {
        original_id: display_id
        for display_id, original_id in enumerate(
            citation_ids,
            start=1,
        )
    }

    def replace_citation(match: re.Match[str]) -> str:
        original_id = int(match.group(1))
        display_id = citation_mapping.get(original_id)

        if display_id is None:
            return match.group(0)

        return f"[{display_id}]"

    new_answer = re.sub(
        r"\[(\d+)\]",
        replace_citation,
        answer,
    )

    return new_answer, citation_mapping


def generate_answer(
    question: str,
    chunks: list[HybridRetrievedChunk],
) -> RAGAnswer:
    """根据已经检索到的 Chunk 生成回答。"""

    if not question.strip():
        raise RAGAnswerError("生成回答失败：问题不能为空")

    try:
        if not chunks:
            return RAGAnswer(
                question=question,
                answer=NO_EVIDENCE_ANSWER,
                citations=[],
            )

        context = format_context(chunks)
        model = create_chat_model()

        response = model.invoke(
            [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(
                    content=(
                        "以下是检索到的履历原文：\n\n"
                        f"{context}\n\n"
                        f"HR 的问题：{question}"
                    )
                ),
            ]
        )

        if not isinstance(response.content, str):
            raise RAGAnswerError(
                "生成模型没有返回有效的文本内容"
            )

        answer = response.content.strip()
        citation_ids = extract_citation_ids(
            answer=answer,
            chunk_count=len(chunks),
        )

        has_no_evidence_answer = answer.startswith(
            NO_EVIDENCE_PREFIX
        )

        # 有事实结论却没有引用时，拒绝返回不可追溯结果
        if not citation_ids and not has_no_evidence_answer:
            raise RAGAnswerError(
                "生成模型没有为回答提供原文引用"
            )

        # “未发现记录”本身没有原文证据，不应引用无关 Chunk
        if has_no_evidence_answer and citation_ids:
            raise RAGAnswerError(
                "无资料回答不应包含原文引用"
            )

        answer, citation_mapping = renumber_citations(
            answer=answer,
            citation_ids=citation_ids,
        )

        citations = [
            Citation(
                # 前端使用连续编号，查找原文仍用原始上下文编号
                citation_id=display_id,
                chunk_id=chunks[original_id - 1].chunk_id,
                source_name=chunks[original_id - 1].source_name,
                page_numbers=chunks[original_id - 1].page_numbers,
                headings=chunks[original_id - 1].headings,
                # 返回真实 Chunk 原文，不让模型自己生成引用内容
                content=chunks[original_id - 1].content,
            )
            for original_id, display_id
            in citation_mapping.items()
        ]

        return RAGAnswer(
            question=question,
            answer=answer,
            citations=citations,
        )

    except RAGAnswerError:
        raise
    except Exception as exc:
        raise RAGAnswerError(
            f"生成履历回答失败：{question}"
        ) from exc


def answer_question(
    question: str,
    top_k: int = settings.retrieval_top_k,
) -> RAGAnswer:
    """不经过 LangGraph 的线性 RAG 问答入口。"""

    try:
        chunks = hybrid_retrieve(
            question=question,
            top_k=top_k,
        )

        return generate_answer(
            question=question,
            chunks=chunks,
        )

    except RAGAnswerError:
        raise
    except Exception as exc:
        raise RAGAnswerError(
            f"生成履历回答失败：{question}"
        ) from exc
