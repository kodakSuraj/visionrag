"""
RAG Pipeline Module for VisionRAG
ChromaDB integration for storing and retrieving frame captions.
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Callable, Any
import config


def init_chroma_collection() -> chromadb.Collection:
    """
    Initialize ChromaDB client and get/create the video frames collection.
    
    Returns:
        ChromaDB Collection instance
    """
    # Create persistent client
    client = chromadb.PersistentClient(
        path=str(config.CHROMA_DB_DIR),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    
    # Get or create collection
    collection = client.get_or_create_collection(
        name=config.CHROMA_COLLECTION_NAME,
        metadata={"description": "Video frame captions for CCTV Q&A"}
    )
    
    return collection


def index_video_frames(
    collection: chromadb.Collection,
    video_id: str,
    frame_records: List[Dict],
    embeddings_fn: Callable[[str], List[float]]
) -> int:
    """
    Index video frames into ChromaDB.
    
    Args:
        collection: ChromaDB collection instance
        video_id: Unique video identifier
        frame_records: List of frame records, each containing:
            - frame_index: int
            - timestamp_seconds: float
            - timestamp_str: str
            - caption: str
        embeddings_fn: Function to generate embeddings from text
        
    Returns:
        Number of frames indexed
    """
    if not frame_records:
        return 0
    
    ids = []
    documents = []
    embeddings = []
    metadatas = []
    
    for record in frame_records:
        # Create unique ID
        frame_id = f"{video_id}_{record['frame_index']}"
        
        # Create document text
        document = (
            f"Video {video_id}, time {record['timestamp_str']}: "
            f"{record['caption']}"
        )
        
        # Generate embedding
        embedding = embeddings_fn(document)
        
        # Create metadata
        metadata = {
            "video_id": video_id,
            "frame_index": record['frame_index'],
            "timestamp_seconds": record['timestamp_seconds'],
            "timestamp_str": record['timestamp_str'],
            "caption": record['caption']
        }
        
        ids.append(frame_id)
        documents.append(document)
        embeddings.append(embedding)
        metadatas.append(metadata)
    
    # Add to collection
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    return len(ids)


def query_video(
    collection: chromadb.Collection,
    video_id: str,
    question: str,
    top_k: int,
    embeddings_fn: Callable[[str], List[float]]
) -> List[Dict[str, Any]]:
    """
    Query the video frames collection for relevant frames.
    
    Args:
        collection: ChromaDB collection instance
        video_id: Video identifier to filter results
        question: User's question
        top_k: Number of results to retrieve
        embeddings_fn: Function to generate embeddings from text
        
    Returns:
        List of dictionaries with:
            - caption: str
            - timestamp_str: str
            - timestamp_seconds: float
            - frame_index: int
            - distance: float (lower is more similar)
    """
    # Generate question embedding
    query_embedding = embeddings_fn(question)
    
    # Query collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"video_id": video_id}  # Filter by video_id
    )
    
    # Format results
    formatted_results = []
    
    if results['metadatas'] and len(results['metadatas'][0]) > 0:
        for i, metadata in enumerate(results['metadatas'][0]):
            distance = results['distances'][0][i] if results['distances'] else 0.0
            
            formatted_results.append({
                "caption": metadata['caption'],
                "timestamp_str": metadata['timestamp_str'],
                "timestamp_seconds": metadata['timestamp_seconds'],
                "frame_index": metadata['frame_index'],
                "distance": distance,
                "similarity_score": 1 / (1 + distance)  # Convert distance to similarity
            })
    
    return formatted_results


def delete_video_frames(collection: chromadb.Collection, video_id: str) -> int:
    """
    Delete all frames for a specific video from the collection.
    
    Args:
        collection: ChromaDB collection instance
        video_id: Video identifier
        
    Returns:
        Number of frames deleted
    """
    # Get all IDs for this video
    results = collection.get(
        where={"video_id": video_id}
    )
    
    if results['ids']:
        collection.delete(ids=results['ids'])
        return len(results['ids'])
    
    return 0


def get_collection_stats(collection: chromadb.Collection) -> Dict[str, Any]:
    """
    Get statistics about the collection.
    
    Returns:
        Dictionary with collection statistics
    """
    count = collection.count()
    
    return {
        "total_frames": count,
        "collection_name": collection.name
    }
