"""
Enhanced Fluent Icons Integration für die Checker-App
Unterstützt lokale PNG-Dateien und dynamische Icon-Anpassung
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, Optional, Union, Tuple, Any
import tkinter as tk

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not available - using emoji fallback only")

class EnhancedFluentIconManager:
    """
    Enhanced Manager für Fluent Icons mit lokaler PNG-Unterstützung
    """
    
    # Standard Fluent Icons Mapping (als Fallback)
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
        'document': '📝',
        'pdf': '📕',
        'image': '🖼️',
        'text': '📄',
        
        # Actions & Controls
        'add': '➕',
        'remove': '➖',
        'delete': '🗑️',
        'edit': '✏️',
        'save': '💾',
        'copy': '📋',
        'paste': '📄',
        'cut': '✂️',
        'undo': '↶',
        'redo': '↷',
        
        # Status & Indicators
        'check': '✅',
        'warning': '⚠️',
        'error': '❌',
        'info': 'ℹ️',
        'success': '✅',
        'loading': '⟳',
        'spinner': '🔄',
        'progress': '📊',
        
        # Workflow & Process
        'workflow': '⚡',
        'process': '🔄',
        'automation': '🤖',
        'analysis': '📊',
        'report': '📋',
        'project': '📁',
        'task': '✓',
        'projects': '📚',
        
        # UI Elements
        'menu': '☰',
        'more': '⋯',
        'expand': '▼',
        'collapse': '▲',
        'arrow_right': '→',
        'arrow_left': '←',
        'arrow_up': '↑',
        'arrow_down': '↓',
        
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
        'schedule': '📆',
        
        # Theme
        'light_mode': '☀️',
        'dark_mode': '🌙',
        'theme': '🎨',
        
        # Additional
        'customer': '👤',
        'user': '👤',
        'users': '👥',
        'restart': '🔄',
        'refresh': '🔄',
        'sync': '🔄',
        'bookmark': '🔖',
        'favorites': '⭐',
        'star': '⭐',
        'lock': '🔒',
        'unlock': '🔓',
        'key': '🔑',
        'share': '📤',
        'export': '📤',
        'import': '📥',
        'upload': '⬆️',
        'download': '⬇️',
        'play': '▶️',
        'pause': '⏸️',
        'stop': '⏹️',
        'previous': '⏮️',
        'next': '⏭️',
        'toolbox': '🧰',
        'tools': '🛠️',
        'puzzle': '🧩',
        'idea': '💡',
        'connect': '🔗',
        'disconnect': '🔌',
        'network': '🌐',
        'cloud': '☁️',
        'database': '🗄️',
        'server': '🖥️',
        'desktop': '🖥️',
        'mobile': '📱',
        'tablet': '📱',
        'print': '🖨️',
        'scan': '📷',
        'camera': '📷',
        'video': '🎥',
        'audio': '🔊',
        'music': '🎵',
        'volume': '🔊',
        'mute': '🔇',
        'battery': '🔋',
        'power': '⚡',
        'wifi': '📶',
        'bluetooth': '📡',
        'location': '📍',
        'map': '🗺️',
        'compass': '🧭',
        'weather': '🌤️',
        'sun': '☀️',
        'moon': '🌙',
        'star': '⭐',
        'heart': '❤️',
        'like': '👍',
        'dislike': '👎',
        'thumbs_up': '👍',
        'thumbs_down': '👎'
    }
    
    # Mapping von Icon-Namen zu Dateinamen (ohne Erweiterung)
    LOCAL_ICON_MAPPING = {
        'home': 'home',
        'search': 'search',
        'settings': 'settings',
        'help': 'info',
        'close': 'close',
        'file': 'file',
        'folder': 'folder',
        'document': 'doc-file',
        'pdf': 'pdf-file',
        'image': 'image-file',
        'text': 'txt-file',
        'add': 'plus',
        'remove': 'close',
        'delete': 'trash-can',
        'edit': 'edit',
        'check': 'check-mark',
        'info': 'info',
        'success': 'check-mark',
        'workflow': 'play',
        'process': 'restart',
        'report': 'doc-file',
        'project': 'folder',
        'projects': 'opened-folder',
        'menu': 'menu',
        'customer': 'about',
        'user': 'about',
        'restart': 'restart',
        'bookmark': 'bookmark',
        'favorites': 'favorites',
        'lock': 'lock',
        'key': 'key',
        'share': 'share',
        'play': 'play',
        'toolbox': 'toolbox',
        'tools': 'toolbox',
        'puzzle': 'puzzle',
        'idea': 'idea',
        'connect': 'connect',
        'clock': 'clock',
        'time': 'clock',
        'mailbox': 'mailbox',
        'mail': 'mailbox',
        'message': 'speech-bubble',
        'picture': 'picture',
        'tick': 'tick-box',
        'done': 'done',
        'padlock': 'padlock'
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialisiert den Enhanced FluentIconManager
        
        Args:
            workspace_path: Pfad zum Workspace (für lokale Icons)
        """
        self.workspace_path = workspace_path or os.getcwd()
        self.icon_cache: Dict[str, Any] = {}
        self.image_cache: Dict[str, ImageTk.PhotoImage] = {}
        self.current_theme = 'light'
        self.custom_icons = {}
        self.default_icon_size = (16, 16)
        
        # Icon-Pfade definieren (Priorität von oben nach unten)
        self.icon_paths = [
            os.path.join(self.workspace_path, 'icons'),
            os.path.join(self.workspace_path, 'assets', 'icons'),
            os.path.join(self.workspace_path, 'assets'),
        ]
        
        # Verfügbare lokale Icons scannen
        self.available_local_icons = self._scan_local_icons()
        
        # Custom Icons aus gespeicherten Einstellungen laden
        self._load_custom_icons()
        
        logging.info(f"Enhanced FluentIconManager initialisiert mit Workspace: {self.workspace_path}")
        logging.debug(f"Icon-Pfade: {self.icon_paths}")
        logging.debug(f"Verfügbare lokale Icons: {len(self.available_local_icons)}")

    def _scan_local_icons(self) -> Dict[str, str]:
        """
        Scannt alle verfügbaren lokalen Icon-Dateien
        
        Returns:
            Dict mit Icon-Namen und ihren Pfaden
        """
        available_icons = {}
        supported_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        for icon_path in self.icon_paths:
            if not os.path.exists(icon_path):
                continue
                
            try:
                for file in os.listdir(icon_path):
                    file_path = os.path.join(icon_path, file)
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(file)
                        if ext.lower() in supported_extensions:
                            # Verschiedene Namensformen speichern
                            available_icons[name.lower()] = file_path
                            available_icons[name.lower().replace('-', '_')] = file_path
                            available_icons[name.lower().replace('_', '-')] = file_path
                            
            except Exception as e:
                logging.warning(f"Fehler beim Scannen von {icon_path}: {e}")
        
        logging.debug(f"Gescannte Icons: {list(available_icons.keys())}")
        return available_icons

    def _find_local_icon(self, icon_name: str) -> Optional[str]:
        """
        Findet lokale Icon-Datei für einen Icon-Namen
        
        Args:
            icon_name: Name des gesuchten Icons
            
        Returns:
            Pfad zur Icon-Datei oder None
        """
        # Direkt nach dem Namen suchen
        search_names = [
            icon_name.lower(),
            icon_name.lower().replace('_', '-'),
            icon_name.lower().replace('-', '_')
        ]
        
        # Auch nach gemapptem Namen suchen
        if icon_name in self.LOCAL_ICON_MAPPING:
            mapped_name = self.LOCAL_ICON_MAPPING[icon_name]
            search_names.extend([
                mapped_name.lower(),
                mapped_name.lower().replace('_', '-'),
                mapped_name.lower().replace('-', '_')
            ])
        
        for search_name in search_names:
            if search_name in self.available_local_icons:
                return self.available_local_icons[search_name]
        
        return None

    def _load_image_icon(self, icon_path: str, size: Tuple[int, int] = None) -> Optional[ImageTk.PhotoImage]:
        """
        Lädt ein Icon aus einer Bilddatei
        
        Args:
            icon_path: Pfad zur Icon-Datei
            size: Gewünschte Größe (width, height)
            
        Returns:
            PhotoImage oder None bei Fehler
        """
        if not PIL_AVAILABLE:
            return None
            
        cache_key = f"{icon_path}_{size or self.default_icon_size}"
        
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        try:
            if not os.path.exists(icon_path):
                logging.warning(f"Icon-Datei nicht gefunden: {icon_path}")
                return None
                
            # Bild laden und skalieren
            with Image.open(icon_path) as img:
                # Größe anpassen
                target_size = size or self.default_icon_size
                if img.size != target_size:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                
                # In PhotoImage konvertieren
                photo = ImageTk.PhotoImage(img)
                
                # Cache speichern
                self.image_cache[cache_key] = photo
                
                logging.debug(f"Icon geladen: {icon_path} -> {target_size}")
                return photo
                
        except Exception as e:
            logging.error(f"Fehler beim Laden von Icon {icon_path}: {e}")
            return None

    def get_icon(self, icon_name: str, size: Tuple[int, int] = None, fallback_to_emoji: bool = True) -> Union[str, ImageTk.PhotoImage, None]:
        """
        Holt ein Icon (lokale Datei oder Emoji-Fallback)
        
        Args:
            icon_name: Name des Icons
            size: Gewünschte Größe für Bilder
            fallback_to_emoji: Bei True wird Emoji als Fallback verwendet
            
        Returns:
            PhotoImage (für lokale Icons), String (für Emoji) oder None
        """
        # Cache-Key erstellen
        cache_key = f"{icon_name}_{size or self.default_icon_size}_{self.current_theme}"
        
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        result = None
        
        # 1. Zuerst nach Custom Icons suchen
        if icon_name in self.custom_icons:
            custom_path = self.custom_icons[icon_name]
            if os.path.exists(custom_path):
                result = self._load_image_icon(custom_path, size)
                if result:
                    logging.debug(f"Custom Icon verwendet: {icon_name} -> {custom_path}")
        
        # 2. Dann nach lokalen Icons suchen
        if not result:
            local_path = self._find_local_icon(icon_name)
            if local_path:
                result = self._load_image_icon(local_path, size)
                if result:
                    logging.debug(f"Lokales Icon verwendet: {icon_name} -> {local_path}")
        
        # 3. Emoji-Fallback verwenden
        if not result and fallback_to_emoji:
            if icon_name in self.FLUENT_ICONS:
                result = self.FLUENT_ICONS[icon_name]
                logging.debug(f"Emoji-Fallback verwendet: {icon_name} -> {result}")
        
        # Cache speichern
        if result:
            self.icon_cache[cache_key] = result
        
        return result

    def get_icon_for_button(self, icon_name: str, size: Tuple[int, int] = (16, 16)) -> Union[str, ImageTk.PhotoImage]:
        """
        Speziell für Buttons - gibt immer ein verwendbares Icon zurück
        
        Args:
            icon_name: Name des Icons
            size: Gewünschte Größe
            
        Returns:
            PhotoImage oder Emoji-String
        """
        icon = self.get_icon(icon_name, size, fallback_to_emoji=True)
        
        # Fallback auf generisches Icon
        if not icon:
            icon = self.get_icon('info', size, fallback_to_emoji=True)
        
        # Letzter Fallback
        if not icon:
            icon = "•"
        
        return icon

    def list_available_icons(self) -> Dict[str, str]:
        """
        Listet alle verfügbaren Icons auf
        
        Returns:
            Dict mit Icon-Namen und ihren Quellen
        """
        available = {}
        
        # Lokale Icons
        for name in self.available_local_icons:
            available[name] = "local"
        
        # Emoji Icons
        for name in self.FLUENT_ICONS:
            if name not in available:
                available[name] = "emoji"
        
        # Custom Icons
        for name in self.custom_icons:
            available[name] = "custom"
        
        return available

    def set_custom_icon(self, icon_name: str, file_path: str):
        """
        Setzt ein Custom Icon
        
        Args:
            icon_name: Name des Icons
            file_path: Pfad zur Icon-Datei
        """
        if os.path.exists(file_path):
            self.custom_icons[icon_name] = file_path
            # Cache für dieses Icon löschen
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon gesetzt: {icon_name} -> {file_path}")
        else:
            logging.warning(f"Custom Icon-Datei nicht gefunden: {file_path}")

    def remove_custom_icon(self, icon_name: str):
        """
        Entfernt ein Custom Icon
        
        Args:
            icon_name: Name des Icons
        """
        if icon_name in self.custom_icons:
            del self.custom_icons[icon_name]
            # Cache für dieses Icon löschen
            keys_to_remove = [k for k in self.icon_cache.keys() if k.startswith(icon_name + "_")]
            for key in keys_to_remove:
                del self.icon_cache[key]
                
            self._save_custom_icons()
            logging.info(f"Custom Icon entfernt: {icon_name}")

    def set_theme(self, theme: str):
        """
        Setzt das aktuelle Theme
        
        Args:
            theme: Theme-Name ('light', 'dark', etc.)
        """
        if theme != self.current_theme:
            self.current_theme = theme
            # Icon-Cache leeren da sich Farben ändern können
            self.icon_cache.clear()
            logging.info(f"Icon-Theme gewechselt zu: {theme}")

    def clear_cache(self):
        """
        Leert den gesamten Icon-Cache
        """
        self.icon_cache.clear()
        self.image_cache.clear()
        logging.info("Icon-Cache geleert")

    def _load_custom_icons(self):
        """
        Lädt gespeicherte Custom Icon-Einstellungen
        """
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    self.custom_icons = json.load(f)
                logging.debug(f"Custom Icons geladen: {len(self.custom_icons)} Icons")
        except Exception as e:
            logging.warning(f"Fehler beim Laden der Custom Icons: {e}")
            self.custom_icons = {}

    def _save_custom_icons(self):
        """
        Speichert Custom Icon-Einstellungen
        """
        config_path = os.path.join(self.workspace_path, "custom_icons.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_icons, f, indent=2, ensure_ascii=False)
            logging.debug("Custom Icons gespeichert")
        except Exception as e:
            logging.warning(f"Fehler beim Speichern der Custom Icons: {e}")

    def get_stats(self) -> Dict[str, int]:
        """
        Gibt Statistiken über verfügbare Icons zurück
        
        Returns:
            Dict mit Icon-Statistiken
        """
        return {
            'local_icons': len(self.available_local_icons),
            'emoji_icons': len(self.FLUENT_ICONS),
            'custom_icons': len(self.custom_icons),
            'cached_icons': len(self.icon_cache),
            'cached_images': len(self.image_cache)
        }

    def __del__(self):
        """
        Cleanup beim Löschen des Objekts
        """
        try:
            self.clear_cache()
        except:
            pass

# Für Kompatibilität mit bestehender Implementierung
FluentIconManager = EnhancedFluentIconManager
