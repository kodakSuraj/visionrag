"""
Ollama Client for VisionRAG
HTTP client wrapper for interacting with local Ollama server.
"""

import requests
from typing import List, Dict, Any
import config


def check_ollama_available() -> bool:
    """
    Check if Ollama server is running and accessible.
    
    Returns:
        True if Ollama is available, False otherwise
    """
    try:
        response = requests.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False


def get_embedding(text: str) -> List[float]:
    """
    Generate embedding for text using Ollama's nomic-embed-text model.
    
    Args:
        text: Input text to embed
        
    Returns:
        List of floats representing the embedding vector
        
    Raises:
        requests.exceptions.RequestException: If Ollama server is unavailable
        ValueError: If embedding generation fails
    """
    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": config.OLLAMA_EMBEDDING_MODEL,
                "prompt": text
            },
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        if "embedding" not in result:
            raise ValueError("No embedding returned from Ollama")
            
        return result["embedding"]
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to connect to Ollama server at {config.OLLAMA_BASE_URL}. "
            f"Please ensure Ollama is running. Error: {str(e)}"
        )


def generate_answer(question: str, context: str) -> str:
    """
    Generate an answer to the question based on the provided context using Ollama's LLM.
    
    Args:
        question: User's question
        context: Retrieved frame descriptions formatted as context
        
    Returns:
        Generated answer as a string
        
    Raises:
        requests.exceptions.RequestException: If Ollama server is unavailable
        ValueError: If answer generation fails
    """
    # Format the full prompt using the template
    full_prompt = config.SYSTEM_PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )
    
    try:
        response = requests.post(
            f"{config.OLLAMA_BASE_URL}/api/generate",
            json={
                "model": config.OLLAMA_LLM_MODEL,
                "prompt": full_prompt,
                "stream": False
            },
            timeout=120  # LLM generation can take longer
        )
        response.raise_for_status()
        
        result = response.json()
        
        if "response" not in result:
            raise ValueError("No response returned from Ollama LLM")
            
        return result["response"].strip()
        
    except requests.exceptions.RequestException as e:
        raise requests.exceptions.RequestException(
            f"Failed to connect to Ollama server at {config.OLLAMA_BASE_URL}. "
            f"Please ensure Ollama is running with the {config.OLLAMA_LLM_MODEL} model. "
            f"Error: {str(e)}"
        )


def test_ollama_models() -> Dict[str, bool]:
    """
    Test if required Ollama models are available.
    
    Returns:
        Dictionary with model names as keys and availability as boolean values
    """
    results = {
        "server": check_ollama_available(),
        "embedding_model": False,
        "llm_model": False
    }
    
    if not results["server"]:
        return results
    
    try:
        # Test embedding model
        get_embedding("test")
        results["embedding_model"] = True
    except:
        pass
    
    try:
        # Test LLM model
        generate_answer("test question", "test context")
        results["llm_model"] = True
    except:
        pass
    
    return results
