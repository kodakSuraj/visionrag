"""
Scene Detection Module
Uses CLIP embeddings and K-Means clustering to identify distinct semantic scenes in a video.
"""

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
import streamlit as st

class SceneDetector:
    def __init__(self, model_id="openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading CLIP model on {self.device}...")
        
        try:
            self.model = CLIPModel.from_pretrained(model_id).to(self.device)
            self.processor = CLIPProcessor.from_pretrained(model_id)
        except Exception as e:
            print(f"Error loading CLIP model: {e}")
            raise

    def extract_keyframes(self, video_path, num_clusters=15, sample_rate=1.0):
        """
        Extract keyframes that represent distinct scenes.
        
        Args:
            video_path: Path to video file
            num_clusters: Number of distinct scenes to find
            sample_rate: FPS to sample for analysis (higher = more precise but slower)
            
        Returns:
            List of dicts containing 'frame', 'timestamp', 'frame_index'
        """
        # 1. Extract raw frames for analysis
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Calculate interval
        interval = int(fps / sample_rate) if sample_rate < fps else 1
        
        frames_buffer = []
        timestamps = []
        frame_indices = []
        
        print(f"Analyzing video at {sample_rate} FPS...")
        
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            if count % interval == 0:
                # Convert BGR to RGB for CLIP
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frames_buffer.append(Image.fromarray(frame_rgb))
                timestamps.append(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000.0)
                frame_indices.append(count)
                
            count += 1
            
        cap.release()
        
        if not frames_buffer:
            return []
            
        # 2. Generate Embeddings
        print(f"Generating embeddings for {len(frames_buffer)} frames...")
        embeddings = self._get_embeddings(frames_buffer)
        
        # 3. Cluster
        # Adjust clusters if video is short
        actual_clusters = min(num_clusters, len(frames_buffer))
        if actual_clusters < 1:
            actual_clusters = 1
            
        print(f"Clustering into {actual_clusters} scenes...")
        kmeans = KMeans(n_clusters=actual_clusters, random_state=42, n_init=10)
        kmeans.fit(embeddings)
        
        # 4. Select Keyframes (closest to cluster centers)
        closest_indices, _ = pairwise_distances_argmin_min(kmeans.cluster_centers_, embeddings)
        selected_indices = sorted(closest_indices)
        
        # 5. Format Output
        keyframes = []
        for idx in selected_indices:
            # We need to convert PIL back to OpenCV BGR for the rest of the pipeline
            pil_img = frames_buffer[idx]
            opencv_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
            
            keyframes.append({
                'frame': opencv_img,
                'timestamp_seconds': timestamps[idx],
                'timestamp_str': self._format_timestamp(timestamps[idx]),
                'frame_index': frame_indices[idx],
                'type': 'visual'
            })
            
        return keyframes

    def _get_embeddings(self, frames, batch_size=32):
        """Generate CLIP embeddings for frames."""
        embeddings = []
        
        for i in range(0, len(frames), batch_size):
            batch = frames[i:i+batch_size]
            inputs = self.processor(images=batch, return_tensors="pt", padding=True).to(self.device)
            
            with torch.no_grad():
                embeds = self.model.get_image_features(**inputs)
                # Normalize
                embeds = embeds / embeds.norm(p=2, dim=-1, keepdim=True)
                embeddings.append(embeds.cpu().numpy())
                
        return np.vstack(embeddings)

    @staticmethod
    def _format_timestamp(seconds):
        """Convert seconds to HH:MM:SS format."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
