# -*- coding: utf-8 -*-
"""
Fluent Design Icon System für Checker App
=========================================

Ersetzt Emojis durch moderne Fluent Design Icons mit SVG-Support.
Bietet konsistente, skalierbare Icons für die gesamte Anwendung.
"""

import customtkinter as ctk
import logging
from typing import Optional, Dict, Tuple, Union
from PIL import Image, ImageDraw, ImageFont
import io
import base64


class FluentIconManager:
    """Manager für Fluent Design Icons mit SVG-Support und Fallback-Generierung."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.icon_cache = {}
        self._setup_fluent_icons()
        
    def _setup_fluent_icons(self):
        """Setup Fluent Design icon definitions."""
        self.fluent_icons = {
            # Navigation Icons - Clean & Modern
            "home": {
                "unicode": "\uE80F",  # Fluent UI Home icon
                "fallback": "🏠",
                "description": "Home/Dashboard"
            },
            "settings": {
                "unicode": "\uE713",  # Fluent UI Settings icon
                "fallback": "⚙️",
                "description": "Settings/Configuration"
            },
            "search": {
                "unicode": "\uE721",  # Fluent UI Search icon
                "fallback": "🔍",
                "description": "Search/Find"
            },
            "menu": {
                "unicode": "\uE700",  # Fluent UI Hamburger menu
                "fallback": "☰",
                "description": "Menu/Navigation"
            },
            
            # Action Icons - Interactive Elements
            "add": {
                "unicode": "\uE710",  # Fluent UI Add icon
                "fallback": "➕",
                "description": "Add/Create New"
            },
            "edit": {
                "unicode": "\uE70F",  # Fluent UI Edit icon
                "fallback": "✏️",
                "description": "Edit/Modify"
            },
            "delete": {
                "unicode": "\uE74D",  # Fluent UI Delete icon
                "fallback": "🗑️",
                "description": "Delete/Remove"
            },
            "save": {
                "unicode": "\uE74E",  # Fluent UI Save icon
                "fallback": "💾",
                "description": "Save/Store"
            },
            "upload": {
                "unicode": "\uE898",  # Fluent UI Upload icon
                "fallback": "📤",
                "description": "Upload/Send"
            },
            "download": {
                "unicode": "\uE896",  # Fluent UI Download icon
                "fallback": "📥",
                "description": "Download/Receive"
            },
            "copy": {
                "unicode": "\uE8C8",  # Fluent UI Copy icon
                "fallback": "📋",
                "description": "Copy/Duplicate"
            },
            "refresh": {
                "unicode": "\uE72C",  # Fluent UI Refresh icon
                "fallback": "🔄",
                "description": "Refresh/Reload"
            },
            
            # Status Icons - Communication & Feedback
            "success": {
                "unicode": "\uE73E",  # Fluent UI Check Circle icon
                "fallback": "✅",
                "description": "Success/Completed"
            },
            "warning": {
                "unicode": "\uE7BA",  # Fluent UI Warning icon
                "fallback": "⚠️",
                "description": "Warning/Caution"
            },
            "error": {
                "unicode": "\uE783",  # Fluent UI Error icon
                "fallback": "❌",
                "description": "Error/Failed"
            },
            "info": {
                "unicode": "\uE946",  # Fluent UI Info icon
                "fallback": "ℹ️",
                "description": "Information/Help"
            },
            "pending": {
                "unicode": "\uE777",  # Fluent UI Clock icon
                "fallback": "⏳",
                "description": "Pending/In Progress"
            },
            
            # Content Icons - Data & Documents
            "document": {
                "unicode": "\uE8A5",  # Fluent UI Document icon
                "fallback": "📄",
                "description": "Document/File"
            },
            "folder": {
                "unicode": "\uE838",  # Fluent UI Folder icon
                "fallback": "📁",
                "description": "Folder/Directory"
            },
            "file": {
                "unicode": "\uE8A5",  # Fluent UI File icon
                "fallback": "📄",
                "description": "File/Document"
            },
            "image": {
                "unicode": "\uE91B",  # Fluent UI Image icon
                "fallback": "🖼️",
                "description": "Image/Picture"
            },
            "archive": {
                "unicode": "\uE8C0",  # Fluent UI Archive icon
                "fallback": "🗃️",
                "description": "Archive/Compressed"
            },
            
            # User & Social Icons
            "user": {
                "unicode": "\uE77B",  # Fluent UI Person icon
                "fallback": "👤",
                "description": "User/Person"
            },
            "team": {
                "unicode": "\uE716",  # Fluent UI People icon
                "fallback": "👥",
                "description": "Team/Group"
            },
            "contact": {
                "unicode": "\uE779",  # Fluent UI Contact icon
                "fallback": "📞",
                "description": "Contact/Phone"
            },
            "mail": {
                "unicode": "\uE715",  # Fluent UI Mail icon
                "fallback": "📧",
                "description": "Email/Message"
            },
            
            # Workflow Icons - Business Processes
            "workflow": {
                "unicode": "\uE8AE",  # Fluent UI Flow icon
                "fallback": "⚡",
                "description": "Workflow/Process"
            },
            "project": {
                "unicode": "\uE8FD",  # Fluent UI Project icon
                "fallback": "📊",
                "description": "Project/Plan"
            },
            "task": {
                "unicode": "\uE73A",  # Fluent UI Task icon
                "fallback": "✓",
                "description": "Task/Todo"
            },
            "calendar": {
                "unicode": "\uE787",  # Fluent UI Calendar icon
                "fallback": "📅",
                "description": "Calendar/Schedule"
            },
            "timer": {
                "unicode": "\uE916",  # Fluent UI Timer icon
                "fallback": "⏱️",
                "description": "Timer/Duration"
            },
            
            # Navigation & Direction Icons
            "back": {
                "unicode": "\uE72B",  # Fluent UI Back icon
                "fallback": "←",
                "description": "Back/Previous"
            },
            "forward": {
                "unicode": "\uE72A",  # Fluent UI Forward icon
                "fallback": "→",
                "description": "Forward/Next"
            },
            "up": {
                "unicode": "\uE70E",  # Fluent UI Up icon
                "fallback": "↑",
                "description": "Up/Ascending"
            },
            "down": {
                "unicode": "\uE70D",  # Fluent UI Down icon
                "fallback": "↓",
                "description": "Down/Descending"
            },
            
            # Media & Control Icons
            "play": {
                "unicode": "\uE768",  # Fluent UI Play icon
                "fallback": "▶️",
                "description": "Play/Start"
            },
            "pause": {
                "unicode": "\uE769",  # Fluent UI Pause icon
                "fallback": "⏸️",
                "description": "Pause/Stop"
            },
            "stop": {
                "unicode": "\uE71A",  # Fluent UI Stop icon
                "fallback": "⏹️",
                "description": "Stop/End"
            },
        }

    def create_fluent_icon(self, parent, icon_name: str, size: int = 24, 
                          color: str = "#6B7280") -> ctk.CTkLabel:
        """
        Create a Fluent Design icon with modern styling.
        
        Args:
            parent: Parent widget
            icon_name: Icon name from fluent_icons
            size: Icon size in pixels
            color: Icon color (hex string)
            
        Returns:
            ctk.CTkLabel: Fluent icon widget
        """
        try:
            cache_key = f"{icon_name}_{size}_{color}"
            
            # Check cache first
            if cache_key in self.icon_cache:
                icon_config = self.icon_cache[cache_key]
            else:
                icon_config = self._generate_icon_config(icon_name, size, color)
                self.icon_cache[cache_key] = icon_config
            
            # Create the icon label
            icon = ctk.CTkLabel(
                parent,
                text=icon_config["text"],
                font=icon_config["font"],
                text_color=color,
                width=size,
                height=size,
            )
            
            return icon
            
        except Exception as e:
            self.logger.error(f"[FLUENT_ICON] Error creating icon {icon_name}: {e}")
            # Fallback to simple text
            return ctk.CTkLabel(parent, text="?", width=size, height=size)

    def _generate_icon_config(self, icon_name: str, size: int, color: str) -> Dict:
        """Generate icon configuration with proper font and character."""
        try:
            icon_def = self.fluent_icons.get(icon_name)
            if not icon_def:
                # Unknown icon - use fallback
                return {
                    "text": "?",
                    "font": ctk.CTkFont(size=size)
                }
            
            # Try to use Fluent UI font if available, otherwise use fallback
            try:
                # Attempt to use Segoe MDL2 Assets (Windows Fluent icons font)
                fluent_font = ctk.CTkFont(family="Segoe MDL2 Assets", size=size)
                return {
                    "text": icon_def["unicode"],
                    "font": fluent_font
                }
            except:
                # Fallback to emoji with standard font
                return {
                    "text": icon_def["fallback"],
                    "font": ctk.CTkFont(size=size)
                }
                
        except Exception as e:
            self.logger.error(f"[FLUENT_ICON] Error generating icon config: {e}")
            return {
                "text": "?",
                "font": ctk.CTkFont(size=size)
            }

    def create_icon_button(self, parent, icon_name: str, text: str = "", 
                          size: int = 24, style: str = "modern", **kwargs) -> ctk.CTkButton:
        """
        Create a modern button with Fluent icon.
        
        Args:
            parent: Parent widget
            icon_name: Icon name
            text: Button text (optional)
            size: Icon size
            style: Button style
            **kwargs: Additional button arguments
            
        Returns:
            ctk.CTkButton: Icon button
        """
        try:
            # Get icon configuration
            icon_def = self.fluent_icons.get(icon_name, {"fallback": "?"})
            
            # Create button text with icon
            if text:
                button_text = f"{icon_def['fallback']} {text}"
            else:
                button_text = icon_def['fallback']
            
            # Style configurations
            styles = {
                "modern": {
                    "corner_radius": 8,
                    "height": 40,
                    "font": ctk.CTkFont(size=14, weight="normal"),
                },
                "icon_only": {
                    "corner_radius": 8,
                    "width": size + 16,
                    "height": size + 16,
                    "font": ctk.CTkFont(size=size),
                },
                "compact": {
                    "corner_radius": 6,
                    "height": 32,
                    "font": ctk.CTkFont(size=12),
                }
            }
            
            style_config = styles.get(style, styles["modern"])
            button_options = {**style_config, **kwargs}
            
            # Create the button
            button = ctk.CTkButton(parent, text=button_text, **button_options)
            
            return button
            
        except Exception as e:
            self.logger.error(f"[FLUENT_ICON] Error creating icon button: {e}")
            raise

    def get_icon_list(self) -> Dict[str, str]:
        """Get list of available icons with descriptions."""
        return {name: info["description"] for name, info in self.fluent_icons.items()}

    def clear_cache(self):
        """Clear the icon cache to free memory."""
        self.icon_cache.clear()
        self.logger.info("[FLUENT_ICON] Icon cache cleared")


# Global instance
fluent_icon_manager = FluentIconManager()


def create_modern_icon_section(parent, title: str, icon_name: str, 
                              content_items: list, column: int = 0) -> ctk.CTkFrame:
    """
    Create a modern section with Fluent icon and content items.
    
    Args:
        parent: Parent container
        title: Section title
        icon_name: Fluent icon name
        content_items: List of content items to display
        column: Grid column position
        
    Returns:
        ctk.CTkFrame: Modern icon section
    """
    try:
        from modern_visual_design import visual_design_manager
        
        # Create section card
        section = visual_design_manager.create_modern_card(parent)
        section.grid(
            row=0, column=column,
            sticky="nsew",
            padx=(0 if column == 0 else 8, 0 if column == 2 else 8),
            pady=0
        )
        
        # Configure internal layout
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)
        
        # Header with icon and title
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        header.grid_columnconfigure(1, weight=1)
        
        # Fluent icon
        icon = fluent_icon_manager.create_fluent_icon(
            header, icon_name, size=24, color="#0078D4"
        )
        icon.grid(row=0, column=0, sticky="w", padx=(0, 12))
        
        # Title
        title_label = visual_design_manager.create_modern_heading(
            header, title, level="s"
        )
        title_label.grid(row=0, column=1, sticky="ew")
        
        # Content area
        content = ctk.CTkScrollableFrame(section, fg_color="transparent")
        content.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 16))
        
        # Add content items
        for i, item in enumerate(content_items):
            if isinstance(item, str):
                # Simple text item
                item_label = visual_design_manager.create_modern_body_text(
                    content, item, size="m"
                )
                item_label.pack(anchor="w", pady=(0, 8))
            else:
                # Custom widget
                item.pack(fill="x", pady=(0, 8))
        
        fluent_icon_manager.logger.info(f"[FLUENT_ICON] Modern icon section created: {title}")
        return section
        
    except Exception as e:
        fluent_icon_manager.logger.error(f"[FLUENT_ICON] Error creating icon section: {e}")
        raise


def integrate_fluent_icons(app):
    """
    Integrate Fluent Design icons into the application.
    
    Args:
        app: CheckerApp instance
    """
    try:
        # Add fluent icon manager to app
        app.fluent_icon_manager = fluent_icon_manager
        
        app.logger.info("[FLUENT_ICON] Fluent Design icons successfully integrated")
        
    except Exception as e:
        app.logger.error(f"[FLUENT_ICON] Error integrating Fluent icons: {e}")
        raise
