"""MCP tool integration."""
from src.mcp.tools import get_tool_definitions
from src.mcp.handlers import handle_tool_call

__all__ = [
    "get_tool_definitions",
    "handle_tool_call",
]
