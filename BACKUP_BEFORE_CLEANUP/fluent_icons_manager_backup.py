"""
Fluent Icons Integration für die Checker-App
Ermöglicht die Verwendung von Fluent Icons und dynamische Icon-Anpassung
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union, Tuple
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - using emoji fallback only")

class FluentIconManager:
    """
    Manager für Fluent Icons Integration
    Ermöglicht dynamische Icon-Auswahl und -Anpassung
    """
    
    # Standard Fluent Icons Mapping
    FLUENT_ICONS = {
        # Navigation & Actions
        'home': '🏠',
        'search': '🔍', 
        'settings': '⚙️',
        'help': '❓',
        'close': '❌',
        'minimize': '➖',
        'maximize': '⬜',
        
        # Files & Documents
        'file': '📄',
        'folder': '📁',
        'folder_open': '📂',
        'document': '📋',
        'save': '💾',
        'export': '📤',
        'import': '📥',
        'upload': '⬆️',
        'download': '⬇️',
        
        # Project Management
        'project': '📁',
        'projects': '📋',
        'task': '✓',
        'help': '❓',
        
        # Workflows & Processes
        'workflow': '⚡',
        'process': '🔄',
        'check': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'success': '✅',
        
        # User & Customer
        'user': '👤',
        'customer': '👥',
        'profile': '👤',
        'account': '🔐',
        
        # Business & Analytics
        'analytics': '📊',
        'chart': '📈',
        'report': '📋',
        'project': '📁',
        'task': '✓',
        
        # Status & Feedback
        'loading': '⟳',
        'spinner': '🔄',
        'progress': '📊',
        'complete': '✅',
        'pending': '⏳',
        
        # UI Elements
        'menu': '☰',
        'more': '⋯',
        'expand': '▼',
        'collapse': '▲',
        'arrow_right': '→',
        'arrow_left': '←',
        'arrow_up': '↑',
        'arrow_down': '↓',
        
        # Dark/Light Mode
        'light_mode': '☀️',
        'dark_mode': '🌙',
        'theme': '🎨',
        
        # Communication
        'mail': '📧',
        'notification': '🔔',
        'message': '💬',
        
        # Quality & Review
        'quality': '⭐',
        'review': '🔍',
        'approval': '✅',
        'feedback': '💭',
        
        # Time & Calendar
        'time': '⏰',
        'calendar': '📅',
        'date': '📅',
        'schedule': '📆'
    }
    
    # Unicode Alternativen für bessere Kompatibilität
    UNICODE_ALTERNATIVES = {
        'workflow': '⚡',
        'process': '🔄',
        'check': '☑',
        'user': '👤',
        'folder': '📁',
        'file': '📄',
        'settings': '⚙',
        'help': '❓',
        'search': '🔍',
        'save': '💾'
    }
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialisiert den Fluent Icon Manager
        
        Args:
            config_file: Pfad zur Icon-Konfigurationsdatei
        """
        self.config_file = config_file or "fluent_icons_config.json"
        self.custom_icons = {}
        self.icon_theme = "default"
        self.use_unicode_fallback = True
        
        self.load_config()
        logging.info("Fluent Icon Manager initialisiert mit Theme: %s", self.icon_theme)
    
    def load_config(self):
        """Lädt die Icon-Konfiguration aus Datei"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    
                self.custom_icons = config.get('custom_icons', {})
                self.icon_theme = config.get('theme', 'default')
                self.use_unicode_fallback = config.get('use_unicode_fallback', True)
                
                logging.debug("Icon-Konfiguration geladen: %d custom icons", len(self.custom_icons))
            else:
                self.save_config()  # Erstelle Standard-Konfiguration
                
        except Exception as e:
            logging.warning("Fehler beim Laden der Icon-Konfiguration: %s", e)
            self.create_default_config()
    
    def save_config(self):
        """Speichert die aktuelle Icon-Konfiguration"""
        try:
            config = {
                'theme': self.icon_theme,
                'use_unicode_fallback': self.use_unicode_fallback,
                'custom_icons': self.custom_icons,
                'version': '1.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
                
            logging.debug("Icon-Konfiguration gespeichert")
            
        except Exception as e:
            logging.error("Fehler beim Speichern der Icon-Konfiguration: %s", e)
    
    def create_default_config(self):
        """Erstellt eine Standard-Icon-Konfiguration"""
        self.custom_icons = {}
        self.icon_theme = "fluent"
        self.use_unicode_fallback = True
        self.save_config()
        
        logging.info("Standard-Icon-Konfiguration erstellt")
    
    def get_icon(self, icon_name: str, fallback: str = "❓") -> str:
        """
        Gibt das Icon für den angegebenen Namen zurück
        
        Args:
            icon_name: Name des Icons
            fallback: Fallback-Icon wenn nicht gefunden
            
        Returns:
            Icon-String (Emoji oder Unicode)
        """
        # 1. Prüfe custom icons
        if icon_name in self.custom_icons:
            return self.custom_icons[icon_name]
        
        # 2. Prüfe Fluent Icons
        if icon_name in self.FLUENT_ICONS:
            return self.FLUENT_ICONS[icon_name]
        
        # 3. Prüfe Unicode Alternativen
        if self.use_unicode_fallback and icon_name in self.UNICODE_ALTERNATIVES:
            return self.UNICODE_ALTERNATIVES[icon_name]
        
        # 4. Fallback
        logging.debug("Icon '%s' nicht gefunden, verwende Fallback: %s", icon_name, fallback)
        return fallback
    
    def set_custom_icon(self, icon_name: str, icon_value: str):
        """
        Setzt ein custom Icon
        
        Args:
            icon_name: Name des Icons
            icon_value: Icon-Wert (Emoji, Unicode, etc.)
        """
        self.custom_icons[icon_name] = icon_value
        self.save_config()
        
        logging.info("Custom Icon gesetzt: %s = %s", icon_name, icon_value)
    
    def set_theme(self, theme_name: str):
        """
        Wechselt das Icon-Theme
        
        Args:
            theme_name: Name des Themes (fluent, minimal, classic)
        """
        self.icon_theme = theme_name
        self.save_config()
        
        logging.info("Icon-Theme gewechselt zu: %s", theme_name)
    
    def get_all_available_icons(self) -> Dict[str, str]:
        """Gibt alle verfügbaren Icons zurück"""
        all_icons = {}
        all_icons.update(self.FLUENT_ICONS)
        all_icons.update(self.UNICODE_ALTERNATIVES)
        all_icons.update(self.custom_icons)
        
        return all_icons
    
    def search_icons(self, search_term: str) -> Dict[str, str]:
        """
        Sucht Icons basierend auf einem Suchbegriff
        
        Args:
            search_term: Suchbegriff
            
        Returns:
            Dictionary mit gefundenen Icons
        """
        all_icons = self.get_all_available_icons()
        found_icons = {}
        
        search_term = search_term.lower()
        
        for name, icon in all_icons.items():
            if search_term in name.lower():
                found_icons[name] = icon
        
        logging.debug("Icon-Suche für '%s': %d Ergebnisse", search_term, len(found_icons))
        return found_icons
    
    def export_icon_list(self, output_file: str = "available_icons.json"):
        """Exportiert eine Liste aller verfügbaren Icons"""
        try:
            all_icons = self.get_all_available_icons()
            
            export_data = {
                'theme': self.icon_theme,
                'total_icons': len(all_icons),
                'icons': all_icons,
                'categories': {
                    'navigation': [k for k in all_icons.keys() if any(term in k for term in ['home', 'menu', 'arrow', 'search'])],
                    'files': [k for k in all_icons.keys() if any(term in k for term in ['file', 'folder', 'document', 'save'])],
                    'workflow': [k for k in all_icons.keys() if any(term in k for term in ['workflow', 'process', 'task', 'project'])],
                    'status': [k for k in all_icons.keys() if any(term in k for term in ['check', 'error', 'warning', 'success'])],
                    'user': [k for k in all_icons.keys() if any(term in k for term in ['user', 'customer', 'profile', 'account'])]
                }
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            logging.info("Icon-Liste exportiert nach: %s", output_file)
            return True
            
        except Exception as e:
            logging.error("Fehler beim Exportieren der Icon-Liste: %s", e)
            return False

# Globale Icon Manager Instanz
icon_manager = FluentIconManager()

def get_icon(name: str, fallback: str = "❓") -> str:
    """Shortcut-Funktion für Icon-Zugriff"""
    return icon_manager.get_icon(name, fallback)

def set_icon_theme(theme: str):
    """Shortcut-Funktion für Theme-Wechsel"""
    icon_manager.set_theme(theme)

def customize_icon(name: str, value: str):
    """Shortcut-Funktion für Icon-Anpassung"""
    icon_manager.set_custom_icon(name, value)

# Vordefinierte Icon-Sets für verschiedene Themes
FLUENT_THEME_ICONS = {
    'workflow_start': '▶️',
    'workflow_pause': '⏸️',
    'workflow_stop': '⏹️',
    'customer_new': '👤➕',
    'customer_edit': '👤✏️',
    'project_active': '📁🟢',
    'project_completed': '📁✅',
    'quality_high': '⭐⭐⭐',
    'quality_medium': '⭐⭐',
    'quality_low': '⭐'
}

MINIMAL_THEME_ICONS = {
    'workflow_start': '▶',
    'workflow_pause': '⏸',
    'workflow_stop': '⏹',
    'customer_new': '+',
    'customer_edit': '✎',
    'project_active': '●',
    'project_completed': '✓',
    'quality_high': '★★★',
    'quality_medium': '★★',
    'quality_low': '★'
}

def apply_fluent_theme():
    """Wendet das Fluent Theme an"""
    for name, icon in FLUENT_THEME_ICONS.items():
        icon_manager.set_custom_icon(name, icon)
    
    icon_manager.set_theme("fluent")
    logging.info("Fluent Theme angewendet")

def apply_minimal_theme():
    """Wendet das Minimal Theme an"""
    for name, icon in MINIMAL_THEME_ICONS.items():
        icon_manager.set_custom_icon(name, icon)
    
    icon_manager.set_theme("minimal")
    logging.info("Minimal Theme angewendet")

if __name__ == "__main__":
    # Test der Icon-Funktionalität
    print("🎨 Fluent Icons Manager Test")
    print("=" * 40)
    
    # Test Icon-Zugriff
    print(f"Workflow Icon: {get_icon('workflow')}")
    print(f"User Icon: {get_icon('user')}")
    print(f"Settings Icon: {get_icon('settings')}")
    
    # Test Custom Icon
    customize_icon('my_custom_icon', '🚀')
    print(f"Custom Icon: {get_icon('my_custom_icon')}")
    
    # Test Icon-Suche
    workflow_icons = icon_manager.search_icons('workflow')
    print(f"Workflow Icons gefunden: {len(workflow_icons)}")
    
    # Export Icon-Liste
    icon_manager.export_icon_list()
    print("✅ Icon-Liste exportiert")
