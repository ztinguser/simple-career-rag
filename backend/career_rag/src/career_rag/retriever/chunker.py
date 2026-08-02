import re
from uuid import NAMESPACE_URL, uuid5

from docling.chunking import HierarchicalChunker
from docling_core.types.doc import DocItemLabel, DoclingDocument, SectionHeaderItem
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from career_rag.config.settings import settings
from career_rag.schemas.document import DocumentChunk


class DocumentChunkError(RuntimeError):
    """文档分块失败。"""


# 第一阶段：Docling 按标题、列表、表格等文档结构切分
docling_chunker = HierarchicalChunker()

# 第二阶段：LangChain 控制最终块的长度
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=100,
    length_function=len,
    separators=[
        "\n\n",
        "\n",
        "。",
        "！",
        "？",
        "；",
        "，",
        " ",
        "",
    ],
)


def repair_heading_levels(document: DoclingDocument) -> None:
    """根据版面字号修复 Docling 识别错误的标题层级。"""

    headers = [
        item
        for item, _ in document.iterate_items()
        if item.label == DocItemLabel.SECTION_HEADER and item.prov
    ]

    if not headers:
        return

    def heading_height(item: SectionHeaderItem) -> float:
        provenance = item.prov[0]
        return provenance.bbox.t - provenance.bbox.b

    main_heading_height = max(heading_height(item) for item in headers)
    entity_heading_active = False

    for item in headers:
        is_main_heading = heading_height(item) >= main_heading_height * 0.9
        is_entity_heading = item.text.lstrip().startswith(("·", "•"))

        if is_main_heading:
            item.level = 1
            entity_heading_active = False
        elif is_entity_heading:
            # 公司等实体标题作为二级标题
            item.level = 2
            entity_heading_active = True
        else:
            # 公司下的“职责、主要技术”等继续保留公司上下文
            item.level = 3 if entity_heading_active else 2


def build_document_chunks(
    document_id: str,
    source_name: str,
) -> list[DocumentChunk]:
    """从 Docling JSON 生成最终的 RAG 文本块。"""

    json_path = settings.parsed_dir / f"{document_id}.json"

    try:
        document = DoclingDocument.load_from_json(json_path)
        repair_heading_levels(document)
        parent_documents: list[Document] = []

        for chunk in docling_chunker.chunk(dl_doc=document):
            content = chunk.text.strip()

            if not content:
                continue

            headings = chunk.meta.headings or []

            # 收集当前块涉及的所有页码
            page_numbers = sorted({
                provenance.page_no
                for item in chunk.meta.doc_items
                for provenance in item.prov
            })

            metadata = {
                "document_id": document_id,
                "source_name": source_name,
                "page_numbers": page_numbers,
                "headings": headings,
            }

            # Docling 可能把同一区域中的字段名和值识别成多个相邻元素。
            # 标题和页码相同时，先合并成一个完整的语义块。
            if (
                parent_documents
                and parent_documents[-1].metadata["headings"] == headings
                and parent_documents[-1].metadata["page_numbers"] == page_numbers
            ):
                previous = parent_documents[-1]
                previous.page_content = f"{previous.page_content} {content}"
            else:
                # LangChain Document 会在二次切分时保留 metadata
                parent_documents.append(
                    Document(
                        page_content=content,
                        metadata=metadata,
                    )
                )

        # 规范 PDF 解析产生的中文冒号空格，不修改实际文字内容
        for parent in parent_documents:
            parent.page_content = re.sub(
                r"[ \t]*：[ \t]*",
                "：",
                parent.page_content,
            )

        if not parent_documents:
            raise DocumentChunkError("文档没有生成有效文本块")

        # 对过长的结构块进行二次切分
        child_documents = text_splitter.split_documents(
            parent_documents
        )

        chunks: list[DocumentChunk] = []

        for index, child in enumerate(child_documents):
            headings = child.metadata["headings"]
            heading_text = "\n".join(headings)

            # 标题用于增强语义检索，但不混入引用原文
            embedding_text = "\n".join(
                part
                for part in [heading_text, child.page_content]
                if part
            )

            # Qdrant Point ID 只能使用整数或合法 UUID
            chunk_id = str(
                uuid5(
                    NAMESPACE_URL,
                    f"{document_id}:{index}",
                )
            )

            chunks.append(
                DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    source_name=source_name,
                    page_numbers=child.metadata["page_numbers"],
                    headings=headings,
                    content=child.page_content,
                    embedding_text=embedding_text,
                )
            )

        return chunks
    except DocumentChunkError:
        raise
    except Exception as exc:
        raise DocumentChunkError(
            f"文档分块失败：{document_id}"
        ) from exc
