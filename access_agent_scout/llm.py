"""This is to get the llm """
import os
from langchain_anthropic import ChatAnthropic
from langchain_ollama import ChatOllama


def get_llm():
    """
    Function that returns different llm models 
    """

    provider = os.getenv("LLM_PROVIDER", "anthropic")
    if provider == "ollama":
        return ChatOllama(
            model="qwen3:8b",
            temperature=0,
            base_url="http://localhost:11434",
            timeout=60
        )
    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
