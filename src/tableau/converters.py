"""File format conversion utilities."""
from pathlib import Path
from typing import Optional

import pandas as pd
import pantab

from src.config import settings, get_logger
from src.models import ConversionResult

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
    
    if path.is_absolute():
        return str(path)
    
    resolved_path = settings.default_file_directory / file_path
    logger.debug(f"Resolved relative path '{file_path}' to '{resolved_path}'")
    return str(resolved_path)


def _find_excel_file(file_path: str) -> str:
    """
    Find Excel file, trying different extensions if needed.
    
    Args:
        file_path: Base file path
        
    Returns:
        Path to found Excel file
        
    Raises:
        FileNotFoundError: If no Excel file found
    """
    file_path = _resolve_file_path(file_path)
    path = Path(file_path)
    
    # If file has extension and exists, use it
    if path.suffix and path.exists():
        logger.debug(f"Found Excel file: {path}")
        return str(path)
    
    # If path exists as-is (maybe no extension given)
    if path.exists():
        return str(path)
    
    # Try common Excel extensions
    excel_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
    
    directory = path.parent
    filename_stem = path.stem if path.suffix else path.name
    
    for ext in excel_extensions:
        potential_path = directory / f"{filename_stem}{ext}"
        if potential_path.exists():
            logger.info(f"Found Excel file with extension {ext}: {potential_path}")
            return str(potential_path)
    
    # Not found
    raise FileNotFoundError(
        f"Excel file not found: {file_path}. "
        f"Tried extensions: {', '.join(excel_extensions)}"
    )


def convert_excel_to_hyper(
    excel_file_path: str,
    hyper_file_path: Optional[str] = None
) -> ConversionResult:
    """
    Convert an Excel file to Tableau Hyper format.
    
    Args:
        excel_file_path: Path to Excel file (.xlsx, .xls, etc.)
        hyper_file_path: Output Hyper file path (optional)
                        If not provided, uses same name with .hyper extension
        
    Returns:
        ConversionResult with details about the conversion
        
    Raises:
        FileNotFoundError: If Excel file not found
        Exception: If conversion fails
    """
    try:
        logger.info(f"Starting Excel to Hyper conversion: {excel_file_path}")
        
        # Find the Excel file (handles missing extensions)
        excel_file_path = _find_excel_file(excel_file_path)
        
        # Determine output path
        if not hyper_file_path:
            excel_path = Path(excel_file_path)
            hyper_file_path = str(excel_path.parent / f"{excel_path.stem}.hyper")
        else:
            hyper_file_path = _resolve_file_path(hyper_file_path)
        
        logger.info(f"Output Hyper file: {hyper_file_path}")
        
        # Read Excel file
        logger.info(f"Reading Excel file...")
        df = pd.read_excel(excel_file_path)
        
        logger.info(f"Excel file loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Convert to Hyper format
        logger.info(f"Converting to Hyper format...")
        pantab.frame_to_hyper(df, hyper_file_path, table="Extract")
        
        logger.info(f"✓ Successfully converted Excel to Hyper: {hyper_file_path}")
        
        # Return conversion result
        return ConversionResult(
            input_file=excel_file_path,
            output_file=hyper_file_path,
            rows=len(df),
            columns=len(df.columns),
            column_names=list(df.columns)
        )
        
    except FileNotFoundError as e:
        logger.error(f"✗ Excel file not found: {e}")
        raise
    except Exception as e:
        logger.error(f"✗ Failed to convert Excel to Hyper: {e}")
        raise


def convert_csv_to_hyper(
    csv_file_path: str,
    hyper_file_path: Optional[str] = None
) -> ConversionResult:
    """
    Convert a CSV file to Tableau Hyper format.
    
    Args:
        csv_file_path: Path to CSV file
        hyper_file_path: Output Hyper file path (optional)
        
    Returns:
        ConversionResult with details about the conversion
    """
    try:
        csv_file_path = _resolve_file_path(csv_file_path)
        
        logger.info(f"Starting CSV to Hyper conversion: {csv_file_path}")
        
        if not Path(csv_file_path).exists():
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")
        
        # Determine output path
        if not hyper_file_path:
            csv_path = Path(csv_file_path)
            hyper_file_path = str(csv_path.parent / f"{csv_path.stem}.hyper")
        else:
            hyper_file_path = _resolve_file_path(hyper_file_path)
        
        logger.info(f"Output Hyper file: {hyper_file_path}")
        
        # Read CSV file
        logger.info(f"Reading CSV file...")
        df = pd.read_csv(csv_file_path)
        
        logger.info(f"CSV file loaded: {len(df)} rows, {len(df.columns)} columns")
        
        # Convert to Hyper format
        logger.info(f"Converting to Hyper format...")
        pantab.frame_to_hyper(df, hyper_file_path, table="Extract")
        
        logger.info(f"✓ Successfully converted CSV to Hyper: {hyper_file_path}")
        
        return ConversionResult(
            input_file=csv_file_path,
            output_file=hyper_file_path,
            rows=len(df),
            columns=len(df.columns),
            column_names=list(df.columns)
        )
        
    except Exception as e:
        logger.error(f"✗ Failed to convert CSV to Hyper: {e}")
        raise
