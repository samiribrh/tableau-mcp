"""Tableau-specific data models."""
from typing import List, Optional

from pydantic import BaseModel, Field


class DatasetInfo(BaseModel):
    """Information about a Tableau dataset."""
    name: str = Field(..., description="Dataset name")
    id: str = Field(..., description="Dataset ID")
    project_id: str = Field(..., description="Project ID")
    file_path: Optional[str] = Field(None, description="File path if uploaded")


class DatasetCheckResult(BaseModel):
    """Result of checking if a dataset exists."""
    exists: bool = Field(..., description="Whether dataset exists")
    name: str = Field(..., description="Dataset name checked")
    id: Optional[str] = Field(None, description="Dataset ID if exists")
    project_id: Optional[str] = Field(None, description="Project ID if exists")
    project: Optional[str] = Field(None, description="Project name")


class ConversionResult(BaseModel):
    """Result of Excel to Hyper conversion."""
    input_file: str = Field(..., description="Input Excel file path")
    output_file: str = Field(..., description="Output Hyper file path")
    rows: int = Field(..., description="Number of rows")
    columns: int = Field(..., description="Number of columns")
    column_names: List[str] = Field(..., description="List of column names")


class ProjectInfo(BaseModel):
    """Information about a Tableau project."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name")
