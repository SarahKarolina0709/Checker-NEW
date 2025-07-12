#!/usr/bin/env python3
"""
Erstellt weitere moderne Icons für die Checker App
Ergänzt die businesswoman und client Icons um weitere professionelle Icons
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_modern_icons():
    """Erstellt weitere moderne, professionelle Icons"""
    
    assets_path = os.path.join(os.path.dirname(__file__), "assets", "icons")
    os.makedirs(assets_path, exist_ok=True)
    
    icon_size = (64, 64)
    
    # 1. Team/Collaboration Icon (für Team-Workflows)
    def create_team_icon():
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Drei Personen-Silhouetten
        # Person 1 (links)
        draw.ellipse([8, 12, 24, 28], fill='#4A90E2')
        draw.rectangle([6, 26, 26, 50], fill='#4A90E2')
        
        # Person 2 (mitte, etwas größer)
        draw.ellipse([24, 8, 40, 24], fill='#5CB3CC')
        draw.rectangle([22, 22, 42, 52], fill='#5CB3CC')
        
        # Person 3 (rechts)
        draw.ellipse([38, 12, 54, 28], fill='#7B68EE')
        draw.rectangle([36, 26, 56, 50], fill='#7B68EE')
        
        return img
    
    # 2. Document/Report Icon (für Berichte)
    def create_report_icon():
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Dokument-Hintergrund
        draw.rectangle([12, 8, 52, 56], fill='white', outline='#E0E0E0', width=2)
        
        # Linien für Text
        for y in [18, 24, 30, 36, 42]:
            draw.rectangle([16, y, 48, y+2], fill='#B0B0B0')
        
        # Diagramm/Chart unten
        draw.rectangle([16, 46, 20, 52], fill='#4A90E2')
        draw.rectangle([22, 44, 26, 52], fill='#5CB3CC')
        draw.rectangle([28, 42, 32, 52], fill='#7B68EE')
        draw.rectangle([34, 48, 38, 52], fill='#FF6B6B')
        
        return img
    
    # 3. Quality/Shield Icon (für Qualitätssicherung)
    def create_quality_icon():
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Schild-Form
        shield_points = [
            (32, 8), (20, 16), (20, 36), (32, 56), (44, 36), (44, 16)
        ]
        draw.polygon(shield_points, fill='#4CAF50', outline='#2E7D32', width=2)
        
        # Häkchen
        check_points = [(26, 32), (30, 36), (38, 24)]
        draw.polygon(check_points, fill='white', outline='white', width=3)
        
        return img
    
    # 4. Translation/Languages Icon
    def create_translation_icon():
        img = Image.new('RGBA', icon_size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Globus
        draw.ellipse([16, 16, 48, 48], fill='#4A90E2', outline='#2E5C8A', width=2)
        
        # Längengrade
        draw.ellipse([20, 20, 44, 44], outline='white', width=1)
        draw.ellipse([24, 24, 40, 40], outline='white', width=1)
        
        # Breitengrade
        draw.arc([16, 16, 48, 48], 0, 180, fill='white', width=1)
        draw.line([16, 32, 48, 32], fill='white', width=1)
        
        # Buchstaben A und B
        try:
            font = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
        
        draw.text((8, 8), "A", fill='#FF6B6B', font=font)
        draw.text((50, 48), "B", fill='#4CAF50', font=font)
        
        return img
    
    # Icons erstellen und speichern
    icons = {
        "team.png": create_team_icon(),
        "report.png": create_report_icon(),
        "quality.png": create_quality_icon(),
        "translation.png": create_translation_icon()
    }
    
    for filename, img in icons.items():
        filepath = os.path.join(assets_path, filename)
        img.save(filepath, "PNG")
        print(f"✅ Icon erstellt: {filepath}")

if __name__ == "__main__":
    print("🎨 Erstelle weitere moderne Icons...")
    create_modern_icons()
    print("✅ Alle Icons erfolgreich erstellt!")
