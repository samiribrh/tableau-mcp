"""Ollama LLM client with tool calling support."""
import json
from typing import Any, Dict, List, Optional

import ollama

from src.config import settings, get_logger
from src.mcp import get_tool_definitions, handle_tool_call

logger = get_logger(__name__)


class OllamaClient:
    """
    Client for interacting with Ollama LLM with tool calling support.
    
    Handles:
    - Chat completion with tool calling
    - Multi-turn tool execution loop
    - Tool result integration back to LLM
    """
    
    def __init__(self, model: Optional[str] = None):
        """
        Initialize Ollama client.
        
        Args:
            model: Model name (defaults to settings.ollama_model)
        """
        self.model = model or settings.ollama_model
        self.tools = self._convert_mcp_tools_to_ollama_format()
        
        logger.info(f"Initialized Ollama client with model: {self.model}")
        logger.info(f"Loaded {len(self.tools)} tools")
    
    def _convert_mcp_tools_to_ollama_format(self) -> List[Dict[str, Any]]:
        """
        Convert MCP tool definitions to Ollama's function calling format.
        
        Returns:
            List of tool definitions in Ollama format
        """
        mcp_tools = get_tool_definitions()
        ollama_tools = []
        
        for tool in mcp_tools:
            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            })
        
        logger.debug(f"Converted {len(ollama_tools)} MCP tools to Ollama format")
        return ollama_tools
    
    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> str:
        """
        Execute an MCP tool and return the result.
        
        Args:
            tool_name: Name of tool to execute
            tool_args: Tool arguments
            
        Returns:
            Tool execution result as JSON string
        """
        try:
            logger.info(f"Executing tool: {tool_name}")
            logger.debug(f"Tool arguments: {tool_args}")
            
            # Call MCP handler
            result = handle_tool_call(tool_name, tool_args)
            
            # Extract text from MCP response
            result_text = result[0].text
            
            logger.debug(f"Tool result: {result_text[:200]}...")
            return result_text
            
        except Exception as e:
            logger.error(f"Tool execution failed: {e}")
            return json.dumps({
                "status": "error",
                "message": str(e)
            })
    
    def chat(
        self,
        messages: List[Dict[str, str]],
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Send chat request to Ollama with tool calling support.
        
        Handles multi-turn conversations where the model may:
        1. Call one or more tools
        2. Receive tool results
        3. Generate final response
        
        Args:
            messages: Conversation history [{"role": "user", "content": "..."}]
            max_iterations: Maximum tool calling iterations to prevent infinite loops
            
        Returns:
            Dict with 'message' (final response) and 'iterations' (tool call count)
        """
        logger.info(f"Starting chat with {len(messages)} messages")
        
        iteration = 0
        
        try:
            # Initial LLM call with tools available
            response = ollama.chat(
                model=self.model,
                messages=messages,
                tools=self.tools
            )
            
            # Tool calling loop
            while iteration < max_iterations:
                iteration += 1
                
                # Check if model wants to call tools
                tool_calls = response.get('message', {}).get('tool_calls')
                
                if not tool_calls:
                    # No more tool calls - we have final response
                    logger.info(f"Chat completed after {iteration} iteration(s)")
                    break
                
                logger.info(f"Iteration {iteration}: Model requested {len(tool_calls)} tool call(s)")
                
                # Add assistant's message (with tool calls) to conversation
                messages.append(response['message'])
                
                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call['function']['name']
                    tool_args = tool_call['function']['arguments']
                    
                    logger.info(f"  → Calling: {tool_name}")
                    
                    # Execute tool
                    tool_result = self._execute_tool(tool_name, tool_args)
                    
                    # Add tool result to messages
                    messages.append({
                        'role': 'tool',
                        'content': tool_result
                    })
                
                # Call LLM again with tool results
                logger.info("  → Sending tool results back to model...")
                response = ollama.chat(
                    model=self.model,
                    messages=messages,
                    tools=self.tools
                )
            
            # Check if we hit max iterations
            if iteration >= max_iterations and response.get('message', {}).get('tool_calls'):
                logger.warning(f"Hit max iterations ({max_iterations}) - forcing response")
                final_message = (
                    "I've executed multiple operations but need to stop here to avoid "
                    "an infinite loop. Here's what I've done so far based on the tool results."
                )
            else:
                final_message = response['message']['content']
            
            return {
                "message": final_message,
                "iterations": iteration
            }
            
        except Exception as e:
            logger.error(f"Chat error: {e}")
            raise
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            Health status dictionary
        """
        try:
            models = ollama.list()
            
            # Handle different response formats
            available_models = []
            if isinstance(models, dict) and 'models' in models:
                # Format: {'models': [{'name': 'llama3.1:8b', ...}, ...]}
                available_models = [
                    m.get('name', m.get('model', 'unknown')) 
                    for m in models['models']
                ]
            elif isinstance(models, dict) and 'model' in models:
                # Single model format
                available_models = [models['model']]
            elif isinstance(models, list):
                # List format
                available_models = [
                    m.get('name', m.get('model', 'unknown')) 
                    for m in models
                ]
            
            return {
                "status": "healthy",
                "ollama_running": True,
                "current_model": self.model,
                "available_models": available_models,
                "tools_count": len(self.tools)
            }
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return {
                "status": "unhealthy",
                "ollama_running": False,
                "error": str(e)
            }


def get_ollama_client(model: Optional[str] = None) -> OllamaClient:
    """
    Factory function to create an Ollama client.
    
    Args:
        model: Model name (optional)
        
    Returns:
        Configured OllamaClient instance
    """
    return OllamaClient(model=model)
