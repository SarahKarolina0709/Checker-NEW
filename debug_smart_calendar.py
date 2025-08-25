import os, sys, traceback
import customtkinter as ctk

# Add src/ui to path
BASE = os.path.dirname(__file__)
src_ui = os.path.join(BASE, 'src', 'ui')
if src_ui not in sys.path:
    sys.path.append(src_ui)

# Dummy app with minimal attributes used by SmartUploadCalendar
class DummyKundenManager:
    def __init__(self):
        # Force demo data path that doesn't exist to avoid FS scanning errors
        self.base_path = os.path.join(BASE, '_nonexistent_kunden_path_')

class DummyApp:
    def __init__(self):
        self.kunden_manager = DummyKundenManager()
        # Optional placeholders the calendar may probe for
        self.workflow_router = None

try:
    from smart_upload_calendar import SmartUploadCalendar
except Exception:
    print('Failed to import SmartUploadCalendar:')
    traceback.print_exc()
    sys.exit(1)

try:
    root = ctk.CTk()
    root.withdraw()  # we don't want to show a window for this debug run
    frame = ctk.CTkFrame(root)
    frame.pack()
    cal = SmartUploadCalendar(master=frame, app=DummyApp(), fg_color="transparent")
    # Call reload to exercise code paths used during app integration
    if hasattr(cal, 'reload'):
        cal.reload()
    print('SmartUploadCalendar instantiated successfully for debug run.')
    sys.exit(0)
except Exception:
    print('SmartUploadCalendar raised an exception during initialization:')
    traceback.print_exc()
    sys.exit(2)
