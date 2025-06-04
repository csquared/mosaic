import sys
from PIL import Image, ImageDraw

# Your confirmed tile palette
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

# Define which indices are "browns" (to exclude in bouquet)
BROWN_INDICES = [9, 10, 11, 12, 19, 20]  # Beige, Taupe, Brown, Dark Brown, Peach, Terracotta

# Create a non-brown palette for the bouquet
NON_BROWN_PALETTE = [c for i, c in enumerate(TILE_COLORS) if i not in BROWN_INDICES]

def quantize_color_to_palette(rgb, palette):
    def dist(c1, c2):
        return sum((a-b)**2 for a, b in zip(c1, c2))
    return min(palette, key=lambda c: dist(rgb, c))

def main():
    if len(sys.argv) < 2:
        print("Usage: python boost.py <input_image.png>")
        sys.exit(1)
    input_path = sys.argv[1]
    output_path = input_path.replace('.png', '_bouquet_colorful.png')

    MOSAIC_WIDTH = 42
    MOSAIC_HEIGHT = 67

    # Define the bouquet rectangle (adjust as needed)
    bouquet_rect = (2, 2, 16, 18)  # (left, top, right, bottom) in tile coordinates

    img = Image.open(input_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    pixelated = img.resize((MOSAIC_WIDTH, MOSAIC_HEIGHT), Image.Resampling.LANCZOS)

    quantized_pixels = []
    for y in range(MOSAIC_HEIGHT):
        for x in range(MOSAIC_WIDTH):
            rgb = pixelated.getpixel((x, y))
            # Check if in bouquet rectangle
            if bouquet_rect[0] <= x <= bouquet_rect[2] and bouquet_rect[1] <= y <= bouquet_rect[3]:
                palette = NON_BROWN_PALETTE
            else:
                palette = TILE_COLORS
            quantized_pixels.append(quantize_color_to_palette(rgb, palette))

    # Create new image with quantized colors
    quantized_img = Image.new('RGB', (MOSAIC_WIDTH, MOSAIC_HEIGHT))
    quantized_img.putdata(quantized_pixels)

    # Save the result
    quantized_img = quantized_img.resize((MOSAIC_WIDTH*10, MOSAIC_HEIGHT*10), Image.Resampling.NEAREST)
    quantized_img.save(output_path)
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    main()
