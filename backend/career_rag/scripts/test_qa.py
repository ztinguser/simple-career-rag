import argparse

from career_rag.services.qa_service import (
    RAGAnswerError,
    answer_question,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="测试带原文引用的履历问答"
    )
    parser.add_argument(
        "question",
        help="HR 提出的问题",
    )
    args = parser.parse_args()

    try:
        result = answer_question(args.question)
    except RAGAnswerError as exc:
        print(exc)
        raise SystemExit(1) from exc

    print("\n回答：")
    print(result.answer)

    print("\n引用原文：")

    if not result.citations:
        print("无")
        return

    for citation in result.citations:
        headings = " > ".join(citation.headings) or "无标题"
        pages = ", ".join(
            str(page) for page in citation.page_numbers
        ) or "未知"

        print("\n" + "=" * 60)
        print(f"引用编号：[{citation.citation_id}]")
        print(f"来源文件：{citation.source_name}")
        print(f"页码：{pages}")
        print(f"标题：{headings}")
        print(f"原文：\n{citation.content}")


if __name__ == "__main__":
    main()