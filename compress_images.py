"""
Compress images for Overleaf upload
Reduces DPI and file size while maintaining quality
"""
from PIL import Image
import os

Image.MAX_IMAGE_PIXELS = None  # Remove limit for reading large images

input_dir = 'outputs'
output_dir = 'outputs_compressed'

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.endswith('.png'):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)
        
        print(f"Compressing {filename}...")
        
        # Open and resize to reasonable size
        img = Image.open(input_path)
        
        # Resize to max 2000 pixels on longest side (good for documents)
        max_size = 2000
        if max(img.size) > max_size:
            ratio = max_size / max(img.size)
            new_size = tuple(int(dim * ratio) for dim in img.size)
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            print(f"  Resized from {img.size} to {new_size}")
        
        # Save with compression
        img.save(output_path, 'PNG', optimize=True, compress_level=9)
        
        # Show file size reduction
        orig_size = os.path.getsize(input_path) / 1024 / 1024
        new_size = os.path.getsize(output_path) / 1024 / 1024
        print(f"  {orig_size:.2f}MB -> {new_size:.2f}MB ({(1-new_size/orig_size)*100:.1f}% reduction)")

print("\nDone! Upload images from 'outputs_compressed' folder to Overleaf")
