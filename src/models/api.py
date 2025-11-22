"""API request/response models."""
from typing import List

from pydantic import BaseModel, Field


class Message(BaseModel):
    """A single message in a conversation."""
    role: str = Field(..., description="Role: 'user', 'assistant', or 'system'")
    content: str = Field(..., description="Message content")
    
    class Config:
        json_schema_extra = {
            "example": {
                "role": "user",
                "content": "Upload sales.xlsx to Tableau"
            }
        }


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    messages: List[Message] = Field(..., description="Conversation history")
    model: str = Field(default="llama3.1:8b", description="AI model to use")
    
    class Config:
        json_schema_extra = {
            "example": {
                "messages": [
                    {"role": "user", "content": "Check if revenue dataset exists"}
                ],
                "model": "llama3.1:8b"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="AI assistant's response")
    role: str = Field(default="assistant", description="Response role")
    iterations: int = Field(default=0, description="Number of tool calls made")
