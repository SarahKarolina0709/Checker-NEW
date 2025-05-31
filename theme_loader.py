import json
import os
from PIL import Image, ImageTk

def lade_theme(theme_file="themes.json"):
    with open(theme_file, "r") as f:
        return json.load(f)

def hex_to_rgb(h):
    return tuple(int(h.strip("#")[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(t):
    return "#%02x%02x%02x" % t

def detect_mode():
    from datetime import datetime
    h = datetime.now().hour
    return "dark" if h >= 18 or h < 7 else "light"

def get_effective_mode(manual_mode):
    return detect_mode() if manual_mode == "auto" else manual_mode

def lade_icons(mode_name, master=None):
    return {}
