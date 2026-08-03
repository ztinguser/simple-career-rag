from openai import OpenAI, OpenAIError

from career_rag.config.settings import settings


class OpenAICompatibleEmbedding:
    """通过 OpenAI 兼容接口调用文本 Embedding 模型。"""

    # text-embedding-v4 每次最多输入 10 条文本
    batch_size = 10

    def __init__(self) -> None:
        if not settings.embedding_api_key:
            raise ValueError("初始化 Embedding 失败：请配置 EMBEDDING_API_KEY")

        self.client = OpenAI(
            api_key=settings.embedding_api_key,
            base_url=settings.embedding_base_url,
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """生成多段文档文本的向量。"""

        if not texts:
            return []

        if any(not text.strip() for text in texts):
            raise ValueError("生成文档向量失败：文本不能为空")

        vectors: list[list[float]] = []

        # 分批调用，避免超过模型单次请求上限
        for start in range(0, len(texts), self.batch_size):
            batch = texts[start : start + self.batch_size]
            vectors.extend(self._embed_batch(batch))

        return vectors

    def embed_query(self, query: str) -> list[float]:
        """生成用户问题的查询向量。"""

        if not query.strip():
            raise ValueError("生成查询向量失败：问题不能为空")

        return self.embed_documents([query])[0]

    def _embed_batch(self, texts: list[str]) -> list[list[float]]:
        try:
            response = self.client.embeddings.create(
                model=settings.embedding_model,
                input=texts,
                dimensions=settings.embedding_dimension,
                encoding_format="float",
            )
        except OpenAIError as exc:
            raise RuntimeError(f"Embedding 模型调用失败：{exc}") from exc

        # 根据 index 排序，确保向量顺序与输入文本一致
        items = sorted(response.data, key=lambda item: item.index)
        vectors = [item.embedding for item in items]

        if len(vectors) != len(texts):
            raise RuntimeError(
                f"Embedding 数量不一致：输入 {len(texts)} 条，"
                f"返回 {len(vectors)} 条"
            )

        if any(
            len(vector) != settings.embedding_dimension
            for vector in vectors
        ):
            raise RuntimeError(
                f"Embedding 向量维度错误，"
                f"期望 {settings.embedding_dimension} 维"
            )

        return vectors