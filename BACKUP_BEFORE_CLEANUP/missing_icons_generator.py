"""
Icon-Generator für fehlende Icons in der Checker-App.
Erstellt einfache, einheitliche SVG-Icons und konvertiert sie zu PNG.
"""

import os
from PIL import Image, ImageDraw, ImageFont

class IconGenerator:
    def __init__(self, icons_dir="icons"):
        self.icons_dir = icons_dir
        self.size = (32, 32)  # Standard-Größe für alle Icons
        self.bg_color = (255, 255, 255, 0)  # Transparent
        self.icon_color = (59, 130, 246)  # Primary blue
        
        # Stelle sicher, dass der Icons-Ordner existiert
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)
    
    def create_simple_icon(self, name, draw_func):
        """Erstellt ein einfaches Icon mit der gegebenen Zeichenfunktion"""
        try:
            # Erstelle neue Bilddatei
            img = Image.new('RGBA', self.size, self.bg_color)
            draw = ImageDraw.Draw(img)
            
            # Rufe die spezifische Zeichenfunktion auf
            draw_func(draw, self.size, self.icon_color)
            
            # Speichere das Icon
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            img.save(icon_path, "PNG")
            print(f"Created icon: {icon_path}")
            return True
            
        except Exception as e:
            print(f"Error creating icon {name}: {e}")
            return False
    
    def draw_rocket(self, draw, size, color):
        """Zeichnet ein Raketen-Icon"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Raketen-Körper
        body_points = [
            (center_x, 4),  # Spitze
            (center_x - 6, center_y),  # Links
            (center_x - 4, h - 8),  # Links unten
            (center_x + 4, h - 8),  # Rechts unten
            (center_x + 6, center_y),  # Rechts
        ]
        draw.polygon(body_points, fill=color)
        
        # Flamme
        flame_points = [
            (center_x - 4, h - 8),
            (center_x, h - 2),
            (center_x + 4, h - 8)
        ]
        draw.polygon(flame_points, fill=(255, 165, 0))  # Orange
        
        # Fenster
        draw.ellipse([center_x - 2, center_y - 4, center_x + 2, center_y], fill=(255, 255, 255))
    
    def draw_quality(self, draw, size, color):
        """Zeichnet ein Qualitäts-Icon (Schild mit Häkchen)"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Schild
        shield_points = [
            (center_x, 4),
            (center_x + 8, 8),
            (center_x + 8, h - 8),
            (center_x, h - 4),
            (center_x - 8, h - 8),
            (center_x - 8, 8)
        ]
        draw.polygon(shield_points, fill=color)
        
        # Häkchen
        check_points = [
            (center_x - 4, center_y),
            (center_x - 1, center_y + 3),
            (center_x + 4, center_y - 2)
        ]
        draw.line(check_points[0] + check_points[1], fill=(255, 255, 255), width=2)
        draw.line(check_points[1] + check_points[2], fill=(255, 255, 255), width=2)
    
    def draw_pdf_file(self, draw, size, color):
        """Zeichnet ein PDF-File Icon"""
        w, h = size
        
        # Dokument
        draw.rectangle([6, 4, w - 6, h - 4], fill=(255, 255, 255), outline=color, width=2)
        
        # Gefaltete Ecke
        fold_points = [(w - 12, 4), (w - 6, 10), (w - 12, 10)]
        draw.polygon(fold_points, fill=color)
        
        # PDF Text
        try:
            # Versuche, eine Schrift zu laden
            font = ImageFont.load_default()
            draw.text((8, h - 16), "PDF", fill=color, font=font)
        except:
            # Fallback ohne Schrift
            draw.text((8, h - 16), "PDF", fill=color)
    
    def draw_doc_file(self, draw, size, color):
        """Zeichnet ein DOC-File Icon"""
        w, h = size
        
        # Dokument
        draw.rectangle([6, 4, w - 6, h - 4], fill=(255, 255, 255), outline=color, width=2)
        
        # Gefaltete Ecke
        fold_points = [(w - 12, 4), (w - 6, 10), (w - 12, 10)]
        draw.polygon(fold_points, fill=color)
        
        # DOC Text
        try:
            font = ImageFont.load_default()
            draw.text((8, h - 16), "DOC", fill=color, font=font)
        except:
            draw.text((8, h - 16), "DOC", fill=color)
    
    def draw_txt_file(self, draw, size, color):
        """Zeichnet ein TXT-File Icon"""
        w, h = size
        
        # Dokument
        draw.rectangle([6, 4, w - 6, h - 4], fill=(255, 255, 255), outline=color, width=2)
        
        # Textzeilen
        for i in range(3):
            y = 10 + i * 4
            draw.line([8, y, w - 8, y], fill=color, width=1)
        
        # TXT Text
        try:
            font = ImageFont.load_default()
            draw.text((8, h - 16), "TXT", fill=color, font=font)
        except:
            draw.text((8, h - 16), "TXT", fill=color)
    
    def draw_upload(self, draw, size, color):
        """Zeichnet ein Upload Icon (Pfeil nach oben)"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Pfeil nach oben
        arrow_points = [
            (center_x, 6),  # Spitze
            (center_x - 6, 14),  # Links
            (center_x - 2, 14),  # Links innen
            (center_x - 2, h - 6),  # Links unten
            (center_x + 2, h - 6),  # Rechts unten
            (center_x + 2, 14),  # Rechts innen
            (center_x + 6, 14)  # Rechts
        ]
        draw.polygon(arrow_points, fill=color)
    
    def draw_download(self, draw, size, color):
        """Zeichnet ein Download Icon (Pfeil nach unten)"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Pfeil nach unten
        arrow_points = [
            (center_x, h - 6),  # Spitze
            (center_x - 6, h - 14),  # Links
            (center_x - 2, h - 14),  # Links innen
            (center_x - 2, 6),  # Links oben
            (center_x + 2, 6),  # Rechts oben
            (center_x + 2, h - 14),  # Rechts innen
            (center_x + 6, h - 14)  # Rechts
        ]
        draw.polygon(arrow_points, fill=color)
    
    def draw_import(self, draw, size, color):
        """Zeichnet ein Import Icon"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Box
        draw.rectangle([4, center_y - 4, w - 4, h - 4], fill=None, outline=color, width=2)
        
        # Pfeil hinein
        arrow_points = [
            (center_x, 4),  # Spitze
            (center_x - 4, 10),  # Links
            (center_x - 1, 10),  # Links innen
            (center_x - 1, center_y - 4),  # Links bis Box
            (center_x + 1, center_y - 4),  # Rechts bis Box
            (center_x + 1, 10),  # Rechts innen
            (center_x + 4, 10)  # Rechts
        ]
        draw.polygon(arrow_points, fill=color)
    
    def draw_link(self, draw, size, color):
        """Zeichnet ein Link/Connect Icon"""
        w, h = size
        center_x, center_y = w // 2, h // 2
        
        # Erste Kette
        draw.ellipse([6, center_y - 3, 12, center_y + 3], fill=None, outline=color, width=2)
        
        # Zweite Kette
        draw.ellipse([w - 12, center_y - 3, w - 6, center_y + 3], fill=None, outline=color, width=2)
        
        # Verbindung
        draw.line([12, center_y, w - 12, center_y], fill=color, width=2)
    
    def draw_chain(self, draw, size, color):
        """Zeichnet ein Chain Icon"""
        self.draw_link(draw, size, color)  # Gleich wie Link
    
    def generate_missing_icons(self):
        """Generiert alle fehlenden Icons"""
        icons_to_create = [
            ("rocket", self.draw_rocket),
            ("quality", self.draw_quality),
            ("pdf-file", self.draw_pdf_file),
            ("doc-file", self.draw_doc_file),
            ("txt-file", self.draw_txt_file),
            ("upload", self.draw_upload),
            ("download", self.draw_download),
            ("import", self.draw_import),
            ("link", self.draw_link),
            ("chain", self.draw_chain),
        ]
        
        created_count = 0
        for name, draw_func in icons_to_create:
            icon_path = os.path.join(self.icons_dir, f"{name}.png")
            
            # Überspringe, wenn Icon bereits existiert
            if os.path.exists(icon_path):
                print(f"Icon {name} already exists, skipping")
                continue
                
            if self.create_simple_icon(name, draw_func):
                created_count += 1
        
        print(f"\nCreated {created_count} new icons")
        return created_count

if __name__ == "__main__":
    # Erstelle Generator und generiere fehlende Icons
    generator = IconGenerator()
    generator.generate_missing_icons()
    
    print("\nIcon generation complete!")
    print(f"Icons directory: {os.path.abspath(generator.icons_dir)}")
