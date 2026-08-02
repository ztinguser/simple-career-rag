import logging
from urllib.parse import quote, unquote
from pathlib import Path
from uuid import uuid4, UUID

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from career_rag.config.settings import settings
from career_rag.schemas.document import (
    ChunkDocumentResponse,
    ParseDocumentResponse,
    UploadDocumentResponse)
from starlette.concurrency import run_in_threadpool
from career_rag.services.document_parser import DocumentParseError,parse_document
from career_rag.retriever.chunker import DocumentChunkError, build_document_chunks

logger = logging.getLogger(__name__)
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
    # Docling 在 Windows 下可能无法读取中文路径，因此磁盘文件名使用 URL 编码
    encoded_filename = quote(filename, safe=".")
    stored_filename = f"{document_id}__{encoded_filename}"
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


@router.post(
    "/parse/{document_id}",
    response_model=ParseDocumentResponse,
)
async def parse_uploaded_document(
    document_id: str,
) -> ParseDocumentResponse:
    """解析已经上传的个人资料。"""

    try:
        # 校验并统一 UUID 格式，避免把非法字符传给文件搜索
        normalized_id = UUID(document_id).hex
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_id 格式不正确",
        ) from exc

    matched_files = list(
        settings.upload_dir.glob(f"{normalized_id}__*")
    )

    if not matched_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到对应的上传文件",
        )

    source_path = matched_files[0]
    encoded_filename = source_path.name.split("__", maxsplit=1)[1]
    # 解析时恢复原文件名
    original_filename = unquote(encoded_filename)

    try:
        # Docling 是耗时的同步任务，放入线程池，避免阻塞 FastAPI
        parsed = await run_in_threadpool(
            parse_document,
            source_path,
            normalized_id,
        )
    except DocumentParseError as exc:
        logger.exception(
            "文档解析失败，document_id=%s",
            normalized_id,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="文档解析失败，请确认文件未损坏且内容可以读取",
        ) from exc

    return ParseDocumentResponse(
        document_id=normalized_id,
        filename=original_filename,
        page_count=parsed.page_count,
        character_count=len(parsed.markdown),
        markdown_preview=parsed.markdown[:500],
        message="文档解析成功",
    )


@router.post(
    "/chunk/{document_id}",
    response_model=ChunkDocumentResponse,
)
async def chunk_parsed_document(
    document_id: str,
) -> ChunkDocumentResponse:
    """生成文档 Chunk，并返回少量预览。"""

    try:
        normalized_id = UUID(document_id).hex
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_id 格式不正确",
        ) from exc

    parsed_path = settings.parsed_dir / f"{normalized_id}.json"

    if not parsed_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="请先解析该文档",
        )

    matched_files = list(
        settings.upload_dir.glob(f"{normalized_id}__*")
    )

    if not matched_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="没有找到对应的原始文件",
        )

    encoded_filename = matched_files[0].name.split(
        "__",
        maxsplit=1,
    )[1]
    original_filename = unquote(encoded_filename)

    try:
        chunks = await run_in_threadpool(
            build_document_chunks,
            normalized_id,
            original_filename,
        )
    except DocumentChunkError as exc:
        logger.exception(
            "文档分块失败，document_id=%s",
            normalized_id,
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="文档分块失败，请检查解析结果",
        ) from exc

    return ChunkDocumentResponse(
        document_id=normalized_id,
        filename=original_filename,
        chunk_count=len(chunks),
        chunks_preview=chunks,
        message="文档分块成功",
    )