from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from career_rag.config.settings import settings
from career_rag.schemas.document import UploadDocumentResponse


router = APIRouter(prefix="/api/documents", tags=["个人资料"])

# 当前项目允许上传的个人资料格式
ALLOWED_SUFFIXES = {
    ".pdf",
    ".md",
    ".jpg",
    ".jpeg",
    ".png",
    ".docx",
}


@router.post(
    "/upload",
    response_model=UploadDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
) -> UploadDocumentResponse:
    """接收并保存一份个人资料文件。"""

    # Path.name 可以去掉用户传入的目录，防止覆盖其他位置的文件
    filename = Path(file.filename or "").name
    suffix = Path(filename).suffix.lower()

    if not filename or suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不支持该文件格式，请上传 PDF、Markdown、图片或 Word 文件",
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="上传的文件不能为空",
        )

    max_size_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"文件不能超过 {settings.max_upload_size_mb} MB",
        )

    document_id = uuid4().hex

    # UUID 防止同名文件互相覆盖，同时保留原始文件名便于追溯
    stored_filename = f"{document_id}__{filename}"
    target_path = settings.upload_dir / stored_filename

    try:
        settings.upload_dir.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(content)
    except OSError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="文件保存失败，请稍后重试",
        ) from exc
    finally:
        await file.close()

    return UploadDocumentResponse(
        document_id=document_id,
        filename=filename,
        size_bytes=len(content),
        message="文件上传成功",
    )