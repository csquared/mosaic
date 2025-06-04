#!/usr/bin/env python3
from PIL import Image, ImageDraw, ImageFilter
import random
import sys
import os

TILE_COLORS = [
    (232, 232, 228),  # Off White
    (201, 201, 196),  # Light Gray
    (170, 170, 164),  # Medium Gray
    (140, 140, 134),  # Warm Gray
    (110, 110, 104),  # Dark Gray
    (80, 80, 74),     # Charcoal
    (60, 60, 54),     # Deep Charcoal
    (255, 255, 255),  # Pure White
    (0, 0, 0),        # Black
    (194, 180, 153),  # Beige
    (160, 140, 110),  # Taupe
    (120, 100, 70),   # Brown
    (70, 50, 30),     # Dark Brown
    (200, 220, 210),  # Pale Green
    (120, 180, 160),  # Sage
    (60, 120, 100),   # Deep Green
    (180, 210, 230),  # Light Blue
    (100, 150, 200),  # Blue
    (40, 80, 140),    # Navy
    (230, 200, 180),  # Peach
    (200, 140, 120),  # Terracotta
    (180, 60, 40),    # Red
    (255, 220, 0),    # Yellow
    (255, 150, 0),    # Orange
]

def quantize_color_to_palette(rgb, palette=TILE_COLORS):
    def dist(c1, c2):
        return sum((a-b)**2 for a, b in zip(c1, c2))
    return min(palette, key=lambda c: dist(rgb, c))

def add_tile_variation(color, variation=15):
    """Add slight color variation to simulate natural tile differences"""
    r, g, b = color
    
    # Keep pure whites and near-whites white
    if r > 230 and g > 230 and b > 230:
        return (255, 255, 255)  # Pure white
    
    # Keep pure blacks black with minimal variation
    if r < 30 and g < 30 and b < 30:
        # Very subtle variation for black tiles
        var = 3
        r = max(0, min(255, r + random.randint(-var, var)))
        g = max(0, min(255, g + random.randint(-var, var)))
        b = max(0, min(255, b + random.randint(-var, var)))
        return (r, g, b)
    
    # For other colors, add normal variation
    r = max(0, min(255, r + random.randint(-variation, variation)))
    g = max(0, min(255, g + random.randint(-variation, variation)))
    b = max(0, min(255, b + random.randint(-variation, variation)))
    return (r, g, b)

def create_tile_with_texture(size, base_color, rounded=False):
    """Create a single tile with texture and slight variations"""
    tile = Image.new('RGB', (size, size), base_color)
    draw = ImageDraw.Draw(tile)
    
    # Check if this is a white/black tile
    r, g, b = base_color
    is_white = r > 230 and g > 230 and b > 230
    is_black = r < 30 and g < 30 and b < 30
    
    # Add texture only for non-white tiles
    if not is_white:
        # Add some texture with random subtle dots
        texture_amount = size // 6 if not is_black else size // 8
        for _ in range(texture_amount):
            x = random.randint(0, size-1)
            y = random.randint(0, size-1)
            # Create subtle texture by slightly varying the color
            texture_variation = 5 if not is_black else 3
            texture_color = add_tile_variation(base_color, texture_variation)
            draw.point((x, y), fill=texture_color)
    
    # Add very subtle edge shading for depth (less pronounced for white tiles)
    edge_factor = 0.95 if not is_white else 0.98
    for i in range(2):
        # Darken edges slightly
        shade_color = tuple(int(c * edge_factor) for c in base_color)
        draw.line([(i, 0), (i, size-1)], fill=shade_color)
        draw.line([(0, i), (size-1, i)], fill=shade_color)
        draw.line([(size-1-i, 0), (size-1-i, size-1)], fill=shade_color)
        draw.line([(0, size-1-i), (size-1, size-1-i)], fill=shade_color)
    
    # Add highlight on opposite edges (skip for white tiles)
    if not is_white:
        for i in range(1):
            highlight_color = tuple(min(255, int(c * 1.05)) for c in base_color)
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
            
            # Normalize whites to pure white
            r, g, b = base_color
            if r > 230 and g > 230 and b > 230:
                tile_color = (255, 255, 255)
            else:
                # Add natural variation between tiles for non-white colors
                tile_color = add_tile_variation(base_color, 10)
            # Snap to nearest available tile color
            tile_color = quantize_color_to_palette(tile_color, TILE_COLORS)
            
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
        ('square', (32, 32, 32), 'gray'),
        ('square', (255, 255, 255), 'white'),
        ('square', (0, 0, 0), 'dark'),
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