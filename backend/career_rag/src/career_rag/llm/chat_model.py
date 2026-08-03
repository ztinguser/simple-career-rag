from langchain_openai import ChatOpenAI

from career_rag.config.settings import settings

class ChatModelConfigError(RuntimeError):
    """生成模型配置错误。"""

def create_chat_model() -> ChatOpenAI:
    """根据环境变量创建 LangChain ChatModel。"""

    return ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        max_retries=2,
        timeout=60,
    )