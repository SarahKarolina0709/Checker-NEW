import os, sys, traceback
import customtkinter as ctk

BASE = os.path.dirname(__file__)

try:
    # Import welcome_screen from repo root
    sys.path.insert(0, BASE)
    import welcome_screen as ws
except Exception:
    print('Failed to import welcome_screen:')
    traceback.print_exc()
    sys.exit(1)

try:
    # Create a hidden root and WelcomeScreen
    ctk.set_appearance_mode("light")
    root = ctk.CTk()
    root.withdraw()

    class DummyApp:
        def show_main_interface(self, workflow_type):
            pass

    screen = ws.WelcomeScreen(root, DummyApp())
    # Directly invoke smart calendar path
    try:
        screen._show_smart_calendar()
        print('Invoked _show_smart_calendar() without crash.')
    except Exception:
        print('Exception inside _show_smart_calendar():')
        traceback.print_exc()

    # Also try the public calendar opener if present
    try:
        if hasattr(screen, '_show_calendar'):
            screen._show_calendar()
            print('Invoked _show_calendar() without crash.')
    except Exception:
        print('Exception inside _show_calendar():')
        traceback.print_exc()

    # Cleanup
    try:
        root.destroy()
    except Exception:
        pass

    sys.exit(0)
except Exception:
    print('Top-level failure while constructing WelcomeScreen or invoking calendar:')
    traceback.print_exc()
    sys.exit(2)
