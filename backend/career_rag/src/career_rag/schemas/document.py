from pydantic import BaseModel

class UploadDocumentResponse(BaseModel):
    """文件上传成功后返回给前端的数据。"""

    document_id: str
    filename: str
    size_bytes: int
    message: str

class ParseDocumentResponse(BaseModel):
    """文档解析完成后返回的数据。"""

    document_id: str
    filename: str
    page_count: int
    character_count: int
    markdown_preview: str
    message: str

class DocumentChunk(BaseModel):
    """一段可以被检索和引用的原文。"""

    # 后面直接作为 Qdrant Point ID
    chunk_id: str
    document_id: str
    source_name: str
    # 该段在原文中的页码
    page_numbers: list[int]
    # 该段所属的标题层级
    headings: list[str]
    # 原文引用
    content: str
    # 标题加原文，用于生成向量
    embedding_text: str

class RetrievedChunk(DocumentChunk):
    """从向量库检索到的文档块。"""

    # Qdrant 返回的余弦相似度分数
    score: float

class ChunkDocumentResponse(BaseModel):
    """文档分块结果。"""

    document_id: str
    filename: str
    chunk_count: int
    chunks_preview: list[DocumentChunk]
    message: str


class HybridRetrievedChunk(RetrievedChunk):
    """经过 Dense 和 BM25 融合后的检索结果。

    保留两个排名，方便观察某个 Chunk 是怎么被召回的
    """
    dense_rank: int | None = None
    bm25_rank: int | None = None
