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

SQUARE_SIZE = 20
PADDING = 4
COLUMNS = 8  # Number of swatches per row

rows = (len(TILE_COLORS) + COLUMNS - 1) // COLUMNS
width = COLUMNS * (SQUARE_SIZE + PADDING) + PADDING
height = rows * (SQUARE_SIZE + PADDING) + PADDING

img = Image.new('RGB', (width, height), (240, 240, 240))
draw = ImageDraw.Draw(img)

for idx, color in enumerate(TILE_COLORS):
    row = idx // COLUMNS
    col = idx % COLUMNS
    x0 = PADDING + col * (SQUARE_SIZE + PADDING)
    y0 = PADDING + row * (SQUARE_SIZE + PADDING)
    x1 = x0 + SQUARE_SIZE
    y1 = y0 + SQUARE_SIZE
    draw.rectangle([x0, y0, x1, y1], fill=color, outline=(0, 0, 0))

img.save('tile_palette.png')
print("Saved tile_palette.png")
