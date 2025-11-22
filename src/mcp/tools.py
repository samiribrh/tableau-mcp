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
                "Excel and CSV files are automatically converted to Hyper format before upload. "
                "IMPORTANT: Use ONLY the filename, not a full path. "
                "Examples: 'sales.xlsx' or 'data.csv' or 'revenue' (extension optional)"
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "FILENAME ONLY (not full path). Examples: 'data.csv', 'sales.xlsx', 'revenue'. "
                            "Files are searched in the configured default directory. "
                            "Extension is optional - system will search for matching files."
                        )
                    },
                    "tableau_project": {
                        "type": "string",
                        "description": (
                            "Tableau project name where the dataset will be uploaded. "
                            "Optional - defaults to configured project."
                        )
                    }
                },
                "required": ["file_path"]
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