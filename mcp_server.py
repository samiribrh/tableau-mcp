import json
import logging

from mcp.types import Tool, TextContent

from tableau_api import connect_tableau, upload_dataset, check_dataset, convert_excel_to_hyper


logging.basicConfig(level=logging.INFO)


def get_tool_definitions() -> list[Tool]:
    """Define all available Tableau tools"""
    return [
        Tool(
            name="upload_dataset",
            description="Upload a dataset to Tableau Server",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the dataset file to upload"
                    },
                    "tableau_project": {
                        "type": "string",
                        "description": "Tableau project name (optional)"
                    }
                },
                "required": ["file_path"]
            }
        ),
        Tool(
            name="check_dataset",
            description="Check if a dataset exists in Tableau Server.",
            inputSchema={
                "type": "object",
                "properties": {
                    "dataset_name": {
                        "type": "string",
                        "description": "Name of the dataset to check"
                    },
                    "tableau_project": {
                        "type": "string",
                        "description": "Tableau project name (optional)"
                    }
                },
                "required": ["dataset_name"]
            }
        ),
        Tool(
            name="convert_excel_to_hyper",
            description="Convert an Excel file (.xlsx, .xls) to Tableau Hyper format (.hyper)",
            inputSchema={
                "type": "object",
                "properties": {
                    "excel_file_path": {
                        "type": "string",
                        "description": "Path to the Excel file to convert"
                    },
                    "hyper_file_path": {
                        "type": "string",
                        "description": "Output path for the Hyper file (optional, defaults to same name with .hyper extension)"
                    }
                },
                "required": ["excel_file_path"]
            }
        )
    ]


def handle_tool_call(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls and route to appropriate functions"""
    try:
        logging.info(f"Tool called: {name} with arguments: {arguments}")
        
        server = connect_tableau()
        
        if name == "upload_dataset":
            result = _handle_upload_dataset(server, arguments)
        elif name == "check_dataset":
            result = _handle_check_dataset(server, arguments)
        elif name == "convert_excel_to_hyper":
            result = _handle_convert_excel_to_hyper(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "action": name,
                "result": result
            }, indent=2)
        )]

    except Exception as e:
        logging.error(f"Error executing tool {name}: {e}")
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "message": str(e)
            }, indent=2)
        )]


def _handle_upload_dataset(server, arguments: dict) -> dict:
    """Handle upload_dataset tool"""
    file_path = arguments.get("file_path")
    tableau_project = arguments.get("tableau_project")
    
    if not file_path:
        raise ValueError("Missing required parameter: file_path")
    
    return upload_dataset(server, file_path, project_name=tableau_project)


def _handle_check_dataset(server, arguments: dict) -> dict:
    """Handle check_dataset tool"""
    dataset_name = arguments.get("dataset_name")
    tableau_project = arguments.get("tableau_project")
    
    if not dataset_name:
        raise ValueError("Missing required parameter: dataset_name")
    
    return check_dataset(server, dataset_name, project_name=tableau_project)


def _handle_convert_excel_to_hyper(arguments: dict) -> dict:
    """Handle convert_excel_to_hyper tool"""
    excel_file_path = arguments.get("excel_file_path")
    hyper_file_path = arguments.get("hyper_file_path")
    
    if not excel_file_path:
        raise ValueError("Missing required parameter: excel_file_path")
    
    return convert_excel_to_hyper(excel_file_path, hyper_file_path)
