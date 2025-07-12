"""
Script to create valid PNG icons for the assets/icons/ folder
Replaces the empty 0-byte PNG files with actual icon images
"""

import os
from PIL import Image, ImageDraw, ImageFont
import json

def create_icon_set():
    """Creates a complete set of valid PNG icons for the Checker app"""
    
    # Icon specifications
    icon_size = (32, 32)
    bg_color = (255, 255, 255, 0)  # Transparent background
    
    # Icon definitions with simple geometric shapes and colors
    icons_to_create = {
        'check-mark.png': {
            'type': 'checkmark',
            'color': (34, 197, 94),  # Green
            'description': 'Checkmark for success states'
        },
        'close.png': {
            'type': 'x',
            'color': (239, 68, 68),  # Red
            'description': 'X symbol for close/cancel'
        },
        'doc-file.png': {
            'type': 'document',
            'color': (59, 130, 246),  # Blue
            'description': 'Document file icon'
        },
        'file.png': {
            'type': 'file',
            'color': (107, 114, 128),  # Gray
            'description': 'Generic file icon'
        },
        'home.png': {
            'type': 'house',
            'color': (34, 197, 94),  # Green
            'description': 'Home/house icon'
        },
        'idea.png': {
            'type': 'lightbulb',
            'color': (251, 191, 36),  # Yellow
            'description': 'Lightbulb for ideas'
        },
        'image-file.png': {
            'type': 'image',
            'color': (168, 85, 247),  # Purple
            'description': 'Image file icon'
        },
        'info.png': {
            'type': 'info',
            'color': (59, 130, 246),  # Blue
            'description': 'Information icon'
        },
        'pdf-file.png': {
            'type': 'pdf',
            'color': (239, 68, 68),  # Red
            'description': 'PDF file icon'
        },
        'play.png': {
            'type': 'play',
            'color': (34, 197, 94),  # Green
            'description': 'Play button triangle'
        },
        'restart.png': {
            'type': 'refresh',
            'color': (59, 130, 246),  # Blue
            'description': 'Refresh/restart icon'
        },
        'settings.png': {
            'type': 'gear',
            'color': (107, 114, 128),  # Gray
            'description': 'Settings gear icon'
        },
        'toolbox.png': {
            'type': 'toolbox',
            'color': (251, 146, 60),  # Orange
            'description': 'Toolbox icon'
        },
        'txt-file.png': {
            'type': 'text',
            'color': (34, 197, 94),  # Green
            'description': 'Text file icon'
        }
    }
    
    assets_icons_path = os.path.join(os.getcwd(), 'assets', 'icons')
    
    if not os.path.exists(assets_icons_path):
        print(f"Error: Directory {assets_icons_path} does not exist!")
        return False
    
    created_icons = []
    errors = []
    
    for filename, config in icons_to_create.items():
        try:
            icon_path = os.path.join(assets_icons_path, filename)
            
            # Create new image with transparency
            img = Image.new('RGBA', icon_size, bg_color)
            draw = ImageDraw.Draw(img)
            
            # Get drawing parameters
            color = config['color']
            icon_type = config['type']
            
            # Draw based on type
            if icon_type == 'checkmark':
                # Draw checkmark
                points = [(8, 16), (14, 22), (24, 10)]
                draw.polygon(points, fill=color)
                # Make it thicker
                for offset in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
                    offset_points = [(p[0] + offset[0], p[1] + offset[1]) for p in points]
                    draw.polygon(offset_points, fill=color)
            
            elif icon_type == 'x':
                # Draw X
                draw.line([(8, 8), (24, 24)], fill=color, width=3)
                draw.line([(8, 24), (24, 8)], fill=color, width=3)
            
            elif icon_type == 'document':
                # Draw document shape
                draw.rectangle([(6, 4), (22, 28)], outline=color, fill=(*color, 180), width=2)
                draw.rectangle([(8, 8), (20, 10)], fill=color)
                draw.rectangle([(8, 12), (20, 14)], fill=color)
                draw.rectangle([(8, 16), (18, 18)], fill=color)
            
            elif icon_type == 'file':
                # Draw generic file
                draw.rectangle([(8, 4), (24, 28)], outline=color, fill=(*color, 120), width=2)
                # Folded corner
                draw.polygon([(20, 4), (24, 8), (20, 8)], fill=color)
            
            elif icon_type == 'house':
                # Draw house
                # Roof
                draw.polygon([(16, 6), (6, 14), (26, 14)], fill=color)
                # House body
                draw.rectangle([(8, 14), (24, 26)], fill=color)
                # Door
                draw.rectangle([(13, 18), (19, 26)], fill=(255, 255, 255))
            
            elif icon_type == 'lightbulb':
                # Draw lightbulb
                draw.ellipse([(10, 8), (22, 20)], fill=color)
                draw.rectangle([(12, 20), (20, 24)], fill=color)
                draw.rectangle([(11, 24), (21, 26)], fill=color)
            
            elif icon_type == 'image':
                # Draw image icon
                draw.rectangle([(4, 6), (28, 26)], outline=color, fill=(*color, 100), width=2)
                # Mountain and sun
                draw.polygon([(6, 20), (12, 12), (18, 20)], fill=color)
                draw.ellipse([(20, 8), (26, 14)], fill=color)
            
            elif icon_type == 'info':
                # Draw info icon (i in circle)
                draw.ellipse([(4, 4), (28, 28)], outline=color, fill=(*color, 100), width=2)
                draw.ellipse([(14, 8), (18, 12)], fill=color)
                draw.rectangle([(14, 14), (18, 24)], fill=color)
            
            elif icon_type == 'pdf':
                # Draw PDF icon
                draw.rectangle([(6, 4), (22, 28)], outline=color, fill=(*color, 180), width=2)
                # PDF text
                try:
                    font = ImageFont.load_default()
                    draw.text((8, 12), "PDF", fill=color, font=font)
                except:
                    draw.rectangle([(8, 12), (20, 20)], fill=color)
            
            elif icon_type == 'play':
                # Draw play triangle
                draw.polygon([(10, 8), (10, 24), (24, 16)], fill=color)
            
            elif icon_type == 'refresh':
                # Draw refresh arrows
                draw.arc([(6, 6), (26, 26)], start=45, end=315, fill=color, width=3)
                # Arrow heads
                draw.polygon([(22, 8), (26, 6), (26, 12)], fill=color)
                draw.polygon([(10, 24), (6, 26), (6, 20)], fill=color)
            
            elif icon_type == 'gear':
                # Draw gear
                center = (16, 16)
                outer_radius = 10
                inner_radius = 6
                # Simplified gear shape
                draw.ellipse([(center[0]-outer_radius, center[1]-outer_radius),
                            (center[0]+outer_radius, center[1]+outer_radius)], 
                            outline=color, fill=(*color, 150), width=2)
                draw.ellipse([(center[0]-inner_radius, center[1]-inner_radius),
                            (center[0]+inner_radius, center[1]+inner_radius)], 
                            fill=(255, 255, 255, 0))
                # Gear teeth (simplified)
                for angle in [0, 45, 90, 135, 180, 225, 270, 315]:
                    import math
                    x = center[0] + int(outer_radius * 1.3 * math.cos(math.radians(angle)))
                    y = center[1] + int(outer_radius * 1.3 * math.sin(math.radians(angle)))
                    draw.rectangle([(x-1, y-1), (x+1, y+1)], fill=color)
            
            elif icon_type == 'toolbox':
                # Draw toolbox
                draw.rectangle([(6, 12), (26, 24)], fill=color)
                draw.rectangle([(8, 8), (24, 12)], fill=(*color, 200))
                # Handle
                draw.ellipse([(12, 6), (20, 10)], outline=color, width=2)
            
            elif icon_type == 'text':
                # Draw text file
                draw.rectangle([(6, 4), (22, 28)], outline=color, fill=(*color, 120), width=2)
                # Text lines
                for y in [10, 14, 18, 22]:
                    draw.rectangle([(8, y), (20, y+1)], fill=color)
            
            # Save the icon
            img.save(icon_path, 'PNG')
            created_icons.append(filename)
            print(f"✅ Created: {filename} ({config['description']})")
            
        except Exception as e:
            errors.append((filename, str(e)))
            print(f"❌ Error creating {filename}: {e}")
    
    # Create metadata file
    try:
        metadata = {
            "created_icons": len(created_icons),
            "total_icons": len(icons_to_create),
            "icon_size": icon_size,
            "format": "PNG with RGBA transparency",
            "created_files": created_icons,
            "errors": errors,
            "descriptions": {name: config['description'] for name, config in icons_to_create.items()}
        }
        
        metadata_path = os.path.join(assets_icons_path, 'icon_metadata.json')
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n📊 Metadata saved to: {metadata_path}")
        
    except Exception as e:
        print(f"Warning: Could not save metadata: {e}")
    
    print(f"\n🎉 Successfully created {len(created_icons)} out of {len(icons_to_create)} icons!")
    
    if errors:
        print(f"⚠️  {len(errors)} errors occurred:")
        for filename, error in errors:
            print(f"   - {filename}: {error}")
    
    return len(errors) == 0

if __name__ == "__main__":
    print("🎨 Creating valid PNG icons for Checker-App...")
    print("=" * 50)
    
    success = create_icon_set()
    
    if success:
        print("\n✅ All icons created successfully!")
        print("The empty PNG files have been replaced with valid icons.")
        print("The Checker-App should now load without icon-related errors.")
    else:
        print("\n⚠️  Some icons could not be created. Check the errors above.")
