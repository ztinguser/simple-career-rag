import argparse

from career_rag.config.settings import settings
from career_rag.retriever.bm25 import (
    BM25RetrieverError,
    bm25_retrieve,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="测试 BM25 关键词检索"
    )
    parser.add_argument(
        "question",
        help="需要检索的问题",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=settings.retrieval_top_k,
        help=f"返回结果数量，默认 {settings.retrieval_top_k}",
    )
    args = parser.parse_args()

    try:
        results = bm25_retrieve(
            question=args.question,
            top_k=args.top_k,
        )
    except BM25RetrieverError as exc:
        print(exc)
        raise SystemExit(1) from exc

    if not results:
        print("没有检索到包含相关关键词的内容")
        return

    print(f"\n问题：{args.question}")
    print(f"命中数量：{len(results)}")

    for index, result in enumerate(results, start=1):
        headings = " > ".join(result.headings) or "无标题"
        pages = ", ".join(
            str(page) for page in result.page_numbers
        ) or "未知"

        print("\n" + "=" * 60)
        print(f"排名：{index}")
        print(f"BM25 分数：{result.score:.4f}")
        print(f"来源：{result.source_name}")
        print(f"页码：{pages}")
        print(f"标题：{headings}")
        print(f"原文：\n{result.content}")


if __name__ == "__main__":
    main()