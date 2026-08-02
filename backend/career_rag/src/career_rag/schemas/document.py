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