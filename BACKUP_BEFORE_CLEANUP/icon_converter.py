
import os
import traceback
from PIL import Image

try:
    import cairosvg
    SVG_SUPPORT = True
except (ImportError, OSError) as e:
    print(f"[WARN] cairosvg is not installed or its dependencies are missing: {e}")
    print("[WARN] SVG to PNG conversion will be skipped. Please install it with: pip install cairosvg")
    SVG_SUPPORT = False

# --- CONFIGURATION ---

# Mapping from the logical icon name used in the app to the Material Icon Theme SVG filename (without .svg)
ICON_MAPPING = {
    # App-specific icons
    "toolbox.png": "tools",
    "plus.png": "add",
    "info.png": "info",
    "restart.png": "refresh",
    "settings.png": "settings-gear", # Using gear variant
    "check-mark.png": "check",
    "close.png": "close",
    "play.png": "play-circle-outline", # Using outline variant
    "home.png": "home",
    "idea.png": "lightbulb",

    # File type icons
    "pdf-file.png": "file-type-pdf",
    "doc-file.png": "file-type-word",
    "txt-file.png": "file-type-text",
    "image-file.png": "file-type-image",
    "file.png": "file",
}

# Path to the Material Icon Theme extension's icon folder
# This might need to be adjusted based on the user's system and extension version
MATERIAL_ICON_SOURCE_PATH = os.path.expanduser("~/.vscode/extensions/pkief.material-icon-theme-6.1.0/icons")

# Destination path for the converted PNG icons
DESTINATION_PATH = os.path.join(os.path.dirname(__file__), "assets", "new_icons")

# --- CONVERSION SCRIPT ---

def convert_svg_to_png(svg_path, png_path, size=(32, 32)):
    """Converts an SVG file to a PNG file."""
    try:
        # Ensure the destination directory exists
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        
        # Convert SVG to PNG bytes
        png_bytes = cairosvg.svg2png(url=svg_path, output_width=size[0], output_height=size[1])
        
        # Write the bytes to a file
        with open(png_path, "wb") as f:
            f.write(png_bytes)
            
        print(f"[SUCCESS] Converted {svg_path} -> {png_path}")
        return True
    except FileNotFoundError:
        print(f"[ERROR] SVG source file not found: {svg_path}")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to convert {svg_path} to {png_path}: {e}")
        traceback.print_exc()
        return False

def create_placeholder_png(png_path, size=(32, 32)):
    """Creates a transparent placeholder PNG if conversion fails."""
    try:
        os.makedirs(os.path.dirname(png_path), exist_ok=True)
        img = Image.new('RGBA', size, (0, 0, 0, 0))
        img.save(png_path, 'PNG')
        print(f"[INFO] Created placeholder icon: {png_path}")
    except Exception as e:
        print(f"[ERROR] Failed to create placeholder icon {png_path}: {e}")

def main():
    """Main function to run the conversion process."""
    if not SVG_SUPPORT:
        print("[EXIT] Exiting script because cairosvg is not available.")
        return

    if not os.path.isdir(MATERIAL_ICON_SOURCE_PATH):
        print(f"[ERROR] Material Icon source directory not found at: {MATERIAL_ICON_SOURCE_PATH}")
        print("[ERROR] Please verify the path to the pkief.material-icon-theme extension.")
        return

    print(f"Source SVG directory: {MATERIAL_ICON_SOURCE_PATH}")
    print(f"Destination PNG directory: {DESTINATION_PATH}")
    print("-" * 30)

    converted_count = 0
    failed_count = 0

    for png_filename, svg_filename in ICON_MAPPING.items():
        svg_path = os.path.join(MATERIAL_ICON_SOURCE_PATH, f"{svg_filename}.svg")
        png_path = os.path.join(DESTINATION_PATH, png_filename)

        if convert_svg_to_png(svg_path, png_path):
            converted_count += 1
        else:
            failed_count += 1
            print(f"Attempting to create a placeholder for {png_filename}...")
            create_placeholder_png(png_path)

    print("-" * 30)
    print(f"Conversion complete. {converted_count} icons converted, {failed_count} failed.")

if __name__ == "__main__":
    main()
