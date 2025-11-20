"""
VisionRAG - CCTV Video Q&A System (V1)
Main Streamlit application
"""

import streamlit as st
from pathlib import Path
import sys

# Add app directory to path
app_dir = Path(__file__).parent
sys.path.insert(0, str(app_dir))

import config
import utils
import llm_client
import video_processing
import captioning
import rag_pipeline


# Page configuration
st.set_page_config(
    page_title="VisionRAG - CCTV Q&A",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_models():
    """Load and cache the captioning model."""
    try:
        model, processor, device = captioning.load_caption_model()
        return model, processor, device
    except Exception as e:
        st.error(f"Failed to load captioning model: {str(e)}")
        return None, None, None


@st.cache_resource
def init_chroma():
    """Initialize and cache ChromaDB collection."""
    try:
        collection = rag_pipeline.init_chroma_collection()
        return collection
    except Exception as e:
        st.error(f"Failed to initialize ChromaDB: {str(e)}")
        return None


def check_system_ready():
    """Check if all required systems are available."""
    issues = []
    
    # Check Ollama
    if not llm_client.check_ollama_available():
        issues.append("⚠️ Ollama server is not running. Please start Ollama and ensure models are pulled.")
    
    # Test models
    model_status = llm_client.test_ollama_models()
    if not model_status.get("embedding_model"):
        issues.append(f"⚠️ Embedding model '{config.OLLAMA_EMBEDDING_MODEL}' not available. Run: `ollama pull {config.OLLAMA_EMBEDDING_MODEL}`")
    if not model_status.get("llm_model"):
        issues.append(f"⚠️ LLM model '{config.OLLAMA_LLM_MODEL}' not available. Run: `ollama pull {config.OLLAMA_LLM_MODEL}`")
    
    return issues


def process_video_pipeline(uploaded_file, video_id, target_fps, model, processor, device, collection):
    """Complete video processing pipeline."""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Save video
        status_text.text("📁 Saving video...")
        progress_bar.progress(10)
        video_path = video_processing.save_uploaded_video(uploaded_file, video_id)
        
        # Get video info
        video_info = video_processing.get_video_info(video_path)
        
        # Step 2: Extract frames
        status_text.text("🎞️ Extracting frames...")
        progress_bar.progress(20)
        frames = video_processing.extract_frames(video_path, target_fps)
        
        if not frames:
            st.error("No frames could be extracted from the video.")
            return None
        
        # Step 3: Generate captions
        status_text.text(f"🖼️ Generating captions for {len(frames)} frames...")
        frame_records = []
        
        for idx, frame_data in enumerate(frames):
            # Update progress
            caption_progress = 20 + int((idx / len(frames)) * 50)
            progress_bar.progress(caption_progress)
            status_text.text(f"🖼️ Captioning frame {idx + 1}/{len(frames)}...")
            
            # Generate caption
            caption = captioning.generate_caption(
                frame_data['frame'],
                model,
                processor,
                device
            )
            
            frame_records.append({
                'frame_index': frame_data['frame_index'],
                'timestamp_seconds': frame_data['timestamp_seconds'],
                'timestamp_str': frame_data['timestamp_str'],
                'caption': caption
            })
        
        # Step 4: Index in ChromaDB
        status_text.text("💾 Indexing captions in vector database...")
        progress_bar.progress(80)
        
        num_indexed = rag_pipeline.index_video_frames(
            collection,
            video_id,
            frame_records,
            llm_client.get_embedding
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Processing complete!")
        
        # Return summary
        return {
            'video_id': video_id,
            'num_frames': len(frames),
            'fps': target_fps,
            'duration': video_info['duration'],
            'video_info': video_info,
            'num_indexed': num_indexed
        }
        
    except Exception as e:
        st.error(f"Error during processing: {str(e)}")
        return None


def main():
    """Main application."""
    
    # Title
    st.title("🎥 VisionRAG - CCTV Q&A Prototype")
    st.markdown("*V1: Video Frame Analysis with RAG-based Question Answering*")
    
    # Initialize session state
    if 'processed_video' not in st.session_state:
        st.session_state.processed_video = None
    
    # Check system readiness
    system_issues = check_system_ready()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # System status
        with st.expander("🔍 System Status", expanded=bool(system_issues)):
            if system_issues:
                for issue in system_issues:
                    st.warning(issue)
            else:
                st.success("✅ All systems ready!")
        
        st.divider()
        
        # Video Input & Processing
        st.subheader("📹 Video Input & Processing")
        
        uploaded_file = st.file_uploader(
            "Upload Video",
            type=['mp4', 'avi', 'mov', 'mkv'],
            help="Upload a CCTV or surveillance video for analysis"
        )
        
        target_fps = st.slider(
            "Frame Sampling Rate (FPS)",
            min_value=config.MIN_FPS,
            max_value=config.MAX_FPS,
            value=config.DEFAULT_FPS,
            step=0.1,
            help="How many frames to extract per second (lower = fewer frames)"
        )
        
        sampling_mode = st.radio(
            "Frame Sampling Mode",
            options=["Fixed FPS (V1 - Active)", "Scene Detection (V2 - Coming Soon)"],
            index=0,
            help="V1 uses fixed FPS sampling. Scene detection will be added in V2."
        )
        
        if sampling_mode != "Fixed FPS (V1 - Active)":
            st.info("🚧 Scene detection will be available in V2")
        
        process_button = st.button(
            "🚀 Process Video",
            type="primary",
            disabled=(uploaded_file is None or bool(system_issues)),
            use_container_width=True
        )
        
        st.divider()
        
        # Model Settings
        st.subheader("🤖 Model Settings")
        
        st.markdown(f"""
        **Captioning:** `{config.CAPTION_MODEL_NAME.split('/')[-1]}`  
        **Embeddings:** `{config.OLLAMA_EMBEDDING_MODEL}`  
        **LLM:** `{config.OLLAMA_LLM_MODEL}`
        """)
        
        st.info("💡 Cloud LLM support (OpenAI, Anthropic) planned for V2")
    
    # Main area
    if process_button and uploaded_file:
        # Load models
        model, processor, device = load_models()
        collection = init_chroma()
        
        if model is None or collection is None:
            st.error("Failed to load required models. Please check the system status.")
            return
        
        # Generate video ID
        video_id = utils.get_video_id(uploaded_file.name)
        
        # Process video
        st.subheader("⚙️ Processing Video")
        result = process_video_pipeline(
            uploaded_file,
            video_id,
            target_fps,
            model,
            processor,
            device,
            collection
        )
        
        if result:
            st.session_state.processed_video = result
            st.success("✅ Video processed successfully!")
            
            # Show summary
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Frames Extracted", result['num_frames'])
            with col2:
                st.metric("Video Duration", f"{result['duration']:.1f}s")
            with col3:
                st.metric("Sampling Rate", f"{result['fps']} fps")
            
            st.balloons()
    
    # Q&A Interface
    if st.session_state.processed_video:
        st.divider()
        st.subheader("💬 Ask Questions About the Video")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            question = st.text_input(
                "Your Question",
                placeholder="e.g., What is happening in the video? Who appears in the footage?",
                label_visibility="collapsed"
            )
        
        with col2:
            top_k = st.slider(
                "Top K Results",
                min_value=config.MIN_TOP_K,
                max_value=config.MAX_TOP_K,
                value=config.DEFAULT_TOP_K,
                help="Number of most relevant frames to retrieve"
            )
        
        ask_button = st.button("🔍 Get Answer", type="primary", disabled=not question)
        
        if ask_button and question:
            collection = init_chroma()
            video_id = st.session_state.processed_video['video_id']
            
            with st.spinner("🤔 Analyzing video and generating answer..."):
                try:
                    # Retrieve relevant frames
                    results = rag_pipeline.query_video(
                        collection,
                        video_id,
                        question,
                        top_k,
                        llm_client.get_embedding
                    )
                    
                    if not results:
                        st.warning("No relevant frames found for your question.")
                        return
                    
                    # Format context for LLM
                    context_parts = []
                    for i, result in enumerate(results, 1):
                        context_parts.append(
                            f"[Frame {i}] time={result['timestamp_str']}\n"
                            f"caption: {result['caption']}"
                        )
                    context = "\n\n".join(context_parts)
                    
                    # Generate answer
                    answer = llm_client.generate_answer(question, context)
                    
                    # Display answer
                    st.markdown("### 🎯 Answer")
                    st.info(answer)
                    
                    # Display retrieved frames
                    with st.expander("📊 Retrieved Frames & Evidence", expanded=True):
                        st.markdown("*Frames used to generate the answer:*")
                        
                        # Create table
                        import pandas as pd
                        df = pd.DataFrame([
                            {
                                "Frame #": r['frame_index'],
                                "Timestamp": r['timestamp_str'],
                                "Caption": r['caption'],
                                "Similarity": f"{r['similarity_score']:.3f}"
                            }
                            for r in results
                        ])
                        
                        st.dataframe(df, use_container_width=True, hide_index=True)
                
                except Exception as e:
                    st.error(f"Error generating answer: {str(e)}")
    
    else:
        # Instructions when no video processed
        st.info("""
        ### 👋 Welcome to VisionRAG!
        
        **Get started in 3 steps:**
        
        1. 📤 **Upload a video** using the sidebar
        2. ⚙️ **Configure settings** (FPS, sampling mode)
        3. 🚀 **Click "Process Video"** to analyze
        
        Once processed, you can ask natural language questions about the video content!
        """)
        
        # Show example questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - *"What is happening in the video?"*
            - *"How many people appear in the footage?"*
            - *"What time did someone enter the building?"*
            - *"Describe the activities between 00:00:10 and 00:00:20"*
            - *"Is there any suspicious activity?"*
            """)


if __name__ == "__main__":
    main()
