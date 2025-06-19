#!/usr/bin/env python3
from PIL import Image
import sys
import os

def create_exact_color_grid(input_path, output_prefix=None):
    """
    Create two versions of the mosaic grid:
    1. A 1:1 pixel representation (42x67)
    2. A larger version with 10x10 squares per color for easy viewing
    """
    # Fixed mosaic dimensions
    MOSAIC_WIDTH = 42
    MOSAIC_HEIGHT = 67
    PREVIEW_SCALE = 10  # Each color will be a 10x10 square in the preview
    
    # Open and prepare the input image
    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to mosaic dimensions - this does the color averaging
    pixelated = img.resize((MOSAIC_WIDTH, MOSAIC_HEIGHT), Image.Resampling.LANCZOS)
    
    # Create the preview image (scaled up version)
    preview_width = MOSAIC_WIDTH * PREVIEW_SCALE
    preview_height = MOSAIC_HEIGHT * PREVIEW_SCALE
    preview = Image.new('RGB', (preview_width, preview_height))
    
    # Fill both images with the exact colors
    for y in range(MOSAIC_HEIGHT):
        for x in range(MOSAIC_WIDTH):
            # Get the exact color for this position
            color = pixelated.getpixel((x, y))
            
            # For the preview, fill a PREVIEW_SCALE x PREVIEW_SCALE square
            for py in range(PREVIEW_SCALE):
                for px in range(PREVIEW_SCALE):
                    preview.putpixel(
                        (x * PREVIEW_SCALE + px, y * PREVIEW_SCALE + py),
                        color
                    )
    
    # Determine output paths
    if output_prefix is None:
        output_prefix = os.path.splitext(input_path)[0]
    
    # Save both versions
    exact_path = f"{output_prefix}_exact.png"
    preview_path = f"{output_prefix}_exact_preview.png"
    
    pixelated.save(exact_path)
    preview.save(preview_path)
    
    print(f"\nExact color grid saved to: {exact_path}")
    print(f"Preview version saved to: {preview_path}")
    print(f"Grid dimensions: {MOSAIC_WIDTH} x {MOSAIC_HEIGHT}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exact_colors.py <input_image>")
        print("Example: python exact_colors.py flower-thrower.jpg")
        sys.exit(1)
    
    input_file = sys.argv[1]
    create_exact_color_grid(input_file) 