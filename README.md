# 🎥 VisionRAG - CCTV Video Q&A System (V1)

A prototype system that enables natural language question answering about CCTV/surveillance videos using Retrieval-Augmented Generation (RAG).

## 🌟 Overview

**VisionRAG** automatically:
1. Extracts frames from uploaded videos at configurable sampling rates
2. Generates natural language captions for each frame using BLIP
3. Stores captions in a vector database (ChromaDB)
4. Answers user questions by retrieving relevant frames and using an LLM

This is **Version 1** - a clean, working prototype designed to be easily extensible for V2 features like scene detection, event extraction, and cloud LLM support.

## 🏗️ Architecture

```
Video Upload → Frame Extraction (OpenCV)
              ↓
         BLIP Captioning
              ↓
    Embedding Generation (Ollama: nomic-embed-text)
              ↓
    Vector Storage (ChromaDB)
              ↓
User Question → RAG Retrieval → LLM Answer (Ollama: llama3:instruct)
```

## ✨ Features (V1)

- ✅ **Video Processing**: Upload MP4/AVI/MOV files and extract frames at fixed FPS
- ✅ **AI Captioning**: BLIP model generates descriptions for each frame
- ✅ **Vector Search**: ChromaDB for efficient semantic retrieval
- ✅ **Local LLM**: Ollama integration with llama3:instruct
- ✅ **Streamlit UI**: Clean, intuitive web interface
- ✅ **Grounded Answers**: LLM responses based only on retrieved frame captions
- ✅ **Transparency**: View retrieved frames and similarity scores

## 🚀 V2 Roadmap (Planned)

- 🔜 Scene-change detection for smarter frame sampling
- 🔜 Event detection and timeline generation
- 🔜 Cloud LLM support (OpenAI, Anthropic)
- 🔜 Multi-video comparison
- 🔜 Export capabilities (reports, highlights)

## 📋 Prerequisites

- **Python**: 3.10 or higher
- **Ollama**: Installed and running locally
  - Download from: https://ollama.ai/
  - Models required:
    - `llama3:instruct` (for Q&A)
    - `nomic-embed-text` (for embeddings)

## 🛠️ Installation

### 1. Clone/Download the Project

```bash
cd s:\CCTV
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**Windows (PowerShell):**
```bash
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
.\venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Setup Ollama

Install Ollama from https://ollama.ai/, then pull the required models:

```bash
ollama pull llama3:instruct
ollama pull nomic-embed-text
```

Ensure Ollama is running (it typically starts automatically after installation).

## 🎮 Usage

### 1. Start the Application

```bash
streamlit run app/main.py
```

The app will open in your browser at `http://localhost:8501`

### 2. Upload & Process Video

1. Click **"Upload Video"** in the sidebar
2. Select a video file (MP4, AVI, MOV)
3. Adjust **Frame Sampling Rate** (default: 1 fps)
   - Lower FPS = fewer frames = faster processing
   - Higher FPS = more frames = better temporal coverage
4. Click **"Process Video"**
5. Wait for processing to complete (progress bar shows status)

### 3. Ask Questions

Once processing is done:

1. Type your question in the text input
2. Adjust **Top K Results** if needed (how many frames to retrieve)
3. Click **"Get Answer"**
4. View the AI-generated answer
5. Expand **"Retrieved Frames & Evidence"** to see which frames were used

### Example Questions

- *"What is happening in the video?"*
- *"How many people appear in the footage?"*
- *"What time did someone enter the building?"*
- *"Describe the scene at 00:00:15"*
- *"Is there any vehicle visible?"*

## 📁 Project Structure

```
s:/CCTV/
├── app/
│   ├── main.py              # Streamlit application entry point
│   ├── config.py            # Configuration (paths, models, defaults)
│   ├── utils.py             # Helper functions (timestamps, IDs)
│   ├── llm_client.py        # Ollama HTTP client wrapper
│   ├── video_processing.py  # Frame extraction with OpenCV
│   ├── captioning.py        # BLIP image captioning
│   └── rag_pipeline.py      # ChromaDB vector storage & retrieval
├── data/
│   ├── videos/              # Uploaded video files
│   ├── frames/              # Extracted frames (optional)
│   └── chroma_db/           # ChromaDB persistent storage
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🔧 Configuration

Edit `app/config.py` to customize:

- Frame sampling defaults (FPS ranges)
- Top-K retrieval defaults
- Model names
- Ollama endpoint
- Data directory paths

## 🐛 Troubleshooting

### Ollama Connection Error

**Problem:** `Failed to connect to Ollama server`

**Solutions:**
- Ensure Ollama is installed and running
- Check if Ollama is accessible at `http://127.0.0.1:11434`
- Verify models are pulled: `ollama list`

### Model Not Found

**Problem:** `Embedding/LLM model not available`

**Solution:** Pull the required models:
```bash
ollama pull llama3:instruct
ollama pull nomic-embed-text
```

### Out of Memory

**Problem:** GPU/CPU runs out of memory during processing

**Solutions:**
- Reduce frame sampling rate (lower FPS)
- Process shorter videos
- If using GPU, ensure CUDA is properly installed
- Close other applications

### Slow Processing

**Problem:** Frame captioning is very slow

**Reasons:**
- BLIP model runs on CPU (slower than GPU)
- High FPS sampling creates many frames

**Solutions:**
- Use lower FPS (0.5 or 1.0)
- Ensure GPU is available if you have CUDA-capable hardware
- Process shorter video segments

## 💡 Tips for Best Results

1. **Start Small**: Test with short videos (10-30 seconds) first
2. **Adjust FPS**: Use 1 fps for general surveillance, 0.5 fps for slow-moving scenes
3. **Clear Questions**: Be specific in your questions for better answers
4. **Review Evidence**: Check the retrieved frames to verify answer quality
5. **GPU Acceleration**: If available, ensure PyTorch can use your GPU for faster captioning

## 🔬 Technical Details

### Models Used

- **Captioning**: `Salesforce/blip-image-captioning-base` (Hugging Face)
- **Embeddings**: `nomic-embed-text` via Ollama
- **LLM**: `llama3:instruct` via Ollama

### Data Flow

1. **Video → Frames**: OpenCV extracts frames at target FPS
2. **Frames → Captions**: BLIP generates natural language descriptions
3. **Captions → Embeddings**: nomic-embed-text creates vector representations
4. **Embeddings → Storage**: ChromaDB stores vectors + metadata
5. **Question → Retrieval**: User question embedded and matched against stored vectors
6. **Context → Answer**: Top-K frames + question sent to llama3:instruct

### Storage

- Videos stored in: `data/videos/`
- ChromaDB persisted in: `data/chroma_db/`
- Each frame stored with metadata: video_id, timestamp, caption, frame_index

## 📄 License

This is a prototype project for demonstration purposes.

## 🤝 Contributing (V2)

V2 will add:
- Scene detection algorithms
- Event timeline extraction
- Cloud LLM integration
- Multi-video analysis
- Export and reporting features

---

**Built with**: Python • Streamlit • OpenCV • BLIP • ChromaDB • Ollama

**Version**: 1.0.0 (Prototype)
