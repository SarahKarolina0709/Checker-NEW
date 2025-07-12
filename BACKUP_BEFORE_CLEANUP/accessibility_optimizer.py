# -*- coding: utf-8 -*-
"""
Accessibility Optimizer - Barrierefreiheits-Optimierungen für Checker App
"""
# import lite_nuclear_ctk_patch as ctk_patch # Apply nuclear anti-dark-mode patch

import tkinter as tk
import customtkinter as ctk
from tkinter import font
import threading
import time
import json
import os
from datetime import datetime

class AccessibilityOptimizer:
    def __init__(self):
        self.settings = self.load_accessibility_settings()
        self.screen_reader_active = False
        self.high_contrast_mode = False
        self.font_scale = 1.0
        self.keyboard_navigation_enabled = True
        
    def load_accessibility_settings(self):
        """Lädt Barrierefreiheits-Einstellungen"""
        try:
            with open("accessibility_settings.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_settings()
    
    def get_default_settings(self):
        """Standard Barrierefreiheits-Einstellungen"""
        return {
            "high_contrast": False,
            "large_fonts": False,
            "screen_reader_support": True,
            "keyboard_navigation": True,
            "focus_indicators": True,
            "audio_feedback": False,
            "reduced_motion": False,
            "color_blind_support": False,
            "font_scale": 1.0,
            "announcement_delay": 0.5
        }
    
    def save_accessibility_settings(self):
        """Speichert Barrierefreiheits-Einstellungen"""
        try:
            with open("accessibility_settings.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern der Accessibility-Einstellungen: {e}")
    
    def apply_accessibility_to_widget(self, widget, widget_type="button", description=""):
        """Wendet Barrierefreiheits-Optimierungen auf ein Widget an"""
        
        # 1. Tastaturnavigation
        if self.settings.get("keyboard_navigation", True):
            widget.bind("<Tab>", self._handle_tab_navigation)
            widget.bind("<Return>", self._handle_enter_key)
            widget.bind("<space>", self._handle_space_key)
        
        # 2. Focus-Indikatoren
        if self.settings.get("focus_indicators", True):
            widget.bind("<FocusIn>", lambda e: self._enhance_focus(e.widget))
            widget.bind("<FocusOut>", lambda e: self._remove_focus(e.widget))
        
        # 3. Screen Reader Support
        if self.settings.get("screen_reader_support", True):
            self._add_aria_attributes(widget, widget_type, description)
        
        # 4. Hochkontrast-Modus
        if self.settings.get("high_contrast", False):
            self._apply_high_contrast(widget)
        
        # 5. Große Schriften
        if self.settings.get("large_fonts", False):
            self._apply_large_fonts(widget)
    
    def _handle_tab_navigation(self, event):
        """Verbesserte Tab-Navigation"""
        widget = event.widget
        
        # Audio-Feedback bei Navigation
        if self.settings.get("audio_feedback", False):
            self._play_navigation_sound()
        
        # Screen Reader Ankündigung
        if hasattr(widget, 'accessibility_description'):
            self._announce_to_screen_reader(widget.accessibility_description)
    
    def _handle_enter_key(self, event):
        """Enter-Taste Behandlung"""
        widget = event.widget
        if hasattr(widget, 'invoke'):  # Buttons
            widget.invoke()
            self._announce_to_screen_reader("Aktiviert")
    
    def _handle_space_key(self, event):
        """Leertaste Behandlung"""
        return self._handle_enter_key(event)
    
    def _enhance_focus(self, widget):
        """Verstärkt Focus-Indikatoren"""
        if hasattr(widget, 'configure'):
            try:
                # Starker Focus-Ring
                widget.configure(
                    highlightthickness=3,
                    highlightcolor="#FF6B35",
                    highlightbackground="#FF6B35"
                )
            except:
                pass
    
    def _remove_focus(self, widget):
        """Entfernt Focus-Indikatoren"""
        if hasattr(widget, 'configure'):
            try:
                widget.configure(
                    highlightthickness=1,
                    highlightcolor="gray",
                    highlightbackground="gray"
                )
            except:
                pass
    
    def _add_aria_attributes(self, widget, widget_type, description):
        """Fügt ARIA-ähnliche Attribute hinzu"""
        widget.accessibility_type = widget_type
        widget.accessibility_description = description
        
        # Erweiterte Beschreibungen basierend auf Widget-Typ
        if widget_type == "button":
            widget.accessibility_role = "button"
        elif widget_type == "entry":
            widget.accessibility_role = "textbox"
        elif widget_type == "label":
            widget.accessibility_role = "text"
        elif widget_type == "frame":
            widget.accessibility_role = "group"
    
    def _apply_high_contrast(self, widget):
        """Wendet Hochkontrast-Design an (Light-Theme-basiert)"""
        high_contrast_colors = {
            "bg": "#FFFFFF",
            "fg": "#000000",
            "select_bg": "#005fcc", # Strong blue for selection
            "select_fg": "#FFFFFF",
            "button_bg": "#E0E0E0", # Light grey
            "button_fg": "#000000",
            "hover_color": "#B0B0B0" # Darker grey for hover
        }
        
        try:
            # General widget background for non-CTK widgets
            if isinstance(widget, tk.Widget) and not isinstance(widget, ctk.CTkBaseClass):
                 if 'bg' in widget.configure():
                    widget.configure(bg=high_contrast_colors["bg"])

            if isinstance(widget, ctk.CTkButton):
                widget.configure(
                    fg_color=high_contrast_colors["button_bg"],
                    text_color=high_contrast_colors["button_fg"],
                    hover_color=high_contrast_colors["hover_color"],
                    border_color=high_contrast_colors["fg"], # Add border for contrast
                    border_width=1
                )
            elif isinstance(widget, ctk.CTkLabel):
                widget.configure(
                    text_color=high_contrast_colors["fg"],
                    bg_color=high_contrast_colors["bg"] # Ensure label bg is white
                )
            elif isinstance(widget, ctk.CTkEntry):
                widget.configure(
                    fg_color=high_contrast_colors["bg"],
                    text_color=high_contrast_colors["fg"],
                    border_color=high_contrast_colors["fg"]
                )
            elif isinstance(widget, (ctk.CTkFrame, ctk.CTkScrollableFrame)):
                 widget.configure(fg_color=high_contrast_colors["bg"])

        except Exception as e:
            print(f"Hochkontrast-Anwendung fehlgeschlagen: {e}")
    
    def _apply_large_fonts(self, widget):
        """Wendet vergrößerte Schriften an"""
        try:
            current_font = widget.cget("font")
            if current_font:
                if isinstance(current_font, str):
                    # String font
                    size = 14 * self.settings.get("font_scale", 1.2)
                    widget.configure(font=(current_font, int(size)))
                elif hasattr(current_font, 'configure'):
                    # CTkFont object
                    current_size = current_font.cget("size")
                    new_size = int(current_size * self.settings.get("font_scale", 1.2))
                    current_font.configure(size=new_size)
        except Exception as e:
            print(f"Schriftvergrößerung fehlgeschlagen: {e}")
    
    def _announce_to_screen_reader(self, message):
        """Kündigt Nachrichten für Screen Reader an"""
        if not self.settings.get("screen_reader_support", True):
            return
        
        # Verzögerung für Screen Reader
        delay = self.settings.get("announcement_delay", 0.5)
        
        def delayed_announcement():
            time.sleep(delay)
            # Für Windows: NVDA/JAWS Unterstützung
            try:
                import pyttsx3
                engine = pyttsx3.init()
                engine.say(message)
                engine.runAndWait()
            except:
                # Fallback: Print für Entwicklung
                print(f"Screen Reader: {message}")
        
        # Asynchrone Ankündigung
        threading.Thread(target=delayed_announcement, daemon=True).start()
    
    def _play_navigation_sound(self):
        """Spielt Navigationston ab"""
        try:
            import winsound
            winsound.Beep(800, 100)  # 800Hz für 100ms
        except:
            pass
    
    def create_accessibility_settings_dialog(self, parent):
        """Erstellt Barrierefreiheits-Einstellungs-Dialog"""
        dialog = ctk.CTkToplevel(parent)
        dialog.title("Barrierefreiheits-Einstellungen")
        dialog.geometry("600x500")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Haupt-Frame
        main_frame = ctk.CTkScrollableFrame(dialog)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Titel
        ctk.CTkLabel(
            main_frame,
            text="♿ Barrierefreiheits-Einstellungen",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=(0, 20))
        
        # Einstellungen
        settings_vars = {}
        
        settings_options = [
            ("high_contrast", "🎨 Hochkontrast-Modus", "Erhöht den Kontrast für bessere Sichtbarkeit"),
            ("large_fonts", "🔍 Große Schriften", "Vergrößert alle Schriften um 20%"),
            ("screen_reader_support", "🔊 Screen Reader Unterstützung", "Unterstützung für Bildschirmlesegeräte"),
            ("keyboard_navigation", "⌨️ Tastaturnavigation", "Vollständige Steuerung über Tastatur"),
            ("focus_indicators", "🎯 Focus-Indikatoren", "Verstärkte visuelle Focus-Markierungen"),
            ("audio_feedback", "🔔 Audio-Feedback", "Töne bei Navigation und Aktionen"),
            ("reduced_motion", "🐌 Reduzierte Animationen", "Weniger Bewegungen und Übergänge"),
            ("color_blind_support", "🌈 Farbenblind-Unterstützung", "Alternative Farbschemata")
        ]
        
        for key, title, description in settings_options:
            frame = ctk.CTkFrame(main_frame)
            frame.pack(fill="x", pady=5)
            
            var = tk.BooleanVar(value=self.settings.get(key, False))
            settings_vars[key] = var
            
            checkbox = ctk.CTkCheckBox(
                frame,
                text=title,
                variable=var,
                font=ctk.CTkFont(size=14, weight="bold")
            )
            checkbox.pack(anchor="w", padx=15, pady=(10, 5))
            
            ctk.CTkLabel(
                frame,
                text=description,
                font=ctk.CTkFont(size=11),
                text_color="gray"
            ).pack(anchor="w", padx=35, pady=(0, 10))
        
        # Font Scale Slider
        font_frame = ctk.CTkFrame(main_frame)
        font_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(
            font_frame,
            text="📏 Schriftgröße-Skalierung",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(anchor="w", padx=15, pady=(10, 5))
        
        font_scale_var = tk.DoubleVar(value=self.settings.get("font_scale", 1.0))
        settings_vars["font_scale"] = font_scale_var
        
        font_slider = ctk.CTkSlider(
            font_frame,
            from_=0.8,
            to=2.0,
            variable=font_scale_var,
            number_of_steps=12
        )
        font_slider.pack(fill="x", padx=15, pady=(0, 5))
        
        scale_label = ctk.CTkLabel(
            font_frame,
            text=f"Aktuelle Skalierung: {font_scale_var.get():.1f}x",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        scale_label.pack(anchor="w", padx=35, pady=(0, 10))
        
        def update_scale_label(*args):
            scale_label.configure(text=f"Aktuelle Skalierung: {font_scale_var.get():.1f}x")
        
        font_scale_var.trace("w", update_scale_label)
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=10)
        
        def save_settings():
            for key, var in settings_vars.items():
                self.settings[key] = var.get()
            self.save_accessibility_settings()
            dialog.destroy()
            
            # Neustarten der Anwendung empfehlen
            import tkinter.messagebox as msgbox
            msgbox.showinfo(
                "Einstellungen gespeichert",
                "Die Barrierefreiheits-Einstellungen wurden gespeichert.\n\n"
                "Einige Änderungen werden erst nach einem Neustart der Anwendung wirksam."
            )
        
        ctk.CTkButton(
            button_frame,
            text="💾 Speichern",
            command=save_settings,
            width=120
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Abbrechen",
            command=dialog.destroy,
            width=120
        ).pack(side="right", padx=5)
        
        # Standard-Button für Tastaturnavigation
        dialog.bind("<Return>", lambda e: save_settings())
        dialog.bind("<Escape>", lambda e: dialog.destroy())
        
        return dialog

# Globale Accessibility-Instanz
accessibility = AccessibilityOptimizer()

def enhance_widget_accessibility(widget, widget_type="button", description=""):
    """Globale Funktion zur Barrierefreiheits-Optimierung"""
    accessibility.apply_accessibility_to_widget(widget, widget_type, description)

def create_accessible_button(parent, text, command=None, **kwargs):
    """Erstellt einen barrierefreien Button"""
    button = ctk.CTkButton(parent, text=text, command=command, **kwargs)
    enhance_widget_accessibility(button, "button", f"Button: {text}")
    return button

def create_accessible_entry(parent, textvariable=None, placeholder="", **kwargs):
    """Erstellt ein barrierefreies Eingabefeld"""
    entry = ctk.CTkEntry(parent, textvariable=textvariable, placeholder_text=placeholder, **kwargs)
    enhance_widget_accessibility(entry, "entry", f"Eingabefeld: {placeholder}")
    return entry

def create_accessible_label(parent, text, **kwargs):
    """Erstellt ein barrierefreies Label"""
    label = ctk.CTkLabel(parent, text=text, **kwargs)
    enhance_widget_accessibility(label, "label", f"Label: {text}")
    return label

# Tastenkombinationen für häufige Aktionen
ACCESSIBILITY_SHORTCUTS = {
    "<Control-plus>": "Schrift vergrößern",
    "<Control-minus>": "Schrift verkleinern", 
    "<Control-0>": "Schrift zurücksetzen",
    "<Control-h>": "Hochkontrast umschalten",
    "<F1>": "Hilfe anzeigen",
    "<Control-comma>": "Einstellungen öffnen"
}

def setup_global_shortcuts(root):
    """Richtet globale Tastenkombinationen ein"""
    def toggle_high_contrast():
        accessibility.settings["high_contrast"] = not accessibility.settings.get("high_contrast", False)
        accessibility.save_accessibility_settings()
        
    def increase_font():
        current = accessibility.settings.get("font_scale", 1.0)
        accessibility.settings["font_scale"] = min(2.0, current + 0.1)
        accessibility.save_accessibility_settings()
        
    def decrease_font():
        current = accessibility.settings.get("font_scale", 1.0)
        accessibility.settings["font_scale"] = max(0.8, current - 0.1)
        accessibility.save_accessibility_settings()
        
    def reset_font():
        accessibility.settings["font_scale"] = 1.0
        accessibility.save_accessibility_settings()
    
    # Tastenkombinationen binden
    root.bind("<Control-h>", lambda e: toggle_high_contrast())
    root.bind("<Control-plus>", lambda e: increase_font())
    root.bind("<Control-minus>", lambda e: decrease_font())
    root.bind("<Control-0>", lambda e: reset_font())

if __name__ == "__main__":
    # Test der Accessibility-Features
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Accessibility Test")
    root.geometry("800x600")
    
    # Accessibility Setup
    setup_global_shortcuts(root)
    
    # Test Widgets
    frame = ctk.CTkFrame(root)
    frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Accessible Widgets
    label = create_accessible_label(frame, "Test Label", font=ctk.CTkFont(size=16))
    label.pack(pady=10)
    
    entry = create_accessible_entry(frame, placeholder="Test Eingabe")
    entry.pack(pady=10)
    
    button = create_accessible_button(frame, "Test Button", command=lambda: print("Button clicked"))
    button.pack(pady=10)
    
    # Settings Button
    settings_btn = create_accessible_button(
        frame, 
        "♿ Barrierefreiheits-Einstellungen",
        command=lambda: accessibility.create_accessibility_settings_dialog(root)
    )
    settings_btn.pack(pady=20)
    
    root.mainloop()
