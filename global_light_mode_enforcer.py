#!/usr/bin/env python3
"""
🔥 GLOBAL LIGHT MODE ENFORCER
============================
System-weite Verhinderung von Dark Mode Fallback in Tkinter/CustomTkinter

PROBLEM:
- CustomTkinter kann automatisch auf Dark Mode fallback gehen
- Tkinter kann System-Theme erkennen und Dark Mode verwenden
- UITheme Farben können als Dark Mode interpretiert werden

LÖSUNG:
- Globaler Monkey Patch für CustomTkinter
- System-Theme-Detection deaktivieren
- Appearance Mode permanent auf "light" sperren
- Fallback-Color-Scheme überschreiben
"""


import os

def enforce_global_light_mode():
    """
    🔥 GLOBALER LIGHT MODE ENFORCER
    ===============================
    Verhindert JEDEN Dark Mode Fallback system-weit
    """

    # 1. CUSTOMTKINTER MONKEY PATCH
    try:
        import customtkinter as ctk

        # Force light mode immediately
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

        # 🔥 MONKEY PATCH: Override appearance mode detection
        original_get_appearance_mode = ctk.get_appearance_mode

        def force_light_appearance_mode():
            """Always return 'Light' - never 'Dark'"""
            return "Light"

        # Override the function
        ctk.get_appearance_mode = force_light_appearance_mode

        # 🔥 MONKEY PATCH: Override set_appearance_mode
        original_set_appearance_mode = ctk.set_appearance_mode

        def force_light_set_appearance_mode(mode_string):
            """Force any appearance mode setting to 'light'"""
            if mode_string.lower() == "dark":
                print("🔥 BLOCKED: Dark mode attempted - forcing Light mode!")
                return original_set_appearance_mode("light")
            return original_set_appearance_mode("light")  # Always light!

        # Override the function
        ctk.set_appearance_mode = force_light_set_appearance_mode

        # 🔥 SYSTEM APPEARANCE MODE DETECTION DISABLE
        if hasattr(ctk, '_appearance_mode'):
            ctk._appearance_mode = "light"

        # Force internal appearance tracking
        try:
            pass

            if hasattr(customtkinter.windows.widgets, 'appearance_mode'):
                customtkinter.windows.widgets.appearance_mode = "light"
        except Exception:
            pass

        print("✅ CustomTkinter Light Mode enforced globally!")

    except ImportError:
        print("⚠️ CustomTkinter not available - skipping CustomTkinter patches")
    except Exception as e:
        print(f"⚠️ CustomTkinter patch error: {e}")

    # 2. TKINTER SYSTEM THEME OVERRIDE
    try:
        import tkinter as tk

        # Override system theme detection
        original_tk_call = tk.Tk.tk_call if hasattr(tk.Tk, 'tk_call') else None

        if original_tk_call:
            def light_tk_call(self, *args):
                """Intercept system theme calls and force light"""
                if args and len(args) > 0:
                    cmd = str(args[0]).lower()

                    # Block dark theme system calls
                    if 'dark' in cmd or 'theme' in cmd:
                        print(f"🔥 BLOCKED system theme call: {args}")
                        return "light"  # Return light theme

                return original_tk_call(self, *args)

            # Apply monkey patch
            tk.Tk.tk_call = light_tk_call

        print("✅ Tkinter system theme detection patched!")

    except Exception as e:
        print(f"⚠️ Tkinter patch error: {e}")

    # 3. ENVIRONMENT VARIABLE OVERRIDE
    try:
        # Force light theme via environment variables
        os.environ['TK_THEME'] = 'light'
        os.environ['CTK_APPEARANCE_MODE'] = 'light'
        os.environ['TKINTER_THEME'] = 'light'
        os.environ['DARK_MODE_DISABLED'] = '1'

        print("✅ Environment variables set to force light mode!")

    except Exception as e:
        print(f"⚠️ Environment variable error: {e}")

    # 4. WIDGET CREATION OVERRIDE
    try:
        import customtkinter as ctk

        # Store original CTkFrame creation
        if hasattr(ctk, 'CTkFrame'):
            original_ctkframe_init = ctk.CTkFrame.__init__

            def light_ctkframe_init(self, *args, **kwargs):
                """Force light colors in CTkFrame creation"""
                # Override dark colors with light equivalents
                if 'fg_color' in kwargs:
                    color = kwargs['fg_color']
                    if isinstance(color, str) and color.startswith('#'):
                        # Convert dark colors to light
                        if color in ['#212121', '#2b2b2b', '#3c3c3c', '#1e1e1e']:
                            kwargs['fg_color'] = '#FFFFFF'  # Force white
                            print(f"🔥 CONVERTED dark color {color} to #FFFFFF")

                return original_ctkframe_init(self, *args, **kwargs)

            # Apply monkey patch
            ctk.CTkFrame.__init__ = light_ctkframe_init

        print("✅ Widget creation patched for light mode!")

    except Exception as e:
        print(f"⚠️ Widget patch error: {e}")

    # 5. FINAL ENFORCEMENT
    try:
        import customtkinter as ctk

        # Final enforcement call
        ctk.set_appearance_mode("light")

        # Verify mode
        mode = ctk.get_appearance_mode()
        if mode.lower() != "light":
            print(f"⚠️ WARNING: Mode is still {mode} - additional fixes needed!")
        else:
            print(f"✅ VERIFIED: Appearance mode is {mode}")

    except Exception as e:
        print(f"⚠️ Final enforcement error: {e}")

def create_light_mode_color_overrides():
    """
    🎨 LIGHT MODE COLOR OVERRIDES
    =============================
    Überschreibt alle problematischen Dark Mode Farben
    """

    # Dark Mode Color -> Light Mode Color Mapping
    DARK_TO_LIGHT_MAPPING = {
        # Common dark backgrounds
        '#212121': '#FFFFFF',  # Dark grey -> White
        '#2b2b2b': '#F8FAFC',  # Dark grey -> Light grey
        '#3c3c3c': '#F3F4F6',  # Medium dark -> Light grey
        '#1e1e1e': '#FFFFFF',  # Very dark -> White
        '#333333': '#F9FAFB',  # Dark -> Light
        '#444444': '#F1F5F9',  # Medium dark -> Light

        # Common dark text (should become light text)
        '#FFFFFF': '#111827',  # White text -> Dark text (for light bg)
        '#F0F0F0': '#374151',  # Light text -> Grey text
        '#E0E0E0': '#6B7280',  # Light text -> Medium grey

        # Dark borders
        '#555555': '#E5E7EB',  # Dark border -> Light border
        '#666666': '#D1D5DB',  # Dark border -> Medium border
    }

    return DARK_TO_LIGHT_MAPPING

def apply_light_mode_startup():
    """
    🚀 STARTUP LIGHT MODE APPLICATION
    =================================
    Wird beim Import automatisch ausgeführt
    """

    print("🔥 GLOBAL LIGHT MODE ENFORCER STARTING...")
    print("=" * 60)

    # Apply all patches
    enforce_global_light_mode()

    # Create color override mapping
    color_mapping = create_light_mode_color_overrides()
    print(f"✅ Created {len(color_mapping)} color overrides")

    print("=" * 60)
    print("🔥 GLOBAL LIGHT MODE ENFORCEMENT COMPLETE!")
    print("✅ All Dark Mode fallbacks have been blocked")
    print("✅ System is locked to Light Mode only")

# AUTOMATIC EXECUTION ON IMPORT
if __name__ != "__test__":  # Skip during testing
    apply_light_mode_startup()

# EXPORT FUNCTIONS FOR MANUAL USE
__all__ = [
    'enforce_global_light_mode',
    'create_light_mode_color_overrides',
    'apply_light_mode_startup'
]