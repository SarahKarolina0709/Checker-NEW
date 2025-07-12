
import os
from PIL import Image, ImageDraw, ImageFont

def create_icon(text, filename, size=(24, 24), bg_color=(255, 255, 255, 0), text_color=(0, 0, 0)):
    """Creates a simple icon with text."""
    # Create a transparent image
    img = Image.new('RGBA', size, bg_color)
    draw = ImageDraw.Draw(img)

    # Use a basic font
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except IOError:
        font = ImageFont.load_default()

    # Get text size and position
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) / 2, (size[1] - text_height) / 2 - 2) # Minor vertical adjustment

    # Draw text
    draw.text(position, text, font=font, fill=text_color)

    # Save the image
    img.save(filename, 'PNG')

def main():
    """Generates all required icons."""
    output_dir = os.path.join(os.path.dirname(__file__), 'assets', 'new_icons')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(f"Generating icons in: {output_dir}")

    icons = {
        "toolbox.png": "W",
        "plus.png": "+",
        "info.png": "i",
        "restart.png": "R",
        "settings.png": "S",
        "check-mark.png": "✓",
        "close.png": "X",
        "play.png": "▶",
        "home.png": "H",
        "idea.png": "!",
        "pdf-file.png": "P",
        "doc-file.png": "D",
        "txt-file.png": "T",
        "image-file.png": "I",
        "file.png": "F"
    }

    for filename, text in icons.items():
        filepath = os.path.join(output_dir, filename)
        try:
            create_icon(text, filepath, text_color=(70, 70, 70))
            print(f"Successfully created {filepath}")
        except Exception as e:
            print(f"Failed to create {filepath}: {e}")

if __name__ == "__main__":
    main()
