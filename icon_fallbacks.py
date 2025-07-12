"""
Optimierte Icon-Fallback-Konfiguration für bessere GUI-Darstellung
"""

# Verbesserte Icon-zu-Emoji-Mappings für alle fehlenden Icons
ICON_EMOJI_MAPPINGS = {
    # Workflow-Icons
    "play": "🚀",
    "document-text": "📄", 
    "magnifying-glass": "🔍",
    "check-circle": "✅",
    "folder-open": "📂",
    
    # Allgemeine Icons
    "businesswoman": "👤",
    "client": "👥",
    "upload": "📤",
    "file": "📁",
    "home": "🏠",
    "settings": "⚙️",
    "theme": "🎨",
    "help": "❓",
    "export": "💾",
    "arrow_left": "←",
    "user-group-woman-man": "👥",
    
    # Workflow-spezifische Icons
    "angebots_workflow": "📊",
    "pruefung_workflow": "🔍", 
    "finalisierung_workflow": "✅",
    "projekt_workflow": "📂",
    
    # Standard-Fallback
    "default": "🔧"
}

def get_emoji_for_icon(icon_name):
    """Gibt das passende Emoji für einen Icon-Namen zurück"""
    return ICON_EMOJI_MAPPINGS.get(icon_name, ICON_EMOJI_MAPPINGS["default"])
