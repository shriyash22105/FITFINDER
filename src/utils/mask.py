import cv2
import numpy as np
from typing import Optional, Tuple
from PIL import Image

def generate_garment_mask(image_path: str) -> Optional[Image.Image]:
    """
    Generates a sophisticated mask from a clothing image using OpenCV.
    Employs thresholding and morphological operations to create a clean, 
    production-ready binary mask suitable for Stable Diffusion Inpainting.
    
    Args:
        image_path (str): The absolute path to the clothing image.
        
    Returns:
        Optional[Image.Image]: A PIL Image representing the generated mask, or None if failed.
    """
    try:
        # Load image via OpenCV
        img = cv2.imread(image_path)
        if img is None:
            raise FileNotFoundError(f"Image not found at {image_path}")
            
        # Convert to Grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian Blur to reduce high-frequency noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Otsu's thresholding for smart binarization
        _, thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Morphological operations to close holes in the garment mask
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        # Dilation to expand the mask slightly (useful for inpainting blending)
        dilated_mask = cv2.dilate(closed, kernel, iterations=1)
        
        # Convert back to PIL Image for Diffusers compatibility
        mask_pil = Image.fromarray(dilated_mask).convert("L")
        return mask_pil
        
    except Exception as e:
        import traceback
        print(f"[ERROR] Failed to generate garment mask: {str(e)}")
        traceback.print_exc()
        return None

def crop_and_pad(image: Image.Image, target_size: Tuple[int, int] = (512, 768)) -> Image.Image:
    """
    Standardizes image dimensions for Diffusion models without skewing aspect ratios.
    Args:
        image (Image.Image): Input PIL Image.
        target_size (tuple): Expected output (width, height) optimal for VTON.
    """
    width, height = image.size
    target_w, target_h = target_size
    
    aspect = width / float(height)
    target_aspect = target_w / float(target_h)
    
    if aspect > target_aspect:
        # Image is wider than target aspect ratio
        new_w = target_w
        new_h = int(target_w / aspect)
    else:
        # Image is taller than target aspect ratio
        new_h = target_h
        new_w = int(target_h * aspect)
        
    img_resized = image.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    # Create a padded background (white)
    new_image = Image.new("RGB", target_size, (255, 255, 255))
    paste_x = (target_w - new_w) // 2
    paste_y = (target_h - new_h) // 2
    new_image.paste(img_resized, (paste_x, paste_y))
    
    return new_image
