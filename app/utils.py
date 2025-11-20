"""
Utility functions for VisionRAG
Helper functions for timing, formatting, and general utilities.
"""

from datetime import datetime
from pathlib import Path
import hashlib


def format_timestamp(seconds: float) -> str:
    """
    Convert seconds to HH:MM:SS format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS)
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def get_video_id(filename: str) -> str:
    """
    Generate a unique video ID from filename.
    
    Args:
        filename: Original video filename
        
    Returns:
        Unique video ID (hash-based)
    """
    # Use filename + timestamp for uniqueness
    timestamp = datetime.now().isoformat()
    unique_string = f"{filename}_{timestamp}"
    
    # Create a short hash
    hash_obj = hashlib.md5(unique_string.encode())
    return hash_obj.hexdigest()[:12]


def ensure_directories(*paths: Path) -> None:
    """
    Ensure all specified directories exist.
    
    Args:
        *paths: Variable number of Path objects to create
    """
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
