import argparse

from career_rag.services.indexing_service import (
    DocumentIndexError,
    index_document,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="将一个已解析文档写入 Qdrant"
    )
    parser.add_argument(
        "document_id",
        help="需要索引的文档 ID",
    )
    args = parser.parse_args()

    try:
        chunks = index_document(args.document_id)
    except DocumentIndexError as exc:
        print(exc)
        raise SystemExit(1) from exc

    print("文档索引成功")
    print(f"document_id：{args.document_id}")
    print(f"Chunk 数量：{len(chunks)}")
    print(f"来源文件：{chunks[0].source_name}")


if __name__ == "__main__":
    main()