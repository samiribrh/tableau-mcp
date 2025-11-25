"""MCP tool definitions."""
from typing import List

from mcp.types import Tool


def get_tool_definitions() -> List[Tool]:
    """
    Define all available Tableau MCP tools.
    
    Returns:
        List of Tool definitions with their schemas
    """
    return [
        Tool(
            name="upload_dataset",
            description=(
                "Upload a dataset file to Tableau Server. "
                "Accepts Excel (.xlsx, .xls), CSV (.csv), or Hyper (.hyper) files. "
                "\n\n"
                "⚠️ CRITICAL WORKFLOW:"
                "\n1. Check if user mentioned a Tableau project name"
                "\n2. If YES → call this tool with both file_path and tableau_project"
                "\n3. If NO → DO NOT call this tool yet! Instead, respond to user:"
                '\n   "Which Tableau project would you like to upload to?"'
                "\n4. Wait for user's reply with project name"
                "\n5. Then call this tool with the project name they provided"
                "\n\n"
                "DO NOT use placeholder values like 'default' or empty strings. "
                "DO NOT call this tool without an actual project name from the user."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Filename only (e.g., 'sales.xlsx', 'data.csv')"
                    },
                    "tableau_project": {
                        "type": "string",
                        "description": "Exact Tableau project name provided by the user (e.g., 'Sales', 'Marketing'). Never use placeholders."
                    }
                },
                "required": ["file_path", "tableau_project"]
            }
        ),
        
        Tool(
            name="check_dataset",
            description=(
                "Check if a dataset exists in Tableau Server. "
                "Searches for the dataset by name within a specific project. "
                "Returns whether the dataset exists and its details if found."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_name": {
                        "type": "string",
                        "description": "Name of the dataset to check"
                    },
                    "tableau_project": {
                        "type": "string",
                        "description": (
                            "Tableau project name to search in. "
                            "Optional - defaults to configured project."
                        )
                    }
                },
                "required": ["dataset_name"]
            }
        ),
        
        Tool(
            name="list_datasets",
            description=(
                "List all datasets in a Tableau project. "
                "Returns name and ID for each dataset found in the project."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "tableau_project": {
                        "type": "string",
                        "description": (
                            "Tableau project name to list datasets from. "
                            "Optional - defaults to configured project."
                        )
                    }
                },
                "required": []
            }
        )
    ]