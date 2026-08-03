from qdrant_client import QdrantClient, models

from career_rag.config.settings import settings
from career_rag.schemas.document import DocumentChunk, RetrievedChunk


class QdrantStoreError(RuntimeError):
    """Qdrant 操作失败。"""


client = QdrantClient(url=settings.qdrant_url)


def ensure_collection() -> bool:
    """确保集合存在，并检查向量维度是否正确。

    返回 True：本次创建了集合。
    返回 False：集合已经存在且配置正确。
    """

    collection_name = settings.qdrant_collection_name

    try:
        if client.collection_exists(collection_name):
            collection = client.get_collection(collection_name)
            vectors_config = collection.config.params.vectors

            if not isinstance(vectors_config, dict):
                raise QdrantStoreError(
                    "Qdrant 集合不是命名向量配置，请重新创建集合"
                )

            dense_config = vectors_config.get("dense")

            if dense_config is None:
                raise QdrantStoreError(
                    "Qdrant 集合缺少 dense 向量配置"
                )

            if dense_config.size != settings.embedding_dimension:
                raise QdrantStoreError(
                    "Qdrant 向量维度不匹配："
                    f"集合为 {dense_config.size} 维，"
                    f"当前模型为 {settings.embedding_dimension} 维。"
                    "请使用 --recreate 重建空集合"
                )

            return False

        client.create_collection(
            collection_name=collection_name,
            vectors_config={
                # 使用命名向量，为后续加入稀疏检索留出空间
                "dense": models.VectorParams(
                    size=settings.embedding_dimension,
                    distance=models.Distance.COSINE,
                )
            },
        )

        return True

    except QdrantStoreError:
        raise
    except Exception as exc:
        raise QdrantStoreError(
            "Qdrant 集合初始化失败，请检查服务是否已经启动"
        ) from exc


def recreate_empty_collection() -> None:
    """删除并重建空集合。

    为避免误删数据，如果集合中已有 Point，则拒绝执行。
    """

    collection_name = settings.qdrant_collection_name

    try:
        if client.collection_exists(collection_name):
            point_count = client.count(
                collection_name=collection_name,
                exact=True,
            ).count

            if point_count > 0:
                raise QdrantStoreError(
                    f"拒绝重建集合：当前集合中已有 {point_count} 条数据"
                )

            client.delete_collection(collection_name)

        ensure_collection()

    except QdrantStoreError:
        raise
    except Exception as exc:
        raise QdrantStoreError("重建 Qdrant 集合失败") from exc


def replace_document_chunks(
    chunks: list[DocumentChunk],
    vectors: list[list[float]],
) -> None:
    """使用新的 Chunk 和向量替换一个文档的旧索引。"""

    if not chunks:
        raise QdrantStoreError("写入 Qdrant 失败：Chunk 不能为空")

    if len(chunks) != len(vectors):
        raise QdrantStoreError(
            f"Chunk 和向量数量不一致："
            f"{len(chunks)} 个 Chunk，{len(vectors)} 个向量"
        )

    if any(
        len(vector) != settings.embedding_dimension
        for vector in vectors
    ):
        raise QdrantStoreError(
            f"写入 Qdrant 失败：向量必须是 "
            f"{settings.embedding_dimension} 维"
        )

    document_ids = {chunk.document_id for chunk in chunks}

    if len(document_ids) != 1:
        raise QdrantStoreError(
            "一次只能写入同一个文档的 Chunk"
        )

    document_id = chunks[0].document_id

    points = [
        models.PointStruct(
            id=chunk.chunk_id,
            vector={
                "dense": vector,
            },
            # 原文及其来源作为 Payload 保存
            payload=chunk.model_dump(exclude={"chunk_id"}),
        )
        for chunk, vector in zip(chunks, vectors, strict=True)
    ]

    try:
        ensure_collection()

        # 重复索引时，先删除该文档的旧 Chunk
        client.delete(
            collection_name=settings.qdrant_collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key="document_id",
                            match=models.MatchValue(
                                value=document_id,
                            ),
                        )
                    ]
                )
            ),
            wait=True,
        )

        client.upsert(
            collection_name=settings.qdrant_collection_name,
            points=points,
            wait=True,
        )

    except QdrantStoreError:
        raise
    except Exception as exc:
        raise QdrantStoreError(
            f"文档向量写入 Qdrant 失败：{document_id}"
        ) from exc


def search_chunks(
    query_vector: list[float],
    top_k: int = settings.retrieval_top_k,
) -> list[RetrievedChunk]:
    """根据查询向量搜索最相关的 Chunk。"""

    if len(query_vector) != settings.embedding_dimension:
        raise QdrantStoreError(
            f"查询向量维度错误：期望 "
            f"{settings.embedding_dimension} 维，"
            f"实际 {len(query_vector)} 维"
        )

    if not 1 <= top_k <= 20:
        raise QdrantStoreError("top_k 必须在 1 到 20 之间")

    try:
        ensure_collection()

        response = client.query_points(
            collection_name=settings.qdrant_collection_name,
            query=query_vector,
            # 指定使用名为 dense 的向量
            using="dense",
            limit=top_k,
            with_payload=True,
            with_vectors=False,
        )

        results: list[RetrievedChunk] = []

        for point in response.points:
            if point.payload is None:
                continue

            results.append(
                RetrievedChunk(
                    chunk_id=str(point.id),
                    score=point.score,
                    **point.payload,
                )
            )

        return results

    except QdrantStoreError:
        raise
    except Exception as exc:
        raise QdrantStoreError(
            "Qdrant 相似度检索失败"
        ) from exc


def list_all_chunks() -> list[DocumentChunk]:
    """读取 Qdrant 中的全部文档 Chunk，不加载向量。"""

    try:
        ensure_collection()

        chunks: list[DocumentChunk] = []
        offset = None

        while True:
            points, next_offset = client.scroll(
                collection_name=settings.qdrant_collection_name,
                # 一次取 100 个
                limit=100,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            for point in points:
                if point.payload is None:
                    continue

                chunks.append(
                    DocumentChunk(
                        chunk_id=str(point.id),
                        **point.payload,
                    )
                )

            if next_offset is None:
                break

            offset = next_offset

        return chunks

    except QdrantStoreError:
        raise
    except Exception as exc:
        raise QdrantStoreError(
            "读取 Qdrant 文档块失败"
        ) from exc