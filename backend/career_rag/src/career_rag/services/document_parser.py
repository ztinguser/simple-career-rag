from dataclasses import dataclass
from pathlib import Path

from docling.document_converter import DocumentConverter
from docling_core.types.doc import ImageRefMode

from career_rag.config.settings import settings


class DocumentParseError(RuntimeError):
    """文档解析失败。"""


@dataclass(slots=True)
class ParsedDocument:
    """解析后的文档信息。"""

    # 解析出的 Markdown 文本
    markdown: str
    # 文档页数
    page_count: int
    # Markdown 文件保存位置
    markdown_path: Path
    # JSON 文件保存位置
    json_path: Path


# 转换器只创建一次，避免每次请求都重复初始化
converter = DocumentConverter()


def parse_document(
    source_path: Path,
    document_id: str,
) -> ParsedDocument:
    """使用 Docling 解析一份本地文档。

    原始文件 -> Docling 解析 -> 得到统一的 Document 对象

    导出 Markdown：用于分块、检索；保存 JSON：保留页码、版面位置等引用信息
    """

    try:
        # 解析原文件
        result = converter.convert(source_path)
        document = result.document

        # traverse_pictures=True 可以包含图片 OCR 后的子文本
        markdown = document.export_to_markdown(
            traverse_pictures=True,
        )

        if not markdown.strip():
            raise DocumentParseError("文档中没有解析出可用文本")

        settings.parsed_dir.mkdir(parents=True, exist_ok=True)

        markdown_path = settings.parsed_dir / f"{document_id}.md"
        json_path = settings.parsed_dir / f"{document_id}.json"

        markdown_path.write_text(markdown, encoding="utf-8")

        # JSON 保留页码、版面坐标等引用信息，但不重复嵌入图片
        document.save_as_json(
            json_path,
            image_mode=ImageRefMode.PLACEHOLDER,
        )

        return ParsedDocument(
            markdown=markdown,
            page_count=document.num_pages(),
            markdown_path=markdown_path,
            json_path=json_path,
        )
    except DocumentParseError:
        raise
    except Exception as exc:
        raise DocumentParseError(
            f"文档解析失败：{source_path.name}"
        ) from exc