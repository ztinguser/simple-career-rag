from urllib.parse import unquote
from uuid import UUID

from career_rag.config.settings import settings
from career_rag.embeddings.openai_compatible import (
    OpenAICompatibleEmbedding,
)
from career_rag.retriever.chunker import build_document_chunks
from career_rag.schemas.document import DocumentChunk
from career_rag.vectorstores.qdrant_store import (
    replace_document_chunks,
)


class DocumentIndexError(RuntimeError):
    """文档索引失败。"""


def index_document(document_id: str) -> list[DocumentChunk]:
    """为一个已解析文档生成 Chunk、向量并写入 Qdrant。"""

    try:
        normalized_id = UUID(document_id).hex
    except ValueError as exc:
        raise DocumentIndexError(
            "文档索引失败：document_id 格式不正确"
        ) from exc

    parsed_path = settings.parsed_dir / f"{normalized_id}.json"

    if not parsed_path.exists():
        raise DocumentIndexError(
            "文档索引失败：请先解析该文档"
        )

    matched_files = list(
        settings.upload_dir.glob(f"{normalized_id}__*")
    )

    if not matched_files:
        raise DocumentIndexError(
            "文档索引失败：没有找到原始文件"
        )

    encoded_filename = matched_files[0].name.split(
        "__",
        maxsplit=1,
    )[1]
    source_name = unquote(encoded_filename)

    try:
        chunks = build_document_chunks(
            document_id=normalized_id,
            source_name=source_name,
        )

        embedding = OpenAICompatibleEmbedding()

        # 标题已包含在 embedding_text 中，content 保持原文
        vectors = embedding.embed_documents(
            [chunk.embedding_text for chunk in chunks]
        )

        replace_document_chunks(chunks, vectors)

        return chunks

    except DocumentIndexError:
        raise
    except Exception as exc:
        raise DocumentIndexError(
            f"文档索引失败：{normalized_id}"
        ) from exc