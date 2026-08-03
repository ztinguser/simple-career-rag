import logging
import re

import jieba
from rank_bm25 import BM25Okapi

from career_rag.config.settings import settings
from career_rag.schemas.document import RetrievedChunk
from career_rag.vectorstores.qdrant_store import list_all_chunks


class BM25RetrieverError(RuntimeError):
    """BM25 关键词检索失败。"""


# 不显示 jieba 初始化词典时的大量日志
jieba.setLogLevel(logging.WARNING)

# 至少包含中文、字母或数字，过滤空格和纯标点
VALID_TOKEN_PATTERN = re.compile(r"[\w\u4e00-\u9fff]")


def tokenize(text: str) -> list[str]:
    """对中英文混合文本进行简单分词。"""

    return [
        token.lower()
        for token in jieba.lcut(text)
        if VALID_TOKEN_PATTERN.search(token)
    ]


def bm25_retrieve(
    question: str,
    top_k: int = settings.retrieval_top_k,
) -> list[RetrievedChunk]:
    """使用 BM25 检索包含相关关键词的原文。"""

    if not question.strip():
        raise BM25RetrieverError("BM25 检索失败：问题不能为空")

    if not 1 <= top_k <= 20:
        raise BM25RetrieverError(
            "BM25 检索失败：top_k 必须在 1 到 20 之间"
        )

    try:
        chunks = list_all_chunks()

        if not chunks:
            return []

        # embedding_text 已经包含标题和原文
        tokenized_corpus = [
            tokenize(chunk.embedding_text)
            for chunk in chunks
        ]

        bm25 = BM25Okapi(tokenized_corpus)
        query_tokens = tokenize(question)
        scores = bm25.get_scores(query_tokens)

        ranked_indices = sorted(
            range(len(chunks)),
            key=lambda index: scores[index],
            reverse=True,
        )

        results: list[RetrievedChunk] = []

        for index in ranked_indices:
            score = float(scores[index])

            # 没有任何关键词命中时，不返回无关 Chunk
            if score <= 0:
                continue

            results.append(
                RetrievedChunk(
                    **chunks[index].model_dump(),
                    score=score,
                )
            )

            if len(results) >= top_k:
                break

        return results

    except BM25RetrieverError:
        raise
    except Exception as exc:
        raise BM25RetrieverError(
            f"BM25 检索失败：{question}"
        ) from exc