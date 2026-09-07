from langchain_anthropic import ChatAnthropic


def get_llm(model: str = "claude-sonnet-4-6", temperature: float = 0):
    return ChatAnthropic(model=model, temperature=temperature)
