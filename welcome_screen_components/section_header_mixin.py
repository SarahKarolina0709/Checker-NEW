"""
Section Header Mixin for Welcome Screen Components
Provides common header creation functionality to eliminate code duplication.
"""

import customtkinter as ctk
from ui_theme import UITheme, enhanced_theme
from animation_engine import animation_engine


class SectionHeaderMixin:
    """
    Mixin class that provides common header creation functionality.
    Implements DRY principle by centralizing repetitive header code.
    """
    
    def create_section_header(self, container, title, subtitle, icon_name, icon_bg_color, icon_emoji_fallback="🔧"):
        """
        Creates a professional header section for welcome screen components.
        
        Args:
            container: Parent container for the header
            title: Main title text
            subtitle: Subtitle text
            icon_name: Name of the icon to load
            icon_bg_color: Background color for the icon
            icon_emoji_fallback: Fallback emoji if icon fails to load
            
        Returns:
            tuple: (header_frame, icon_bg_frame) for further customization if needed
        """
        # Professional header frame
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=UITheme.SPACING_L, pady=(UITheme.SPACING_L, UITheme.SPACING_M))
        header_frame.grid_columnconfigure(1, weight=1)

        # Professional icon background
        icon_bg = ctk.CTkFrame(
            header_frame,
            fg_color=icon_bg_color,
            corner_radius=UITheme.CORNER_RADIUS,
            width=48,
            height=48
        )
        icon_bg.grid(row=0, column=0, rowspan=2, sticky="w", padx=(0, UITheme.SPACING_M))
        icon_bg.grid_propagate(False)

        # Load professional icon
        try:
            icon = self.app.get_icon(icon_name, (24, 24))
            if icon:
                icon_label = ctk.CTkLabel(icon_bg, image=icon, text="")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                raise Exception("Icon not found")
        except Exception:
            # Professional emoji fallback
            from icon_fallbacks import get_emoji_for_icon
            emoji = get_emoji_for_icon(icon_name) if icon_name != icon_emoji_fallback else icon_emoji_fallback
            emoji_label = ctk.CTkLabel(
                icon_bg,
                text=emoji,
                font=ctk.CTkFont(size=16),
                text_color=enhanced_theme.get_color('text_on_primary')
            )
            emoji_label.place(relx=0.5, rely=0.5, anchor="center")

        # Professional title
        title_label = ctk.CTkLabel(
            header_frame,
            text=title,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_HEADING_LARGE, weight="bold"),
            text_color=enhanced_theme.get_color('text_primary'),
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")

        # Professional subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text=subtitle,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY_SMALL),
            text_color=enhanced_theme.get_color('text_secondary'),
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew", pady=(UITheme.SPACING_XS, 0))

        return header_frame, icon_bg
    
    def create_input_section(self, parent, row, label_text, entry_widget=None, placeholder_text="", pady=(0, 0)):
        """
        Creates a standardized input section with label and entry field.
        Implements DRY principle for form field creation.
        
        Args:
            parent: Parent widget
            row: Grid row position
            label_text: Text for the label
            entry_widget: Existing entry widget to use (optional)
            placeholder_text: Placeholder text for the entry
            pady: Padding for the section
            
        Returns:
            CTkEntry: The created or provided entry widget
        """
        section_frame = ctk.CTkFrame(parent, fg_color="transparent")
        section_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        section_frame.grid_columnconfigure(0, weight=1)
        
        # Label with consistent styling
        label = ctk.CTkLabel(
            section_frame,
            text=label_text,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=15, weight="bold"),
            text_color=enhanced_theme.get_color('text_secondary'),
            anchor="w"
        )
        label.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        # Entry field with consistent styling
        if entry_widget is None:
            entry_widget = ctk.CTkEntry(
                section_frame,
                placeholder_text=placeholder_text,
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="normal"),
                fg_color=enhanced_theme.get_color('card'),
                border_color=enhanced_theme.get_color('border'),
                text_color=enhanced_theme.get_color('text_primary'),
                height=48,
                corner_radius=UITheme.CORNER_RADIUS
            )
        entry_widget.grid(row=1, column=0, sticky="ew")
        
        return entry_widget
    
    def create_info_card(self, parent, title, subtitle, icon_name, icon_bg_color, 
                        button_text="", button_callback=None, button_icon="", 
                        height=96, row=0):
        """
        Creates a modern, professional info card with elegant design.
        
        Args:
            parent: Parent widget
            title: Main title text
            subtitle: Subtitle/description text
            icon_name: Name of the icon to load
            icon_bg_color: Background color for the icon
            button_text: Text for the action button (optional)
            button_callback: Callback for the action button (optional)
            button_icon: Icon name for the button (optional)
            height: Minimum height of the card
            row: Grid row position
            
        Returns:
            CTkFrame: The created card frame
        """
        # Professional card with modern design
        card = ctk.CTkFrame(
            parent,
            **UITheme.CARD_STYLE_MODERN,
            height=height
        )
        card.grid(row=row, column=0, sticky="ew", pady=(0, UITheme.SPACING_M), padx=UITheme.SPACING_XS)
        card.grid_columnconfigure(0, weight=0)  # Icon: fixed width
        card.grid_columnconfigure(1, weight=1)  # Text: expands
        card.grid_columnconfigure(2, weight=0)  # Button: fixed width
        card.grid_rowconfigure(0, weight=1)
        card.grid_propagate(False)
        
        # Professional hover effects
        self._add_professional_hover_effects(card, icon_bg_color)
        
        # Modern icon container
        icon_container = ctk.CTkFrame(
            card,
            fg_color=icon_bg_color,
            corner_radius=UITheme.CORNER_RADIUS,
            width=56,
            height=56
        )
        icon_container.grid(row=0, column=0, sticky="ns", padx=UITheme.SPACING_M, pady=UITheme.SPACING_M)
        icon_container.grid_propagate(False)
        
        # Load professional icon
        self._load_professional_icon(icon_container, icon_name)
        
        # Professional text container
        text_container = ctk.CTkFrame(card, fg_color="transparent")
        text_container.grid(row=0, column=1, sticky="nsew", padx=(UITheme.SPACING_S, UITheme.SPACING_M), pady=UITheme.SPACING_M)
        text_container.grid_columnconfigure(0, weight=1)
        text_container.grid_rowconfigure(0, weight=0)
        text_container.grid_rowconfigure(1, weight=1)
        
        # Professional title
        title_label = ctk.CTkLabel(
            text_container,
            text=title,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_HEADING_SMALL, weight="bold"),
            text_color=enhanced_theme.get_color('text_primary'),
            anchor="w",
            justify="left"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, UITheme.SPACING_XS))
        
        # Professional subtitle
        subtitle_label = ctk.CTkLabel(
            text_container,
            text=subtitle,
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY_SMALL),
            text_color=enhanced_theme.get_color('text_secondary'),
            anchor="w",
            justify="left",
            wraplength=280
        )
        subtitle_label.grid(row=1, column=0, sticky="new")
        
        # Professional action button
        if button_text and button_callback:
            button = ctk.CTkButton(
                card,
                text=button_text,
                command=button_callback,
                **UITheme.BUTTON_STYLE_PRIMARY,
                width=88,
                height=36
            )
            button.grid(row=0, column=2, sticky="ns", padx=(UITheme.SPACING_S, UITheme.SPACING_M), pady=UITheme.SPACING_M)
            
            # Professional button hover effect
            self._add_professional_button_hover(button)
        
        return card
    
    def create_scrollable_list(self, parent, row, height=200, padx=20, pady=(0, 20)):
        """
        Creates a standardized scrollable list container.
        Implements DRY principle for scrollable content areas.
        
        Args:
            parent: Parent widget
            row: Grid row position
            height: Height of the scrollable area
            padx: Horizontal padding
            pady: Vertical padding
            
        Returns:
            CTkScrollableFrame: The created scrollable frame
        """
        # Ensure height is never None to prevent scaling errors
        if height is None:
            height = 200
            
        scrollable_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            label_text="",
            scrollbar_button_color=enhanced_theme.get_color('primary'),
            scrollbar_button_hover_color=enhanced_theme.get_color('primary_hover'),
            height=height
        )
        scrollable_frame.grid(row=row, column=0, sticky="nsew", padx=padx, pady=pady)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        return scrollable_frame
    
    def create_button_group(self, parent, button_configs, row=0, pady=(25, 0)):
        """
        Creates a group of buttons using configuration data.
        Implements DRY principle for button creation.
        
        Args:
            parent: Parent widget
            button_configs: List of button configuration dictionaries
            row: Grid row position
            pady: Vertical padding
            
        Returns:
            list: List of created buttons
        """
        buttons_frame = ctk.CTkFrame(parent, fg_color="transparent")
        buttons_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        
        # Configure grid columns based on number of buttons
        for i in range(len(button_configs)):
            buttons_frame.grid_columnconfigure(i, weight=1)
        
        buttons = []
        for i, config in enumerate(button_configs):
            if hasattr(self, 'welcome_screen') and hasattr(self.welcome_screen, 'create_icon_button'):
                button = self.welcome_screen.create_icon_button(
                    buttons_frame,
                    text=config.get("text", "Button"),
                    icon_name=config.get("icon_name", "default"),
                    callback=config.get("callback", lambda: None),
                    style=config.get("style", UITheme.BUTTON_STYLE_PRIMARY),
                    width=config.get("width", 100)
                )
                button.grid(
                    row=0, 
                    column=i, 
                    sticky="ew", 
                    padx=config.get("padx", (5, 5))
                )
                buttons.append(button)
        
        return buttons

    def create_status_indicator(self, parent, text, row=0, icon="💡", pady=(20, 0)):
        """
        Creates a standardized status indicator with icon and text.
        Implements DRY principle for status/tip messages.
        
        Args:
            parent: Parent widget
            text: Status message text
            row: Grid row position
            icon: Icon/emoji to display
            pady: Vertical padding
            
        Returns:
            CTkFrame: The created status frame
        """
        status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        status_frame.grid(row=row, column=0, sticky="ew", pady=pady)
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=f"{icon} {text}",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="normal"),
            text_color=enhanced_theme.get_color('text_secondary'),
            anchor="w"
        )
        status_label.grid(row=0, column=0, sticky="ew")
        
        return status_frame
    
    def create_animated_button(self, parent, text, callback, style="primary", 
                             icon_name=None, width=120, height=40, **kwargs):
        """
        Creates a beautiful animated button with hover effects.
        
        Args:
            parent: Parent widget
            text: Button text
            callback: Click callback
            style: Button style ('primary', 'success', 'danger', 'warning')
            icon_name: Optional icon name
            width: Button width
            height: Button height
            **kwargs: Additional button parameters
            
        Returns:
            CTkButton: The created animated button
        """
        # Define color schemes for different styles
        button_styles = {
            'primary': {
                'fg_color': enhanced_theme.get_color('primary'),
                'hover_color': enhanced_theme.get_color('primary_hover'),
                'text_color': enhanced_theme.get_color('text_on_primary')
            },
            'success': {
                'fg_color': enhanced_theme.get_color('success'),
                'hover_color': enhanced_theme.get_color('success_hover'),
                'text_color': enhanced_theme.get_color('text_on_primary')
            },
            'danger': {
                'fg_color': enhanced_theme.get_color('danger'),
                'hover_color': enhanced_theme.get_color('danger_hover'),
                'text_color': enhanced_theme.get_color('text_on_primary')
            },
            'warning': {
                'fg_color': enhanced_theme.get_color('warning'),
                'hover_color': '#e0a800',
                'text_color': '#000000'
            }
        }
        
        # Get style colors
        colors = button_styles.get(style, button_styles['primary'])
        
        # Create button with icon if specified
        button_kwargs = {
            'master': parent,
            'text': text,
            'command': callback,
            'font': ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=13, weight="bold"),
            'fg_color': colors['fg_color'],
            'hover_color': colors['hover_color'],
            'text_color': colors['text_color'],
            'corner_radius': UITheme.CORNER_RADIUS,
            'width': width,
            'height': height,
            **kwargs
        }
        
        # Add icon if specified
        if icon_name and hasattr(self, 'app'):
            try:
                icon = self.app.get_icon(icon_name, (20, 20))
                if icon:
                    button_kwargs['image'] = icon
                    button_kwargs['compound'] = "left"
            except Exception:
                pass  # Continue without icon
        
        button = ctk.CTkButton(**button_kwargs)
        
        # Add subtle hover animation
        self._add_button_hover_effect(button, colors)
        
        return button
    
    def _add_button_hover_effect(self, button, colors):
        """Adds premium hover animation to buttons with smooth transitions."""
        original_cursor = button.cget('cursor') or ""
        original_fg_color = colors['fg_color']
        hover_fg_color = colors['hover_color']
        
        # Store animation state
        button._is_hovered = False
        
        def on_enter(event):
            if button._is_hovered:
                return
            button._is_hovered = True
            
            button.configure(cursor="hand2")
            
            # Premium hover transition with scale and color
            animation_engine.animate_scale_smooth(button, scale_factor=1.05, duration=200)
            animation_engine.animate_color_transition(
                button, original_fg_color, hover_fg_color, 
                duration=200, property_name="fg_color", 
                easing=animation_engine.ease_out_quart
            )
            
        def on_leave(event):
            if not button._is_hovered:
                return
            button._is_hovered = False
            
            button.configure(cursor=original_cursor)
            
            # Smooth return transition
            animation_engine.animate_scale_smooth(button, scale_factor=1.0, duration=250)
            animation_engine.animate_color_transition(
                button, hover_fg_color, original_fg_color,
                duration=250, property_name="fg_color",
                easing=animation_engine.ease_out_quart
            )
        
        def on_click(event):
            if button._is_hovered:
                # Premium click effect
                animation_engine.animate_premium_click_effect(
                    button, flash_color="#FFFFFF", scale_factor=1.12, duration=150
                )
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_click)

    def _animate_button_color(self, button, from_color, to_color):
        """Legacy method - replaced by animation engine."""
        pass  # No longer used
    
    def _add_professional_hover_effects(self, card, icon_bg_color):
        """Add professional hover effects to cards."""
        original_fg_color = enhanced_theme.get_color('card')
        hover_fg_color = enhanced_theme.get_color('surface')
        original_border_color = enhanced_theme.get_color('border')
        hover_border_color = icon_bg_color
        
        def on_card_enter(event):
            card.configure(
                fg_color=hover_fg_color,
                border_color=hover_border_color,
                border_width=2
            )
            
        def on_card_leave(event):
            card.configure(
                fg_color=original_fg_color,
                border_color=original_border_color,
                border_width=1
            )
        
        # Bind events to all child widgets
        def bind_recursive(widget):
            try:
                widget.bind("<Enter>", on_card_enter)
                widget.bind("<Leave>", on_card_leave)
                for child in widget.winfo_children():
                    bind_recursive(child)
            except:
                pass
        
        bind_recursive(card)
    
    def _load_professional_icon(self, container, icon_name):
        """Load and display professional icon."""
        try:
            icon = self.app.get_icon(icon_name, (28, 28))
            if icon:
                icon_label = ctk.CTkLabel(container, image=icon, text="")
                icon_label.place(relx=0.5, rely=0.5, anchor="center")
            else:
                # Fallback to emoji
                emoji_map = {
                    'angebots_workflow': '💼',
                    'pruefung_workflow': '🔍',
                    'finalisierung_workflow': '✅',
                    'projekt_workflow': '📊',
                    'play': '▶️',
                    'upload': '📤',
                    'businesswoman': '👤'
                }
                emoji = emoji_map.get(icon_name, '🔧')
                emoji_label = ctk.CTkLabel(
                    container,
                    text=emoji,
                    font=ctk.CTkFont(size=20),
                    text_color=UITheme.COLOR_TEXT_ON_PRIMARY
                )
                emoji_label.place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            # Final fallback
            fallback_label = ctk.CTkLabel(
                container,
                text="⚙️",
                font=ctk.CTkFont(size=20),
                text_color=UITheme.COLOR_TEXT_ON_PRIMARY
            )
            fallback_label.place(relx=0.5, rely=0.5, anchor="center")
    
    def _add_professional_button_hover(self, button):
        """Add professional button hover effects."""
        original_fg_color = button.cget("fg_color")
        
        def on_button_enter(event):
            button.configure(cursor="hand2")
            
        def on_button_leave(event):
            button.configure(cursor="arrow")
        
        button.bind("<Enter>", on_button_enter)
        button.bind("<Leave>", on_button_leave)
