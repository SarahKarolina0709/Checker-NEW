
import os
from PIL import Image

# Directory for the new icons
icon_dir = os.path.join(os.path.dirname(__file__), "assets", "new_icons")
os.makedirs(icon_dir, exist_ok=True)

# List of icon filenames
icon_files = [
    "toolbox.png", "plus.png", "info.png", "restart.png", "settings.png",
    "check-mark.png", "close.png", "play.png", "home.png", "idea.png",
    "pdf-file.png", "doc-file.png", "txt-file.png", "image-file.png", "file.png"
]

# Create a 1x1 transparent pixel image
img = Image.new('RGBA', (1, 1), (0, 0, 0, 0))

# Save the image for each icon name
for filename in icon_files:
    filepath = os.path.join(icon_dir, filename)
    try:
        img.save(filepath, "PNG")
        print(f"Successfully created placeholder icon: {filepath}")
    except Exception as e:
        print(f"Failed to create icon {filepath}: {e}")

print("Icon recreation process complete.")
