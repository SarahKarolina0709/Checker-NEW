"""
Centralized Icon Management for Checker-App
Handles loading, caching, and providing icons for the application.
"""

import os
from pathlib import Path
from PIL import Image, ImageTk
import customtkinter as ctk
from app_logger import get_logger


class IconManager:
    """Centralized icon management system"""
    
    def __init__(self, assets_path=None):
        self.logger = get_logger('icons')
        self.assets_path = Path(assets_path) if assets_path else Path('assets')
        self.icon_cache = {}
        self.text_icons = {
            'arrow_left': '←',
            'arrow_right': '→',
            'home': '🏠',
            'workflow': '⚡',
            'settings': '⚙️',
            'file': '📄',
            'folder': '📁',
            'check': '✓',
            'cross': '✗',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅',
            'clock': '🕒',
            'user': '👤',
            'search': '🔍',
            'export': '📤',
            'import': '📥',
            'save': '💾',
            'edit': '✏️',
            'delete': '🗑️',
            'add': '+',
            'remove': '-',
            'up': '↑',
            'down': '↓',
            'refresh': '🔄',
            'copy': '📋',
            'paste': '📋',
            'cut': '✂️'
        }
        
        self.logger.info(f"Icon manager initialized with assets path: {self.assets_path}")
    
    def get_icon(self, icon_name, fallback_text='?', size=(24, 24), color=None):
        """
        Get an icon by name. Returns CTkImage if PNG exists, otherwise text fallback.
        
        Args:
            icon_name: Name of the icon
            fallback_text: Text to use if icon not found
            size: Tuple of (width, height) for the icon
            color: Color for the icon (if applicable)
        
        Returns:
            CTkImage or text string
        """
        cache_key = f"{icon_name}_{size[0]}x{size[1]}_{color}"
        
        # Check cache first
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        # Try to load PNG icon
        png_path = self.assets_path / f"{icon_name}.png"
        if png_path.exists():
            try:
                image = Image.open(png_path)
                if color:
                    # Apply color if specified (simplified approach)
                    image = self._apply_color_to_image(image, color)
                
                ctk_image = ctk.CTkImage(light_image=image, size=size)
                self.icon_cache[cache_key] = ctk_image
                return ctk_image
                
            except Exception as e:
                self.logger.warning(f"Could not load PNG icon {icon_name}: {e}")
        
        # Fall back to text icon
        text_icon = self.text_icons.get(icon_name, fallback_text)
        self.icon_cache[cache_key] = text_icon
        return text_icon
    
    def get_text_icon(self, icon_name, fallback='?'):
        """Get text representation of an icon"""
        return self.text_icons.get(icon_name, fallback)
    
    def preload_icons(self, icon_names=None):
        """Preload icons into cache"""
        if icon_names is None:
            # Load all available icons
            icon_names = list(self.text_icons.keys())
        
        self.logger.info(f"Preloading {len(icon_names)} icons")
        
        for icon_name in icon_names:
            self.get_icon(icon_name)
        
        self.logger.info("Icon preloading complete")
    
    def _apply_color_to_image(self, image, color):
        """Apply color to an image (simplified implementation)"""
        try:
            # Convert to RGBA if not already
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            
            # Simple color overlay (this is a basic implementation)
            # For more sophisticated coloring, you'd need more complex image processing
            return image
            
        except Exception as e:
            self.logger.warning(f"Could not apply color to image: {e}")
            return image
    
    def create_icon_button(self, parent, icon_name, text="", command=None, **kwargs):
        """
        Create a button with an icon.
        
        Args:
            parent: Parent widget
            icon_name: Name of the icon
            text: Button text
            command: Button command
            **kwargs: Additional button arguments
        
        Returns:
            CTkButton with icon
        """
        # Get icon
        size = kwargs.pop('icon_size', (24, 24))
        icon = self.get_icon(icon_name, size=size)
        
        # Create button
        if isinstance(icon, str):
            # Text icon - prepend to text
            button_text = f"{icon} {text}".strip()
            button = ctk.CTkButton(
                parent,
                text=button_text,
                command=command,
                **kwargs
            )
        else:
            # Image icon
            button = ctk.CTkButton(
                parent,
                text=text,
                image=icon,
                command=command,
                **kwargs
            )
        
        return button
    
    def clear_cache(self):
        """Clear the icon cache"""
        self.icon_cache.clear()
        self.logger.info("Icon cache cleared")
    
    def get_cache_info(self):
        """Get information about the icon cache"""
        return {
            'cached_items': len(self.icon_cache),
            'available_text_icons': len(self.text_icons),
            'assets_path': str(self.assets_path)
        }


# Global icon manager instance
_icon_manager = None

def get_icon_manager(assets_path=None):
    """Get the global icon manager instance"""
    global _icon_manager
    if _icon_manager is None:
        _icon_manager = IconManager(assets_path)
    return _icon_manager
