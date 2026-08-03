from qdrant_client import QdrantClient, models

from career_rag.config.settings import settings


class QdrantStoreError(RuntimeError):
    """Qdrant 操作失败。"""


client = QdrantClient(
    url=settings.qdrant_url,
)


def ensure_collection() -> bool:
    """确保履历向量集合存在。

    返回 True 表示本次创建了集合；
    返回 False 表示集合原本已经存在。
    """

    collection_name = settings.qdrant_collection_name

    try:
        if client.collection_exists(collection_name):
            return False

        client.create_collection(
            collection_name=collection_name,
            # 使用命名向量，为后续加入 BM25 稀疏向量留出空间
            vectors_config={
                "dense": models.VectorParams(
                    size=settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                )
            },
        )

        return True
    except Exception as exc:
        raise QdrantStoreError(
            "Qdrant 集合初始化失败，请检查服务是否已经启动"
        ) from exc