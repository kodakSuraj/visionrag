"""
Audio Processing Module
Uses OpenAI Whisper to transcribe audio from video files.
"""

import whisper
import os
import torch
try:
    from moviepy.editor import VideoFileClip
except ImportError:
    try:
        # MoviePy v2.0+
        from moviepy.video.io.VideoFileClip import VideoFileClip
    except ImportError:
        # Fallback or re-raise
        from moviepy import VideoFileClip

class AudioProcessor:
    def __init__(self, model_size="base"):
        # Whisper runs well on CPU, but use CUDA if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Loading Whisper model ({model_size}) on {self.device}...")
        
        try:
            self.model = whisper.load_model(model_size, device=self.device)
        except Exception as e:
            print(f"Error loading Whisper model: {e}")
            raise

    def process_video(self, video_path):
        """
        Extract and transcribe audio from video.
        
        Returns:
            List of dicts containing 'text', 'start', 'end', 'timestamp_str'
        """
        # 1. Extract Audio
        audio_path = str(video_path).replace(os.path.splitext(video_path)[1], ".mp3")
        
        try:
            print(f"Extracting audio from {video_path}...")
            video = VideoFileClip(str(video_path))
            
            if video.audio is None:
                print("No audio track found.")
                return []
                
            video.audio.write_audiofile(audio_path, verbose=False, logger=None)
            video.close()
            
        except Exception as e:
            print(f"Error extracting audio: {e}")
            return []
            
        # 2. Transcribe
        if not os.path.exists(audio_path):
            return []
            
        print("Transcribing audio...")
        try:
            result = self.model.transcribe(audio_path)
            
            segments = []
            for segment in result["segments"]:
                start = segment["start"]
                text = segment["text"].strip()
                
                if not text:
                    continue
                    
                segments.append({
                    'caption': f"[AUDIO TRANSCRIPT] {text}",
                    'timestamp_seconds': start,
                    'timestamp_str': self._format_timestamp(start),
                    'frame_index': -1, # Special index for audio
                    'type': 'audio'
                })
                
            # Cleanup
            try:
                os.remove(audio_path)
            except:
                pass
                
            return segments
            
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return []

    @staticmethod
    def _format_timestamp(seconds):
        """Convert seconds to HH:MM:SS format."""
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
