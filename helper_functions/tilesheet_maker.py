from PIL import Image
import os

# Directory containing the PNG files
base_directory = '../graphics'

# Directories to exclude
exclude_dirs = ['levels', 'idle', 'walking', 'cloud', 'particles', 'projectiles', 'ui', 'spells', 'weapons', 'animation', 'original_image','precipitation', 'keys', 'drops', 'screens', 'precipitation', 'digits']

# Path to the tilesheet file
tilesheet_path = os.path.join(base_directory, 'tilesheet.png')

# Remove the existing tilesheet file if it exists
if os.path.exists(tilesheet_path):
    os.remove(tilesheet_path)

# List all PNG files in the directory and subdirectories, excluding specified directories
files = []
for root, dirnames, filenames in os.walk(base_directory):
    # Remove directories to exclude
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]

    for filename in filenames:
        if filename.endswith('.png') and filename != 'tilesheet.png':
            files.append(os.path.join(root, filename))

# Sort the files to ensure consistent order
files.sort()

# Open all images and store them in a list
images = [Image.open(file) for file in files]

# Set the size of each tile
tile_width, tile_height = 16, 16

# Create a set to store unique tiles
unique_tiles = set()

# Extract and store all 16x16 tiles, ensuring no duplicates
tiles = []
for image in images:
    image_width, image_height = image.size
    for y in range(0, image_height, tile_height):
        for x in range(0, image_width, tile_width):
            tile = image.crop((x, y, x + tile_width, y + tile_height))
            tile_tuple = tuple(tile.getdata())  # Convert image to a tuple for uniqueness check
            if tile_tuple not in unique_tiles:
                unique_tiles.add(tile_tuple)
                tiles.append(tile)

# Calculate the total number of unique tiles
num_tiles = len(tiles)

# Determine the size of the tilesheet
tiles_per_row = 10  # Adjust based on your preference
tilesheet_width = tile_width * tiles_per_row
tilesheet_height = tile_height * ((num_tiles + tiles_per_row - 1) // tiles_per_row)

# Create a blank image for the tilesheet
tilesheet = Image.new('RGBA', (tilesheet_width, tilesheet_height))

# Paste each unique tile into the tilesheet
tile_index = 0
for tile in tiles:
    ts_x = (tile_index % tiles_per_row) * tile_width
    ts_y = (tile_index // tiles_per_row) * tile_height
    tilesheet.paste(tile, (ts_x, ts_y))
    tile_index += 1

# Save the tilesheet
tilesheet.save(tilesheet_path)
