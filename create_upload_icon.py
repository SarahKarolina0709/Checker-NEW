#!/usr/bin/env python3
"""
Erstellt ein Upload-Icon für die Checker App
"""

import os
from PIL import Image, ImageDraw

def create_upload_icon():
    """Erstellt ein einfaches Upload-Icon"""
    
    # Icon-Größe
    size = 32
    
    # Neues Bild erstellen
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Pfeil nach oben zeichnen
    # Pfeilspitze
    arrow_tip = [(size//2, 4), (size//2 - 6, 12), (size//2 + 6, 12)]
    draw.polygon(arrow_tip, fill=(100, 100, 100, 255))
    
    # Pfeilschaft
    shaft_width = 4
    shaft_left = size//2 - shaft_width//2
    shaft_right = size//2 + shaft_width//2
    draw.rectangle([shaft_left, 10, shaft_right, 24], fill=(100, 100, 100, 255))
    
    # Basis-Linie
    draw.rectangle([6, 26, size-6, 28], fill=(100, 100, 100, 255))
    
    # Icon speichern
    icon_path = os.path.join('icons', 'upload.png')
    img.save(icon_path)
    print(f"Upload-Icon erstellt: {icon_path}")
    
    return icon_path

if __name__ == "__main__":
    # Prüfe ob icons-Ordner existiert
    if not os.path.exists('icons'):
        print("Icons-Ordner nicht gefunden!")
        exit(1)
    
    # Erstelle Upload-Icon
    create_upload_icon()
    print("Upload-Icon erfolgreich erstellt!")
