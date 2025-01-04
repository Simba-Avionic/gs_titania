from PIL import Image
import os
import math
import re

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
output_image = os.path.join(script_dir, "merged_grid.png")

# Load all PNG images in the directory and filter by the Hz part in the filename
image_files = [os.path.join(script_dir, f) for f in os.listdir(script_dir) if f.endswith('.png')]

# Define a regular expression pattern to extract the Hz values from the filenames
hz_pattern = re.compile(r'(\d+)Hz')

# Function to extract the Hz value from the filename
def extract_hz(filename):
    match = hz_pattern.search(filename)
    if match:
        return int(match.group(1))  # Return Hz as an integer
    return float('inf')  # If no Hz found, return a high value to sort at the end

# Sort the images by the Hz values extracted from the filenames (ascending order)
image_files.sort(key=extract_hz)

# Calculate the grid size (square or as close to square as possible)
num_images = len(image_files)
cols = math.ceil(math.sqrt(num_images))  # Number of columns
rows = math.ceil(num_images / cols)      # Number of rows

# Open all images and ensure they have the same dimensions as the first image
images = [Image.open(img) for img in image_files]
img_width, img_height = images[0].size  # Use the size of the first image as a reference

# Create a blank image with the size of the grid
grid_img = Image.new('RGB', (cols * img_width, rows * img_height))

# Paste each image into the grid
for index, img in enumerate(images):
    row = index // cols
    col = index % cols
    grid_img.paste(img, (col * img_width, row * img_height))

# Save the final grid image
grid_img.save(output_image)
print(f"Grid image saved as {output_image}")