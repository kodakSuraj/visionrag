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
# Use environment variable for base URL if available (crucial for deployment)
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
OLLAMA_EMBEDDING_MODEL = os.getenv("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text")
OLLAMA_LLM_MODEL = os.getenv("OLLAMA_LLM_MODEL", "llama3:instruct")

# ChromaDB configuration
CHROMA_COLLECTION_NAME = "video_frames"

# Processing defaults
DEFAULT_FPS = 1.0
MIN_FPS = 0.2
MAX_FPS = 5.0

# RAG defaults
DEFAULT_TOP_K = 10  # Increased from 5 to provide more context
MIN_TOP_K = 3
MAX_TOP_K = 20

# LLM prompt template
SYSTEM_PROMPT_TEMPLATE = """You are an expert security analyst and video intelligence assistant.
Your task is to answer questions about a video based on the provided frame descriptions.

CONTEXT FROM VIDEO FRAMES:
{context}

INSTRUCTIONS:
1. Analyze the provided frame descriptions carefully.
2. Synthesize information across multiple frames to understand the sequence of events.
3. If the answer is explicitly found in the descriptions, provide a clear and concise answer.
4. If the answer can be inferred from the sequence of frames, explain your reasoning.
5. If the information is missing or ambiguous, state clearly what you know and what is unknown.
6. Do not hallucinate details not present in the descriptions.

User question: {question}

Answer:"""
