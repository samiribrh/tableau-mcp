"""MCP tool-related models."""
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ToolDefinition(BaseModel):
    """Definition of an MCP tool."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters schema")


class ToolResult(BaseModel):
    """Result of tool execution."""
    status: str = Field(..., description="'success' or 'error'")
    action: Optional[str] = Field(None, description="Action performed")
    result: Optional[Dict[str, Any]] = Field(None, description="Result data")
    message: Optional[str] = Field(None, description="Error message if failed")
