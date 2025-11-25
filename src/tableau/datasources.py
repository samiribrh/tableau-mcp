"""Tableau dataset operations."""
from pathlib import Path
from typing import Optional, List

import tableauserverclient as TSC

from src.config import settings, get_logger
from src.models import DatasetInfo, DatasetCheckResult
from src.tableau.client import TableauClient

logger = get_logger(__name__)


def _resolve_file_path(file_path: str) -> str:
    """
    Resolve file path (absolute or relative to default directory).
    
    Args:
        file_path: File path to resolve
        
    Returns:
        Resolved absolute path as string
    """
    path = Path(file_path)
    
    # If already absolute, return as-is
    if path.is_absolute():
        return str(path)
    
    # Otherwise, resolve relative to default directory
    resolved_path = settings.default_file_directory / file_path
    logger.debug(f"Resolved relative path '{file_path}' to '{resolved_path}'")
    return str(resolved_path)


def get_project_id(
    client: TableauClient,
    project_name: Optional[str] = None
) -> Optional[str]:
    """
    Get Tableau project ID by name.
    
    Args:
        client: Connected Tableau client
        project_name: Project name (defaults to settings)
        
    Returns:
        Project ID if found, None otherwise
    """
    project_name = project_name or settings.tableau_project_name
    
    try:
        logger.info(f"Looking for project: '{project_name}'")
        
        all_projects, _ = client.server.projects.get()
        
        for project in all_projects:
            if project.name == project_name:
                logger.info(f"✓ Found project '{project_name}' (ID: {project.id})")
                return project.id
        
        logger.warning(f"✗ Project '{project_name}' not found")
        return None
        
    except Exception as e:
        logger.error(f"Error retrieving projects: {e}")
        raise


def upload_dataset(
    client: TableauClient,
    file_path: str,
    project_name: Optional[str] = None
) -> DatasetInfo:
    """
    Upload a dataset to Tableau Server.
    
    Args:
        client: Connected Tableau client
        file_path: Path to dataset file (.hyper, .tds, .tdsx)
        project_name: Target project name (defaults to settings)
        
    Returns:
        DatasetInfo with upload details
        
    Raises:
        Exception: If project not found or upload fails
    """
    if not project_name:
        raise ValueError("Project name is required")
    
    try:
        # Resolve file path
        file_path = _resolve_file_path(file_path)
        logger.info(f"Starting upload for dataset: {file_path}")
        
        # Verify file exists
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get project ID
        project_id = get_project_id(client, project_name)
        if not project_id:
            raise Exception(f"Project '{project_name}' not found on Tableau Server")
        
        # Create datasource item
        datasource_item = TSC.DatasourceItem(project_id)
        
        # Upload (overwrite if exists)
        logger.info(f"Uploading to project '{project_name}'...")
        new_datasource = client.server.datasources.publish(
            datasource_item,
            file_path,
            mode=TSC.Server.PublishMode.Overwrite
        )
        
        logger.info(f"✓ Successfully uploaded '{new_datasource.name}'")
        
        # Return as DatasetInfo model
        return DatasetInfo(
            name=new_datasource.name,
            id=new_datasource.id,
            project_id=project_id,
            file_path=file_path
        )
        
    except Exception as e:
        logger.error(f"✗ Failed to upload dataset '{file_path}': {e}")
        raise


def check_dataset(
    client: TableauClient,
    dataset_name: str,
    project_name: Optional[str] = None
) -> DatasetCheckResult:
    """
    Check if a dataset exists in Tableau Server.
    
    Args:
        client: Connected Tableau client
        dataset_name: Name of dataset to check
        project_name: Project name to search in (defaults to settings)
        
    Returns:
        DatasetCheckResult indicating if dataset exists
    """
    project_name = project_name or settings.tableau_project_name
    
    try:
        logger.info(f"Checking if dataset '{dataset_name}' exists in project '{project_name}'")
        
        # Get project ID
        project_id = get_project_id(client, project_name)
        if not project_id:
            raise Exception(f"Project '{project_name}' not found on Tableau Server")
        
        # Get all datasources
        all_datasources, _ = client.server.datasources.get()
        
        # Search for dataset in the specific project
        for ds in all_datasources:
            if ds.name == dataset_name and ds.project_id == project_id:
                logger.info(f"✓ Dataset '{dataset_name}' found in project '{project_name}'")
                return DatasetCheckResult(
                    exists=True,
                    name=ds.name,
                    id=ds.id,
                    project_id=ds.project_id
                )
        
        # Not found
        logger.info(f"✗ Dataset '{dataset_name}' not found in project '{project_name}'")
        return DatasetCheckResult(
            exists=False,
            name=dataset_name,
            project=project_name
        )
        
    except Exception as e:
        logger.error(f"Error checking dataset '{dataset_name}': {e}")
        raise


def list_datasets(
    client: TableauClient,
    project_name: Optional[str] = None
) -> List[DatasetInfo]:
    """
    List all datasets in a project.
    
    Args:
        client: Connected Tableau client
        project_name: Project name (defaults to settings)
        
    Returns:
        List of DatasetInfo objects
    """
    project_name = project_name or settings.tableau_project_name
    
    try:
        logger.info(f"Listing datasets in project '{project_name}'")
        
        # Get project ID
        project_id = get_project_id(client, project_name)
        if not project_id:
            raise Exception(f"Project '{project_name}' not found on Tableau Server")
        
        # Get all datasources in project
        all_datasources, _ = client.server.datasources.get()
        
        datasets = []
        for ds in all_datasources:
            if ds.project_id == project_id:
                datasets.append(DatasetInfo(
                    name=ds.name,
                    id=ds.id,
                    project_id=ds.project_id
                ))
        
        logger.info(f"✓ Found {len(datasets)} datasets in project '{project_name}'")
        return datasets
        
    except Exception as e:
        logger.error(f"Error listing datasets: {e}")
        raise
