"""File management utilities for video uploads and temp cleanup.

Per architecture: videos go to uploads/ immediately (never kept in memory),
temp/ cleaned after pipeline completes.
"""

import os
import shutil
import time
from pathlib import Path

# Storage directories — configurable via env vars (for HF Spaces /data persistence)
_DATA_ROOT = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parent.parent)))
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", str(_DATA_ROOT / "uploads")))
TEMP_DIR = Path(os.getenv("TEMP_DIR", str(_DATA_ROOT / "temp")))
REPORTS_DIR = Path(os.getenv("REPORTS_DIR", str(_DATA_ROOT / "reports")))

# Allowed video extensions
ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi"}

# Max file size: 500 MB (matches Streamlit config)
MAX_FILE_SIZE_MB = 500


def ensure_dirs() -> None:
    """Create uploads/, temp/, reports/ directories if they don't exist."""
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# Ensure directories exist on import (StaticFiles mount in server.py needs them)
ensure_dirs()


def allowed_file(filename: str) -> bool:
    """Check if file extension is an allowed video format (mp4, mov, avi)."""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


def get_file_size_mb(file_path: str) -> float:
    """Return file size in megabytes."""
    return os.path.getsize(file_path) / (1024 * 1024)


def save_upload(uploaded_file) -> str:
    """Save an uploaded file to uploads/ with timestamp prefix.

    Args:
        uploaded_file: A Streamlit UploadedFile object (has .name, .read(), .size).

    Returns:
        str: Full path to the saved file.

    The file is written immediately to disk — never kept in memory (per architecture).
    """
    ensure_dirs()
    timestamp = int(time.time())
    safe_name = f"{timestamp}_{uploaded_file.name}"
    dest_path = str(UPLOAD_DIR / safe_name)

    with open(dest_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return dest_path


def save_upload_bytes(filename: str, data: bytes) -> str:
    """Save raw bytes to uploads/ with timestamp prefix.

    Args:
        filename: Original filename (used for extension).
        data: File content as bytes.

    Returns:
        str: Full path to the saved file.
    """
    ensure_dirs()
    timestamp = int(time.time())
    safe_name = f"{timestamp}_{filename}"
    dest_path = str(UPLOAD_DIR / safe_name)

    with open(dest_path, "wb") as f:
        f.write(data)

    return dest_path


def cleanup_temp() -> None:
    """Remove all files from the temp/ directory.

    Called after the analysis pipeline completes. Preserves the directory
    itself but removes all contents.
    """
    if TEMP_DIR.exists():
        for item in TEMP_DIR.iterdir():
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def get_upload_path(filename: str) -> str:
    """Get full path for a file in uploads/."""
    return str(UPLOAD_DIR / filename)
