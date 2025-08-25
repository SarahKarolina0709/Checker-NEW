"""
Modern UI components (buttons, cards, inputs, metric cards) built with design-system colors and sizing.
Text styling is inherited from the host; this module does not set any text styling explicitly.
"""

import customtkinter as ctk
from design_system import DesignSystem
from typing import Optional, Dict, Any


def _t(colors: Dict[str, Any], key: str, fallback_token: str):
    """Central token resolver to avoid repeated DesignSystem.get_color calls."""
    return colors.get(key, DesignSystem.get_color(fallback_token))


class ModernUIComponents:
    """Collection of modern UI components for professional interfaces.
    Text styling is centralized in the host and not overridden here.
    """

    @staticmethod
    def create_professional_card(parent, title, design_system, grid_config=None, accent_color=None) -> Dict[str, Any]:
        colors = design_system.get('colors', {})
        comps = design_system.get('components', {})
        spacing = design_system.get('spacing', {})
        borders = comps.get('borders', {})
        card_cfg = comps.get('card', {})
        # Prefer central design system tokens
        border_color = _t(colors, 'surface_border', 'surface_border')
        radius = card_cfg.get('border_radius', borders.get('radius_xl', 12))
        border_width = card_cfg.get('border_width', borders.get('width_thin', 1))
        padding = card_cfg.get('padding', spacing.get('lg', 24))

        card = ctk.CTkFrame(
            parent,
            fg_color=_t(colors, 'surface', 'surface'),
            corner_radius=radius,
            border_width=border_width,
            border_color=border_color,
        )

        if grid_config:
            card.grid(**grid_config)
        else:
            card.pack(fill="both", expand=True)

        # Simple header with optional accent (use primary_light if accent not provided)
        header_color = accent_color or _t(colors, 'primary_light', 'primary_light')
        header = ctk.CTkFrame(card, fg_color=header_color, corner_radius=radius, height=spacing.get('4xl', 60))
        header.pack(fill="x")
        header.pack_propagate(False)

        # Optional top accent strip when a different accent is passed
        if accent_color and accent_color != _t(colors, 'primary_light', 'primary_light'):
            ctk.CTkFrame(header, fg_color=accent_color, height=3).pack(side="top", fill="x")

        title_container = ctk.CTkFrame(header, fg_color="transparent")
        title_container.pack(fill="both", expand=True)

        title_label = ctk.CTkLabel(
            title_container,
            text=title,
            text_color=_t(colors, 'gray_900', 'gray_900'),
            anchor="center",
        )
        title_label.place(relx=0.5, rely=0.5, anchor="center")

        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=padding, pady=padding)

        return {"card": card, "content_frame": content, "header": header, "title_label": title_label}

    @staticmethod
    def create_professional_button(parent, text, command, design_system, style: str = "primary", size: str = "md", style_overrides: Optional[dict] = None, **kwargs) -> ctk.CTkButton:
        colors = design_system.get('colors', {})
        comps = design_system.get('components', {})
        borders = comps.get('borders', {})
        heights = comps.get('heights', {})
        btn_tokens = comps.get('buttons', {})

        def resolve(token_key: str, fallback_token: str):
            return _t(colors, token_key, fallback_token)

        btn_primary = resolve('button_primary', 'primary')
        btn_primary_hover = resolve('button_primary_hover', 'primary_hover')
        btn_primary_text = resolve('button_primary_text', 'white')

        btn_secondary = resolve('button_secondary', 'secondary')
        btn_secondary_hover = resolve('button_secondary_hover', 'secondary_hover')
        btn_secondary_text = resolve('button_secondary_text', 'white')

        btn_warning = resolve('button_warning', 'warning')
        btn_warning_hover = resolve('button_warning_hover', 'warning_hover')
        btn_warning_text = resolve('button_warning_text', 'white')

        btn_danger = resolve('button_danger', 'error')
        btn_danger_hover = resolve('button_danger_hover', 'error_hover')
        btn_danger_text = resolve('button_danger_text', 'white')

        styles = {
            'primary': {'fg_color': btn_primary, 'hover_color': btn_primary_hover, 'text_color': btn_primary_text},
            'secondary': {'fg_color': btn_secondary, 'hover_color': btn_secondary_hover, 'text_color': btn_secondary_text},
            'danger': {'fg_color': btn_danger, 'hover_color': btn_danger_hover, 'text_color': btn_danger_text, 'border_width': 1, 'border_color': btn_danger},
            'warning': {'fg_color': btn_warning, 'hover_color': btn_warning_hover, 'text_color': btn_warning_text},
        }
        style_cfg = {**styles.get(style, styles['primary']), **(style_overrides or {})}

        height_md = heights.get('button_md', 38)
        height_sm = heights.get('button_sm', max(28, int(height_md * 0.84)))
        height_lg = heights.get('button_lg', int(height_md * 1.2))
        radius = borders.get('radius_md', 8)
        sizes = {"sm": height_sm, "md": height_md, "lg": height_lg}
        chosen_height = sizes.get(str(size).lower(), height_md)

        if kwargs.get('state') == 'disabled':
            style_cfg['fg_color'] = _t(colors, 'button_disabled', 'gray_200')
            style_cfg['hover_color'] = style_cfg['fg_color']
            style_cfg['text_color'] = _t(colors, 'button_disabled_text', 'gray_500')

        btn_w = btn_tokens.get('min_width_md', 140)

        button = ctk.CTkButton(
            parent,
            text=text,
            command=command,
            width=kwargs.pop('width', btn_w),
            height=chosen_height,
            corner_radius=radius,
            **style_cfg,
            **kwargs,
        )
        ModernUIComponents._add_button_hover_effect(button)
        return button

    @staticmethod
    def create_input_group(parent, label_text, design_system, placeholder: str = "", **kwargs) -> Dict[str, Any]:
        colors = design_system.get('colors', {})
        comps = design_system.get('components', {})
        spacing = design_system.get('spacing', {})
        borders = comps.get('borders', {})
        heights = comps.get('heights', {})
        input_cfg = comps.get('input', {})

        container = ctk.CTkFrame(parent, fg_color="transparent")
        label = ctk.CTkLabel(
            container,
            text=label_text,
            text_color=_t(colors, 'gray_700', 'gray_700'),
        )
        label.pack(anchor="w", pady=(0, spacing.get('xs', 6)))

        entry = ctk.CTkEntry(
            container,
            placeholder_text=placeholder or f"{label_text} eingeben …",
            height=heights.get('input', input_cfg.get('height', 36)),
            fg_color=_t(colors, 'input_bg', 'input_bg'),
            border_width=input_cfg.get('border_width', borders.get('width_medium', 2)),
            border_color=_t(colors, 'input_border', 'input_border'),
            corner_radius=input_cfg.get('border_radius', borders.get('radius_md', 8)),
            text_color=_t(colors, 'input_text', 'input_text'),
            placeholder_text_color=_t(colors, 'input_placeholder', 'gray_400'),
            **kwargs,
        )
        # Decoupled focus handlers
        entry.bind('<FocusIn>', lambda _e: ModernUIComponents._on_focus_in_entry(entry, colors))
        entry.bind('<FocusOut>', lambda _e: ModernUIComponents._on_focus_out_entry(entry, colors))

        entry.pack(fill="x", pady=(0, spacing.get('md', 12)))
        container.pack(fill="x", pady=(0, spacing.get('lg', 16)))

        return {"container": container, "label": label, "entry": entry}
    

    @staticmethod
    def create_metric_card(parent, title, value, icon, design_system, trend: Optional[str] = None, color_scheme: str = "primary") -> ctk.CTkFrame:
        colors = design_system.get('colors', {})
        spacing = design_system.get('spacing', {})
        comps = design_system.get('components', {})
        borders = comps.get('borders', {})

        card = ctk.CTkFrame(
            parent,
            fg_color=_t(colors, 'surface', 'surface'),
            corner_radius=borders.get('radius_lg', 10),
            border_width=borders.get('width_thin', 1),
            border_color=_t(colors, 'surface_border', 'surface_border')
        )
        content = ctk.CTkFrame(card, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=spacing.get('lg', 16), pady=spacing.get('md', 12))
        top = ctk.CTkFrame(content, fg_color="transparent")
        top.pack(fill="x")
        # Fixed-width icon/text slot for alignment stability
        icon_slot = ctk.CTkFrame(top, fg_color="transparent", width=28, height=1)
        icon_slot.pack(side="left")
        icon_slot.pack_propagate(False)
        if icon:
            ctk.CTkLabel(icon_slot, text=str(icon), text_color=_t(colors, 'info', 'primary')).pack(fill="both", expand=True)

        if trend:
            text, is_up = ModernUIComponents._trend_str(trend)
            trend_color = _t(colors, 'success_500' if is_up else 'error_500', 'success' if is_up else 'error')
            ctk.CTkLabel(top, text=text, text_color=trend_color).pack(side="right")

        ctk.CTkLabel(
            content,
            text=str(value),
            text_color=_t(colors, 'gray_900', 'gray_900'),
        ).pack(pady=(spacing.get('sm', 8), spacing.get('xs', 6)))
        ctk.CTkLabel(
            content,
            text=title,
            text_color=_t(colors, 'gray_600', 'gray_600'),
        ).pack()
        return card

    @staticmethod
    def _add_button_hover_effect(button):
        # Cache initial border to restore later
        if not hasattr(button, "_initial_border_color"):
            try:
                button._initial_border_color = button.cget("border_color")
                button._initial_border_width = button.cget("border_width")
            except Exception:
                button._initial_border_color = None
                button._initial_border_width = None

        def on_enter(_):
            try:
                button.configure(cursor="hand2")
                hover_col = button.cget("hover_color")
                if hover_col is not None:
                    button.configure(border_color=hover_col)
                if button._initial_border_width is not None:
                    bw0 = int(button._initial_border_width or 0)
                    button.configure(border_width=(bw0 + 1) if bw0 < 2 else bw0)
            except Exception:
                pass

        def on_leave(_):
            try:
                button.configure(cursor="")
                if button._initial_border_color is not None:
                    button.configure(border_color=button._initial_border_color)
                if button._initial_border_width is not None:
                    button.configure(border_width=button._initial_border_width)
            except Exception:
                pass

        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)

    @staticmethod
    def _on_focus_in_entry(entry, colors):
        # Focus-in visual using tokens only
        try:
            entry.configure(
                border_color=_t(colors, 'input_border_focus', 'primary'),
                fg_color=colors.get('input_bg_focus', entry.cget('fg_color')),
            )
        except Exception:
            entry.configure(border_color=DesignSystem.get_color('primary'))

    @staticmethod
    def _on_focus_out_entry(entry, colors):
        # Restore neutral border using tokens only
        try:
            entry.configure(border_color=_t(colors, 'input_border', 'input_border'))
        except Exception:
            entry.configure(border_color=DesignSystem.get_color('surface_border'))

    @staticmethod
    def _trend_str(trend: Any):
        """Parse trend into display text and positivity flag.
        Accepts numbers or strings like '+3.2%', '-1', '3,2%'.
        Returns: (text, is_up)
        """
        try:
            s = str(trend)
            v = float(s.replace('%', '').replace(',', '.'))
            arrow = '↗' if v >= 0 else '↘'
            suffix = '%' if '%' in s else ''
            return f"{arrow} {v:+g}{suffix}", (v >= 0)
        except Exception:
            s = str(trend).strip()
            up = s.startswith('+')
            clean = s if up else s.lstrip('+-')
            return (f"↗ {clean}" if up else f"↘ {clean}"), up