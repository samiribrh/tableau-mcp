import logging
from pathlib import Path

import pandas as pd
import pantab
import tableauserverclient as TSC

from config import TABLEAU_SERVER, TABLEAU_SITE_ID, TABLEAU_PAT_NAME, TABLEAU_PAT_SECRET, TABLEAU_PROJECT_NAME, DEFAULT_FILE_DIRECTORY


def connect_tableau():
    try:
        tableau_auth = TSC.PersonalAccessTokenAuth(
            token_name=TABLEAU_PAT_NAME,
            personal_access_token=TABLEAU_PAT_SECRET,
            site_id=TABLEAU_SITE_ID
        )

        server = TSC.Server(TABLEAU_SERVER, use_server_version=True)

        server.auth.sign_in(tableau_auth)

        logging.info("Connected to Tableau Server succesfully.")
        return server
    
    except Exception as e:
        logging.error(f"Failed to connect to Tableau: {e}")
        raise


def _resolve_file_path(file_path):
    path = Path(file_path)
    
    if path.is_absolute():
        return str(path)
    
    resolved_path = Path(DEFAULT_FILE_DIRECTORY) / file_path
    logging.info(f"Resolved relative path '{file_path}' to '{resolved_path}'")
    return str(resolved_path)


def get_project_id(server, project_name=TABLEAU_PROJECT_NAME):
    try:
        all_projects, _ = server.projects.get()
        for project in all_projects:
            if project.name == project_name:
                return project.id
        logging.warning(f"Project '{project_name}' not found.")
        return None
    except Exception as e:
        logging.error(f"Error retrieving projects: {e}")
        raise


def upload_dataset(server, file_path, project_name=TABLEAU_PROJECT_NAME):
    try:
        file_path = _resolve_file_path(file_path)

        logging.info(f"Starting upload for dataset: {file_path}")

        project_id = get_project_id(server, project_name)
        if not project_id:
            raise Exception(f"Project '{project_name}' not found on Tableau Server.")
        
        datasource_item = TSC.DatasourceItem(project_id)

        new_datasource = server.datasources.publish(
            datasource_item,
            file_path,
            mode=TSC.Server.PublishMode.Overwrite
        )

        logging.info(f"Successfully uploaded dataset '{file_path}' to project '{project_name}'.")

        return {
            "name": new_datasource.name,
            "id": new_datasource.id,
            "project_id": project_id,
            "file_path": file_path
        }
    
    except Exception as e:
        logging.error(f"Failed to upload dataset '{file_path}': {e}")
        raise


def check_dataset(server, dataset_name, project_name=TABLEAU_PROJECT_NAME):
    try:        
        logging.info(f"Checking if dataset '{dataset_name}' exists in project '{project_name}'...")

        project_id = get_project_id(server, project_name)
        if not project_id:
            raise Exception(f"Project '{project_name}' not found on Tableau Server.")
        
        all_datasources, _ = server.datasources.get()

        for ds in all_datasources:
            if ds.name == dataset_name and ds.project_id == project_id:
                logging.info(f"Dataset '{dataset_name}' found in project '{project_name}'.")
                return {
                    "exists": True,
                    "name": ds.name,
                    "id": ds.id,
                    "project_id": ds.project_id
                }
            
            logging.info(f"Dataset '{dataset_name}' not found in project '{project_name}'.")
            return {"exists": False, "name": dataset_name, "project": project_name}
        
    except Exception as e:
        logging.error(f"Error checking dataset '{dataset_name}': {e}")
        raise


def convert_excel_to_hyper(excel_file_path, hyper_file_path=None):
    try:        
        logging.info(f"Starting conversion of Excel file: {excel_file_path}")

        excel_file_path = _find_excel_file(excel_file_path)
        
        if not Path(excel_file_path).exists():
            raise FileNotFoundError(f"Excel file not found: {excel_file_path}")
        
        if not hyper_file_path:
            excel_path = Path(excel_file_path)
            hyper_file_path = str(excel_path.parent / f"{excel_path.stem}.hyper")

        else:
            hyper_file_path = _resolve_file_path(hyper_file_path)
        
        logging.info(f"Reading Excel file: {excel_file_path}")
        df = pd.read_excel(excel_file_path)
        
        logging.info(f"Converting to Hyper format: {hyper_file_path}")
        pantab.frame_to_hyper(df, hyper_file_path, table="Extract")
        
        logging.info(f"Successfully converted Excel to Hyper: {hyper_file_path}")
        
        return {
            "input_file": excel_file_path,
            "output_file": hyper_file_path,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns)
        }
    
    except Exception as e:
        logging.error(f"Failed to convert Excel to Hyper: {e}")
        raise


def _find_excel_file(file_path):
    file_path = _resolve_file_path(file_path)
    path = Path(file_path)
    
    if path.suffix and path.exists():
        return str(path)
    
    if path.exists():
        return str(path)
    
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    
    directory = path.parent
    filename_stem = path.stem if path.suffix else path.name
    
    for ext in excel_extensions:
        potential_path = directory / f"{filename_stem}{ext}"
        if potential_path.exists():
            logging.info(f"Found Excel file: {potential_path}")
            return str(potential_path)
    
    logging.warning(f"Could not find Excel file with any common extension for: {file_path}")
    return file_path