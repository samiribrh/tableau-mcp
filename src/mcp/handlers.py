"""MCP tool execution handlers."""
import json
from pathlib import Path
from typing import Dict, Any, List

from mcp.types import TextContent

from src.config import get_logger
from src.tableau import (
    get_tableau_client,
    upload_dataset,
    check_dataset,
    list_datasets,
    convert_excel_to_hyper,
    convert_csv_to_hyper,
)

logger = get_logger(__name__)


def handle_tool_call(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """
    Handle MCP tool execution.
    
    Routes tool calls to appropriate handlers and returns formatted results.
    
    Args:
        name: Tool name to execute
        arguments: Tool arguments as dictionary
        
    Returns:
        List of TextContent with execution results
    """
    try:
        logger.info(f"Executing tool: {name}")
        logger.debug(f"Arguments: {arguments}")
        
        # Route to appropriate handler
        if name == "upload_dataset":
            result = _handle_upload_dataset(arguments)
        elif name == "check_dataset":
            result = _handle_check_dataset(arguments)
        elif name == "list_datasets":
            result = _handle_list_datasets(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        # Return success response
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "success",
                "action": name,
                "result": result
            }, indent=2, default=str)
        )]
        
    except Exception as e:
        logger.error(f"Tool execution failed: {name} - {e}")
        
        # Return error response
        return [TextContent(
            type="text",
            text=json.dumps({
                "status": "error",
                "action": name,
                "message": str(e)
            }, indent=2)
        )]


def _handle_upload_dataset(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle upload_dataset tool with automatic format conversion.
    
    Automatically converts Excel/CSV files to Hyper format before upload.
    """
    file_path = arguments.get("file_path")
    tableau_project = arguments.get("tableau_project")
    
    if not file_path:
        raise ValueError("Missing required parameter: file_path")
    
    from src.config import settings
    
    # Parse the file path
    path = Path(file_path)
    
    # If it's an absolute path but doesn't exist, extract just the filename
    if path.is_absolute() and not path.exists():
        logger.warning(f"Absolute path doesn't exist: {path}, trying filename only")
        path = Path(path.name)  # Extract just the filename
    
    # If not absolute, prepend default directory
    if not path.is_absolute():
        path = settings.default_file_directory / path
        logger.info(f"Resolved to: {path}")
    
    logger.info(f"Processing file: {path}")
    
    # Detect file type and auto-convert if needed
    file_extension = path.suffix.lower()
    
    # If no extension, try to find the file
    if not file_extension:
        logger.info(f"No extension specified, searching for file: {path.stem}")
        
        # Try different extensions
        possible_extensions = ['.hyper', '.xlsx', '.xls', '.csv', '.xlsm', '.xlsb']
        found_path = None
        
        for ext in possible_extensions:
            test_path = path.parent / f"{path.stem}{ext}"
            if test_path.exists():
                found_path = test_path
                file_extension = ext
                logger.info(f"Found file: {found_path}")
                break
        
        if not found_path:
            raise FileNotFoundError(
                f"Could not find file '{path.stem}' with extensions: {possible_extensions}. "
                f"Searched in: {path.parent}"
            )
        
        path = found_path
    
    # Check if file exists
    if not path.exists():
        # Try searching for similar files
        parent_dir = path.parent
        filename_stem = path.stem
        
        logger.info(f"File not found at {path}, searching directory: {parent_dir}")
        
        # List all files in directory
        if parent_dir.exists():
            all_files = list(parent_dir.glob(f"{filename_stem}.*"))
            if all_files:
                logger.info(f"Found similar files: {[f.name for f in all_files]}")
                # Use the first match
                path = all_files[0]
                file_extension = path.suffix.lower()
                logger.info(f"Using: {path}")
            else:
                available_files = list(parent_dir.glob("*"))[:10]  # Show first 10
                raise FileNotFoundError(
                    f"File not found: {path}\n"
                    f"Available files in {parent_dir}:\n" +
                    "\n".join(f"  - {f.name}" for f in available_files)
                )
        else:
            raise FileNotFoundError(f"Directory not found: {parent_dir}")
    
    # Auto-convert Excel/CSV to Hyper
    hyper_path = path
    conversion_info = None
    
    if file_extension in ['.xlsx', '.xls', '.xlsm', '.xlsb']:
        logger.info(f"Excel file detected - converting to Hyper format...")
        conversion_result = convert_excel_to_hyper(str(path))
        hyper_path = Path(conversion_result.output_file)
        conversion_info = {
            "converted_from": "Excel",
            "original_file": str(path),
            "rows": conversion_result.rows,
            "columns": conversion_result.columns
        }
        logger.info(f"✓ Converted Excel to Hyper: {hyper_path}")
    
    elif file_extension == '.csv':
        logger.info(f"CSV file detected - converting to Hyper format...")
        conversion_result = convert_csv_to_hyper(str(path))
        hyper_path = Path(conversion_result.output_file)
        conversion_info = {
            "converted_from": "CSV",
            "original_file": str(path),
            "rows": conversion_result.rows,
            "columns": conversion_result.columns
        }
        logger.info(f"✓ Converted CSV to Hyper: {hyper_path}")
    
    elif file_extension == '.hyper':
        logger.info(f"Hyper file detected - no conversion needed")
    
    else:
        raise ValueError(
            f"Unsupported file format: {file_extension}. "
            f"Supported formats: .hyper, .xlsx, .xls, .csv"
        )
    
    # Upload to Tableau
    logger.info(f"Uploading to Tableau Server...")
    with get_tableau_client() as client:
        dataset_info = upload_dataset(
            client,
            str(hyper_path),
            project_name=tableau_project
        )
    
    # Build result
    result = dataset_info.model_dump()
    
    # Add conversion info if file was converted
    if conversion_info:
        result["conversion"] = conversion_info
    
    return result


def _handle_check_dataset(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle check_dataset tool."""
    dataset_name = arguments.get("dataset_name")
    tableau_project = arguments.get("tableau_project")
    
    if not dataset_name:
        raise ValueError("Missing required parameter: dataset_name")
    
    # Connect to Tableau and check
    with get_tableau_client() as client:
        result = check_dataset(
            client,
            dataset_name,
            project_name=tableau_project
        )
    
    return result.model_dump()


def _handle_list_datasets(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Handle list_datasets tool."""
    tableau_project = arguments.get("tableau_project")
    
    # Connect to Tableau and list
    with get_tableau_client() as client:
        datasets = list_datasets(
            client,
            project_name=tableau_project
        )
    
    return {
        "count": len(datasets),
        "datasets": [ds.model_dump() for ds in datasets]
    }
