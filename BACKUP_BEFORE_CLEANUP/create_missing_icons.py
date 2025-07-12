
"""
Script zum Erstellen der wichtigsten fehlenden Icons für die Checker-App
Erstellt professionelle PNG-Icons anstatt Emoji-basierte Icons
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

def create_icon(name, emoji, path="icons", size=(32, 32)):
    """Legacy-Funktion für Emoji-Icons (wird beibehalten für Kompatibilität)"""
    if not os.path.exists(path):
        os.makedirs(path)
    
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("seguiemj.ttf", 16)
    except IOError:
        font = ImageFont.load_default()

    draw.text((size[0]//4, size[1]//4), emoji, font=font, fill="black")
    
    image.save(os.path.join(path, f"{name}.png"))

def create_professional_icon(name, draw_func, path="icons", size=128):
    """Erstellt professionelle Icons mit Zeichenfunktionen"""
    if not os.path.exists(path):
        os.makedirs(path)
    
    icon_path = os.path.join(path, f"{name}.png")
    
    # Nur erstellen wenn nicht vorhanden
    if os.path.exists(icon_path):
        print(f"⏭️  Bereits vorhanden: {name}.png")
        return False
    
    try:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Icon-spezifische Zeichenfunktion aufrufen
        draw_func(draw, size)
        
        img.save(icon_path, "PNG")
        print(f"✅ Erstellt: {name}.png")
        return True
    except Exception as e:
        print(f"❌ Fehler bei {name}: {e}")
        return False

# Icon-Zeichenfunktionen

def draw_arrow_left(draw, size):
    """Zeichnet einen modernen Zurück-Pfeil"""
    center_x, center_y = size // 2, size // 2
    arrow_size = size // 3
    color = (37, 99, 235, 255)  # Blau #2563EB
    
    # Pfeil-Punkte definieren
    points = [
        (center_x + arrow_size//2, center_y - arrow_size//2),  # Oben rechts
        (center_x - arrow_size//2, center_y),                  # Links (Spitze)
        (center_x + arrow_size//2, center_y + arrow_size//2),  # Unten rechts
    ]
    
    draw.polygon(points, fill=color)

def draw_user(draw, size):
    """Zeichnet ein modernes Benutzer-Icon"""
    center_x, center_y = size // 2, size // 2
    color = (37, 99, 235, 255)  # Blau
    
    # Kopf (Kreis)
    head_radius = size // 8
    head_top = center_y - size // 3
    draw.ellipse([
        center_x - head_radius, head_top - head_radius,
        center_x + head_radius, head_top + head_radius
    ], fill=color)
    
    # Körper (unterer Kreis/Oval)
    body_width = size // 3
    body_height = size // 4
    body_top = center_y - size // 12
    draw.ellipse([
        center_x - body_width//2, body_top,
        center_x + body_width//2, body_top + body_height
    ], fill=color)

def draw_workflow(draw, size):
    """Zeichnet ein Workflow-Icon (Flussdiagramm)"""
    rect_width = size // 6
    rect_height = size // 8
    spacing = size // 4
    color = (37, 99, 235, 255)  # Blau
    
    # Drei verbundene Rechtecke
    x1 = size // 6
    y1 = size // 2 - rect_height // 2
    draw.rectangle([x1, y1, x1 + rect_width, y1 + rect_height], fill=color)
    
    x2 = x1 + rect_width + spacing
    draw.rectangle([x2, y1, x2 + rect_width, y1 + rect_height], fill=color)
    
    x3 = x2 + rect_width + spacing
    draw.rectangle([x3, y1, x3 + rect_width, y1 + rect_height], fill=color)
    
    # Verbindungslinien
    line_y = size // 2
    draw.rectangle([x1 + rect_width, line_y - 2, x2, line_y + 2], fill=color)
    draw.rectangle([x2 + rect_width, line_y - 2, x3, line_y + 2], fill=color)
    
    # Pfeile
    arrow_size = 6
    arrow1_x = x1 + rect_width + spacing//2
    draw.polygon([
        (arrow1_x - arrow_size, line_y - arrow_size//2),
        (arrow1_x, line_y),
        (arrow1_x - arrow_size, line_y + arrow_size//2)
    ], fill=color)
    
    arrow2_x = x2 + rect_width + spacing//2
    draw.polygon([
        (arrow2_x - arrow_size, line_y - arrow_size//2),
        (arrow2_x, line_y),
        (arrow2_x - arrow_size, line_y + arrow_size//2)
    ], fill=color)

def draw_analytics(draw, size):
    """Zeichnet ein Analytics-Icon (Balkendiagramm)"""
    color = (37, 99, 235, 255)  # Blau
    bar_width = size // 8
    spacing = size // 12
    base_y = size - size // 4
    start_x = size // 4
    
    # Verschiedene Balkenhöhen
    heights = [size//6, size//3, size//4, size//2, size//3]
    
    for i, height in enumerate(heights):
        x = start_x + i * (bar_width + spacing)
        draw.rectangle([x, base_y - height, x + bar_width, base_y], fill=color)
    
    # Achsen
    axis_color = (71, 85, 105, 255)  # Grau
    draw.rectangle([start_x - 4, size//6, start_x, base_y + 2], fill=axis_color)
    draw.rectangle([start_x - 4, base_y, start_x + len(heights) * (bar_width + spacing), base_y + 4], fill=axis_color)

def draw_error(draw, size):
    """Zeichnet ein Error-Icon (X in Kreis)"""
    center_x, center_y = size // 2, size // 2
    radius = size // 3
    
    # Roter Kreis
    draw.ellipse([
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius
    ], fill=(239, 68, 68, 255))  # Rot #EF4444
    
    # Weißes X
    x_size = radius // 2
    line_width = 8
    
    draw.line([
        (center_x - x_size, center_y - x_size),
        (center_x + x_size, center_y + x_size)
    ], fill=(255, 255, 255, 255), width=line_width)
    
    draw.line([
        (center_x - x_size, center_y + x_size),
        (center_x + x_size, center_y - x_size)
    ], fill=(255, 255, 255, 255), width=line_width)

def draw_success(draw, size):
    """Zeichnet ein Success-Icon (Häkchen in Kreis)"""
    center_x, center_y = size // 2, size // 2
    radius = size // 3
    
    # Grüner Kreis
    draw.ellipse([
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius
    ], fill=(16, 185, 129, 255))  # Grün #10B981
    
    # Weißes Häkchen
    check_size = radius // 2
    line_width = 8
    
    check_points = [
        (center_x - check_size//2, center_y),
        (center_x - check_size//4, center_y + check_size//2),
        (center_x + check_size//2, center_y - check_size//2)
    ]
    
    draw.line([check_points[0], check_points[1]], fill=(255, 255, 255, 255), width=line_width)
    draw.line([check_points[1], check_points[2]], fill=(255, 255, 255, 255), width=line_width)

def draw_help_icon(draw, size):
    """Zeichnet ein Hilfe-Icon (Fragezeichen in Kreis)"""
    center_x, center_y = size // 2, size // 2
    radius = size // 3
    
    # Blauer Kreis
    draw.ellipse([
        center_x - radius, center_y - radius,
        center_x + radius, center_y + radius
    ], fill=(37, 99, 235, 255))  # Blau #2563EB
    
    # Weißes Fragezeichen
    try:
        font = ImageFont.truetype("arial.ttf", size//3)
    except:
        font = ImageFont.load_default()
    
    text = "?"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    text_x = center_x - text_width // 2
    text_y = center_y - text_height // 2
    
    draw.text((text_x, text_y), text, fill=(255, 255, 255, 255), font=font)

def draw_theme(draw, size):
    """Zeichnet ein Theme-Icon (Palette)"""
    center_x, center_y = size // 2, size // 2
    radius = size // 3
    
    colors = [
        (37, 99, 235, 255),   # Blau
        (16, 185, 129, 255),  # Grün
        (245, 158, 11, 255),  # Orange
        (239, 68, 68, 255),   # Rot
        (139, 69, 19, 255),   # Braun
        (147, 51, 234, 255),  # Lila
    ]
    
    angle_per_segment = 360 // len(colors)
    for i, color in enumerate(colors):
        start_angle = i * angle_per_segment
        end_angle = (i + 1) * angle_per_segment
        
        draw.pieslice([
            center_x - radius, center_y - radius,
            center_x + radius, center_y + radius
        ], start_angle, end_angle, fill=color)
    
    # Weißer Kreis in der Mitte
    inner_radius = radius // 3
    draw.ellipse([
        center_x - inner_radius, center_y - inner_radius,
        center_x + inner_radius, center_y + inner_radius
    ], fill=(255, 255, 255, 255))

def draw_refresh(draw, size):
    """Zeichnet ein Refresh-Icon (Kreispfeil)"""
    center_x, center_y = size // 2, size // 2
    radius = size // 3
    color = (37, 99, 235, 255)  # Blau
    
    # Kreisbogen (vereinfacht als Ellipse mit Lücke)
    outer_radius = radius
    inner_radius = radius - size // 16
    
    # Hauptkreis
    draw.ellipse([
        center_x - outer_radius, center_y - outer_radius,
        center_x + outer_radius, center_y + outer_radius
    ], outline=color, width=size//16)
    
    # Pfeilspitze
    arrow_x = center_x + radius
    arrow_y = center_y
    arrow_size = size // 12
    
    draw.polygon([
        (arrow_x, arrow_y),
        (arrow_x - arrow_size, arrow_y - arrow_size),
        (arrow_x - arrow_size, arrow_y + arrow_size)
    ], fill=color)

def draw_save(draw, size):
    """Zeichnet ein Save-Icon (Diskette)"""
    margin = size // 6
    color = (37, 99, 235, 255)  # Blau
    
    # Hauptrechteck (Diskette)
    draw.rectangle([margin, margin, size - margin, size - margin], fill=color)
    
    # Oberer Bereich (Label-Bereich)
    label_height = size // 6
    draw.rectangle([
        margin, margin,
        size - margin, margin + label_height
    ], fill=(71, 85, 105, 255))
    
    # Metallclip oben rechts
    clip_size = size // 12
    draw.rectangle([
        size - margin - clip_size, margin,
        size - margin, margin + clip_size
    ], fill=(156, 163, 175, 255))

def draw_export(draw, size):
    """Zeichnet ein Export-Icon (Pfeil aus Box)"""
    color = (37, 99, 235, 255)  # Blau
    
    # Box (Container)
    box_margin = size // 4
    box_rect = [box_margin, box_margin + size//6, size - box_margin, size - box_margin]
    draw.rectangle(box_rect, outline=color, width=4)
    
    # Pfeil nach oben/außen
    arrow_center_x = size // 2
    arrow_bottom = box_margin + size//6
    arrow_top = box_margin
    arrow_width = size // 8
    
    # Pfeilschaft
    draw.rectangle([
        arrow_center_x - arrow_width//4, arrow_top + size//12,
        arrow_center_x + arrow_width//4, arrow_bottom
    ], fill=color)
    
    # Pfeilspitze
    draw.polygon([
        (arrow_center_x, arrow_top),
        (arrow_center_x - arrow_width//2, arrow_top + size//12),
        (arrow_center_x + arrow_width//2, arrow_top + size//12)
    ], fill=color)

def draw_person(draw, size):
    """Alias für draw_user - Zeichnet Benutzer-Icon"""
    draw_user(draw, size)

def draw_folder_icon(draw, size):
    """Zeichnet ein Ordner-Icon"""
    color = (245, 158, 11, 255)  # Orange
    margin = size // 6
    
    # Ordner-Grundform
    folder_width = size - 2 * margin
    folder_height = size // 2
    folder_y = size // 2 - folder_height // 2
    
    # Hauptordner
    draw.rectangle([
        margin, folder_y,
        margin + folder_width, folder_y + folder_height
    ], fill=color)
    
    # Ordner-Tab
    tab_width = folder_width // 3
    tab_height = folder_height // 4
    draw.rectangle([
        margin, folder_y - tab_height,
        margin + tab_width, folder_y
    ], fill=color)

def create_all_professional_icons():
    """Erstellt alle professionellen Icons"""
    icons_to_create = [
        ("arrow_left", draw_arrow_left),
        ("user", draw_user),
        ("person", draw_person),  # Alias für user
        ("workflow", draw_workflow),
        ("analytics", draw_analytics),
        ("error", draw_error),
        ("success", draw_success),
        ("help_icon", draw_help_icon),
        ("theme", draw_theme),
        ("refresh", draw_refresh),
        ("save", draw_save),
        ("export", draw_export),
        ("folder_icon", draw_folder_icon),
    ]
    
    print("🎨 Erstelle professionelle Icons für die Checker-App...")
    print("=" * 60)
    
    created_count = 0
    for icon_name, draw_func in icons_to_create:
        if create_professional_icon(icon_name, draw_func):
            created_count += 1
    
    print("=" * 60)
    print(f"📊 {created_count} neue professionelle Icons erstellt!")
    return created_count

if __name__ == "__main__":
    # Zuerst professionelle Icons erstellen
    created_professional = create_all_professional_icons()
    
    print("\n" + "=" * 60)
    print("🔄 Erstelle verbleibende Emoji-basierte Icons als Fallback...")
    
    # Dann Emoji-basierte Icons für die verbleibenden
    icons_to_create = {
        "file_icon": "�",
        "export_icon": "📤", 
        "report_icon": "📊",
        "analyze_icon": "�",
        "save_icon": "💾",
        "load_icon": "📥",
        "options_icon": "🔧",
        "quit_icon": "❌",
        "star": "⭐",
    }

    created_emoji = 0
    for name, emoji in icons_to_create.items():
        icon_path = os.path.join("icons", f"{name}.png")
        if not os.path.exists(icon_path):
            create_icon(name, emoji)
            print(f"✅ Erstellt: {name}.png (Emoji)")
            created_emoji += 1
        else:
            print(f"⏭️  Bereits vorhanden: {name}.png")

    print("=" * 60)
    print(f"✅ Icon-Erstellung abgeschlossen!")
    print(f"📊 Gesamt: {created_professional} professionelle + {created_emoji} Emoji-Icons erstellt")
