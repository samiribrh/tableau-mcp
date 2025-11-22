# Tableau MCP Server - AI Coding Agent Guide

## Architecture Overview

This is a **Model Context Protocol (MCP) server** that bridges Claude Desktop with Tableau Server. The architecture has three layers:

1. **MCP Layer** (`main.py`): Async MCP server using stdio transport - handles tool registration and routing
2. **Tool Handler Layer** (`mcp_server.py`): Maps MCP tool calls to Tableau operations, handles validation and error formatting
3. **API Layer** (`tableau_api.py`): Direct Tableau Server interactions using `tableauserverclient` and Excel-to-Hyper conversion with `pantab`

**Data Flow**: Claude Desktop → stdio JSON-RPC → MCP handlers → Tableau API functions → Tableau Server

## Critical Patterns

### File Path Resolution (`tableau_api.py`)

All file operations use `_resolve_file_path()` which:
- Accepts absolute paths as-is
- Resolves relative paths against `DEFAULT_FILE_DIRECTORY` from `.env`
- Smart Excel finder: `_find_excel_file()` auto-detects `.xlsx`, `.xls`, `.xlsm`, `.xlsb` if extension omitted

```python
# User can specify: "sales_data" and it finds "sales_data.xlsx" in DEFAULT_FILE_DIRECTORY
file_path = _resolve_file_path(file_path)
excel_file_path = _find_excel_file(excel_file_path)
```

### Tableau Authentication

Uses **Personal Access Token (PAT)** authentication only (no username/password). Connection established in `connect_tableau()` with site-scoped auth:

```python
tableau_auth = TSC.PersonalAccessTokenAuth(
    token_name=TABLEAU_PAT_NAME,
    personal_access_token=TABLEAU_PAT_SECRET,
    site_id=TABLEAU_SITE_ID  # Empty string for default site
)
```

### Project-Scoped Operations

All dataset operations require resolving project name to project ID via `get_project_id()`. Default project comes from `TABLEAU_PROJECT_NAME` in config.

## Tool Development Workflow

**To add a new MCP tool:**

1. Implement business logic in `tableau_api.py` (function receives `server` + params)
2. Add `Tool` definition with JSON Schema in `get_tool_definitions()` (`mcp_server.py`)
3. Create `_handle_your_tool()` wrapper in `mcp_server.py` (extracts args, validates, calls API)
4. Route in `handle_tool_call()` elif chain

**Return format**: All tools return `list[TextContent]` with JSON containing `{"status": "success/error", "result": {...}}`

## Environment Configuration

Required `.env` variables (loaded via `python-dotenv` in `config.py`):
- `TABLEAU_SERVER`: Full URL with `https://`
- `TABLEAU_PAT_NAME` + `TABLEAU_PAT_SECRET`: From Tableau Server PAT
- `TABLEAU_SITE_ID`: Empty string for default site
- `TABLEAU_PROJECT_NAME`: Default project (e.g., "Sales")
- `DEFAULT_FILE_DIRECTORY`: Base path for relative file references (defaults to Downloads)

## Running & Debugging

**Local testing** (outside Claude Desktop):
```powershell
poetry run python main.py  # Starts stdio server, awaits JSON-RPC on stdin
```

**Claude Desktop integration**: Configured via `%APPDATA%\Claude\claude_desktop_config.json` (Windows) with:
```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "poetry",
      "args": ["run", "python", "main.py"],
      "cwd": "C:\\path\\to\\tableau-mcp"
    }
  }
}
```

**Logs**: Standard Python `logging` to INFO level. Claude Desktop logs in `%APPDATA%\Claude\logs\`

## Key Dependencies

- `mcp` (v1.21.0): MCP SDK for tool definitions and stdio server
- `tableauserverclient` (v0.38): Official Tableau REST API client
- `pantab` (v5.2.2): Pandas DataFrame ↔ Hyper file conversion
- `pandas` + `openpyxl`: Excel reading for Hyper conversion

## Common Gotchas

- **Excel conversion**: `pantab.frame_to_hyper()` always creates table named "Extract" (Tableau convention)
- **Overwrite mode**: `upload_dataset()` uses `TSC.Server.PublishMode.Overwrite` - will replace existing datasources
- **Async context**: `main.py` is async, but `tableau_api.py` and `mcp_server.py` are synchronous (Tableau client is sync)
- **Path separators**: Use raw strings (`r'C:\path'`) or forward slashes in `.env` for Windows paths
