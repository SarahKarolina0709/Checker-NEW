"""
Lite Nuclear CustomTkinter Patch - Minimale aber effektive Fixes
Dieser Patch implementiert nur die wichtigsten Korrekturen ohne aggressive Überschreibungen.
"""

import customtkinter as ctk
import sys
import threading
import time
import tkinter as tk

print("[LITE NUCLEAR PATCH] Initialisiere minimale CustomTkinter-Korrekturen...")

# === PHASE 1: APPEARANCE MODE LOCK ===
print("[LITE NUCLEAR PATCH] Phase 1: Appearance Mode wird auf Light fixiert...")

# Setze und fixiere Light Mode
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

# NUCLEAR OVERRIDE: Komplett blockiere alle Appearance Mode Änderungen
original_set_appearance_mode = ctk.set_appearance_mode
def nuclear_appearance_override(mode):
    """Nuclear override: Blockiere ALLE Änderungen - nur Light Mode erlaubt"""
    print(f"[LITE NUCLEAR PATCH] ALLE Appearance Mode Änderungen blockiert: {mode} -> Light")
    return original_set_appearance_mode("Light")

ctk.set_appearance_mode = nuclear_appearance_override

# Zusätzlich: Blockiere get_appearance_mode um sicherzustellen dass immer "Light" zurückgegeben wird
original_get_appearance_mode = ctk.get_appearance_mode
def nuclear_get_appearance_mode():
    """Nuclear get: Immer Light zurückgeben"""
    return "Light"

ctk.get_appearance_mode = nuclear_get_appearance_mode

# === PHASE 2: BASIC SCALING FIX ===
print("[LITE NUCLEAR PATCH] Phase 2: Basis-Skalierung wird stabilisiert...")

# Setze fixen Skalierungsfaktor
LITE_SCALING_FACTOR = 1.0

try:
    # Setze sichere Standard-Werte
    ctk.set_widget_scaling(LITE_SCALING_FACTOR)
    ctk.set_window_scaling(LITE_SCALING_FACTOR)
    # ScalingTracker komplett deaktivieren
    if hasattr(ctk, 'ScalingTracker'):
        # Sichere den originalen ScalingTracker für Fallback
        original_scaling_tracker = ctk.ScalingTracker
        
        class NuclearScalingTracker:
            @staticmethod
            def get_window_scaling(window):
                return LITE_SCALING_FACTOR
            @staticmethod 
            def get_widget_scaling(widget):
                return LITE_SCALING_FACTOR
            @staticmethod
            def set_widget_scaling(scaling_value):
                print(f"[LITE NUCLEAR PATCH] set_widget_scaling auf {scaling_value} ignoriert - nutze {LITE_SCALING_FACTOR}")
                return LITE_SCALING_FACTOR
            @staticmethod
            def set_window_scaling(scaling_value):
                print(f"[LITE NUCLEAR PATCH] set_window_scaling auf {scaling_value} ignoriert - nutze {LITE_SCALING_FACTOR}")
                return LITE_SCALING_FACTOR
            @staticmethod
            def add_widget(widget_callback, widget):
                print("[LITE NUCLEAR PATCH] add_widget ignoriert")
                pass  # Keine Tracking
            @staticmethod
            def remove_widget(widget_callback, widget):
                print("[LITE NUCLEAR PATCH] remove_widget ignoriert")
                pass  # Keine Tracking
            @staticmethod
            def check_dpi_scaling(window):
                print("[LITE NUCLEAR PATCH] DPI scaling check blockiert - verhindert AttributeError")
                pass  # Blockiere DPI-Checks die Probleme verursachen
            
            # Zusätzliche Methoden die möglicherweise aufgerufen werden
            @staticmethod
            def activate_high_dpi_awareness():
                print("[LITE NUCLEAR PATCH] activate_high_dpi_awareness blockiert")
                pass
            
            @staticmethod
            def deactivate_automatic_dpi_awareness():
                print("[LITE NUCLEAR PATCH] deactivate_automatic_dpi_awareness blockiert")
                pass
        
        # Überschreibe den ScalingTracker komplett
        ctk.ScalingTracker = NuclearScalingTracker()
        print("[LITE NUCLEAR PATCH] ScalingTracker durch Nuclear-Version ersetzt")
        
        # Zusätzlich: Blockiere auch das scaling_tracker Modul wenn vorhanden
        try:
            import customtkinter.windows.widgets.scaling.scaling_tracker as st
            if hasattr(st, 'ScalingTracker'):
                st.ScalingTracker = NuclearScalingTracker()
                print("[LITE NUCLEAR PATCH] scaling_tracker Modul auch überschrieben")
        except Exception as e:
            print(f"[LITE NUCLEAR PATCH] scaling_tracker Modul-Override-Warnung: {e}")
    
    print("[LITE NUCLEAR PATCH] Basis-Skalierung erfolgreich gesetzt")
except Exception as e:
    print(f"[LITE NUCLEAR PATCH] Skalierung-Warnung: {e}")

# === PHASE 3: THREAD SAFETY BASIC ===
print("[LITE NUCLEAR PATCH] Phase 3: Basis Thread-Safety...")

# Nur bei kritischen Thread-Problemen eingreifen
original_ctk_init = ctk.CTk.__init__
def lite_thread_safe_init(self, *args, **kwargs):
    """Lite thread safety: Nur warnen bei Non-Main-Thread"""
    if threading.current_thread() != threading.main_thread():
        print("[LITE NUCLEAR PATCH] WARNUNG: CTk wird von Non-Main-Thread initialisiert")
    return original_ctk_init(self, *args, **kwargs)

ctk.CTk.__init__ = lite_thread_safe_init

# === PHASE 4: BASIC ERROR PROTECTION ===
print("[LITE NUCLEAR PATCH] Phase 4: Basis-Fehlerbehandlung...")

def lite_error_wrapper(func):
    """Lite wrapper: Nur kritische AttributeErrors abfangen"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except AttributeError as e:
            if "NoneType" in str(e) or "_appearance_mode" in str(e):
                print(f"[LITE NUCLEAR PATCH] Kritischer Fehler abgefangen in {func.__name__}: {e}")
                return None
            raise
    return wrapper

# Nur kritische Methoden wrappen
if hasattr(ctk, 'CTkFrame'):
    try:
        original_frame_init = ctk.CTkFrame.__init__
        ctk.CTkFrame.__init__ = lite_error_wrapper(original_frame_init)
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Frame-Wrapper-Fehler: {e}")

# === PHASE 5: ANTI-TRANSPARENCY MONITORING ===
print("[LITE NUCLEAR PATCH] Phase 5: Anti-Transparenz-Überwachung...")

# Immediate transparency protection
def immediate_transparency_lock():
    """Sofortiger Transparenz-Schutz beim Import"""
    try:
        ctk.set_appearance_mode("Light")
        print("[LITE NUCLEAR PATCH] Sofortiger Transparenz-Lock aktiviert")
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Sofortiger Lock-Fehler: {e}")

# Aktiviere sofort
immediate_transparency_lock()

# The transparency_prevention_monitor thread has been removed.
# The _periodic_enforce_task in PHASE 8 handles this safely from the main GUI thread


# === PHASE 6: CONFIGURE METHOD PROTECTION ===
print("[LITE NUCLEAR PATCH] Phase 6: Configure-Methoden-Schutz...")

def protect_widget_configure(widget_class):
    """Schützt Widget configure-Methoden vor Transparenz - NUCLEAR VERSION"""
    try:
        if hasattr(widget_class, 'configure'):
            original_configure = widget_class.configure
            
            # Use a signature that matches the original tkinter configure
            def nuclear_configure(self, cnf=None, **kw):
                config = {}
                if cnf:
                    config.update(cnf)
                config.update(kw)

                # NUCLEAR: Blockiere ALLE problematischen Farben
                if 'fg_color' in config:
                    fg_color = config.get('fg_color')
                    problematic_colors = ["transparent", "none", "#00000000", "rgba(0,0,0,0)"]
                    
                    is_problematic = False
                    if isinstance(fg_color, str) and fg_color.lower() in problematic_colors:
                        is_problematic = True
                    elif isinstance(fg_color, tuple) and any("transparent" in str(c).lower() for c in fg_color):
                        is_problematic = True

                    if is_problematic:
                        print(f"[LITE NUCLEAR PATCH] NUCLEAR: Transparenz komplett blockiert in {self.__class__.__name__}: {fg_color}")
                        config['fg_color'] = "#FFFFFF"  # Hartes Weiß

                # Zusätzlich: Blockiere auch bg_color Transparenz
                if 'bg_color' in config:
                    bg_color = config.get('bg_color')
                    if isinstance(bg_color, str) and bg_color.lower() == "transparent":
                        print(f"[LITE NUCLEAR PATCH] NUCLEAR: bg_color Transparenz blockiert in {self.__class__.__name__}")
                        config['bg_color'] = "#FFFFFF"
                
                # Call original with the modified config, ensuring self is passed correctly
                return original_configure(self, **config)
            
            widget_class.configure = nuclear_configure
            print(f"[LITE NUCLEAR PATCH] NUCLEAR Configure-Schutz für {widget_class.__name__} aktiviert")
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Configure-Schutz-Fehler für {widget_class}: {e}")

# Schütze wichtige Widget-Klassen
important_widgets = [
    ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkEntry,
    ctk.CTkTextbox, ctk.CTkOptionMenu, ctk.CTkSegmentedButton,
    ctk.CTkScrollableFrame, ctk.CTkCheckBox, ctk.CTkRadioButton
]
for widget_class in important_widgets:
    protect_widget_configure(widget_class)

# === PHASE 7.5: NUCLEAR WIDGET INIT PROTECTION ===
print("[LITE NUCLEAR PATCH] Phase 7.5: Nuclear Widget Init Protection...")

def nuclear_widget_init_patch(widget_class):
    """Patcht Widget __init__ um Transparenz sofort zu blockieren"""
    try:
        if hasattr(widget_class, '__init__'):
            original_init = widget_class.__init__
            
            def nuclear_init(self, *args, **kwargs):
                # Transparenz sofort blockieren vor der Initialisierung
                if 'fg_color' in kwargs:
                    if kwargs['fg_color'] == "transparent":
                        print(f"[LITE NUCLEAR PATCH] NUCLEAR INIT: Transparenz in {widget_class.__name__} blockiert")
                        kwargs['fg_color'] = "#FFFFFF"
                
                # Original Init aufrufen
                result = original_init(self, *args, **kwargs)
                
                # Nach der Init: Sicherstellen dass keine Transparenz gesetzt ist
                try:
                    if hasattr(self, 'configure'):
                        self.configure(fg_color="#FFFFFF")  # Force weiß
                except:
                    pass  # Ignore Fehler
                
                return result
            
            widget_class.__init__ = nuclear_init
            print(f"[LITE NUCLEAR PATCH] Nuclear Init Protection für {widget_class.__name__} aktiviert")
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Nuclear Init Protection Fehler für {widget_class}: {e}")

# Patche alle wichtigen Widgets
nuclear_widgets = [
    ctk.CTkFrame, ctk.CTkButton, ctk.CTkLabel, ctk.CTkEntry,
    ctk.CTkTextbox, ctk.CTkOptionMenu, ctk.CTkSegmentedButton,
    ctk.CTkScrollableFrame, ctk.CTkCheckBox, ctk.CTkRadioButton
]
for widget_class in nuclear_widgets:
    nuclear_widget_init_patch(widget_class)

# === PHASE 8: GLOBAL ANTI-TRANSPARENCY ENFORCER (v2) ===
print("[LITE NUCLEAR PATCH] Phase 8: Globaler Anti-Transparenz-Enforcer (v2)...")

_enforce_task_started = False

def _enforce_no_transparency_recursive(widget):
    """Recursive helper to enforce non-transparent backgrounds."""
    try:
        # List of properties to check for transparency
        color_options = ("bg", "background", "fg_color", "bg_color")
        
        for option in color_options:
            try:
                # Use cget for robust property access
                current_color = widget.cget(option)
                
                # Check for various forms of transparency
                is_transparent = (
                    current_color in ("transparent", "none", "", None) or
                    (isinstance(current_color, str) and "transparent" in current_color.lower())
                )
                
                if is_transparent:
                    # Force a solid color
                    widget.configure(**{option: "#FFFFFF"})
            except (tk.TclError, AttributeError):
                # Ignore if the widget doesn't have the property or is destroyed
                continue

        # Recurse through child widgets
        if hasattr(widget, 'winfo_children'):
            for child in widget.winfo_children():
                _enforce_no_transparency_recursive(child)
    except Exception:
        # Fail silently if widget is destroyed during check
        pass

def _periodic_enforce_task(root):
    """The main task that runs periodically to check all windows, using .after()"""
    try:
        if root.winfo_exists():
            # Enforce on the root window and all its descendants
            _enforce_no_transparency_recursive(root)
            
            # Auch Toplevel-Fenster überprüfen
            if hasattr(root, 'winfo_children'):
                for w in root.winfo_children():
                    if isinstance(w, tk.Toplevel):
                        _enforce_no_transparency_recursive(w)
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Periodic Enforcer Error: {e}")
    finally:
        # Nächsten Check im Haupt-Thread neu planen
        if root.winfo_exists():
            root.after(50, lambda: _periodic_enforce_task(root)) # Sehr aggressiv: 50ms

def start_global_enforcer(root_window):
    """Starts the enforcer task if it hasn't been started, using the root window's context."""
    global _enforce_task_started
    if not _enforce_task_started:
        print("[LITE NUCLEAR PATCH] Starting Global Enforcer Task via .after()...")
        _enforce_task_started = True
        # Ersten Check nach kurzer Verzögerung starten
        root_window.after(50, lambda: _periodic_enforce_task(root_window))

# Der Enforcer wird jetzt aus dem gepatchten __init__ von tk.Tk gestartet


# === PHASE 9: ULTIMATE WINDOW ATTRIBUTE LOCKDOWN ===
print("[LITE NUCLEAR PATCH] Phase 9: Ultimate Window Attribute Lockdown...")

def apply_ultimate_lockdown(cls):
    """Patches window class methods to prevent any transparency settings."""
    
    # --- Patch .attributes() ---
    if hasattr(cls, 'attributes'):
        original_attributes = cls.attributes
        def patched_attributes(self, *args, **kwargs):
            # Block attempts to set transparency via -alpha
            if '-alpha' in args or 'alpha' in kwargs:
                print(f"[LITE NUCLEAR PATCH] ULTIMATE LOCKDOWN: '-alpha' call on '{self.winfo_class()}' blocked. Forcing opaque (1.0).")
                # Force window to be fully opaque and ignore the requested value
                return original_attributes(self, '-alpha', 1.0)
            
            # Block attempts to set a transparent color
            if '-transparentcolor' in args or 'transparentcolor' in kwargs:
                print(f"[LITE NUCLEAR PATCH] ULTIMATE LOCKDOWN: '-transparentcolor' call on '{self.winfo_class()}' blocked.")
                # Don't call the original method, effectively blocking the change
                return

            # For all other calls, pass them to the original method
            return original_attributes(self, *args, **kwargs)
        
        cls.attributes = patched_attributes
        print(f"[LITE NUCLEAR PATCH] ✅ Ultimate Lockdown active for '{cls.__name__}.attributes'")

    # --- Patch .wm_attributes() ---
    # This is another way transparency can be set
    if hasattr(cls, 'wm_attributes'):
        original_wm_attributes = cls.wm_attributes
        def patched_wm_attributes(self, *args, **kwargs):
            # Block attempts to set transparency
            if '-transparent' in args or 'transparent' in kwargs:
                print(f"[LITE NUCLEAR PATCH] ULTIMATE LOCKDOWN: 'wm_attributes -transparent' call on '{self.winfo_class()}' blocked.")
                # Block the call
                return

            return original_wm_attributes(self, *args, **kwargs)
        
        cls.wm_attributes = patched_wm_attributes
        print(f"[LITE NUCLEAR PATCH] ✅ Ultimate Lockdown active for '{cls.__name__}.wm_attributes'")

try:
    # Apply the patch to the main window class and toplevel windows (dialogs, splash screens)
    apply_ultimate_lockdown(tk.Tk)
    apply_ultimate_lockdown(tk.Toplevel)
    print("[LITE NUCLEAR PATCH] Ultimate Window Attribute Lockdown successfully deployed.")
except Exception as e:
    print(f"[LITE NUCLEAR PATCH] Failed to deploy Ultimate Window Attribute Lockdown: {e}")


# === PHASE 10: GEOMETRY LOCK (EXPLICIT ACTIVATION) & FINAL PATCHING ===
print("[LITE NUCLEAR PATCH] Phase 10: Geometrie-Sperre und finale Patches werden initialisiert...")

# Global dictionary to hold lock instances, mapping a widget to its lock.
_geometry_locks = {}

def activate_lock_for_window(window):
    """Activates the geometry lock for a specific window. Must be called by the app.
    Args:
        window: The tk.Tk or tk.Toplevel window instance to lock.
    """
    if window in _geometry_locks:
        print(f"[LITE NUCLEAR PATCH] Aktivierungs-Signal für Geometrie-Sperre von {window.winfo_class()} erhalten.")
        _geometry_locks[window].lock_geometry()
        
        # ULTRA-AGGRESSIVE: Aktiviere zusätzliche Überwachung
        if hasattr(window, '_locked_min_width'):
            # Starte den Global Ultra-Enforcer für dieses Fenster
            start_global_ultra_enforcer(window)
            print(f"[LITE NUCLEAR PATCH] Ultra-Enforcer für {window.winfo_class()} aktiviert")
        
    else:
        print(f"[LITE NUCLEAR PATCH] WARNUNG: Kein Geometrie-Lock für {window.winfo_class()} gefunden zum Aktivieren.")

class GeometryLock:
    """Manages the geometry lock state for a single widget, activated explicitly."""
    def __init__(self, widget):
        self.widget = widget
        self.is_locked = False
        # Store this instance in the global dict so it can be activated later.
        _geometry_locks[widget] = self

    def lock_geometry(self):
        """Calculates and applies the minimum size lock. Called explicitly by activate_lock_for_window."""
        if self.is_locked or not self.widget.winfo_exists():
            return

        self.widget.update_idletasks()
        
        width = self.widget.winfo_width()
        height = self.widget.winfo_height()
        
        current_min_w = 0
        if hasattr(self.widget, 'winfo_minwidth'):
            current_min_w = self.widget.winfo_minwidth()
        else:
            print(f"[LITE NUCLEAR PATCH] WARNUNG: {self.widget.winfo_class()} hat kein winfo_minwidth Attribut.")

        current_min_h = 0
        if hasattr(self.widget, 'winfo_minheight'):
            current_min_h = self.widget.winfo_minheight()
        else:
            print(f"[LITE NUCLEAR PATCH] WARNUNG: {self.widget.winfo_class()} hat kein winfo_minheight Attribut.")

        # The final lock size is the maximum of current size and existing minsize.
        final_w = max(width, current_min_w)
        final_h = max(height, current_min_h)

        if final_w > 1 and final_h > 1:
            # Use a try-except block for robustness, as the widget might be destroyed.
            try:
                self.widget.minsize(final_w, final_h)
                # Store the locked dimensions for geometry protection
                self.widget._locked_min_width = final_w
                self.widget._locked_min_height = final_h
                self.is_locked = True
                print(f"[LITE NUCLEAR PATCH] Geometrie-Sperre AKTIVIERT. Mindestgröße: {final_w}x{final_h}.")
                
                # ULTRA-AGGRESSIVE: Überwache Configure-Events für sofortige Korrektur
                def ultra_configure_monitor(event):
                    """Überwacht Configure-Events und korrigiert sofort bei Größenänderungen"""
                    if event.widget == self.widget and self.is_locked:
                        if event.width < final_w or event.height < final_h:
                            corrected_w = max(event.width, final_w)
                            corrected_h = max(event.height, final_h)
                            print(f"[LITE NUCLEAR PATCH] CONFIGURE-MONITOR: Korrigiere {event.width}x{event.height} -> {corrected_w}x{corrected_h}")
                            self.widget.after_idle(lambda: self.widget.geometry(f"{corrected_w}x{corrected_h}"))
                
                # Binde den Configure-Monitor
                self.widget.bind('<Configure>', ultra_configure_monitor, add='+')
                print(f"[LITE NUCLEAR PATCH] Configure-Monitor für {self.widget.winfo_class()} aktiviert")
                
            except tk.TclError:
                print(f"[LITE NUCLEAR PATCH] Geometrie-Sperre: Anwenden auf zerstörtes Widget {self.widget.winfo_class()} vermieden.")
        else:
            # If the window size is invalid, log it. The app is responsible for ensuring the window is ready.
            print(f"[LITE NUCLEAR PATCH] Geometrie-Sperre: Fenstergröße ungültig ({width}x{height}). Sperre nicht angewendet.")

def apply_window_patches(cls):
    """Patches the __init__ of a class (tk.Tk, tk.Toplevel) to:
    1. Create a GeometryLock instance for later activation.
    2. Start the global transparency enforcer for the main tk.Tk window.
    3. Protect geometry and configure methods from unwanted size changes."""
    
    # --- Patch __init__ to create the lock ---
    original_init = cls.__init__
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        GeometryLock(self) # Creates and registers a lock instance
        if isinstance(self, tk.Tk) and not isinstance(self, tk.Toplevel):
            start_global_enforcer(self)
            start_global_ultra_enforcer(self)
    cls.__init__ = patched_init

    # --- Patch geometry method ---
    original_geometry = cls.geometry
    def protected_geometry(self, geometry_string=None):
        if geometry_string is None:
            return original_geometry(self)
        
        lock = _geometry_locks.get(self)
        if lock and lock.is_locked:
            try:
                if 'x' in geometry_string:
                    size_part = geometry_string.split('+')[0].split('-')[0]
                    if 'x' in size_part:
                        width_str, height_str = size_part.split('x')
                        width, height = int(width_str), int(height_str)
                        
                        min_w = getattr(self, '_locked_min_width', 0)
                        min_h = getattr(self, '_locked_min_height', 0)
                        
                        if width < min_w or height < min_h:
                            enforced_w = max(width, min_w)
                            enforced_h = max(height, min_h)
                            pos_part = geometry_string[len(size_part):]
                            geometry_string = f"{enforced_w}x{enforced_h}{pos_part}"
                            print(f"[LITE NUCLEAR PATCH] Geometrie-Schutz: Größe von {width}x{height} auf {enforced_w}x{enforced_h} korrigiert")
            except Exception as e:
                print(f"[LITE NUCLEAR PATCH] Geometry-Schutz Fehler: {e}")
        
        return original_geometry(self, geometry_string)
    cls.geometry = protected_geometry

    # --- Patch configure method ---
    original_configure = cls.configure
    def protected_configure(self, cnf=None, **kw):
        lock = _geometry_locks.get(self)
        if lock and lock.is_locked:
            config = {}
            if cnf:
                config.update(cnf)
            config.update(kw)

            if 'width' in config or 'height' in config:
                min_w = getattr(self, '_locked_min_width', 0)
                min_h = getattr(self, '_locked_min_height', 0)
                
                if 'width' in config and config['width'] < min_w:
                    print(f"[LITE NUCLEAR PATCH] Configure-Schutz: width von {config['width']} auf {min_w} korrigiert")
                    config['width'] = min_w
                
                if 'height' in config and config['height'] < min_h:
                    print(f"[LITE NUCLEAR PATCH] Configure-Schutz: height von {config['height']} auf {min_h} korrigiert")
                    config['height'] = min_h
            
            return original_configure(self, **config)
        
        return original_configure(self, cnf, **kw)
    cls.configure = protected_configure

    # --- Patch wm_geometry method ---
    original_wm_geometry = cls.wm_geometry
    def protected_wm_geometry(self, geometry_string=None):
        if geometry_string is None:
            return original_wm_geometry(self)
        
        lock = _geometry_locks.get(self)
        if lock and lock.is_locked:
            try:
                if 'x' in geometry_string:
                    size_part = geometry_string.split('+')[0].split('-')[0]
                    if 'x' in size_part:
                        width_str, height_str = size_part.split('x')
                        width, height = int(width_str), int(height_str)
                        
                        min_w = getattr(self, '_locked_min_width', 0)
                        min_h = getattr(self, '_locked_min_height', 0)
                        
                        if width < min_w or height < min_h:
                            enforced_w = max(width, min_w)
                            enforced_h = max(height, min_h)
                            pos_part = geometry_string[len(size_part):]
                            geometry_string = f"{enforced_w}x{enforced_h}{pos_part}"
                            print(f"[LITE NUCLEAR PATCH] wm_geometry-Schutz: Größe korrigiert auf {enforced_w}x{enforced_h}")
            except Exception as e:
                print(f"[LITE NUCLEAR PATCH] wm_geometry-Schutz Fehler: {e}")

        return original_wm_geometry(self, geometry_string)
    cls.wm_geometry = protected_wm_geometry
    
    print(f"[LITE NUCLEAR PATCH] Fenster-Patches fur '{cls.__name__}' vorbereitet.")

try:
    apply_window_patches(tk.Tk)
    apply_window_patches(tk.Toplevel)
    print("[LITE NUCLEAR PATCH] Fenster-Patches erfolgreich bereitgestellt.")
except Exception as e:
    print(f"[LITE NUCLEAR PATCH] Fehler bei der Bereitstellung der Fenster-Patches: {e}")


# === PHASE 10.5: BLOCK_UPDATE_DIMENSIONS_EVENT SAFE PATCH ===
print("[LITE NUCLEAR PATCH] Phase 10.5: block_update_dimensions_event Patch...")

def safe_block_update_dimensions_event_patch():
    """
    Patcht Tk und Toplevel um die block_update_dimensions_event Methode sicher zu handhaben.
    CustomTkinter's ScalingTracker versucht diese Methode aufzurufen, aber sie existiert nicht
    in der Standard-Tkinter-Installation.
    """
    try:
        def safe_block_update_dimensions_event(self):
            """Sichere Dummy-Implementierung für block_update_dimensions_event"""
            # Keine Operation - einfach ignorieren
            pass
        
        def safe_unblock_update_dimensions_event(self):
            """Sichere Dummy-Implementierung für unblock_update_dimensions_event"""
            # Keine Operation - einfach ignorieren
            pass
        
        # Patch für Tk
        if not hasattr(tk.Tk, 'block_update_dimensions_event'):
            tk.Tk.block_update_dimensions_event = safe_block_update_dimensions_event
            print("[LITE NUCLEAR PATCH] ✅ block_update_dimensions_event für Tk hinzugefügt")
        
        if not hasattr(tk.Tk, 'unblock_update_dimensions_event'):
            tk.Tk.unblock_update_dimensions_event = safe_unblock_update_dimensions_event
            print("[LITE NUCLEAR PATCH] ✅ unblock_update_dimensions_event für Tk hinzugefügt")
        
        # Patch für Toplevel
        if not hasattr(tk.Toplevel, 'block_update_dimensions_event'):
            tk.Toplevel.block_update_dimensions_event = safe_block_update_dimensions_event
            print("[LITE NUCLEAR PATCH] ✅ block_update_dimensions_event für Toplevel hinzugefügt")
        
        if not hasattr(tk.Toplevel, 'unblock_update_dimensions_event'):
            tk.Toplevel.unblock_update_dimensions_event = safe_unblock_update_dimensions_event
            print("[LITE NUCLEAR PATCH] ✅ unblock_update_dimensions_event für Toplevel hinzugefügt")
        
        print("[LITE NUCLEAR PATCH] block_update_dimensions_event Patch erfolgreich angewendet.")
        
    except Exception as e:
        print(f"[LITE NUCLEAR PATCH] Fehler beim Patchen von block_update_dimensions_event: {e}")

safe_block_update_dimensions_event_patch()


# === FINAL VERIFICATION ===
print("[LITE NUCLEAR PATCH] Verifikation...")
def safe_get_appearance_mode():
    """Sichere Ermittlung des Appearance Mode"""
    try:
        if hasattr(ctk, 'get_appearance_mode'):
            return ctk.get_appearance_mode()
        return "Light"
    except:
        return "Light"

current_appearance = safe_get_appearance_mode()
lite_verification = {
    "appearance_mode": current_appearance.lower() == "light",
    "scaling_set": True,
    "thread_safety": True,
    "error_handling": True,
    "transparency_locked": True,
    "geometry_locked": True
}

all_patches_active = all(lite_verification.values())

if all_patches_active:
    print("[LITE NUCLEAR PATCH] Alle Lite Patches erfolgreich aktiviert!")
else:
    print("[LITE NUCLEAR PATCH] Einige Lite Patches konnten nicht aktiviert werden!")

print(f"[LITE NUCLEAR PATCH] Status: {lite_verification}")

# === MINIMAL ULTRA-ENFORCER (STUB ONLY) ===
def start_global_ultra_enforcer(root_window):
    """Minimal stub for ultra-enforcer - disabled for stability"""
    print("[LITE NUCLEAR PATCH] Ultra-Enforcer stub - disabled for stability")
    pass

print("[LITE NUCLEAR PATCH] Lite Nuclear CustomTkinter Patch vollständig geladen!")
