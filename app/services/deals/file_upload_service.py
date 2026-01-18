"""Service for handling deal document uploads."""

import os
import shutil
from pathlib import Path
from uuid import uuid4


class FileUploadService:
    """Service for handling deal document uploads."""

    ALLOWED_EXTENSIONS = [".pdf", ".docx", ".doc"]
    UPLOAD_DIR = Path("./data/uploads/deals")

    def __init__(self):
        self.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    def validate_file_type(self, filename: str) -> bool:
        """Check if file extension is allowed."""
        _, ext = os.path.splitext(filename.lower())
        return ext in self.ALLOWED_EXTENSIONS

    async def save_uploaded_file(self, data: bytes, original_name: str) -> dict:
        """
        Save uploaded file content to custom storage.

        Args:
            data: File content bytes
            original_name: Original filename from upload

        Returns:
            dict with name, path, size, size_formatted
        """
        filename = os.path.basename(original_name)
        _, ext = os.path.splitext(filename.lower())

        # Generate unique filename to prevent collisions
        unique_name = f"{os.path.splitext(filename)[0]}-{uuid4().hex[:8]}{ext}"
        dest = self.UPLOAD_DIR / unique_name

        # Write bytes to permanent storage
        with open(dest, "wb") as f:
            f.write(data)

        file_size = dest.stat().st_size

        return {
            "name": filename,
            "unique_name": unique_name,
            "path": str(dest),
            "size": file_size,
            "size_formatted": self.format_file_size(file_size),
        }

    @staticmethod
    def format_file_size(size_bytes: int) -> str:
        """Format bytes to human-readable size."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"
