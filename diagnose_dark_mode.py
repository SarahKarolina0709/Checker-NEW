#!/usr/bin/env python3
"""
Dark Mode Diagnostic Tool
=========================
Diagnose und Fix für Dark Mode Probleme

Gemäß Anweisungen: Niemals Dark Mode verwenden!
Immer nur Light Mode: ctk.set_appearance_mode("light")
"""

import customtkinter as ctk
from design_system import get_color, get_font

def diagnose_dark_mode():
    """Diagnose Dark Mode Probleme"""
    print("DARK MODE DIAGNOSTIC STARTED")
    print("=" * 50)

    # 1. Check CustomTkinter Version
    try:
        version = getattr(ctk, '__version__', 'unknown')
        print(f"CustomTkinter Version: {version}")
    except Exception as e:
        print(f"Cannot get CustomTkinter version: {e}")

    # 2. Check Current Appearance Mode
    try:
        current_mode = ctk.get_appearance_mode()
        print(f"Current Appearance Mode: {current_mode}")

        if isinstance(current_mode, str) and current_mode.lower() == 'dark':
            print("CRITICAL: Dark Mode is active!")
            print("FIXING: Setting to Light Mode...")
            ctk.set_appearance_mode("light")
            print("FIXED: Set to Light Mode")
        else:
            print("GOOD: Light Mode is active")

    except Exception as e:
        print(f"Cannot get appearance mode: {e}")

    # 3. Force Light Mode
    print("\nENFORCING LIGHT MODE...")
    try:
        ctk.set_appearance_mode("light")
        print("Light Mode enforced successfully")

        # Verify
        new_mode = ctk.get_appearance_mode()
        print(f"Verified Mode: {new_mode}")

    except Exception as e:
        print(f"Error enforcing Light Mode: {e}")

    # 4. Test Simple Window
    print("\nTESTING SIMPLE WINDOW...")
    try:
        # Create test window
        root = ctk.CTk()
        root.title("Dark Mode Test - Should be Light!")
        root.geometry("400x300")

        # Force light mode again
        ctk.set_appearance_mode("light")

        # Test elements
        test_frame = ctk.CTkFrame(
            root,
            fg_color=get_color('surface'),
            border_width=2,
            border_color=get_color('surface_border')
        )
        test_frame.pack(fill="both", expand=True, padx=20, pady=20)

        title_label = ctk.CTkLabel(
            test_frame,
            text="DARK MODE TEST",
            font=ctk.CTkFont(*get_font('heading_md')),
            text_color=get_color('gray_900')
        )
        title_label.pack(pady=20)

        status_label = ctk.CTkLabel(
            test_frame,
            text="This should be LIGHT MODE",
            font=ctk.CTkFont(*get_font('body_md')),
            text_color=get_color('gray_700')
        )
        status_label.pack(pady=10)

        mode_label = ctk.CTkLabel(
            test_frame,
            text=f"Mode: {ctk.get_appearance_mode()}",
            font=ctk.CTkFont(*get_font('button_sm')),
            text_color=get_color('success_600')
        )
        mode_label.pack(pady=5)

        # Test button
        test_button = ctk.CTkButton(
            test_frame,
            text="LIGHT MODE CONFIRMED",
            font=ctk.CTkFont(*get_font('button_md')),
            fg_color=get_color('info'),
            hover_color=get_color('info_hover'),
            text_color=get_color('white'),
            height=40,
            command=lambda: print("Light Mode Button Clicked!")
        )
        test_button.pack(pady=20)

        # Instructions
        instr_label = ctk.CTkLabel(
            test_frame,
            text="If you see dark colors, there's a problem!",
            font=ctk.CTkFont(*get_font('caption')),
            text_color=get_color('gray_500')
        )
        instr_label.pack(pady=5)

        print("Test window created successfully")
        print("INSTRUCTIONS:")
        print("   - Window should have WHITE background")
        print("   - All text should be DARK on WHITE")
        print("   - Button should be BLUE")
        print("   - If you see dark themes, there's a bug!")

        root.mainloop()

    except Exception as e:
        print(f"Error creating test window: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnose_dark_mode()