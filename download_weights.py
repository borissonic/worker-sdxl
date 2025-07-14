import os
import torch
import requests
from pathlib import Path
from diffusers import (
    StableDiffusionXLPipeline,
    StableDiffusionXLImg2ImgPipeline,
    AutoencoderKL,
)


def download_civitai_model(url, destination_path):
    """
    Downloads a model from CivitAI to the specified destination.
    """
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    
    print(f"Downloading model from {url} to {destination_path}")
    
    # Check for CivitAI API key in environment
    civitai_api_key = os.environ.get('CIVITAI_API_KEY')
    
    headers = {}
    if civitai_api_key:
        headers['Authorization'] = f'Bearer {civitai_api_key}'
        print("Using CivitAI API key for authentication")
    else:
        print("Warning: No CIVITAI_API_KEY found in environment. Download may fail if model requires authentication.")
    
    try:
        response = requests.get(url, headers=headers, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        block_size = 8192
        downloaded = 0
        
        with open(destination_path, 'wb') as file:
            for chunk in response.iter_content(chunk_size=block_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        progress = downloaded / total_size * 100
                        print(f"Download progress: {progress:.1f}%", end='\r')
        
        print(f"\nModel downloaded successfully to {destination_path}")
        return True
    except Exception as e:
        print(f"Error downloading model: {e}")
        return False


def fetch_pretrained_model(model_class, model_name, **kwargs):
    """
    Fetches a pretrained model from the HuggingFace model hub.
    """
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return model_class.from_pretrained(model_name, **kwargs)
        except OSError as err:
            if attempt < max_retries - 1:
                print(
                    f"Error encountered: {err}. Retrying attempt {attempt + 1} of {max_retries}..."
                )
            else:
                raise


def get_diffusion_pipelines():
    """
    Downloads the Pony Realism model from CivitAI and prepares the pipelines.
    """
    # Define paths for model storage
    model_dir = "/models"
    pony_model_path = os.path.join(model_dir, "pony_realism.safetensors")
    
    # Download Pony Realism model if not already present
    if not os.path.exists(pony_model_path):
        civitai_url = "https://civitai.com/api/download/models/1920896"
        download_civitai_model(civitai_url, pony_model_path)
    else:
        print(f"Pony Realism model already exists at {pony_model_path}")
    
    # Download VAE separately
    common_args = {
        "torch_dtype": torch.float16,
        "use_safetensors": True,
    }
    
    vae = fetch_pretrained_model(
        AutoencoderKL, "madebyollin/sdxl-vae-fp16-fix", **{"torch_dtype": torch.float16}
    )
    
    # Also download the refiner for compatibility
    refiner = fetch_pretrained_model(
        StableDiffusionXLImg2ImgPipeline,
        "stabilityai/stable-diffusion-xl-refiner-1.0",
        **common_args,
    )
    
    return pony_model_path, refiner, vae


if __name__ == "__main__":
    get_diffusion_pipelines()
