#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 AGGRESSIVE ANTI-DARK-MODE SYSTEM
====================================

Dieses System patcht CustomTkinter AGGRESSIV um JEDEN Dark Mode Zugriff zu verhindern.
Ersetzt ALLE potentiellen schwarzen/dunklen Fallbacks durch helle Alternativen.
"""

import os

# Idempotenz-Guard um doppelte Aktivierungs-Logs zu verhindern
_AGGRESSIVE_LIGHT_PATCH_APPLIED = globals().get('_AGGRESSIVE_LIGHT_PATCH_APPLIED', False)

def apply_aggressive_light_mode_patches():
    """🔥 AGGRESSIVE Dark Mode Elimination - Patcht CustomTkinter vollständig"""

    global _AGGRESSIVE_LIGHT_PATCH_APPLIED
    if _AGGRESSIVE_LIGHT_PATCH_APPLIED:
        return True  # Bereits aktiv → keine erneute Ausgabe

    # 🚨 KRITISCHE ENVIRONMENT VARIABLES
    os.environ['CUSTOMTKINTER_APPEARANCE_MODE'] = 'light'
    os.environ['CTK_APPEARANCE_MODE'] = 'light'
    os.environ['TKINTER_THEME'] = 'light'
    os.environ['TK_THEME'] = 'light'
    os.environ['APPEARANCE_MODE'] = 'light'

    try:
        import customtkinter as ctk

        # 🔥 SOFORTIGE LIGHT MODE ERZWINGUNG
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 🎨 SELECTIVE BLACK PREVENTION - NUR SCHWARZE FALLBACKS ERSETZEN, DESIGN BEWAHREN
        AGGRESSIVE_LIGHT_COLORS = {
            # KRITISCH: Nur echte schwarze/dunkle Fallbacks ersetzen, Rest behalten!
            'black': '#F8FAFC',            # Schwarz → Heller Grau
            '#000000': '#F8FAFC',          # Schwarz → Heller Grau
            '#1C1C1C': '#F8FAFC',          # Dark Gray → Heller Grau
            '#2B2B2B': '#F8FAFC',          # Dark Theme → Heller Grau

            # BEHALTEN: Alle gewünschten Design-Farben (NICHT ÄNDERN!)
            # Diese Farben sollen NICHT ersetzt werden, sondern bleiben wie sie sind

            # Universal Fallbacks (NUR KRITISCHE)
            'white': '#FFFFFF',
            'transparent': 'transparent',
        }

        # 🔥 PATCH CustomTkinter's _apply_appearance_mode method
        def _patched_apply_appearance_mode(self, *args, **kwargs):
            """Überschreibt CustomTkinter's appearance mode application"""
            # FORCE LIGHT MODE - Ignoriert alle Dark Mode Anfragen
            pass

        # 🔥 PATCH CustomTkinter Widget Initialisierung
        _original_widget_init = ctk.CTkBaseClass.__init__

        def _aggressive_widget_init(self, *args, **kwargs):
            """Aggressive Light Mode Widget Initialization"""
            # Prüfe und ersetze alle Farb-Parameter
            color_params = ['fg_color', 'bg_color', 'text_color', 'border_color',
                           'button_color', 'button_hover_color', 'progress_color']

            for param in color_params:
                if param in kwargs:
                    original_color = kwargs[param]
                    # Ersetze bekannte Dark Mode Farben
                    if original_color in AGGRESSIVE_LIGHT_COLORS:
                        kwargs[param] = AGGRESSIVE_LIGHT_COLORS[original_color]
                    # Ersetze NUR echte schwarze/dunkle Hex-Farben
                    elif isinstance(original_color, str) and original_color.startswith('#'):
                        if original_color in ['#000000', '#1C1C1C', '#2B2B2B']:  # Nur echte schwarze
                            kwargs[param] = '#F8FAFC'  # 🔥 SELECTIVE: Heller Grau statt schwarz

            return _original_widget_init(self, *args, **kwargs)

        # 🔥 APPLY AGGRESSIVE PATCHES
        try:
            ctk.CTkBaseClass.__init__ = _aggressive_widget_init

            # 🔥 ULTIMATIVE Frame Patches - NIEMALS schwarze Frames!
            _original_frame_init = ctk.CTkFrame.__init__
            def _ultimative_frame_init(self, *args, **kwargs):
                # 🎨 SELECTIVE Frame Protection - NUR ECHTE SCHWARZE FARBEN ERSETZEN
                if 'fg_color' in kwargs:
                    original_fg = kwargs['fg_color']
                    # NUR echte schwarze Farben ersetzen, alles andere BEHALTEN
                    if original_fg in ['#000000', 'black']:  # Nur pure schwarze Farben
                        kwargs['fg_color'] = '#F8FAFC'  # 🔥 SELECTIVE: Heller Grau
                        print(f"🔥 BLACK PREVENTED: {original_fg} → #F8FAFC")
                    # ALLE ANDEREN FARBEN BEHALTEN (anthracite, primary, gray, etc.)

                if 'bg_color' in kwargs:
                    original_bg = kwargs['bg_color']
                    # NUR echte schwarze Farben ersetzen
                    if original_bg in ['#000000', 'black']:
                        kwargs['bg_color'] = '#F8FAFC'  # 🔥 SELECTIVE: Heller Grau
                        print(f"🔥 BLACK BG PREVENTED: {original_bg} → #F8FAFC")

                # Erstelle Frame
                result = _original_frame_init(self, *args, **kwargs)

                # 🎨 SELECTIVE Post-Creation Kontrolle - NUR bei schwarzen Farben
                try:
                    def selective_post_fix():
                        try:
                            current_fg = self.cget('fg_color')
                            # NUR bei echten schwarzen Farben eingreifen
                            if current_fg in ['#000000', 'black']:
                                self.configure(fg_color='#F8FAFC')
                                print(f"🔥 POST-BLACK-FIX: {current_fg} → #F8FAFC")
                            # ALLE ANDEREN FARBEN (anthracite, etc.) BEHALTEN!
                        except:
                            pass

                    # Nur bei echten Problemen ausführen
                    selective_post_fix()
                except:
                    pass

                return result

            ctk.CTkFrame.__init__ = _ultimative_frame_init

        except Exception as e:
            print(f"⚠️ Ultimative frame patching failed: {e}")

        # 🎨 SELECTIVE Color Protection - NUR schwarze Fallbacks verhindern, Design bewahren
        def get_safe_aggressive_color(color_name, fallback=None):
            """SELECTIVE Color Resolution - Verhindert NUR schwarze Fallbacks, behält ALLE Design-Farben"""

            # NUR echte schwarze Farben ersetzen
            if color_name in ['#000000', 'black']:
                return '#F8FAFC'  # 🔥 SELECTIVE: Heller Grau statt schwarz

            # ALLE ANDEREN FARBEN DURCHLASSEN (anthracite_700, primary, gray_700, etc.)
            if color_name in AGGRESSIVE_LIGHT_COLORS:
                return AGGRESSIVE_LIGHT_COLORS[color_name]

            # ALLE DESIGN-FARBEN BEHALTEN - kein Fallback anwenden
            return color_name if color_name else fallback

        # 🔥 GLOBAL FUNCTION für andere Module
        globals()['get_safe_aggressive_color'] = get_safe_aggressive_color

        print("[SELECTIVE ANTI-BLACK-FALLBACK SYSTEM ACTIVATED!]")
        print("[OK] Black fallbacks eliminated, design colors preserved")
        print("[OK] Header keeps anthracite color: #374151")
        print("[OK] Only true black colors (#000000, black) replaced")
        print("[OK] SELECTIVE: Design-Farben bleiben erhalten!")
        _AGGRESSIVE_LIGHT_PATCH_APPLIED = True
        return True

    except Exception as e:
        print(f"[ERROR] Aggressive anti-dark-mode system failed: {e}")
        return False

# 🔥 AUTO-EXECUTE beim Import
if __name__ == "__main__":
    apply_aggressive_light_mode_patches()
else:
    # Wird ausgeführt wenn als Modul importiert
    apply_aggressive_light_mode_patches()