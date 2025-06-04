#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter
import random
import sys
import os

def add_tile_variation(color, variation=15):
    """Add slight color variation to simulate natural tile differences"""
    r, g, b = color
    r = max(0, min(255, r + random.randint(-variation, variation)))
    g = max(0, min(255, g + random.randint(-variation, variation)))
    b = max(0, min(255, b + random.randint(-variation, variation)))
    return (r, g, b)

def create_tile_with_texture(size, base_color, rounded=False):
    """Create a single tile with texture and slight variations"""
    tile = Image.new('RGB', (size, size), base_color)
    draw = ImageDraw.Draw(tile)
    
    # Add some texture with random subtle dots
    for _ in range(size // 4):
        x = random.randint(0, size-1)
        y = random.randint(0, size-1)
        # Create subtle texture by slightly varying the color
        texture_color = add_tile_variation(base_color, 8)
        draw.point((x, y), fill=texture_color)
    
    # Add subtle edge shading for depth
    for i in range(2):
        # Darken edges slightly
        shade_color = tuple(int(c * 0.9) for c in base_color)
        draw.line([(i, 0), (i, size-1)], fill=shade_color)
        draw.line([(0, i), (size-1, i)], fill=shade_color)
        draw.line([(size-1-i, 0), (size-1-i, size-1)], fill=shade_color)
        draw.line([(0, size-1-i), (size-1, size-1-i)], fill=shade_color)
    
    # Add highlight on opposite edges
    for i in range(1):
        highlight_color = tuple(min(255, int(c * 1.1)) for c in base_color)
        draw.line([(i+2, 2), (i+2, size-3)], fill=highlight_color)
        draw.line([(2, i+2), (size-3, i+2)], fill=highlight_color)
    
    if rounded:
        # Create rounded corners for penny tiles
        mask = Image.new('L', (size, size), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.ellipse([0, 0, size-1, size-1], fill=255)
        tile.putalpha(mask)
    
    return tile

def create_mosaic_with_grout(input_path, output_path=None, tile_size=40, grout_width=3, 
                            grout_color=(128, 128, 128), tile_style='square'):
    """
    Create a realistic mosaic simulation with grout lines and tile texture
    """
    # Mosaic dimensions in tiles
    MOSAIC_WIDTH = 42   
    MOSAIC_HEIGHT = 67
    
    # Open and prepare the input image
    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to mosaic dimensions
    pixelated = img.resize((MOSAIC_WIDTH, MOSAIC_HEIGHT), Image.Resampling.LANCZOS)
    
    # Calculate output image size
    output_width = MOSAIC_WIDTH * tile_size + (MOSAIC_WIDTH + 1) * grout_width
    output_height = MOSAIC_HEIGHT * tile_size + (MOSAIC_HEIGHT + 1) * grout_width
    
    # Create output image with grout color background
    output = Image.new('RGB', (output_width, output_height), grout_color)
    
    print(f"Creating {tile_style} tile mosaic...")
    print(f"Output size: {output_width}x{output_height} pixels")
    
    # Place tiles
    for y in range(MOSAIC_HEIGHT):
        for x in range(MOSAIC_WIDTH):
            # Get the color for this tile
            base_color = pixelated.getpixel((x, y))
            
            # Add natural variation between tiles
            tile_color = add_tile_variation(base_color, 10)
            
            # Create the tile with texture
            tile = create_tile_with_texture(tile_size, tile_color, 
                                           rounded=(tile_style == 'penny'))
            
            # Calculate position including grout
            pos_x = x * (tile_size + grout_width) + grout_width
            pos_y = y * (tile_size + grout_width) + grout_width
            
            # Paste the tile
            if tile_style == 'penny' and tile.mode == 'RGBA':
                output.paste(tile, (pos_x, pos_y), tile)
            else:
                output.paste(tile, (pos_x, pos_y))
        
        # Progress indicator
        if (y + 1) % 10 == 0:
            print(f"Progress: {(y + 1) / MOSAIC_HEIGHT * 100:.1f}%")
    
    # Add subtle grout texture
    draw = ImageDraw.Draw(output)
    for _ in range(output_width * output_height // 50):
        x = random.randint(0, output_width-1)
        y = random.randint(0, output_height-1)
        # Only add texture to grout areas (check if we're not on a tile)
        pixel_color = output.getpixel((x, y))
        if pixel_color == grout_color:
            grout_texture = add_tile_variation(grout_color, 20)
            draw.point((x, y), fill=grout_texture)
    
    # Apply a very subtle blur to soften hard edges
    output = output.filter(ImageFilter.SMOOTH_MORE)
    
    # Save the output
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_mosaic_simulation_{tile_style}.png"
    
    output.save(output_path, quality=95)
    
    # Also create a smaller preview version
    preview_width = 800
    preview_height = int(output_height * (preview_width / output_width))
    preview = output.resize((preview_width, preview_height), Image.Resampling.LANCZOS)
    preview_path = output_path.replace('.png', '_preview.png')
    preview.save(preview_path)
    
    print(f"\nMosaic simulation saved to: {output_path}")
    print(f"Preview version saved to: {preview_path}")
    print(f"Total tiles: {MOSAIC_WIDTH * MOSAIC_HEIGHT:,}")
    
    # Calculate actual physical dimensions
    physical_width = MOSAIC_WIDTH  # inches
    physical_height = MOSAIC_HEIGHT  # inches
    print(f"\nPhysical dimensions: {physical_width}\" x {physical_height}\"")
    print(f"With {grout_width}px grout (simulating ~1/8\" grout lines)")

def create_multiple_styles(input_path):
    """Create simulations with different tile styles and grout colors"""
    styles = [
        ('square', (128, 128, 128), 'gray'),
        ('square', (255, 255, 255), 'white'),
        ('square', (64, 64, 64), 'dark'),
        ('penny', (128, 128, 128), 'gray')
    ]
    
    for tile_style, grout_color, grout_name in styles:
        print(f"\n=== Creating {tile_style} tiles with {grout_name} grout ===")
        output_name = f"{os.path.splitext(input_path)[0]}_mosaic_{tile_style}_{grout_name}_grout.png"
        create_mosaic_with_grout(input_path, output_name, 
                               tile_style=tile_style, grout_color=grout_color)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mosaic_simulator.py <input_image> [style]")
        print("Styles: square (default), penny, all")
        print("Example: python mosaic_simulator.py image.jpg square")
        print("         python mosaic_simulator.py image.jpg all")
        sys.exit(1)
    
    input_file = sys.argv[1]
    style = sys.argv[2] if len(sys.argv) > 2 else 'square'
    
    if style == 'all':
        create_multiple_styles(input_file)
    else:
        create_mosaic_with_grout(input_file, tile_style=style)