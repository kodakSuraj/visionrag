"""
Image Captioning Module for VisionRAG
BLIP model integration for generating captions from video frames.
"""

import numpy as np
from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
import config


def load_caption_model():
    """
    Load the BLIP image captioning model and processor.
    
    Returns:
        Tuple of (model, processor, device)
    """
    # Determine device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    
    print(f"Loading BLIP captioning model on {device}...")
    
    # Load processor and model (suppress slow processor warning)
    processor = BlipProcessor.from_pretrained(config.CAPTION_MODEL_NAME, use_fast=False)
    model = BlipForConditionalGeneration.from_pretrained(config.CAPTION_MODEL_NAME)
    
    # Move model to device
    model = model.to(device)
    model.eval()  # Set to evaluation mode
    
    print(f"BLIP model loaded successfully on {device}")
    
    return model, processor, device


def generate_caption(
    image: np.ndarray,
    model: BlipForConditionalGeneration,
    processor: BlipProcessor,
    device: str
) -> str:
    """
    Generate a caption for an image using BLIP model.
    
    Args:
        image: Image as NumPy array (BGR format from OpenCV)
        model: BLIP model instance
        processor: BLIP processor instance
        device: Device to run inference on ('cuda' or 'cpu')
        
    Returns:
        Generated caption as a string
    """
    # Convert BGR (OpenCV) to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image_rgb)
    
    # Process image
    inputs = processor(pil_image, return_tensors="pt").to(device)
    
    # Generate caption
    with torch.no_grad():
        outputs = model.generate(**inputs, max_length=50)
    
    # Decode caption
    caption = processor.decode(outputs[0], skip_special_tokens=True)
    
    return caption


# Need to import cv2 for color conversion
import cv2
