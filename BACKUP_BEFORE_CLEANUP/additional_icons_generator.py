"""
Zusätzliche Icons für spezielle Anwendungsfälle.
"""

import os
from PIL import Image, ImageDraw

class AdditionalIconGenerator:
    def __init__(self, icons_dir="icons"):
        self.icons_dir = icons_dir
        self.size = (32, 32)
        self.bg_color = (255, 255, 255, 0)  # Transparent
        self.icon_color = (59, 130, 246)  # Primary blue
        
    def create_icon(self, name, draw_func):
        """Erstellt ein Icon mit der gegebenen Zeichenfunktion"""
        try:
            img = Image.new('RGBA', self.size, self.bg_color)
            draw = ImageDraw.Draw(img)
            draw_func(draw, self.size, self.icon_color)
            
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            img.save(icon_path, "PNG")
            print(f"Created icon: {icon_path}")
            return True
        except Exception as e:
            print(f"Error creating icon {name}: {e}")
            return False
    
    def draw_notification(self, draw, size, color):
        """Zeichnet ein Benachrichtigungs-Icon"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Glocke
        bell_top = center_y - 8
        bell_bottom = center_y + 4
        bell_width = 12
        
        # Glocken-Körper
        points = [
            (center_x - bell_width//2, bell_bottom),
            (center_x - bell_width//3, bell_top + 2),
            (center_x + bell_width//3, bell_top + 2),
            (center_x + bell_width//2, bell_bottom)
        ]
        draw.polygon(points, fill=color)
        
        # Glocken-Aufhängung
        draw.ellipse([center_x - 2, bell_top - 2, center_x + 2, bell_top + 2], fill=color)
        
        # Glocken-Klöppel
        draw.ellipse([center_x - 1, bell_bottom, center_x + 1, bell_bottom + 2], fill=color)
    
    def draw_calendar(self, draw, size, color):
        """Zeichnet ein Kalender-Icon"""
        w, h = size
        
        # Kalender-Rahmen
        draw.rectangle([6, 8, w - 6, h - 4], fill=(255, 255, 255), outline=color, width=2)
        
        # Kalender-Header
        draw.rectangle([6, 8, w - 6, 16], fill=color)
        
        # Kalender-Bindung (Spiralen)
        for x in [10, 14, 18, 22]:
            if x < w - 6:
                draw.ellipse([x - 1, 4, x + 1, 8], fill=color)
        
        # Kalender-Gitter
        for y in [18, 22, 26]:
            if y < h - 4:
                draw.line([8, y, w - 8, y], fill=color, width=1)
        
        for x in [12, 16, 20]:
            if x < w - 6:
                draw.line([x, 16, x, h - 6], fill=color, width=1)
    
    def draw_clipboard(self, draw, size, color):
        """Zeichnet ein Clipboard-Icon"""
        w, h = size
        
        # Clipboard-Basis
        draw.rectangle([6, 6, w - 6, h - 4], fill=(255, 255, 255), outline=color, width=2)
        
        # Clipboard-Clip
        draw.rectangle([center_x - 4, 4, center_x + 4, 10], fill=color)
        draw.rectangle([center_x - 3, 5, center_x + 3, 9], fill=(255, 255, 255))
        
        center_x = w // 2
        
        # Textzeilen
        for y in [14, 18, 22]:
            if y < h - 6:
                draw.line([8, y, w - 8, y], fill=color, width=1)
    
    def draw_certificate(self, draw, size, color):
        """Zeichnet ein Zertifikat-Icon"""
        w, h = size
        center_x = w // 2
        
        # Zertifikat-Basis
        draw.rectangle([4, 6, w - 4, h - 8], fill=(255, 255, 255), outline=color, width=2)
        
        # Siegel
        draw.ellipse([center_x - 6, h - 14, center_x + 6, h - 2], fill=color)
        draw.ellipse([center_x - 4, h - 12, center_x + 4, h - 4], fill=(255, 255, 255))
        
        # Bänder
        band_points = [
            (center_x - 2, h - 8),
            (center_x - 4, h - 2),
            (center_x, h - 4),
            (center_x + 4, h - 2),
            (center_x + 2, h - 8)
        ]
        draw.polygon(band_points, fill=(220, 53, 69))  # Rot
        
        # Textzeilen
        for y in [10, 14, 18]:
            draw.line([6, y, w - 6, y], fill=color, width=1)
    
    def draw_tag(self, draw, size, color):
        """Zeichnet ein Tag-Icon"""
        w, h = size
        
        # Tag-Form
        tag_points = [
            (6, 8),
            (w - 10, 8),
            (w - 6, 12),
            (w - 10, 16),
            (6, 16)
        ]
        draw.polygon(tag_points, fill=color)
        
        # Tag-Loch
        draw.ellipse([8, 10, 12, 14], fill=(255, 255, 255))
        
        # Tag-String
        draw.line([6, 12, 2, 12], fill=color, width=2)
    
    def draw_pin(self, draw, size, color):
        """Zeichnet ein Pin/Standort-Icon"""
        w, h = size
        center_x = w // 2
        
        # Pin-Körper (Tropfen-Form)
        pin_points = [
            (center_x, 6),  # Spitze
            (center_x - 6, 14),  # Links
            (center_x - 4, 18),  # Links unten
            (center_x, 20),  # Mitte unten
            (center_x + 4, 18),  # Rechts unten
            (center_x + 6, 14)  # Rechts
        ]
        draw.polygon(pin_points, fill=color)
        
        # Pin-Punkt
        draw.ellipse([center_x - 3, 10, center_x + 3, 16], fill=(255, 255, 255))
    
    def generate_additional_icons(self):
        """Generiert zusätzliche nützliche Icons"""
        icons_to_create = [
            ("notification", self.draw_notification),
            ("calendar", self.draw_calendar),
            ("clipboard", self.draw_clipboard),
            ("certificate", self.draw_certificate),
            ("tag", self.draw_tag),
            ("pin", self.draw_pin),
        ]
        
        created_count = 0
        for name, draw_func in icons_to_create:
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            
            # Überspringe, wenn Icon bereits existiert
            if os.path.exists(icon_path):
                print(f"Icon {name} already exists, skipping")
                continue
                
            if self.create_icon(name, draw_func):
                created_count += 1
        
        print(f"\nCreated {created_count} additional icons")
        return created_count

if __name__ == "__main__":
    generator = AdditionalIconGenerator()
    generator.generate_additional_icons()
    print("\nAdditional icon generation complete!")
