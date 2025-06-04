#!/usr/bin/env python3
from PIL import Image
import sys
import os

def create_mosaic_preview(input_path, output_path=None):
    """
    Create a pixelated preview of an image for a 67x42 tile mosaic
    """
    # Mosaic dimensions (in tiles/pixels)
    MOSAIC_WIDTH = 42
    MOSAIC_HEIGHT = 67
    
    # Open the input image
    img = Image.open(input_path)
    
    # Convert to RGB if necessary (handles PNG transparency, etc.)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to mosaic dimensions using LANCZOS for better quality
    pixelated = img.resize((MOSAIC_WIDTH, MOSAIC_HEIGHT), Image.Resampling.LANCZOS)
    
    # Scale back up for viewing (each pixel becomes a visible square)
    # Using nearest neighbor to maintain hard edges
    preview_size = (MOSAIC_WIDTH * 10, MOSAIC_HEIGHT * 10)  # 10x scale for viewing
    preview = pixelated.resize(preview_size, Image.Resampling.NEAREST)
    
    # Generate output filename if not provided
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_mosaic_preview.png"
    
    # Save the preview
    preview.save(output_path)
    
    # Also save the actual pixel-perfect version
    pixel_perfect_path = output_path.replace('.png', '_exact.png')
    pixelated.save(pixel_perfect_path)
    
    print(f"Mosaic preview saved to: {output_path}")
    print(f"Exact pixel version saved to: {pixel_perfect_path}")
    print(f"Mosaic dimensions: {MOSAIC_WIDTH} x {MOSAIC_HEIGHT} tiles")
    print(f"Total tiles needed: {MOSAIC_WIDTH * MOSAIC_HEIGHT:,}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mosaic_preview.py <input_image> [output_image]")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    create_mosaic_preview(input_file, output_file)
