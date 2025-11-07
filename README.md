# Tableau MCP Server

A Model Context Protocol (MCP) server that enables Claude Desktop to interact with Tableau Server. Upload datasets, check data sources, and convert Excel files to Tableau Hyper format - all through natural language.

## Features

- **Upload Datasets**: Publish data sources to Tableau Server
- **Check Datasets**: Verify if datasets exist in your Tableau projects
- **Excel to Hyper Conversion**: Convert Excel files (.xlsx, .xls, .xlsm, .xlsb) to Tableau Hyper format

## Prerequisites

- Python 3.10 or higher
- Claude Desktop App
- Tableau Server with Personal Access Token (PAT)
- Windows, macOS, or Linux

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/samiribrh/tableau-mcp.git
cd tableau-mcp
```

### 2. Install Dependencies

This project uses [Poetry](https://python-poetry.org/) for dependency management.

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install project dependencies
poetry install
```

Or install manually with pip:

```bash
pip install mcp tableauserverclient pantab pandas python-dotenv openpyxl
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Tableau Server Configuration
TABLEAU_SERVER=https://your-tableau-server.com
TABLEAU_SITE_ID=your-site-id
TABLEAU_PAT_NAME=your-pat-name
TABLEAU_PAT_SECRET=your-pat-secret
TABLEAU_PROJECT_NAME=Sales

# Optional: Default file directory
DEFAULT_FILE_DIRECTORY=C:\Users\YourUsername\Downloads
```

#### How to Get Your Tableau PAT:

1. Log in to Tableau Server
2. Click your profile icon → **My Account Settings**
3. Scroll to **Personal Access Tokens**
4. Click **Create new token**
5. Enter a token name and click **Create**
6. Copy the token secret (you won't see it again!)

### 4. Configure Claude Desktop

#### Windows

Open or create: `%APPDATA%\Claude\claude_desktop_config.json`

**Using Poetry:**

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "main.py"
      ],
      "cwd": "C:\\path\\to\\tableau-mcp"
    }
  }
}
```

**Using Python directly:**

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "C:\\Python313\\python.exe",
      "args": [
        "C:\\path\\to\\tableau-mcp\\main.py"
      ],
      "cwd": "C:\\path\\to\\tableau-mcp"
    }
  }
}
```

#### macOS/Linux

Open or create: `~/Library/Application Support/Claude/claude_desktop_config.json`

**Using Poetry:**

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "poetry",
      "args": [
        "run",
        "python",
        "main.py"
      ],
      "cwd": "/path/to/tableau-mcp"
    }
  }
}
```

**Using Python directly:**

```json
{
  "mcpServers": {
    "tableau-mcp": {
      "command": "/usr/local/bin/python3",
      "args": [
        "/path/to/tableau-mcp/main.py"
      ],
      "cwd": "/path/to/tableau-mcp"
    }
  }
}
```

### 5. Restart Claude Desktop

Completely close and reopen Claude Desktop for changes to take effect.

## Usage

Once configured, you can interact with Tableau through natural language in Claude Desktop:

### Convert Excel to Hyper

```
"Convert sales_data to hyper format"
→ Finds sales_data.xlsx in Downloads and converts to sales_data.hyper

"Convert Q4_report.xlsx to hyper"
→ Converts the specific file to Hyper format

"Convert C:\Documents\data.xlsx to output.hyper"
→ Converts with custom output path
```

### Upload Datasets

```
"Upload revenue.hyper to Tableau"
→ Uploads to default project (from .env)

"Upload customer_data.hyper to Marketing project"
→ Uploads to specific project

"Upload C:\Reports\sales.hyper to Sales project"
→ Upload from custom path
```

### Check Datasets

```
"Check if sales_data exists in Tableau"
→ Checks in default project

"Does customer_report exist in the Marketing project?"
→ Checks specific project
```

### Combined Workflows

```
"Convert monthly_sales to hyper and upload it to the Finance project"
→ Converts Excel file and uploads in one go
```

## Project Structure

```
tableau-mcp/
├── main.py              # MCP server entry point
├── mcp_server.py        # Tool definitions and handlers
├── tableau_api.py       # Tableau Server API interactions
├── config.py            # Configuration management
├── utils.py             # Helper utilities
├── .env                 # Environment variables (create this)
├── pyproject.toml       # Poetry dependencies
├── poetry.lock          # Locked dependencies
└── README.md            # This file
```

## Available Tools

### 1. `convert_excel_to_hyper`

Converts Excel files to Tableau Hyper format.

**Parameters:**
- `excel_file_path` (required): Path to Excel file (with or without extension)
- `hyper_file_path` (optional): Output path for .hyper file

**Supported formats:** `.xlsx`, `.xls`, `.xlsm`, `.xlsb`

### 2. `upload_dataset`

Uploads a dataset to Tableau Server.

**Parameters:**
- `file_path` (required): Path to the file to upload
- `tableau_project` (optional): Target project name

### 3. `check_dataset`

Checks if a dataset exists on Tableau Server.

**Parameters:**
- `dataset_name` (required): Name of the dataset
- `tableau_project` (optional): Project to check in

## Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `TABLEAU_SERVER` | Tableau Server URL | - | Yes |
| `TABLEAU_SITE_ID` | Site identifier | `''` | No |
| `TABLEAU_PAT_NAME` | Personal Access Token name | - | Yes |
| `TABLEAU_PAT_SECRET` | Personal Access Token secret | - | Yes |
| `TABLEAU_PROJECT_NAME` | Default project name | `Sales` | No |
| `DEFAULT_FILE_DIRECTORY` | Default file location | User's Downloads | No |

## Troubleshooting

### Server Not Appearing in Claude Desktop

1. **Check config file location**: Make sure you're editing the correct `claude_desktop_config.json`
2. **Verify Python path**: Ensure the Python executable path is correct
3. **Check file paths**: Use absolute paths in the config
4. **Restart completely**: Close Claude Desktop from Task Manager/Activity Monitor
5. **Check logs**: Look in `%APPDATA%\Claude\logs\` (Windows) or `~/Library/Logs/Claude/` (macOS)

### Module Not Found Errors

```bash
# Ensure all dependencies are installed with Poetry
poetry install

# Or add a specific package
poetry add package-name

# If using pip directly
pip install mcp tableauserverclient pantab pandas python-dotenv openpyxl
```

### Tableau Connection Issues

1. **Verify PAT credentials**: Test manually with Tableau Server Client
2. **Check server URL**: Must include `https://`
3. **Verify site ID**: Leave empty for default site
4. **Network access**: Ensure you can reach Tableau Server

### File Not Found Errors

1. **Check default directory**: Verify `DEFAULT_FILE_DIRECTORY` in `.env`
2. **Use absolute paths**: Provide full paths if relative paths don't work
3. **Check file extensions**: Ensure Excel files have proper extensions

## Development

### Adding New Tools

1. Add function to `tableau_api.py`
2. Add tool definition to `get_tool_definitions()` in `mcp_server.py`
3. Add handler function `_handle_your_tool()` in `mcp_server.py`
4. Route in `handle_tool_call()` in `mcp_server.py`

Example:

```python
# In tableau_api.py
def your_new_function(param1, param2):
    # Implementation
    pass

# In mcp_server.py - get_tool_definitions()
Tool(
    name="your_tool",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
    }
)

# In mcp_server.py - handle_tool_call()
elif name == "your_tool":
    result = _handle_your_tool(arguments)
```

### Running Tests

```bash
# Test the server manually with Poetry
poetry run python main.py
# Then send a JSON-RPC request via stdin

# Test Tableau connection
poetry run python -c "from tableau_api import connect_tableau; connect_tableau()"

# Add development dependencies
poetry add --group dev pytest pytest-asyncio

# Run tests (if you create them)
poetry run pytest
```

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- Uses [Tableau Server Client](https://github.com/tableau/server-client-python)
- Powered by [pantab](https://github.com/innobi/pantab) for Hyper conversion

## Support

- [Report Issues](https://github.com/samiribrh/tableau-mcp/issues)
- Contact: samiribrahimov2277@gmail.com
- [MCP Documentation](https://modelcontextprotocol.io/docs)
- [Tableau API Docs](https://tableau.github.io/server-client-python/)

## Changelog

### v1.0.0 (2024-11-07)
- Initial release
- Excel to Hyper conversion
- Dataset upload functionality
- Dataset existence checking

---
