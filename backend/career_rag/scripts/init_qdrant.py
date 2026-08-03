from career_rag.config.settings import settings
from career_rag.vectorstores.qdrant_store import (
    ensure_collection,
)


def main() -> None:
    created = ensure_collection()

    if created:
        print(
            "Qdrant 集合创建成功："
            f"{settings.qdrant_collection_name}"
        )
    else:
        print(
            "Qdrant 集合已经存在："
            f"{settings.qdrant_collection_name}"
        )


if __name__ == "__main__":
    main()