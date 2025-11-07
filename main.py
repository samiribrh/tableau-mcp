import asyncio
import logging

from mcp.server import Server
from mcp.server.stdio import stdio_server

from mcp_server import get_tool_definitions, handle_tool_call

logging.basicConfig(level=logging.INFO)

# Create MCP server instance
app = Server("tableau-mcp")


@app.list_tools()
async def list_tools():
    """List available Tableau tools"""
    return get_tool_definitions()


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    """Handle tool calls"""
    return handle_tool_call(name, arguments)


async def main():
    """Main entry point for the MCP server"""
    logging.info("Starting Tableau MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
    