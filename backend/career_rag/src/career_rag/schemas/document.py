from pydantic import BaseModel

class UploadDocumentResponse(BaseModel):
    """文件上传成功后返回给前端的数据。"""

    document_id: str
    filename: str
    size_bytes: int
    message: str