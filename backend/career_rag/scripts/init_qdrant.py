import argparse

from career_rag.config.settings import settings
from career_rag.vectorstores.qdrant_store import (
    ensure_collection,
    recreate_empty_collection,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="初始化 Qdrant 集合")
    parser.add_argument(
        "--recreate",
        action="store_true",
        help="删除并重新创建空集合",
    )
    args = parser.parse_args()

    if args.recreate:
        recreate_empty_collection()
        print(
            "Qdrant 空集合重建成功："
            f"{settings.qdrant_collection_name}，"
            f"{settings.embedding_dimension} 维"
        )
        return

    created = ensure_collection()

    if created:
        print(
            "Qdrant 集合创建成功："
            f"{settings.qdrant_collection_name}，"
            f"{settings.embedding_dimension} 维"
        )
    else:
        print(
            "Qdrant 集合已经存在且配置正确："
            f"{settings.qdrant_collection_name}，"
            f"{settings.embedding_dimension} 维"
        )


if __name__ == "__main__":
    main()