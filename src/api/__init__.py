"""API layer for web interface and Ollama integration."""
from src.api.ollama_client import OllamaClient, get_ollama_client
from src.api.routes import router

__all__ = [
    "OllamaClient",
    "get_ollama_client",
    "router",
]
