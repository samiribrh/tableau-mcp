"""FastAPI routes for the Tableau AI Assistant."""
from typing import List

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from src.config import get_logger
from src.models import ChatRequest, ChatResponse
from src.mcp import get_tool_definitions
from src.api.ollama_client import get_ollama_client

logger = get_logger(__name__)

# Create router
router = APIRouter()


@router.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Handle chat requests with AI tool calling.
    
    The AI can call Tableau tools to:
    - Upload datasets
    - Check if datasets exist
    - List datasets
    - Convert files to Hyper format
    
    Args:
        request: Chat request with message history
        
    Returns:
        AI response after potentially calling tools
    """
    try:
        logger.info(f"Received chat request with {len(request.messages)} messages")
        
        # Convert Pydantic models to dicts
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        # Get Ollama client
        client = get_ollama_client(model=request.model)
        
        # Process chat with tool calling
        result = client.chat(messages)
        
        # Return response
        return ChatResponse(
            message=result["message"],
            role="assistant",
            iterations=result["iterations"]
        )
        
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {str(e)}"
        )


@router.get("/api/tools")
async def list_tools() -> JSONResponse:
    """
    List all available Tableau tools.
    
    Returns tool definitions with their parameters.
    Useful for debugging and understanding what the AI can do.
    """
    try:
        tools = get_tool_definitions()
        
        return JSONResponse(content={
            "tools": [
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
                for tool in tools
            ]
        })
        
    except Exception as e:
        logger.error(f"List tools error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list tools: {str(e)}"
        )


@router.get("/api/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    
    Verifies:
    - FastAPI server is running
    - Ollama is accessible
    - Available models
    """
    try:
        client = get_ollama_client()
        health_status = client.check_health()
        
        return JSONResponse(content=health_status)
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )
