import argparse

from career_rag.agents.query_planner import (
    QueryPlannerError,
    plan_query,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="测试履历查询规划器"
    )
    parser.add_argument(
        "question",
        help="HR 提出的问题",
    )
    args = parser.parse_args()

    try:
        plan = plan_query(args.question)
    except QueryPlannerError as exc:
        print(exc)
        raise SystemExit(1) from exc

    print(plan.model_dump_json(indent=2))


if __name__ == "__main__":
    main()