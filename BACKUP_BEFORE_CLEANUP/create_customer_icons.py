"""
Creates customer-related icons for the recent projects section
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_businesswoman_icon():
    """Creates a businesswoman icon"""
    # Create a 64x64 image with transparent background
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Professional blue color scheme
    primary_color = (41, 98, 255)  # Blue
    secondary_color = (80, 120, 255)  # Light blue
    accent_color = (255, 255, 255)  # White
    
    # Draw head (circle)
    head_radius = 12
    head_center = (32, 20)
    draw.ellipse([
        head_center[0] - head_radius, head_center[1] - head_radius,
        head_center[0] + head_radius, head_center[1] + head_radius
    ], fill=secondary_color, outline=primary_color, width=2)
    
    # Draw body (rounded rectangle for professional suit)
    body_top = 32
    body_width = 24
    body_height = 26
    body_left = 32 - body_width // 2
    body_right = 32 + body_width // 2
    
    # Draw suit jacket
    draw.rounded_rectangle([
        body_left, body_top,
        body_right, body_top + body_height
    ], radius=4, fill=primary_color, outline=primary_color)
    
    # Draw suit details (lapels)
    draw.line([body_left + 4, body_top + 2, 32 - 2, body_top + 8], fill=accent_color, width=2)
    draw.line([body_right - 4, body_top + 2, 32 + 2, body_top + 8], fill=accent_color, width=2)
    
    # Draw briefcase/folder
    briefcase_width = 8
    briefcase_height = 6
    briefcase_x = body_right + 2
    briefcase_y = body_top + 8
    
    draw.rounded_rectangle([
        briefcase_x, briefcase_y,
        briefcase_x + briefcase_width, briefcase_y + briefcase_height
    ], radius=2, fill=secondary_color, outline=primary_color, width=1)
    
    return image

def create_client_icon():
    """Creates a client/customer icon"""
    # Create a 64x64 image with transparent background
    size = (64, 64)
    image = Image.new('RGBA', size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Professional green color scheme
    primary_color = (34, 139, 34)  # Forest green
    secondary_color = (144, 238, 144)  # Light green
    accent_color = (255, 255, 255)  # White
    
    # Draw multiple people silhouettes to represent clients
    def draw_person(x_offset, y_offset, scale=1.0):
        # Head
        head_radius = int(8 * scale)
        head_center = (x_offset, y_offset)
        draw.ellipse([
            head_center[0] - head_radius, head_center[1] - head_radius,
            head_center[0] + head_radius, head_center[1] + head_radius
        ], fill=secondary_color, outline=primary_color, width=1)
        
        # Body
        body_width = int(12 * scale)
        body_height = int(16 * scale)
        body_top = y_offset + head_radius + 2
        body_left = x_offset - body_width // 2
        body_right = x_offset + body_width // 2
        
        draw.rounded_rectangle([
            body_left, body_top,
            body_right, body_top + body_height
        ], radius=int(3 * scale), fill=primary_color, outline=primary_color)
    
    # Draw three people representing clients
    draw_person(20, 16, 0.8)  # Left person (smaller)
    draw_person(32, 12, 1.0)  # Center person (larger)
    draw_person(44, 16, 0.8)  # Right person (smaller)
    
    # Draw connecting lines to show relationship
    draw.line([26, 28, 38, 28], fill=secondary_color, width=2)
    
    # Add handshake symbol at bottom
    handshake_y = 50
    draw.ellipse([28, handshake_y, 36, handshake_y + 8], fill=accent_color, outline=primary_color, width=2)
    draw.arc([30, handshake_y + 2, 34, handshake_y + 6], 0, 180, fill=primary_color, width=2)
    
    return image

def save_icons():
    """Save the icons to the assets folder"""
    assets_path = Path("assets/icons")
    assets_path.mkdir(parents=True, exist_ok=True)
    
    # Create and save businesswoman icon
    businesswoman_icon = create_businesswoman_icon()
    businesswoman_path = assets_path / "businesswoman.png"
    businesswoman_icon.save(businesswoman_path, "PNG")
    print(f"✅ Created businesswoman icon: {businesswoman_path}")
    
    # Create and save client icon
    client_icon = create_client_icon()
    client_path = assets_path / "client.png"
    client_icon.save(client_path, "PNG")
    print(f"✅ Created client icon: {client_path}")
    
    return businesswoman_path, client_path

if __name__ == "__main__":
    print("Creating customer-related icons...")
    businesswoman_path, client_path = save_icons()
    print("✅ All customer icons created successfully!")
