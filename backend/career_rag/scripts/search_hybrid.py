import argparse

from career_rag.config.settings import settings
from career_rag.retriever.hybrid import (
    HybridRetrieverError,
    hybrid_retrieve,
)


def format_rank(rank: int | None) -> str:
    return str(rank) if rank is not None else "-"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="测试 Dense 和 BM25 混合检索"
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
        results = hybrid_retrieve(
            question=args.question,
            top_k=args.top_k,
        )
    except HybridRetrieverError as exc:
        print(exc)
        raise SystemExit(1) from exc

    if not results:
        print("没有检索到相关内容")
        return

    print(f"\n问题：{args.question}")
    print(f"命中数量：{len(results)}")

    for index, result in enumerate(results, start=1):
        headings = " > ".join(result.headings) or "无标题"
        pages = ", ".join(
            str(page) for page in result.page_numbers
        ) or "未知"

        print("\n" + "=" * 60)
        print(f"最终排名：{index}")
        print(f"RRF 分数：{result.score:.6f}")
        print(f"Dense 排名：{format_rank(result.dense_rank)}")
        print(f"BM25 排名：{format_rank(result.bm25_rank)}")
        print(f"来源：{result.source_name}")
        print(f"页码：{pages}")
        print(f"标题：{headings}")
        print(f"原文：\n{result.content}")


if __name__ == "__main__":
    main()