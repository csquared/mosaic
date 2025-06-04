#!/usr/bin/env python3
from PIL import Image
from collections import Counter
import sys
import os
import colorsys

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

def rgb_to_hex(rgb):
    """Convert RGB tuple to hex color"""
    return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])

def quantize_color_to_palette(rgb, palette=TILE_COLORS):
    """Quantize an RGB color to the nearest color in the given palette."""
    def dist(c1, c2):
        return sum((a-b)**2 for a, b in zip(c1, c2))
    return min(palette, key=lambda c: dist(rgb, c))

def create_mosaic_preview_with_analysis(input_path, output_path=None, max_colors=20, color_reduction=32):
    """
    Create a pixelated preview and analyze colors for a 67x42 tile mosaic
    """
    # Mosaic dimensions (in tiles/pixels)
    MOSAIC_WIDTH = 42 
    MOSAIC_HEIGHT = 67   
    
    # Open the input image
    img = Image.open(input_path)
    
    # Convert to RGB if necessary
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # Resize to mosaic dimensions
    pixelated = img.resize((MOSAIC_WIDTH, MOSAIC_HEIGHT), Image.Resampling.LANCZOS)
    
    # Quantize colors to tile palette
    pixels = list(pixelated.getdata())
    quantized_pixels = [quantize_color_to_palette(p, TILE_COLORS) for p in pixels]
    
    # Create new image with quantized colors
    quantized_img = Image.new('RGB', (MOSAIC_WIDTH, MOSAIC_HEIGHT))
    quantized_img.putdata(quantized_pixels)
    
    # Analyze colors
    color_counts = Counter(quantized_pixels)
    
    # Sort colors by frequency
    sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Group similar colors (optional - for now we'll show exact colors)
    print("\n=== MOSAIC COLOR ANALYSIS ===")
    print(f"Total tiles: {MOSAIC_WIDTH * MOSAIC_HEIGHT:,}")
    print(f"Unique colors after quantization: {len(sorted_colors)}")
    print("\n=== TILE REQUIREMENTS ===")
    
    # Show top colors
    colors_to_show = min(max_colors, len(sorted_colors))
    total_shown = 0
    
    for i, (color, count) in enumerate(sorted_colors[:colors_to_show]):
        percentage = (count / len(pixels)) * 100
        hex_color = rgb_to_hex(color)
        total_shown += count
        
        # Create a color description
        r, g, b = color
        if r < 50 and g < 50 and b < 50:
            desc = "Black/Dark Gray"
        elif r > 200 and g > 200 and b > 200:
            desc = "White/Light Gray"
        elif r > g and r > b:
            desc = "Reddish"
        elif g > r and g > b:
            desc = "Greenish"
        elif b > r and b > g:
            desc = "Bluish"
        else:
            desc = "Gray"
        
        print(f"{i+1:2d}. {hex_color} ({desc:15s}): {count:4d} tiles ({percentage:5.1f}%)")
    
    if len(sorted_colors) > colors_to_show:
        remaining = len(pixels) - total_shown
        print(f"\n    Other colors: {remaining} tiles ({(remaining/len(pixels)*100):.1f}%)")
    
    # Create color palette image
    palette_height = 50
    palette_img = Image.new('RGB', (MOSAIC_WIDTH * 10, palette_height * min(10, len(sorted_colors))))
    
    for i, (color, count) in enumerate(sorted_colors[:10]):
        # Draw a bar for each color
        for y in range(i * palette_height, (i + 1) * palette_height):
            for x in range(int(MOSAIC_WIDTH * 10 * count / len(pixels))):
                palette_img.putpixel((x, y), color)
    
    # Scale up preview for viewing
    preview_size = (MOSAIC_WIDTH * 10, MOSAIC_HEIGHT * 10)
    preview = quantized_img.resize(preview_size, Image.Resampling.NEAREST)
    
    # Generate output filenames
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_mosaic_preview.png"
    
    # Save images
    preview.save(output_path)
    pixel_perfect_path = output_path.replace('.png', '_exact.png')
    quantized_img.save(pixel_perfect_path)
    palette_path = output_path.replace('.png', '_palette.png')
    palette_img.save(palette_path)
    
    print(f"\n=== FILES SAVED ===")
    print(f"Preview: {output_path}")
    print(f"Exact pixels: {pixel_perfect_path}")
    print(f"Color palette: {palette_path}")
    
    # Suggest tile groupings
    print("\n=== SUGGESTED TILE GROUPINGS ===")
    blacks = sum(count for color, count in sorted_colors if all(c < 50 for c in color))
    whites = sum(count for color, count in sorted_colors if all(c > 200 for c in color))
    grays = sum(count for color, count in sorted_colors if 50 <= min(color) and max(color) <= 200 and max(color) - min(color) < 30)
    colors = len(pixels) - blacks - whites - grays
    
    print(f"Black tiles needed: ~{blacks:,}")
    print(f"White tiles needed: ~{whites:,}")
    print(f"Gray tiles needed: ~{grays:,}")
    print(f"Colored tiles needed: ~{colors:,}")
    
    # Generate a simplified color map for easier tile selection
    print("\n=== SIMPLIFIED COLOR MAP ===")
    simplified = quantized_img.copy()
    
    # Map each pixel to simplified colors
    for x in range(MOSAIC_WIDTH):
        for y in range(MOSAIC_HEIGHT):
            r, g, b = simplified.getpixel((x, y))
            
            # Simplify to basic colors
            if all(c < 50 for c in (r, g, b)):
                simplified.putpixel((x, y), (0, 0, 0))  # Pure black
            elif all(c > 200 for c in (r, g, b)):
                simplified.putpixel((x, y), (255, 255, 255))  # Pure white
            elif max(r, g, b) - min(r, g, b) < 30:
                # It's a gray - pick closest standard gray
                avg = (r + g + b) // 3
                if avg < 85:
                    simplified.putpixel((x, y), (64, 64, 64))  # Dark gray
                elif avg < 170:
                    simplified.putpixel((x, y), (128, 128, 128))  # Medium gray
                else:
                    simplified.putpixel((x, y), (192, 192, 192))  # Light gray
    
    # Save simplified version
    simplified_preview = simplified.resize(preview_size, Image.Resampling.NEAREST)
    simplified_path = output_path.replace('.png', '_simplified.png')
    simplified_preview.save(simplified_path)
    print(f"Simplified preview: {simplified_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mosaic_analyzer.py <input_image> [output_image] [color_reduction]")
        print("color_reduction: Number of color levels to reduce to (default: 32)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    color_reduction = int(sys.argv[3]) if len(sys.argv) > 3 else 32
    
    create_mosaic_preview_with_analysis(input_file, output_file, color_reduction=color_reduction)
