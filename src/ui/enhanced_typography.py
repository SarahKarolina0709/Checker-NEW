"""
Enhanced Typography and Layout System
=====================================
Improved typography, spacing, and layout consistency for the Checker Pro Suite.
"""

from typing import Dict, Tuple, Optional, Any

from dataclasses import dataclass
import customtkinter as ctk

@dataclass
class TypographyConfig:
    """Enhanced typography configuration with consistent font sizes and styles."""

    # Font families (fallback chain)
    PRIMARY_FONT = "Segoe UI"
    SECONDARY_FONT = "Arial"
    MONOSPACE_FONT = "Consolas"

    # Heading sizes
    HEADING_XL = 28      # Main titles
    HEADING_L = 22       # Section headers
    HEADING_M = 18       # Subsection headers
    HEADING_S = 16       # Card titles

    # Body text sizes
    BODY_L = 14          # Main body text
    BODY_M = 12          # Secondary text
    BODY_S = 10          # Captions and metadata

    # Button text sizes
    BUTTON_L = 14        # Primary buttons
    BUTTON_M = 12        # Secondary buttons
    BUTTON_S = 10        # Small buttons

    # Icon sizes
    ICON_XL = 48         # Large icons
    ICON_L = 32          # Medium icons
    ICON_M = 24          # Standard icons
    ICON_S = 16          # Small icons
    ICON_XS = 12         # Tiny icons

@dataclass
class SpacingConfig:
    """Consistent spacing configuration using 8px grid system."""

    # Base spacing unit (8px grid)
    BASE_UNIT = 8

    # Spacing multipliers
    XS = BASE_UNIT * 0.5    # 4px
    S = BASE_UNIT * 1       # 8px
    M = BASE_UNIT * 2       # 16px
    L = BASE_UNIT * 3       # 24px
    XL = BASE_UNIT * 4      # 32px
    XXL = BASE_UNIT * 6     # 48px

    # Component-specific spacing
    CARD_PADDING = M        # 16px
    SECTION_PADDING = L     # 24px
    CONTAINER_PADDING = XL  # 32px

    # Margins
    ELEMENT_MARGIN = S      # 8px
    SECTION_MARGIN = L      # 24px
    CONTAINER_MARGIN = XL   # 32px

@dataclass
class LayoutConfig:
    """Layout configuration for consistent component sizing."""

    # Card dimensions
    CARD_WIDTH = 380
    CARD_HEIGHT = 160
    CARD_RADIUS = 12

    # Button dimensions
    BUTTON_HEIGHT_L = 44
    BUTTON_HEIGHT_M = 36
    BUTTON_HEIGHT_S = 28

    # Input dimensions
    INPUT_HEIGHT = 40
    INPUT_WIDTH = 280

    # Container dimensions
    SECTION_MAX_WIDTH = 480
    CONTENT_MAX_WIDTH = 1200

class EnhancedUIHelper:
    """Helper class for creating consistent UI elements with enhanced styling."""

    def __init__(self):
        self.typography = TypographyConfig()
        self.spacing = SpacingConfig()
        self.layout = LayoutConfig()

    def create_heading(self, parent, text: str, level: str = "M", **kwargs) -> ctk.CTkLabel:
        """Create a consistently styled heading."""

        # Font size mapping
        size_map = {
            "XL": self.typography.HEADING_XL,
            "L": self.typography.HEADING_L,
            "M": self.typography.HEADING_M,
            "S": self.typography.HEADING_S
        }

        # Weight mapping
        weight_map = {
            "XL": "bold",
            "L": "bold",
            "M": "bold",
            "S": "normal"
        }

        size = size_map.get(level, self.typography.HEADING_M)
        weight = weight_map.get(level, "bold")

        # Default styling
        defaults = {
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=size,
                weight=weight
            ),
            "text_color": "#1A1A1A",
            "anchor": "w"
        }

        # Merge with user kwargs
        defaults.update(kwargs)

        return ctk.CTkLabel(parent, text=text, **defaults)

    def create_body_text(self, parent, text: str, size: str = "M", **kwargs) -> ctk.CTkLabel:
        """Create consistently styled body text."""

        size_map = {
            "L": self.typography.BODY_L,
            "M": self.typography.BODY_M,
            "S": self.typography.BODY_S
        }

        font_size = size_map.get(size, self.typography.BODY_M)

        defaults = {
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=font_size
            ),
            "text_color": "#4A4A4A",
            "anchor": "w",
            "wraplength": 300
        }

        defaults.update(kwargs)

        return ctk.CTkLabel(parent, text=text, **defaults)

    def create_card(self, parent, **kwargs) -> ctk.CTkFrame:
        """Create a consistently styled card."""

        defaults = {
            "width": self.layout.CARD_WIDTH,
            "height": self.layout.CARD_HEIGHT,
            "corner_radius": self.layout.CARD_RADIUS,
            "fg_color": "#FFFFFF",
            "border_width": 1,
            "border_color": "#E0E0E0"
        }

        defaults.update(kwargs)

        return ctk.CTkFrame(parent, **defaults)

    def create_primary_button(self, parent, text: str, **kwargs) -> ctk.CTkButton:
        """Create a consistently styled primary button."""

        defaults = {
            "text": text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BUTTON_L,
                weight="bold"
            ),
            "height": self.layout.BUTTON_HEIGHT_L,
            "corner_radius": 8,
            "fg_color": "#0078D4",
            "hover_color": "#106EBE",
            "text_color": "#FFFFFF"
        }

        defaults.update(kwargs)

        return ctk.CTkButton(parent, **defaults)

    def create_secondary_button(self, parent, text: str, **kwargs) -> ctk.CTkButton:
        """Create a consistently styled secondary button."""

        defaults = {
            "text": text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BUTTON_M,
                weight="normal"
            ),
            "height": self.layout.BUTTON_HEIGHT_M,
            "corner_radius": 8,
            "fg_color": "#F8F9FA",
            "hover_color": "#E1E5E9",
            "text_color": "#1A1A1A",
            "border_width": 1,
            "border_color": "#D1D5DB"
        }

        defaults.update(kwargs)

        return ctk.CTkButton(parent, **defaults)

    def create_input_field(self, parent, placeholder: str = "", **kwargs) -> ctk.CTkEntry:
        """Create a consistently styled input field."""

        defaults = {
            "placeholder_text": placeholder,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_M
            ),
            "height": self.layout.INPUT_HEIGHT,
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#E0E0E0",
            "fg_color": "#FFFFFF",
            "text_color": "#1A1A1A",
            "placeholder_text_color": "#9CA3AF"
        }

        defaults.update(kwargs)

        return ctk.CTkEntry(parent, **defaults)

    def create_textarea(self, parent, placeholder: str = "", **kwargs) -> ctk.CTkTextbox:
        """Create a consistently styled textarea."""

        defaults = {
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_M
            ),
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#E0E0E0",
            "fg_color": "#FFFFFF",
            "text_color": "#1A1A1A",
            "wrap": "word",
            "height": 100
        }

        defaults.update(kwargs)

        textbox = ctk.CTkTextbox(parent, **defaults)
        if placeholder:
            textbox.insert("0.0", placeholder)

        return textbox

    def create_form_group(self, parent, label: str, **kwargs) -> ctk.CTkFrame:
        """Create a form group with label and input field."""

        group = ctk.CTkFrame(parent, fg_color="transparent")

        # Label
        label_widget = self.create_body_text(group, label, size="M")
        label_widget.pack(anchor="w", pady=(0, self.spacing.XS))

        return group

    def create_form_row(self, parent, **kwargs) -> ctk.CTkFrame:
        """Create a horizontal form row for multiple inputs."""

        row = ctk.CTkFrame(parent, fg_color="transparent")

        return row

    def create_select_field(self, parent, values: list, **kwargs) -> ctk.CTkComboBox:
        """Create a consistently styled select field."""

        defaults = {
            "values": values,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_M
            ),
            "height": self.layout.INPUT_HEIGHT,
            "corner_radius": 8,
            "border_width": 1,
            "border_color": "#E0E0E0",
            "fg_color": "#FFFFFF",
            "text_color": "#1A1A1A",
            "button_color": "#F1F5F9",
            "button_hover_color": "#E2E8F0"
        }

        defaults.update(kwargs)

        return ctk.CTkComboBox(parent, **defaults)

    def create_checkbox(self, parent, text: str, **kwargs) -> ctk.CTkCheckBox:
        """Create a consistently styled checkbox."""

        defaults = {
            "text": text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_M
            ),
            "text_color": "#4A4A4A",
            "fg_color": "#0078D4",
            "hover_color": "#106EBE",
            "border_width": 2,
            "border_color": "#E0E0E0",
            "corner_radius": 4
        }

        defaults.update(kwargs)

        return ctk.CTkCheckBox(parent, **defaults)

    def create_radio_button(self, parent, text: str, **kwargs) -> ctk.CTkRadioButton:
        """Create a consistently styled radio button."""

        defaults = {
            "text": text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_M
            ),
            "text_color": "#4A4A4A",
            "fg_color": "#0078D4",
            "hover_color": "#106EBE",
            "border_width": 2,
            "border_color": "#E0E0E0"
        }

        defaults.update(kwargs)

        return ctk.CTkRadioButton(parent, **defaults)

    def create_label_input_pair(self, parent, label: str, input_type: str = "entry", **kwargs) -> tuple:
        """Create a label-input pair with consistent styling."""

        container = ctk.CTkFrame(parent, fg_color="transparent")

        # Label
        label_widget = self.create_body_text(container, label, size="M")
        label_widget.pack(anchor="w", pady=(0, self.spacing.XS))

        # Input field based on type
        if input_type == "entry":
            input_widget = self.create_input_field(container, **kwargs)
        elif input_type == "textarea":
            input_widget = self.create_textarea(container, **kwargs)
        elif input_type == "select":
            input_widget = self.create_select_field(container, **kwargs)
        elif input_type == "checkbox":
            input_widget = self.create_checkbox(container, **kwargs)
        elif input_type == "radio":
            input_widget = self.create_radio_button(container, **kwargs)
        else:
            input_widget = self.create_input_field(container, **kwargs)

        input_widget.pack(fill="x", pady=(0, self.spacing.M))

        return container, input_widget

    def create_search_field(self, parent, placeholder: str = "Suchen...", **kwargs) -> ctk.CTkEntry:
        """Create a search field with search icon."""

        # Create container for search field and icon
        search_container = ctk.CTkFrame(parent, fg_color="transparent")

        # Search icon
        search_icon = ctk.CTkLabel(
            search_container,
            text="🔍",
            font=ctk.CTkFont(size=self.typography.ICON_S),
            width=20
        )
        search_icon.pack(side="left", padx=(self.spacing.S, 0))

        # Search field
        search_field = self.create_input_field(
            search_container,
            placeholder=placeholder,
            **kwargs
        )
        search_field.pack(side="left", fill="x", expand=True, padx=(self.spacing.S, 0))

        return search_container

    def create_workflow_card(self, parent, title: str, description: str, icon: str = "", **kwargs) -> ctk.CTkFrame:
        """Create a workflow card with consistent styling."""

        card = self.create_card(parent, **kwargs)

        # Content container
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.spacing.CARD_PADDING, pady=self.spacing.CARD_PADDING)

        # Header with icon and title
        header = ctk.CTkFrame(content, fg_color="transparent")
        header.pack(fill="x", pady=(0, self.spacing.S))

        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                header,
                text=icon,
                font=ctk.CTkFont(size=self.typography.ICON_M),
                width=self.typography.ICON_M
            )
            icon_label.pack(side="left", padx=(0, self.spacing.S))

        # Title
        title_label = self.create_heading(header, title, level="S")
        title_label.pack(side="left", fill="x", expand=True)

        # Description
        desc_label = self.create_body_text(content, description, size="M")
        desc_label.pack(fill="x", pady=(self.spacing.S, 0))

        # Apply hover effect
        self.apply_card_hover_effect(card)

        return card

    def create_info_card(self, parent, title: str, value: str, **kwargs) -> ctk.CTkFrame:
        """Create an information card with consistent styling."""

        card = self.create_card(parent, height=120, **kwargs)

        # Content container
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.spacing.CARD_PADDING, pady=self.spacing.CARD_PADDING)

        # Value (large)
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.HEADING_L,
                weight="bold"
            ),
            text_color="#0078D4"
        )
        value_label.pack(anchor="w")

        # Title (smaller)
        title_label = self.create_body_text(content, title, size="M")
        title_label.pack(anchor="w", pady=(self.spacing.XS, 0))

        return card

    def create_section_container(self, parent, **kwargs) -> ctk.CTkFrame:
        """Create a consistently styled section container."""

        defaults = {
            "fg_color": "#FFFFFF",
            "corner_radius": 12,
            "border_width": 1,
            "border_color": "#E0E0E0"
        }

        defaults.update(kwargs)

        return ctk.CTkFrame(parent, **defaults)

    def apply_card_hover_effect(self, card: ctk.CTkFrame):
        """Apply hover effects to a card."""
        try:
            # Store original colors
            original_fg_color = card.cget("fg_color")
            original_border_color = card.cget("border_color")

            # Hover colors
            hover_fg_color = "#F8FAFC"
            hover_border_color = "#0078D4"

            def on_enter(event):
                """Handle mouse enter."""
                try:
                    card.configure(fg_color=hover_fg_color, border_color=hover_border_color)
                except:
                    pass

            def on_leave(event):
                """Handle mouse leave."""
                try:
                    card.configure(fg_color=original_fg_color, border_color=original_border_color)
                except:
                    pass

            # Bind hover events
            card.bind("<Enter>", on_enter)
            card.bind("<Leave>", on_leave)

            # Also bind to child widgets for better hover experience
            def bind_recursive(widget):
                """Recursively bind hover events to all child widgets."""
                try:
                    widget.bind("<Enter>", on_enter)
                    widget.bind("<Leave>", on_leave)
                    for child in widget.winfo_children():
                        bind_recursive(child)
                except:
                    pass

            bind_recursive(card)

        except Exception as e:
            print(f"Error applying card hover effect: {e}")

    def apply_button_hover_effect(self, button: ctk.CTkButton, hover_color: str = "#4A90E2"):
        """Apply hover effects to a button."""
        try:
            original_color = button.cget("fg_color")

            def on_enter(event):
                try:
                    button.configure(fg_color=hover_color)
                except:
                    pass

            def on_leave(event):
                try:
                    button.configure(fg_color=original_color)
                except:
                    pass

            button.bind("<Enter>", on_enter)
            button.bind("<Leave>", on_leave)

        except Exception as e:
            print(f"Error applying button hover effect: {e}")

    def create_gradient_card(self, parent, gradient_colors: tuple = ("#F8FAFC", "#E1E5E9"), **kwargs) -> ctk.CTkFrame:
        """Create a card with gradient-like background effect."""

        defaults = {
            "width": self.layout.CARD_WIDTH,
            "height": self.layout.CARD_HEIGHT,
            "corner_radius": self.layout.CARD_RADIUS,
            "fg_color": gradient_colors[0],  # Start with lighter color
            "border_width": 1,
            "border_color": "#E0E0E0"
        }

        defaults.update(kwargs)

        card = ctk.CTkFrame(parent, **defaults)

        # Add subtle shadow effect through nested frames
        shadow_frame = ctk.CTkFrame(
            card,
            fg_color=gradient_colors[1],  # Slightly darker for depth
            corner_radius=defaults["corner_radius"] - 2
        )
        shadow_frame.place(relx=0.02, rely=0.02, relwidth=0.96, relheight=0.96)

        return card

    def create_status_badge(self, parent, text: str, status: str = "info", **kwargs) -> ctk.CTkFrame:
        """Create a colored status badge."""

        # Status color mapping
        status_colors = {
            "success": {"bg": "#10B981", "text": "#FFFFFF"},
            "warning": {"bg": "#F59E0B", "text": "#FFFFFF"},
            "error": {"bg": "#EF4444", "text": "#FFFFFF"},
            "info": {"bg": "#1F4E79", "text": "#FFFFFF"},  # Vereinheitlichtes Brand-Blau
            "neutral": {"bg": "#6B7280", "text": "#FFFFFF"}
        }

        colors = status_colors.get(status, status_colors["info"])

        badge = ctk.CTkFrame(
            parent,
            fg_color=colors["bg"],
            corner_radius=12,
            height=24,
            **kwargs
        )

        badge_text = ctk.CTkLabel(
            badge,
            text=text,
            font=ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BODY_S,
                weight="bold"
            ),
            text_color=colors["text"]
        )
        badge_text.pack(padx=8, pady=2)

        return badge

    def create_icon_button(self, parent, text: str, icon: str = "", icon_size: int = None, **kwargs) -> ctk.CTkButton:
        """Create a button with icon and text."""

        if icon_size is None:
            icon_size = self.typography.ICON_S

        # Combine icon and text
        button_text = f"{icon} {text}" if icon else text

        defaults = {
            "text": button_text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BUTTON_M,
                weight="normal"
            ),
            "height": self.layout.BUTTON_HEIGHT_M,
            "corner_radius": 8,
            "fg_color": "#F8F9FA",
            "hover_color": "#E1E5E9",
            "text_color": "#1A1A1A",
            "border_width": 1,
            "border_color": "#D1D5DB"
        }

        defaults.update(kwargs)

        return ctk.CTkButton(parent, **defaults)

    def create_animated_progress_bar(self, parent, **kwargs) -> ctk.CTkProgressBar:
        """Create a progress bar with smooth animations."""

        defaults = {
            "height": 8,
            "corner_radius": 4,
            "fg_color": "#E5E7EB",
            "progress_color": "#0078D4"
        }

        defaults.update(kwargs)

        return ctk.CTkProgressBar(parent, **defaults)

    def create_floating_action_button(self, parent, text: str, **kwargs) -> ctk.CTkButton:
        """Create a floating action button with shadow effect."""

        defaults = {
            "text": text,
            "font": ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.BUTTON_L,
                weight="bold"
            ),
            "width": 56,
            "height": 56,
            "corner_radius": 28,  # Perfect circle
            "fg_color": "#0078D4",
            "hover_color": "#106EBE",
            "text_color": "#FFFFFF"
        }

        defaults.update(kwargs)

        return ctk.CTkButton(parent, **defaults)

    def create_modern_card_with_header(self, parent, title: str, subtitle: str = "", icon: str = "", **kwargs) -> ctk.CTkFrame:
        """Create a modern card with header section."""

        card = self.create_card(parent, **kwargs)

        # Header section with background
        header = ctk.CTkFrame(
            card,
            fg_color="#F8FAFC",
            corner_radius=8,
            height=60
        )
        header.pack(fill="x", padx=16, pady=(16, 8))

        # Header content
        header_content = ctk.CTkFrame(header, fg_color="transparent")
        header_content.pack(fill="both", expand=True, padx=16, pady=12)

        # Icon
        if icon:
            icon_label = ctk.CTkLabel(
                header_content,
                text=icon,
                font=ctk.CTkFont(size=self.typography.ICON_M),
                width=32,
                height=32
            )
            icon_label.pack(side="left", padx=(0, 12))

        # Text content
        text_frame = ctk.CTkFrame(header_content, fg_color="transparent")
        text_frame.pack(side="left", fill="both", expand=True)

        # Title
        title_label = self.create_heading(text_frame, title, level="S")
        title_label.pack(anchor="w")

        # Subtitle
        if subtitle:
            subtitle_label = self.create_body_text(
                text_frame,
                subtitle,
                size="S",
                text_color="#6B7280"
            )
            subtitle_label.pack(anchor="w", pady=(2, 0))

        # Content area
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        return card, content

    def create_metric_card(self, parent, value: str, label: str, trend: str = "", trend_positive: bool = True, **kwargs) -> ctk.CTkFrame:
        """Create a metric display card."""

        card = self.create_card(parent, height=120, **kwargs)

        # Content
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=20, pady=16)

        # Value
        value_label = ctk.CTkLabel(
            content,
            text=value,
            font=ctk.CTkFont(
                family=self.typography.PRIMARY_FONT,
                size=self.typography.HEADING_XL,
                weight="bold"
            ),
            text_color="#0078D4"
        )
        value_label.pack(anchor="w")

        # Label and trend row
        bottom_row = ctk.CTkFrame(content, fg_color="transparent")
        bottom_row.pack(fill="x", pady=(8, 0))

        # Label
        label_widget = self.create_body_text(
            bottom_row,
            label,
            size="M",
            text_color="#6B7280"
        )
        label_widget.pack(side="left")

        # Trend indicator
        if trend:
            trend_color = "#10B981" if trend_positive else "#EF4444"
            trend_icon = "↗" if trend_positive else "↘"

            trend_label = ctk.CTkLabel(
                bottom_row,
                text=f"{trend_icon} {trend}",
                font=ctk.CTkFont(
                    family=self.typography.PRIMARY_FONT,
                    size=self.typography.BODY_S,
                    weight="bold"
                ),
                text_color=trend_color
            )
            trend_label.pack(side="right")

        return card

# Global instance
ui_helper = EnhancedUIHelper()

# Convenience functions
def create_heading(parent, text: str, level: str = "M", **kwargs) -> ctk.CTkLabel:
    """Create a consistently styled heading."""
    return ui_helper.create_heading(parent, text, level, **kwargs)

def create_body_text(parent, text: str, size: str = "M", **kwargs) -> ctk.CTkLabel:
    """Create consistently styled body text."""
    return ui_helper.create_body_text(parent, text, size, **kwargs)

def create_card(parent, **kwargs) -> ctk.CTkFrame:
    """Create a consistently styled card."""
    return ui_helper.create_card(parent, **kwargs)

def create_primary_button(parent, text: str, **kwargs) -> ctk.CTkButton:
    """Create a consistently styled primary button."""
    return ui_helper.create_primary_button(parent, text, **kwargs)

def create_secondary_button(parent, text: str, **kwargs) -> ctk.CTkButton:
    """Create a consistently styled secondary button."""
    return ui_helper.create_secondary_button(parent, text, **kwargs)

def create_input_field(parent, placeholder: str = "", **kwargs) -> ctk.CTkEntry:
    """Create a consistently styled input field."""
    return ui_helper.create_input_field(parent, placeholder, **kwargs)

def create_textarea(parent, placeholder: str = "", **kwargs) -> ctk.CTkTextbox:
    """Create a consistently styled textarea."""
    return ui_helper.create_textarea(parent, placeholder, **kwargs)

def create_form_group(parent, label: str, **kwargs) -> ctk.CTkFrame:
    """Create a form group with label and input field."""
    return ui_helper.create_form_group(parent, label, **kwargs)

def create_form_row(parent, **kwargs) -> ctk.CTkFrame:
    """Create a horizontal form row for multiple inputs."""
    return ui_helper.create_form_row(parent, **kwargs)

def create_select_field(parent, values: list, **kwargs) -> ctk.CTkComboBox:
    """Create a consistently styled select field."""
    return ui_helper.create_select_field(parent, values, **kwargs)

def create_checkbox(parent, text: str, **kwargs) -> ctk.CTkCheckBox:
    """Create a consistently styled checkbox."""
    return ui_helper.create_checkbox(parent, text, **kwargs)

def create_radio_button(parent, text: str, **kwargs) -> ctk.CTkRadioButton:
    """Create a consistently styled radio button."""
    return ui_helper.create_radio_button(parent, text, **kwargs)

def create_label_input_pair(parent, label: str, input_type: str = "entry", **kwargs) -> tuple:
    """Create a label-input pair with consistent styling."""
    return ui_helper.create_label_input_pair(parent, label, input_type, **kwargs)

def create_search_field(parent, placeholder: str = "Suchen...", **kwargs) -> ctk.CTkEntry:
    """Create a search field with search icon."""
    return ui_helper.create_search_field(parent, placeholder, **kwargs)

def create_workflow_card(parent, title: str, description: str, icon: str = "", **kwargs) -> ctk.CTkFrame:
    """Create a workflow card with consistent styling."""
    return ui_helper.create_workflow_card(parent, title, description, icon, **kwargs)

def create_info_card(parent, title: str, value: str, **kwargs) -> ctk.CTkFrame:
    """Create an information card with consistent styling."""
    return ui_helper.create_info_card(parent, title, value, **kwargs)

def create_form_group(parent, label: str, **kwargs) -> ctk.CTkFrame:
    """Create a form group with label and input field."""
    return ui_helper.create_form_group(parent, label, **kwargs)

def create_form_row(parent, **kwargs) -> ctk.CTkFrame:
    """Create a horizontal form row for multiple inputs."""
    return ui_helper.create_form_row(parent, **kwargs)

def create_select_field(parent, values: list, **kwargs) -> ctk.CTkComboBox:
    """Create a consistently styled select field."""
    return ui_helper.create_select_field(parent, values, **kwargs)

def create_checkbox(parent, text: str, **kwargs) -> ctk.CTkCheckBox:
    """Create a consistently styled checkbox."""
    return ui_helper.create_checkbox(parent, text, **kwargs)

def create_radio_button(parent, text: str, **kwargs) -> ctk.CTkRadioButton:
    """Create a consistently styled radio button."""
    return ui_helper.create_radio_button(parent, text, **kwargs)

def create_label_input_pair(parent, label: str, input_type: str = "entry", **kwargs) -> tuple:
    """Create a label-input pair with consistent styling."""
    return ui_helper.create_label_input_pair(parent, label, input_type, **kwargs)

def create_search_field(parent, placeholder: str = "Suchen...", **kwargs) -> ctk.CTkEntry:
    """Create a search field with search icon."""
    return ui_helper.create_search_field(parent, placeholder, **kwargs)

def create_workflow_card(parent, title: str, description: str, icon: str = "", **kwargs) -> ctk.CTkFrame:
    """Create a workflow card with consistent styling."""
    return ui_helper.create_workflow_card(parent, title, description, icon, **kwargs)

def create_info_card(parent, title: str, value: str, **kwargs) -> ctk.CTkFrame:
    """Create an information card with consistent styling."""
    return ui_helper.create_info_card(parent, title, value, **kwargs)

def create_section_container(parent, **kwargs) -> ctk.CTkFrame:
    """Create a consistently styled section container."""
    return ui_helper.create_section_container(parent, **kwargs)