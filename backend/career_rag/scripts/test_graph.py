import argparse

from career_rag.graph.workflow import (
    CareerRAGGraphError,
    run_career_rag_graph,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="测试 LangGraph 履历问答"
    )
    parser.add_argument(
        "question",
        help="HR 提出的问题",
    )
    args = parser.parse_args()

    try:
        result = run_career_rag_graph(args.question)
    except CareerRAGGraphError as exc:
        print(exc)
        raise SystemExit(1) from exc

    print("\n回答：")
    print(result.answer)

    print("\n引用：")

    if not result.citations:
        print("无")
        return

    for citation in result.citations:
        pages = ", ".join(
            str(page) for page in citation.page_numbers
        ) or "未知"

        print(
            f"[{citation.citation_id}] "
            f"{citation.source_name}，第 {pages} 页"
        )
        print(citation.content)


if __name__ == "__main__":
    main()
