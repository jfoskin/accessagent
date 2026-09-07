import os
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama


def get_llm(model: str = "claude-sonnet-4-6", temperature: float = 0):
    """
    Function that returns different llm models 
    """

    provider = os.getenv("LLM_PROVIDER", "anthropic")
    if provider == "ollama":
        return ChatOllama(model=model, temperature=0)
    return ChatAnthropic(model=model, temperature=temperature)
