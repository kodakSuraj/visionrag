"""
VisionRAG Configuration
Central configuration for paths, model names, and API endpoints.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
VIDEOS_DIR = DATA_DIR / "videos"
FRAMES_DIR = DATA_DIR / "frames"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"

# Ensure directories exist
for dir_path in [DATA_DIR, VIDEOS_DIR, FRAMES_DIR, CHROMA_DB_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# Model configurations
CAPTION_MODEL_NAME = "Salesforce/blip-image-captioning-base"

# Ollama configurations
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_EMBEDDING_MODEL = "nomic-embed-text"
OLLAMA_LLM_MODEL = "llama3:instruct"

# ChromaDB configuration
CHROMA_COLLECTION_NAME = "video_frames"

# Processing defaults
DEFAULT_FPS = 1.0
MIN_FPS = 0.2
MAX_FPS = 5.0

# RAG defaults
DEFAULT_TOP_K = 5
MIN_TOP_K = 3
MAX_TOP_K = 10

# LLM prompt template
SYSTEM_PROMPT_TEMPLATE = """You are an assistant that answers questions about a CCTV-like video.

Here are descriptions of frames retrieved as relevant:

{context}

Answer the user's question based only on these descriptions. If the answer is not clearly present in the context, say that you don't know.

User question: {question}

Answer:"""
