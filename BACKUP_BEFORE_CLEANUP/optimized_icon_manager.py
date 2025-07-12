"""
Optimized Icon Manager für bessere HighDPI-Unterstützung mit CTkImage
Behebt alle CustomTkinter CTkImage-Warnungen und verbessert die Performance
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

try:
    import customtkinter as ctk
    CTK_AVAILABLE = True
except ImportError:
    CTK_AVAILABLE = False
    logging.warning("CustomTkinter not available")

class OptimizedIconManager:
    """
    Optimized Icon Manager mit perfekter HighDPI-Unterstützung durch CTkImage
    """
    
    # Kompakte Icon-Zuordnung für die wichtigsten Icons
    ICON_MAPPING = {
        # Core UI Icons
        'home': 'home',
        'search': 'search', 
        'settings': 'settings',
        'help': 'info',
        'close': 'close',
        'menu': 'menu',
        'theme': 'theme',
        'user': 'person',
        'customer': 'person',
        
        # Navigation
        'arrow_left': 'arrow_left',
        'arrow_right': 'arrow_right',
        'arrow_up': 'arrow_up',
        'arrow_down': 'arrow_down',
        
        # Actions
        'add': 'plus',
        'edit': 'edit',
        'delete': 'trash_can',
        'save': 'save',
        'export': 'export',
        'import': 'import',
        'copy': 'copy',
        'check': 'check',
        'done': 'done',
        
        # Files
        'file': 'file',
        'folder': 'folder',
        'document': 'doc_file',
        'pdf': 'pdf_file',
        'image': 'image_file',
        
        # Workflow
        'workflow': 'workflow',
        'project': 'folder',
        'projects': 'opened_folder',
        'toolbox': 'toolbox',
        'tools': 'toolbox',
        'rocket': 'rocket',
        
        # Status
        'success': 'success',
        'error': 'error',
        'warning': 'warning',
        'info': 'info',
        'loading': 'refresh',
        
        # Quality & Review
        'quality': 'star',
        'review': 'search',
        'approval': 'check',
        'spell_check': 'spell_check_20'
    }
    
    # Emoji-Fallbacks für bessere Kompatibilität
    EMOJI_FALLBACKS = {
        'home': '🏠',
        'search': '🔍',
        'settings': '⚙️',
        'help': '❓',
        'close': '❌',
        'menu': '☰',
        'theme': '🎨',
        'user': '👤',
        'customer': '👤',
        'arrow_left': '←',
        'arrow_right': '→',
        'arrow_up': '↑',
        'arrow_down': '↓',
        'add': '➕',
        'edit': '✏️',
        'delete': '🗑️',
        'save': '💾',
        'export': '📤',
        'import': '📥',
        'copy': '📋',
        'check': '✅',
        'done': '✅',
        'file': '📄',
        'folder': '📁',
        'document': '📝',
        'pdf': '📕',
        'image': '🖼️',
        'workflow': '⚡',
        'project': '📁',
        'projects': '📚',
        'toolbox': '🧰',
        'tools': '🛠️',
        'rocket': '🚀',
        'success': '✅',
        'error': '❌',
        'warning': '⚠️',
        'info': 'ℹ️',
        'loading': '🔄',
        'quality': '⭐',
        'review': '🔍',
        'approval': '✅',
        'spell_check': '✓'
    }

    def __init__(self, workspace_path: Optional[str] = None):
        """
        Initialisiert den optimierten Icon Manager
        
        Args:
            workspace_path: Pfad zum Workspace (für lokale Icons)
        """
        self.workspace_path = workspace_path or os.getcwd()
        
        # Separate Caches für verschiedene Icon-Typen
        self.ctk_image_cache: Dict[str, ctk.CTkImage] = {}  # CTkImage Cache für HighDPI
        self.photoimage_cache: Dict[str, ImageTk.PhotoImage] = {}  # PhotoImage Cache für Fallback
        self.pil_image_cache: Dict[str, Image.Image] = {}  # PIL Image Cache für Verarbeitung
        
        # Verfügbare Icons scannen
        self.icon_paths = [
            os.path.join(self.workspace_path, 'icons'),
            os.path.join(self.workspace_path, 'assets'),
            os.path.join(self.workspace_path, 'assets', 'icons'),
        ]
        
        self.available_icons = self._scan_available_icons()
        
        # Standard-Größen für verschiedene Anwendungsfälle
        self.size_presets = {
            'tiny': (12, 12),
            'small': (16, 16),
            'medium': (20, 20),
            'large': (24, 24),
            'xlarge': (32, 32),
            'huge': (48, 48)
        }
        
        logging.info(f"Optimized Icon Manager initialisiert mit {len(self.available_icons)} verfügbaren Icons")

    def _scan_available_icons(self) -> Dict[str, str]:
        """Scannt verfügbare Icon-Dateien"""
        available = {}
        extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        
        for icon_path in self.icon_paths:
            if not os.path.exists(icon_path):
                continue
                
            try:
                for file in os.listdir(icon_path):
                    file_path = os.path.join(icon_path, file)
                    if os.path.isfile(file_path):
                        name, ext = os.path.splitext(file)
                        if ext.lower() in extensions and os.path.getsize(file_path) > 50:
                            # Verschiedene Namensformen
                            available[name.lower()] = file_path
                            available[name.lower().replace('-', '_')] = file_path
                            available[name.lower().replace('_', '-')] = file_path
            except Exception as e:
                logging.warning(f"Fehler beim Scannen von {icon_path}: {e}")
                
        return available

    def _find_icon_path(self, icon_name: str) -> Optional[str]:
        """Findet den Pfad für ein Icon"""
        # Direkter Name
        search_names = [
            icon_name.lower(),
            icon_name.lower().replace('_', '-'),
            icon_name.lower().replace('-', '_')
        ]
        
        # Gemappter Name
        if icon_name in self.ICON_MAPPING:
            mapped_name = self.ICON_MAPPING[icon_name]
            search_names.extend([
                mapped_name.lower(),
                mapped_name.lower().replace('_', '-'),
                mapped_name.lower().replace('-', '_')
            ])
        
        for search_name in search_names:
            if search_name in self.available_icons:
                return self.available_icons[search_name]
        
        return None

    def _load_pil_image(self, icon_path: str, size: Tuple[int, int]) -> Optional[Image.Image]:
        """Lädt und skaliert ein PIL Image"""
        if not PIL_AVAILABLE:
            return None
            
        cache_key = f"{icon_path}_{size}"
        if cache_key in self.pil_image_cache:
            return self.pil_image_cache[cache_key]
        
        try:
            # Image laden und validieren
            img = Image.open(icon_path)
            if img.mode not in ('RGB', 'RGBA'):
                img = img.convert('RGBA')
            
            # Skalieren mit hoher Qualität
            if img.size != size:
                img = img.resize(size, Image.Resampling.LANCZOS)
            
            # Cache speichern
            self.pil_image_cache[cache_key] = img
            return img
            
        except Exception as e:
            logging.warning(f"Fehler beim Laden von {icon_path}: {e}")
            return None

    def get_ctk_image(self, icon_name: str, size: Tuple[int, int] = (20, 20)) -> Optional[ctk.CTkImage]:
        """
        Lädt ein Icon als CTkImage für optimale HighDPI-Unterstützung
        
        Args:
            icon_name: Name des Icons
            size: Gewünschte Größe
            
        Returns:
            CTkImage oder None bei Fehler
        """
        if not CTK_AVAILABLE:
            return None
            
        cache_key = f"ctk_{icon_name}_{size}"
        if cache_key in self.ctk_image_cache:
            return self.ctk_image_cache[cache_key]
        
        # Icon-Pfad finden
        icon_path = self._find_icon_path(icon_name)
        if not icon_path:
            logging.debug(f"Icon '{icon_name}' nicht gefunden")
            return None
        
        # PIL Image laden
        pil_image = self._load_pil_image(icon_path, size)
        if not pil_image:
            return None
        
        try:
            # CTkImage erstellen mit light/dark Unterstützung
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,  # Für jetzt dasselbe Image für beide Modi
                size=size
            )
            
            # Cache speichern
            self.ctk_image_cache[cache_key] = ctk_image
            logging.debug(f"CTkImage erfolgreich erstellt für '{icon_name}' ({size})")
            return ctk_image
            
        except Exception as e:
            logging.warning(f"Fehler beim Erstellen von CTkImage für '{icon_name}': {e}")
            return None

    def get_photoimage(self, icon_name: str, size: Tuple[int, int] = (20, 20)) -> Optional[ImageTk.PhotoImage]:
        """
        Lädt ein Icon als PhotoImage (Fallback für Kompatibilität)
        
        Args:
            icon_name: Name des Icons
            size: Gewünschte Größe
            
        Returns:
            PhotoImage oder None bei Fehler
        """
        if not PIL_AVAILABLE:
            return None
            
        cache_key = f"photo_{icon_name}_{size}"
        if cache_key in self.photoimage_cache:
            return self.photoimage_cache[cache_key]
        
        # Icon-Pfad finden
        icon_path = self._find_icon_path(icon_name)
        if not icon_path:
            return None
        
        # PIL Image laden
        pil_image = self._load_pil_image(icon_path, size)
        if not pil_image:
            return None
        
        try:
            # PhotoImage erstellen
            photo_image = ImageTk.PhotoImage(pil_image)
            
            # Cache speichern
            self.photoimage_cache[cache_key] = photo_image
            return photo_image
            
        except Exception as e:
            logging.warning(f"Fehler beim Erstellen von PhotoImage für '{icon_name}': {e}")
            return None

    def get_icon(self, icon_name: str, size: Union[Tuple[int, int], str] = (20, 20), 
                prefer_ctk: bool = True) -> Optional[Union[ctk.CTkImage, ImageTk.PhotoImage]]:
        """
        Universelle Icon-Getter-Methode mit intelligenter Auswahl
        
        Args:
            icon_name: Name des Icons
            size: Größe als Tuple oder Preset-Name
            prefer_ctk: Bevorzuge CTkImage für HighDPI-Unterstützung
            
        Returns:
            CTkImage, PhotoImage oder None
        """
        # Größe verarbeiten
        if isinstance(size, str):
            size = self.size_presets.get(size, (20, 20))
        
        # CTkImage bevorzugen wenn verfügbar
        if prefer_ctk and CTK_AVAILABLE:
            ctk_image = self.get_ctk_image(icon_name, size)
            if ctk_image:
                return ctk_image
        
        # Fallback zu PhotoImage
        photo_image = self.get_photoimage(icon_name, size)
        if photo_image:
            return photo_image
        
        # Kein Image verfügbar
        logging.debug(f"Kein Icon gefunden für '{icon_name}'")
        return None

    def get_emoji_fallback(self, icon_name: str) -> str:
        """
        Gibt Emoji-Fallback für ein Icon zurück
        
        Args:
            icon_name: Name des Icons
            
        Returns:
            Emoji-String oder '?'
        """
        return self.EMOJI_FALLBACKS.get(icon_name, '?')

    def preload_common_icons(self, icon_list: Optional[list] = None):
        """
        Lädt häufig verwendete Icons vor für bessere Performance
        
        Args:
            icon_list: Liste der zu ladenden Icons (optional)
        """
        if icon_list is None:
            # Standard-Icons vorladen
            icon_list = [
                'home', 'search', 'settings', 'help', 'close', 'menu', 'theme',
                'arrow_left', 'arrow_right', 'add', 'edit', 'delete', 'save',
                'check', 'done', 'file', 'folder', 'workflow', 'rocket'
            ]
        
        common_sizes = [(16, 16), (20, 20), (24, 24), (32, 32)]
        
        for icon_name in icon_list:
            for size in common_sizes:
                # CTkImage vorladen
                self.get_ctk_image(icon_name, size)
                # PhotoImage vorladen (für Fallback)
                self.get_photoimage(icon_name, size)
        
        logging.info(f"Vorladen abgeschlossen: {len(icon_list)} Icons in {len(common_sizes)} Größen")

    def clear_cache(self):
        """Leert alle Icon-Caches"""
        self.ctk_image_cache.clear()
        self.photoimage_cache.clear()
        self.pil_image_cache.clear()
        logging.info("Icon-Caches geleert")

    def get_cache_stats(self) -> Dict[str, int]:
        """Gibt Cache-Statistiken zurück"""
        return {
            'ctk_images': len(self.ctk_image_cache),
            'photo_images': len(self.photoimage_cache),
            'pil_images': len(self.pil_image_cache),
            'available_icons': len(self.available_icons)
        }

    def create_icon_button(self, parent, icon_name: str, text: str = "", 
                          command=None, size: Union[Tuple[int, int], str] = (20, 20),
                          **kwargs) -> ctk.CTkButton:
        """
        Erstellt einen Button mit optimiertem Icon
        
        Args:
            parent: Parent Widget
            icon_name: Name des Icons
            text: Button-Text
            command: Callback-Funktion
            size: Icon-Größe
            **kwargs: Zusätzliche Button-Parameter
            
        Returns:
            CTkButton mit optimiertem Icon
        """
        icon = self.get_icon(icon_name, size, prefer_ctk=True)
        
        button = ctk.CTkButton(
            master=parent,
            text=text,
            image=icon,
            command=command,
            **kwargs
        )
        
        # Icon-Referenz speichern um Garbage Collection zu verhindern
        if icon:
            button._icon_ref = icon
        
        return button

# Globale Instanz für einfache Verwendung
_global_icon_manager = None

def get_global_icon_manager(workspace_path: Optional[str] = None) -> OptimizedIconManager:
    """Gibt die globale Icon Manager Instanz zurück"""
    global _global_icon_manager
    if _global_icon_manager is None:
        _global_icon_manager = OptimizedIconManager(workspace_path)
    return _global_icon_manager

def get_icon(icon_name: str, size: Union[Tuple[int, int], str] = (20, 20)) -> Optional[Union[ctk.CTkImage, ImageTk.PhotoImage]]:
    """Convenience-Funktion für schnellen Icon-Zugriff"""
    manager = get_global_icon_manager()
    return manager.get_icon(icon_name, size)

def preload_icons():
    """Lädt häufig verwendete Icons vor"""
    manager = get_global_icon_manager()
    manager.preload_common_icons()
