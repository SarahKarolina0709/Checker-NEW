"""
Simplified ScalingTracker Kill Switch
Einfacher und direkter Ansatz zur Deaktivierung des ScalingTrackers
"""

print("[SCALING KILL] ScalingTracker Kill Switch wird aktiviert...")

def kill_scaling_tracker():
    """Tötet den ScalingTracker komplett ab"""
    try:
        import customtkinter
        
        # Direkte Überschreibung des ScalingTrackers
        class DeadScalingTracker:
            """Komplett inaktiver ScalingTracker"""
            
            def __init__(self):
                pass
            
            @staticmethod
            def get_window_scaling(window=None):
                return 1.0
            
            @staticmethod 
            def get_widget_scaling(widget=None):
                return 1.0
            
            @staticmethod
            def set_widget_scaling(scaling_value):
                print(f"[SCALING KILL] set_widget_scaling({scaling_value}) -> ignored")
                return 1.0
            
            @staticmethod
            def set_window_scaling(scaling_value):
                print(f"[SCALING KILL] set_window_scaling({scaling_value}) -> ignored")
                return 1.0
            
            @staticmethod
            def add_widget(widget_callback, widget):
                # Komplett ignorieren
                pass
            
            @staticmethod
            def remove_widget(widget_callback, widget):
                # Komplett ignorieren
                pass
            
            @staticmethod
            def check_dpi_scaling(window):
                print("[SCALING KILL] check_dpi_scaling() -> KILLED")
                # Das ist die Methode die den AttributeError verursacht - komplett blockieren
                pass
            
            @staticmethod
            def activate_high_dpi_awareness():
                print("[SCALING KILL] activate_high_dpi_awareness() -> ignored")
                pass
            
            @staticmethod
            def deactivate_automatic_dpi_awareness():
                print("[SCALING KILL] deactivate_automatic_dpi_awareness() -> ignored")
                pass
            
            # Alle anderen möglichen Methoden auch abfangen
            def __getattr__(self, name):
                print(f"[SCALING KILL] ScalingTracker.{name}() -> blocked")
                return lambda *args, **kwargs: None
        
        # Überschreibe den ScalingTracker
        customtkinter.ScalingTracker = DeadScalingTracker
        print("[SCALING KILL] ✅ CustomTkinter ScalingTracker erfolgreich getötet")
        
        # Auch das scaling_tracker Modul überschreiben falls es existiert
        try:
            import customtkinter.windows.widgets.scaling.scaling_tracker as st_module
            st_module.ScalingTracker = DeadScalingTracker
            print("[SCALING KILL] ✅ scaling_tracker Modul auch getötet")
        except ImportError:
            print("[SCALING KILL] scaling_tracker Modul nicht gefunden (das ist ok)")
        
        # Auch in den widgets den ScalingTracker ersetzen
        try:
            import customtkinter.windows.widgets as widgets
            if hasattr(widgets, 'ScalingTracker'):
                widgets.ScalingTracker = DeadScalingTracker
                print("[SCALING KILL] ✅ widgets ScalingTracker auch getötet")
        except ImportError:
            pass
            
        return True
        
    except ImportError:
        print("[SCALING KILL] CustomTkinter noch nicht importiert - wird später getötet")
        return False
    except Exception as e:
        print(f"[SCALING KILL] Fehler beim Töten des ScalingTrackers: {e}")
        return False

def install_scaling_kill():
    """Installiert den ScalingTracker Kill Switch"""
    # Versuche sofort zu töten
    if kill_scaling_tracker():
        print("[SCALING KILL] ScalingTracker sofort getötet")
    
    # Zusätzlich: Installiere einen Hook für spätere Importe
    original_setattr = setattr
    
    def kill_setattr(obj, name, value):
        # Wenn jemand versucht einen ScalingTracker zu setzen, ersetze ihn
        if name == 'ScalingTracker' and hasattr(value, 'check_dpi_scaling'):
            print(f"[SCALING KILL] ScalingTracker-Assignment abgefangen auf {obj}")
            # Ersetze durch unseren toten Tracker
            kill_scaling_tracker()
            return  # Ignoriere das ursprüngliche Assignment
        return original_setattr(obj, name, value)
    
    # Überschreibe setattr global (temporär)
    import builtins
    builtins.setattr = kill_setattr
    
    print("[SCALING KILL] Kill Switch installiert")

# Aktiviere den Kill Switch sofort
install_scaling_kill()

print("[SCALING KILL] ScalingTracker Kill Switch erfolgreich geladen")
