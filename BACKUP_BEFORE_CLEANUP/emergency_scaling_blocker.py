"""
Emergency ScalingTracker Blocker
Blockiert den ScalingTracker bevor er Probleme verursachen kann
"""

import sys

print("[EMERGENCY PATCH] ScalingTracker-Blocker wird aktiviert...")

# Intercepte das scaling_tracker Modul beim Import
class ScalingTrackerBlocker:
    def __init__(self):
        self.blocked_modules = [
            'customtkinter.windows.widgets.scaling.scaling_tracker',
            'customtkinter.windows.widgets.scaling',
        ]
        self.install_import_hook()
    
    def install_import_hook(self):
        """Installiert Import-Hook um ScalingTracker zu blockieren"""
        import builtins
        original_import = builtins.__import__
        
        def patched_import(name, globals=None, locals=None, fromlist=(), level=0):
            if 'scaling_tracker' in name:
                print(f"[EMERGENCY PATCH] Import blockiert: {name}")
                # Erstelle Mock-Modul
                return self.create_mock_scaling_tracker()
            return original_import(name, globals, locals, fromlist, level)
        
        builtins.__import__ = patched_import
        print("[EMERGENCY PATCH] Import-Hook installiert")
    
    def create_mock_scaling_tracker(self):
        """Erstellt Mock ScalingTracker Modul"""
        class MockModule:
            class ScalingTracker:
                @staticmethod
                def get_window_scaling(window):
                    return 1.0
                @staticmethod 
                def get_widget_scaling(widget):
                    return 1.0
                @staticmethod
                def set_widget_scaling(scaling_value):
                    print(f"[EMERGENCY PATCH] Mock set_widget_scaling: {scaling_value}")
                    return 1.0
                @staticmethod
                def set_window_scaling(scaling_value):
                    print(f"[EMERGENCY PATCH] Mock set_window_scaling: {scaling_value}")
                    return 1.0
                @staticmethod
                def add_widget(widget_callback, widget):
                    print("[EMERGENCY PATCH] Mock add_widget")
                    pass
                @staticmethod
                def remove_widget(widget_callback, widget):
                    print("[EMERGENCY PATCH] Mock remove_widget")
                    pass
                @staticmethod
                def check_dpi_scaling(window):
                    print("[EMERGENCY PATCH] Mock check_dpi_scaling - BLOCKIERT")
                    pass
                @staticmethod
                def activate_high_dpi_awareness():
                    print("[EMERGENCY PATCH] Mock activate_high_dpi_awareness")
                    pass
                @staticmethod
                def deactivate_automatic_dpi_awareness():
                    print("[EMERGENCY PATCH] Mock deactivate_automatic_dpi_awareness")
                    pass
        
        return MockModule()

# Aktiviere Emergency Blocker
if 'customtkinter' not in sys.modules:
    blocker = ScalingTrackerBlocker()
    print("[EMERGENCY PATCH] ScalingTracker-Blocker erfolgreich aktiviert")
else:
    print("[EMERGENCY PATCH] CustomTkinter bereits importiert - zu spät für Blocker")

# Zusätzlicher direkter Patch für bereits geladene Module
try:
    import customtkinter
    if hasattr(customtkinter, 'ScalingTracker'):
        print("[EMERGENCY PATCH] Direkte ScalingTracker-Überschreibung...")
        
        class EmergencyScalingTracker:
            @staticmethod
            def get_window_scaling(window):
                return 1.0
            @staticmethod 
            def get_widget_scaling(widget):
                return 1.0
            @staticmethod
            def set_widget_scaling(scaling_value):
                return 1.0
            @staticmethod
            def set_window_scaling(scaling_value):
                return 1.0
            @staticmethod
            def add_widget(widget_callback, widget):
                pass
            @staticmethod
            def remove_widget(widget_callback, widget):
                pass
            @staticmethod
            def check_dpi_scaling(window):
                print("[EMERGENCY PATCH] DPI Check blockiert!")
                pass
            @staticmethod
            def activate_high_dpi_awareness():
                pass
            @staticmethod
            def deactivate_automatic_dpi_awareness():
                pass
        
        customtkinter.ScalingTracker = EmergencyScalingTracker()
        print("[EMERGENCY PATCH] CustomTkinter ScalingTracker direkt überschrieben")
        
except ImportError:
    print("[EMERGENCY PATCH] CustomTkinter noch nicht importiert")

print("[EMERGENCY PATCH] Emergency ScalingTracker Blocker geladen")
