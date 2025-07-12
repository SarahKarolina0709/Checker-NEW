"""
Nuclear CustomTkinter ScalingTracker Killer
============================================
This module completely disables all CustomTkinter scaling functionality
to prevent window geometry issues and invalid command name errors.
"""

import sys
import types

def nuclear_disable_scaling():
    """
    Nuclear option: Completely disables all CustomTkinter scaling functionality
    """
    print("[NUCLEAR] Starting nuclear CustomTkinter scaling disabler...")
    
    try:
        # Step 1: Disable DPI awareness
        import customtkinter as ctk
        ctk.deactivate_automatic_dpi_awareness()
        ctk.set_widget_scaling(1.0)
        ctk.set_window_scaling(1.0)
        print("[NUCLEAR] DPI awareness disabled")
        
        # Step 2: Replace ScalingTracker module entirely
        try:
            import customtkinter.windows.widgets.scaling.scaling_tracker as scaling_tracker
            
            # Create a completely safe mock module
            class NuclearScalingTracker:
                """Nuclear dummy ScalingTracker that does absolutely nothing"""
                
                def __init__(self, *args, **kwargs):
                    self._widgets = set()
                    self._scaling_factor = 1.0
                
                def check_dpi_scaling(self, *args, **kwargs):
                    """Nuclear safe method - does nothing"""
                    return None
                
                def add_widget(self, widget, *args, **kwargs):
                    """Nuclear safe method - just tracks widget"""
                    if widget:
                        self._widgets.add(widget)
                
                def remove_widget(self, widget, *args, **kwargs):
                    """Nuclear safe method - just removes widget"""
                    if widget and widget in self._widgets:
                        self._widgets.remove(widget)
                
                def set_widget_scaling(self, scaling_value, *args, **kwargs):
                    """Nuclear safe method - does nothing"""
                    return None
                
                def get_widget_scaling(self, *args, **kwargs):
                    """Nuclear safe method - always returns 1.0"""
                    return 1.0
                
                def update_scaling_factor(self, *args, **kwargs):
                    """Nuclear safe method - does nothing"""
                    return None
                
                def __getattr__(self, name):
                    """Nuclear safe fallback - returns safe dummy function"""
                    def safe_dummy(*args, **kwargs):
                        return None
                    return safe_dummy
            
            # Replace the class
            scaling_tracker.ScalingTracker = NuclearScalingTracker
            print("[NUCLEAR] ScalingTracker class completely replaced")
            
            # Also replace any existing instances
            if hasattr(scaling_tracker, '_scaling_tracker'):
                scaling_tracker._scaling_tracker = NuclearScalingTracker()
                print("[NUCLEAR] Existing ScalingTracker instance replaced")
            
        except ImportError:
            print("[NUCLEAR] ScalingTracker module not found - probably already disabled")
        except Exception as e:
            print(f"[NUCLEAR] Could not replace ScalingTracker: {e}")
        
        # Step 3: Disable all after() callbacks related to scaling
        try:
            import tkinter as tk
            
            # Override Tk and Toplevel's after method to filter out scaling calls
            original_after = tk.Misc.after
            
            def safe_after(self, ms, func=None, *args, **kwargs):
                """Safe after method that filters out scaling-related calls"""
                try:
                    # Check if this is a scaling-related callback
                    if func and hasattr(func, '__name__'):
                        func_name = str(func.__name__)
                        if 'check_dpi_scaling' in func_name or 'scaling' in func_name.lower():
                            print(f"[NUCLEAR] Blocked scaling callback: {func_name}")
                            return "nuclear_blocked"
                    
                    # Check string representations that might contain scaling calls
                    if isinstance(func, str) and ('check_dpi_scaling' in func or 'scaling' in func.lower()):
                        print(f"[NUCLEAR] Blocked scaling string callback: {func}")
                        return "nuclear_blocked"
                    
                    # Allow all other callbacks
                    return original_after(self, ms, func, *args, **kwargs)
                    
                except Exception as e:
                    print(f"[NUCLEAR] Error in safe_after: {e}")
                    return "nuclear_error"
            
            # Apply the patch
            tk.Misc.after = safe_after
            print("[NUCLEAR] After method patched to block scaling callbacks")
            
        except Exception as e:
            print(f"[NUCLEAR] Could not patch after method: {e}")
        
        # Step 4: Block problematic after_idle calls
        try:
            import tkinter as tk
            original_after_idle = tk.Misc.after_idle
            
            def safe_after_idle(self, func, *args, **kwargs):
                """Safe after_idle that blocks scaling calls"""
                try:
                    if func and hasattr(func, '__name__'):
                        func_name = str(func.__name__)
                        if 'check_dpi_scaling' in func_name or 'scaling' in func_name.lower():
                            print(f"[NUCLEAR] Blocked scaling after_idle: {func_name}")
                            return "nuclear_blocked"
                    
                    if isinstance(func, str) and ('check_dpi_scaling' in func or 'scaling' in func.lower()):
                        print(f"[NUCLEAR] Blocked scaling string after_idle: {func}")
                        return "nuclear_blocked"
                    
                    return original_after_idle(self, func, *args, **kwargs)
                    
                except Exception as e:
                    print(f"[NUCLEAR] Error in safe_after_idle: {e}")
                    return "nuclear_error"
            
            tk.Misc.after_idle = safe_after_idle
            print("[NUCLEAR] After_idle method patched")
            
        except Exception as e:
            print(f"[NUCLEAR] Could not patch after_idle: {e}")
        
        print("[NUCLEAR] Nuclear scaling disabler completed successfully")
        return True
        
    except Exception as e:
        print(f"[NUCLEAR] Nuclear disabler failed: {e}")
        return False

# Apply nuclear patch immediately on import
if __name__ != "__main__":
    nuclear_disable_scaling()
