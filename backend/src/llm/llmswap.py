import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


def getLLM(provider: Optional[str] = None, model_name: Optional[str] = None, temperature: float = 0):
    provider = (provider or os.getenv("LLM_PROVIDER", "gemini")).lower()
    model_name = model_name or os.getenv("MODEL_NAME")
    """
    the getLLM function will be used to add swapping of model functionality 
    this will simply be if you want to swap models, so that way, we can utilize 
    the frontend explicitly using different models. 
    """
    # if the provider is gemini 
    if provider == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        if not model_name:
            model_name = "gemini-3.0-flash"
        return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)

    if provider == "ollama":
        from langchain_ollama import ChatOllama
        if not model_name:
            model_name = "llama3.1"
        return ChatOllama(model=model_name, temperature=temperature)

    raise ValueError(f"Unknown provider: {provider}")
