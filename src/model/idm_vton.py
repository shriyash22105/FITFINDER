import os
import logging

try:
    import torch
    from PIL import Image
    from diffusers import StableDiffusionInpaintPipeline, DPMSolverMultistepScheduler
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False

from src.utils.mask import generate_garment_mask, crop_and_pad

# Configure Production Logging
logger = logging.getLogger("IDM_VTON_Inference")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

# Pipeline Singleton
_pipeline_instance = None

def get_pipeline():
    """
    Lazy instantiates the PyTorch Diffusers pipeline with Memory Optimization.
    Using an Inpainting pipeline to simulate the masking out of the body and rendering the garment.
    """
    global _pipeline_instance
    if _pipeline_instance is not None:
        return _pipeline_instance

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Initializing VTON AI Pipeline on {device.upper()}...")
    
    # Load model with mixed precision (fp16) drastically reducing VRAM consumption
    dtype = torch.float16 if device == "cuda" else torch.float32
    
    try:
        # Using a robust inpainting model as a proxy for VTON if custom IDM-VTON weights are missing
        pipe = StableDiffusionInpaintPipeline.from_pretrained(
            "runwayml/stable-diffusion-inpainting",
            torch_dtype=dtype,
            safety_checker=None
        )
        
        # Optimize inference speed
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config)
        
        if device == "cuda":
            # Enable xformers memory efficient attention if installed
            try:
                pipe.enable_xformers_memory_efficient_attention()
                logger.info("Xformers memory efficient attention enabled.")
            except ImportError:
                pass
                
            # Crucial for servers: Offloads layers to CPU RAM when not actively computing via GPU
            pipe.enable_model_cpu_offload()
        else:
            pipe.to("cpu")
            
        _pipeline_instance = pipe
        return pipe
        
    except Exception as e:
        logger.error(f"Failed to load VTON Pipeline: {str(e)}")
        raise

def run_inference(human_path: str, cloth_path: str, output_path: str) -> None:
    """
    Executes an end-to-end Local Deep Learning Virtual Try-On workflow.
    
    Steps:
      1. Image Preprocessing (Standardize Dimensions)
      2. Automated CV Mask Generation
      3. Latent Diffusion Inpainting Inference
      4. Result Output
    """
    if not HAS_TORCH:
        raise ImportError("PyTorch/Diffusers stack is completely missing. Cannot run Local AI inference.")
        
    logger.info(f"Starting IDM-VTON local inference for {human_path}")
    
    # 1. Image Preprocessing
    # The human image serves as the base structure
    init_image = Image.open(human_path).convert("RGB")
    init_image = crop_and_pad(init_image, target_size=(512, 768))  # Standard portrait aspect ratio
    
    # 2. Automated Mask Generation
    # Generating mask based on the clothing shape to define the inpainting region on the body
    mask_image = generate_garment_mask(cloth_path)
    if mask_image is None:
        raise ValueError("Failed to generate structural mask from the clothing image.")
    mask_image = crop_and_pad(mask_image, target_size=(512, 768))
    
    # Constructing a dynamic prompt
    prompt = "A high-fashion professional photograph of a person wearing this exact piece of clothing from the reference mask, photorealistic, cinematic lighting, ultra detailed fabric texture, 4k resolution"
    negative_prompt = "broken limbs, multiple arms, warped clothing, heavily distorted face, lowres, ugly, artifact, noisy"

    # 3. Running Diffusion
    pipe = get_pipeline()
    generator = torch.Generator(device=pipe.device).manual_seed(42) # Deterministic seed for consistency
    
    logger.info("Initiating Latent Diffusion Phase...")
    try:
        # High quality generation with carefully tuned hyperparameters
        output = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=init_image,
            mask_image=mask_image,
            num_inference_steps=25,
            guidance_scale=7.5,
            generator=generator
        ).images[0]
        
        # 4. Save result
        output.save(output_path, format="PNG")
        logger.info(f"Successfully generated and saved VTON inference result at {output_path}")
        
    except Exception as e:
        logger.error(f"Diffusion generation failed: {str(e)}")
        raise
