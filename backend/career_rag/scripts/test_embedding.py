from career_rag.embeddings.openai_compatible import (
    OpenAICompatibleEmbedding,
)


def main() -> None:
    embedding = OpenAICompatibleEmbedding()

    texts = [
        "熟悉 Java、Spring Boot 和 MySQL",
        "具有 React 和 TypeScript 前端开发经验",
    ]

    vectors = embedding.embed_documents(texts)
    query_vector = embedding.embed_query("她会前端开发吗？")

    print(f"文档数量：{len(texts)}")
    print(f"文档向量数量：{len(vectors)}")
    print(f"文档向量维度：{len(vectors[0])}")
    print(f"查询向量维度：{len(query_vector)}")
    print(f"第一个向量前 5 个数字：{vectors[0][:5]}")


if __name__ == "__main__":
    main()