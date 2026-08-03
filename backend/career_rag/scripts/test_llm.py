from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from career_rag.llm.chat_model import (
    ChatModelConfigError,
    create_chat_model,
)


def main() -> None:
    try:
        model = create_chat_model()

        response = model.invoke(
            [
                SystemMessage(
                    content="你是一个简洁的中文助手。"
                ),
                HumanMessage(
                    content="只回复：生成模型连接成功"
                ),
            ]
        )
    except ChatModelConfigError as exc:
        print(exc)
        raise SystemExit(1) from exc
    except Exception as exc:
        print(f"生成模型调用失败：{exc}")
        raise SystemExit(1) from exc

    print(f"模型回复：{response.content}")
    print(
        "实际模型："
        f"{response.response_metadata.get('model_name', '未知')}"
    )


if __name__ == "__main__":
    main()