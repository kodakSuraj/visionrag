# 🚀 Quick Start Guide - VisionRAG

## ✅ What's Complete

Your VisionRAG V1 application is fully implemented and ready to use! Here's what you have:

### 📦 Application Files (7 modules)
- ✓ `app/main.py` - Full Streamlit UI (450+ lines)
- ✓ `app/config.py` - Configuration management  
- ✓ `app/utils.py` - Helper functions
- ✓ `app/llm_client.py` - Ollama HTTP client
- ✓ `app/video_processing.py` - Frame extraction
- ✓ `app/captioning.py` - BLIP integration
- ✓ `app/rag_pipeline.py` - ChromaDB operations

### 📄 Documentation & Scripts
- ✓ `README.md` - Complete documentation (300+ lines)
- ✓ `requirements.txt` - All dependencies
- ✓ `.gitignore` - Git configuration
- ✓ `setup.ps1` - Automated setup script
- ✓ `run.ps1` - Quick launch (PowerShell)
- ✓ `run.bat` - Quick launch (Batch)

### 🔧 Environment Setup
- ✓ Virtual environment created (`venv/`)
- ✓ All dependencies installed
- ✓ Git repository initialized
- ✓ Initial commits made

## 🎯 Next Steps

### 1. Ensure Ollama is Running

VisionRAG requires Ollama with two models. Check if you have them:

```powershell
# Check Ollama is running
ollama list

# If models are missing, pull them:
ollama pull llama3:instruct
ollama pull nomic-embed-text
```

### 2. Start the Application

**Option A - Quick Launch:**
```powershell
.\run.ps1
```

**Option B - Manual Launch:**
```powershell
.\venv\Scripts\Activate.ps1
streamlit run app/main.py
```

The app will open at: **http://localhost:8501**

### 3. Test with a Sample Video

1. **Upload**: Click "Upload Video" in the sidebar
2. **Configure**: Set FPS to 1.0 (good default)
3. **Process**: Click "Process Video"
4. **Wait**: Processing takes a few minutes depending on video length
5. **Ask**: Type a question like "What is happening in the video?"
6. **Review**: Check the answer and retrieved frames

## 💡 Usage Tips

### Best Practices
- Start with **short videos** (10-30 seconds) for testing
- Use **1.0 FPS** for general surveillance footage
- Use **0.5 FPS** for slow-moving scenes
- Use **2-3 FPS** for fast action or detailed analysis

### Good Questions to Ask
- "What is happening in the video?"
- "How many people appear?"
- "What time did [event] occur?"
- "Describe the scene at [timestamp]"
- "Is there a [object/person] visible?"

## 🔍 System Requirements

### Before Running, Ensure:

1. **Python 3.10+** is installed
2. **Ollama** is installed and running
3. **Models are pulled**:
   - `llama3:instruct` (for Q&A, ~4.7 GB)
   - `nomic-embed-text` (for embeddings, ~274 MB)
4. **Virtual environment** is activated
5. **Dependencies** are installed (already done)

### Hardware Recommendations
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space (for models + videos)
- **GPU**: Optional but recommended for faster captioning
  - CUDA-capable NVIDIA GPU automatically detected
  - CPU-only works but slower for BLIP model

## 🐛 Troubleshooting

### "Ollama server is not running"
**Solution**: Start Ollama - it should auto-start after installation, or run `ollama serve`

### "Model not available"
**Solution**: Pull the models:
```powershell
ollama pull llama3:instruct
ollama pull nomic-embed-text
```

### Slow Processing
**Causes**:
- Running on CPU (normal - BLIP is compute-intensive)
- High FPS setting (more frames = more time)
- Long video

**Solutions**:
- Reduce FPS to 0.5-1.0
- Use shorter videos for testing
- Enable GPU if available

### Import Errors
**Solution**: Ensure venv is activated and dependencies installed:
```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 📊 What to Expect

### Processing Time (Estimates)
| Video Length | FPS | Frames | Processing Time (CPU) |
|--------------|-----|--------|----------------------|
| 10 seconds   | 1.0 | 10     | ~30-60 seconds       |
| 30 seconds   | 1.0 | 30     | ~1-2 minutes         |
| 1 minute     | 1.0 | 60     | ~2-4 minutes         |

*GPU processing is 5-10x faster*

### Q&A Response Time
- Query embedding: ~1 second
- Vector search: <1 second  
- LLM answer generation: ~2-5 seconds
- **Total**: ~3-7 seconds per question

## 🎨 Features to Try

1. **Multiple Questions**: Ask different questions about the same video
2. **Temporal Queries**: Ask about specific time ranges
3. **Object Detection**: Ask "Is there a car/person/object?"
4. **Counting**: Ask "How many people appear?"
5. **Description**: Ask "What is happening at 00:00:15?"

## 📈 Future (V2)

Coming in V2:
- Scene-change detection (smarter frame sampling)
- Event timeline generation
- Cloud LLM support (OpenAI, Anthropic)
- Multi-video comparison
- Export reports and highlights

## 🔗 Git Repository

Your project is version controlled:
```bash
git status        # Check status
git log           # View commits
git add .         # Stage changes
git commit -m ""  # Commit changes
```

To push to GitHub:
```bash
# Create a new repository on GitHub, then:
git remote add origin https://github.com/yourusername/visionrag.git
git push -u origin main
```

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Implementation Details**: See walkthrough artifact
- **Code Comments**: All files have detailed docstrings

## ✨ You're Ready!

Everything is set up and ready to go. Just run `.\run.ps1` and start analyzing videos!

---

**Questions?** Check the comprehensive `README.md` for detailed guidance.

**Issues?** Review the troubleshooting section above or check Ollama/model status.

Happy analyzing! 🎥🔍
