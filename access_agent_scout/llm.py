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
        model = os.getenv("OLLAMA_MODEL")
        if not model:
            raise ValueError(
                "OLLAMA_MODEL is not set. Copy .env.example to .env and set it "
                "(e.g. OLLAMA_MODEL=qwen3:8b)."
            )
        return ChatOllama(model=model, temperature=0, base_url="http://localhost:11434", sync_client_kwargs={"timeout": 60})

    return ChatAnthropic(model="claude-sonnet-4-6", temperature=0)
