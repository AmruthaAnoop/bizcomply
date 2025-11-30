"""Utility functions for handling file uploads and downloads."""
import csv
import io
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import pandas as pd
from fastapi import HTTPException, UploadFile, status
from fastapi.responses import FileResponse, StreamingResponse

from app.core.config import settings


class FileHandler:
    """Handles file operations for import/export functionality."""
    
    @staticmethod
    def get_export_directory() -> Path:
        """Get the directory for storing exported files."""
        export_dir = Path(settings.EXPORT_DIR) if hasattr(settings, 'EXPORT_DIR') else Path("exports")
        export_dir.mkdir(parents=True, exist_ok=True)
        return export_dir
    
    @staticmethod
    def save_upload_file(upload_file: UploadFile, subdirectory: str = "uploads") -> Path:
        """Save an uploaded file to the server."""
        try:
            # Create the uploads directory if it doesn't exist
            upload_dir = Path("data") / subdirectory
            upload_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a unique filename
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            file_extension = Path(upload_file.filename).suffix if upload_file.filename else ""
            filename = f"{timestamp}_{upload_file.filename or 'file'}{file_extension}"
            file_path = upload_dir / filename
            
            # Save the file
            with open(file_path, "wb") as buffer:
                buffer.write(upload_file.file.read())
                
            return file_path
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving uploaded file: {str(e)}"
            )
    
    @staticmethod
    def delete_file(file_path: Union[str, Path]) -> bool:
        """Delete a file from the server."""
        try:
            file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                return True
            return False
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deleting file: {str(e)}"
            )
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filename: str = "export") -> StreamingResponse:
        """Export data to a CSV file."""
        try:
            if not data:
                return {"message": "No data to export"}
                
            # Convert data to CSV
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=data[0].keys(), quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(data)
            
            # Create a streaming response
            response = StreamingResponse(
                iter([output.getvalue()]),
                media_type="text/csv",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.csv",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
            
            return response
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exporting to CSV: {str(e)}"
            )
    
    @staticmethod
    def export_to_excel(data: List[Dict[str, Any]], filename: str = "export") -> StreamingResponse:
        """Export data to an Excel file."""
        try:
            if not data:
                return {"message": "No data to export"}
                
            # Convert data to DataFrame
            df = pd.DataFrame(data)
            
            # Create a BytesIO buffer
            output = io.BytesIO()
            
            # Write Excel file to buffer
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Export")
            
            # Reset buffer position
            output.seek(0)
            
            # Create a streaming response
            return StreamingResponse(
                output,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.xlsx",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exporting to Excel: {str(e)}"
            )
    
    @staticmethod
    def export_to_json(data: List[Dict[str, Any]], filename: str = "export") -> StreamingResponse:
        """Export data to a JSON file."""
        try:
            return StreamingResponse(
                iter([json.dumps(data, indent=2, default=str)]),
                media_type="application/json",
                headers={
                    "Content-Disposition": f"attachment; filename={filename}.json",
                    "Access-Control-Expose-Headers": "Content-Disposition"
                }
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exporting to JSON: {str(e)}"
            )
    
    @staticmethod
    def read_csv(file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Read data from a CSV file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                return list(reader)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading CSV file: {str(e)}"
            )
    
    @staticmethod
    def read_excel(file_path: Union[str, Path], sheet_name: str = None) -> List[Dict[str, Any]]:
        """Read data from an Excel file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            # Read Excel file
            if sheet_name:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            else:
                # Read the first sheet by default
                xls = pd.ExcelFile(file_path)
                df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])
                
            # Convert DataFrame to list of dictionaries
            return df.to_dict(orient="records")
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading Excel file: {str(e)}"
            )
    
    @staticmethod
    def read_json(file_path: Union[str, Path]) -> Union[Dict, List]:
        """Read data from a JSON file."""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid JSON file: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error reading JSON file: {str(e)}"
            )


def get_file_handler() -> FileHandler:
    """Dependency for getting a file handler instance."""
    return FileHandler()
