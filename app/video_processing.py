"""
Video Processing Module for VisionRAG
Handles video upload, frame extraction, and timestamp management.
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple
import config
import utils


def save_uploaded_video(uploaded_file, video_id: str) -> str:
    """
    Save an uploaded video file to disk.
    
    Args:
        uploaded_file: Streamlit UploadedFile object
        video_id: Unique identifier for the video
        
    Returns:
        Path to saved video file as string
    """
    # Get file extension from original filename
    original_filename = uploaded_file.name
    extension = Path(original_filename).suffix
    
    # Create video filename
    video_filename = f"{video_id}{extension}"
    video_path = config.VIDEOS_DIR / video_filename
    
    # Save the file
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return str(video_path)


def get_video_info(video_path: str) -> Dict[str, any]:
    """
    Get basic information about a video file.
    
    Args:
        video_path: Path to video file
        
    Returns:
        Dictionary with video metadata (fps, frame_count, duration, width, height)
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    duration = frame_count / fps if fps > 0 else 0
    
    cap.release()
    
    return {
        "fps": fps,
        "frame_count": frame_count,
        "duration": duration,
        "width": width,
        "height": height
    }


def extract_frames(video_path: str, target_fps: float = 1.0) -> List[Dict]:
    """
    Extract frames from video at a specified sampling rate.
    
    Args:
        video_path: Path to video file
        target_fps: Target frames per second for extraction (default: 1.0)
        
    Returns:
        List of dictionaries, each containing:
            - frame_index: Sequential frame number
            - timestamp_seconds: Timestamp in seconds
            - timestamp_str: Formatted timestamp (HH:MM:SS)
            - frame: NumPy array (BGR format)
            
    Raises:
        ValueError: If video cannot be opened
    """
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise ValueError(f"Could not open video file: {video_path}")
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Calculate frame interval
    # If target_fps is 1.0 and video is 30fps, we take every 30th frame
    frame_interval = int(video_fps / target_fps) if target_fps > 0 else 1
    frame_interval = max(1, frame_interval)  # At least 1
    
    extracted_frames = []
    frame_idx = 0
    actual_frame_number = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Check if this frame should be extracted
        if actual_frame_number % frame_interval == 0:
            timestamp_seconds = actual_frame_number / video_fps
            timestamp_str = utils.format_timestamp(timestamp_seconds)
            
            extracted_frames.append({
                "frame_index": frame_idx,
                "timestamp_seconds": timestamp_seconds,
                "timestamp_str": timestamp_str,
                "frame": frame.copy()  # Copy to avoid reference issues
            })
            
            frame_idx += 1
        
        actual_frame_number += 1
    
    cap.release()
    
    # TODO V2: Add scene-change detection mode here
    # This would analyze consecutive frames and extract only when
    # significant visual changes are detected, reducing redundant frames
    
    return extracted_frames


def save_frame_image(frame: np.ndarray, video_id: str, frame_index: int) -> str:
    """
    Save a frame as an image file (optional utility for debugging/visualization).
    
    Args:
        frame: Frame as NumPy array (BGR)
        video_id: Video identifier
        frame_index: Frame index
        
    Returns:
        Path to saved image
    """
    # Create video-specific folder
    video_frames_dir = config.FRAMES_DIR / video_id
    video_frames_dir.mkdir(parents=True, exist_ok=True)
    
    # Save frame
    frame_filename = f"frame_{frame_index:06d}.jpg"
    frame_path = video_frames_dir / frame_filename
    
    cv2.imwrite(str(frame_path), frame)
    
    return str(frame_path)
