"""
🏗️ MODERN UI COMPONENTS FOR PROFESSIONAL GUI
Modern reusable UI components for enhanced user experience
"""

import customtkinter as ctk

class ModernUIComponents:
    """Collection of modern UI components for professional interfaces"""

    @staticmethod
    def create_professional_card(parent, title, design_system, grid_config=None, accent_color=None):
        """Create modern professional card with Enterprise-Grade colors und optionaler Akzentfarbe"""
        # Main card container mit verbesserter Border-Farbe (Fallback falls nicht verfügbar)
        border_color = design_system['colors'].get('gray_300', '#D1D5DB')  # Fallback hinzugefügt

        card = ctk.CTkFrame(parent,
                          fg_color="#FFFFFF",
                          corner_radius=design_system['components']['card']['border_radius'],
                          border_width=design_system['components']['card']['border_width'],
                          border_color=border_color)

        if grid_config:
            card.grid(**grid_config)
        else:
            card.pack(fill="both", expand=True)  # Default packing wenn kein grid_config

        # Subtle shadow effect (simulated with layered frame) - Fixed Color
        shadow_layer = ctk.CTkFrame(card,
                                  fg_color="#E0E0E0",  # Valid light gray shadow
                                  corner_radius=design_system['components']['card']['border_radius'],
                                  height=2)
        shadow_layer.place(relx=0, rely=1, relwidth=1, anchor="sw")

        # Professional header mit Enterprise-Farben und funktionsspezifischer Akzentfarbe
        header_color = accent_color or design_system['colors'].get('primary_50', '#F0F6FF')

        # Corner radius für header - CustomTkinter unterstützt keine Tupel!
        card_radius = design_system['components']['card']['border_radius']
        header_corner_radius = card_radius if isinstance(card_radius, (int, float)) else 8

        header = ctk.CTkFrame(card,
                            fg_color=header_color,
                            corner_radius=header_corner_radius,  # Nur einfacher Radius
                            height=60)
        header.pack(fill="x")
        header.pack_propagate(False)

        # Accent border für funktionsspezifische Hierarchie (nur wenn unterschiedlich)
        primary_50_fallback = design_system['colors'].get('primary_50', '#F0F6FF')
        if accent_color and accent_color != primary_50_fallback:
            accent_border = ctk.CTkFrame(header,
                                       fg_color=accent_color,
                                       height=3)
            accent_border.pack(side="top", fill="x")

        # Perfekt zentrierte Titel-Container
        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(fill="both", expand=True)

        title_label = ctk.CTkLabel(title_container,
                                 text=title,
                                 font=design_system['typography']['heading_sm'],
                                 text_color=design_system['colors'].get('gray_900', '#2C3542'),  # Fallback
                                 anchor="center")  # Explizite Zentrierung
        title_label.place(relx=0.5, rely=0.5, anchor="center")  # Perfekte Zentrierung

        # Content area (mit sicherem Padding-Zugriff)
        card_padding = design_system['components']['card']['padding']
        safe_padding = card_padding if isinstance(card_padding, (int, float)) else 20

        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.pack(fill="both", expand=True,
                         padx=safe_padding,
                         pady=safe_padding)

        return {'card': card, 'content_frame': content_frame, 'header': header}

    @staticmethod
    def create_professional_button(parent, text, command, design_system, style="primary", **kwargs):
        """Create modern button with ordentlichem Schriftsystem"""
        styles = {
            'primary': {
                'fg_color': design_system['colors']['primary_600'],    # Enterprise Akzent-Blau (behält Kontrast zu Anthrazit)
                'hover_color': design_system['colors']['primary_700'],  # Aktivzustand
                'text_color': '#FFFFFF',
                'font': design_system['typography']['button_md']        # Einheitliche Standard Button Schrift
            },
            'secondary': {
                'fg_color': design_system['colors'].get('anthracite_700', '#455A73'),  # Anthrazit für Secondary Buttons
                'hover_color': design_system['colors'].get('anthracite_600', '#566B82'),  # Helleres Anthrazit für Hover
                'text_color': '#FFFFFF',  # Weiß für besseren Kontrast auf Anthrazit
                'border_width': 1,
                'border_color': design_system['colors'].get('anthracite_600', '#566B82'), # Anthrazit-Rand
                'font': design_system['typography']['button_md']        # Einheitliche Standard Button Schrift
            },
            'danger': {
                'fg_color': '#A21B1B',      # Noch sanfteres, dunkleres Rot für professionellen Look
                'hover_color': '#991B1B',    # Weicherer Hover-Effekt
                'text_color': '#FFFFFF',
                'font': design_system['typography']['button_md'],       # Einheitliche Standard Button Schrift
                'border_width': 1,
                'border_color': '#8B1A1A'    # Sanfter Rahmen für Eleganz
            },
            'warning': {
                'fg_color': design_system['colors']['warning_600'],    # Enterprise Warning-Farbe
                'hover_color': design_system['colors']['warning_700'],  # Dunklerer Hover
                'text_color': '#FFFFFF',
                'font': design_system['typography']['button_md']        # Einheitliche Standard Button Schrift
            }
        }

        style_config = styles.get(style, styles['primary'])

        # Merge with any custom kwargs
        button_config = {
            'text': text,
            'command': command,
            'height': design_system['components']['button']['height'],
            'corner_radius': design_system['components']['button']['border_radius'],
            **style_config,
            **kwargs
        }

        button = ctk.CTkButton(parent, **button_config)

        # Add hover animations
        ModernUIComponents._add_button_hover_effect(button)

        return button

    @staticmethod
    def create_input_group(parent, label_text, design_system, placeholder="", **kwargs):
        """Create modern input field with floating labels"""
        container = ctk.CTkFrame(parent, fg_color="transparent")

        # Label
        label = ctk.CTkLabel(container,
                           text=label_text,
                           font=design_system['typography']['body_md'],
                           text_color=design_system['colors']['gray_700'])
        label.pack(anchor="w", pady=(0, design_system['spacing']['xs']))

        # Entry field mit einheitlicher Schriftart und verbessertem Kontrast
        entry_config = {
            'placeholder_text': placeholder or f"Enter {label_text.lower()}...",
            'height': design_system['components']['input']['height'],
            'font': design_system['typography']['input_text'],              # Einheitliche Input Font
            'fg_color': "#FFFFFF",
            'border_width': design_system['components']['input']['border_width'],
            'border_color': design_system['colors']['gray_300'],
            'corner_radius': design_system['components']['input']['border_radius'],
            'text_color': design_system['colors']['gray_900'],              # Dunklerer Text für besseren Kontrast
            'placeholder_text_color': design_system['colors']['gray_450'],   # Verbesserter Placeholder-Kontrast
            **kwargs
        }

        entry = ctk.CTkEntry(container, **entry_config)

        # Focus effects
        def on_focus_in(event):
            entry.configure(border_color=design_system['colors']['primary_500'])
        def on_focus_out(event):
            entry.configure(border_color=design_system['colors']['gray_300'])

        entry.bind('<FocusIn>', on_focus_in)
        entry.bind('<FocusOut>', on_focus_out)

        entry.pack(fill="x", pady=(0, design_system['spacing']['md']))
        container.pack(fill="x", pady=(0, design_system['spacing']['lg']))

        return {'container': container, 'label': label, 'entry': entry}

    @staticmethod
    def create_metric_card(parent, title, value, icon, design_system, trend=None, color_scheme="primary"):
        """Create professional metric cards like modern dashboards"""
        card = ctk.CTkFrame(parent,
                          fg_color="#FFFFFF",
                          corner_radius=10,
                          border_width=1,
                          border_color=design_system['colors']['gray_200'])

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=design_system['spacing']['lg'], pady=design_system['spacing']['md'])

        # Icon and trend row
        top_row = ctk.CTkFrame(content, fg_color="transparent")
        top_row.pack(fill="x")

        icon_label = ctk.CTkLabel(top_row,
                                text=icon,
                                font=ctk.CTkFont(size=20),  # Etwas kleiner für bessere Proportionen
                                text_color=design_system['colors']['primary_600'])  # Enterprise Akzent-Blau für Icons
        icon_label.pack(side="left")

        if trend:
            trend_color = design_system['colors']['success_600'] if trend.startswith('+') else design_system['colors']['error_600']  # Enterprise Trend-Farben
            trend_label = ctk.CTkLabel(top_row,
                                     text=f"↗ {trend}" if trend.startswith('+') else f"↘ {trend}",
                                     font=design_system['typography']['caption'],
                                     text_color=trend_color)
            trend_label.pack(side="right")

        # Value mit ordentlicher Schriftart aus Design System
        value_label = ctk.CTkLabel(content,
                                 text=str(value),
                                 font=design_system['typography']['metric_value'],      # Ordentliche Metrik-Schrift
                                 text_color=design_system['colors']['gray_900'])  # Wärmeres Anthrazit für Werte
        value_label.pack(pady=(design_system['spacing']['sm'], design_system['spacing']['xs']))

        # Title mit ordentlicher Schriftart
        title_label = ctk.CTkLabel(content,
                                 text=title,
                                 font=design_system['typography']['metric_label'],      # Ordentliche Metrik-Label Schrift
                                 text_color=design_system['colors']['gray_600'])
        title_label.pack()

        return card

    @staticmethod
    def _add_button_hover_effect(button):
        """Add subtle hover animation to buttons"""
        def on_enter(event):
            button.configure(cursor="hand2")

        def on_leave(event):
            button.configure(cursor="")

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)