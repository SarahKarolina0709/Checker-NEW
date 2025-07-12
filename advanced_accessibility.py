# -*- coding: utf-8 -*-
"""
Erweiterte Barrierefreiheits-Features für Checker App
Unterstützt WCAG 2.1 AA Standards und erweiterte Assistive Technologies
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
import threading
import time
import json
import os
import subprocess
import platform
from datetime import datetime
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Import-Fehler: No module named 'speech_recognition'")
    SPEECH_RECOGNITION_AVAILABLE = False
    sr = None
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np

class AdaptiveInterface:
    """Stub/Minimal AdaptiveInterface for compatibility with EnhancedAccessibilityManager."""
    def __init__(self, manager):
        self.manager = manager
    def initialize(self, root_widget):
        pass

class AdvancedAccessibility:
    def __init__(self):
        self.settings = self.load_advanced_settings()
        self.voice_control_active = False
        self.eye_tracking_mode = False
        self.gesture_control = False
        self.color_correction = None
        self.magnifier_window = None
        self.voice_commands = {}
        self.screen_reader_buffer = []
        
    def load_advanced_settings(self):
        """Lädt erweiterte Accessibility-Einstellungen"""
        try:
            with open("advanced_accessibility.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return self.get_default_advanced_settings()
    
    def get_default_advanced_settings(self):
        """Standard erweiterte Einstellungen"""
        return {
            "voice_control": False,
            "eye_tracking": False,
            "gesture_control": False,
            "color_blindness_type": "none",  # protanopia, deuteranopia, tritanopia
            "magnification_level": 1.0,
            "screen_reader_voice": "default",
            "reading_speed": 200,  # WPM
            "dyslexia_support": False,
            "cognitive_load_reduction": False,
            "motor_assistance": False,
            "switch_navigation": False,
            "voice_commands_enabled": True,
            "auto_scroll": False,
            "simplified_interface": False,
            "attention_indicators": False
        }
    
    def save_advanced_settings(self):
        """Speichert erweiterte Einstellungen"""
        try:
            with open("advanced_accessibility.json", "w", encoding="utf-8") as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")
    
    def setup_voice_control(self, root_widget):
        """Initialisiert Sprachsteuerung"""
        if not self.settings.get("voice_control", False):
            return
        
        self.voice_control_active = True
        self.setup_voice_commands()
        
        # Voice Control Thread starten
        voice_thread = threading.Thread(target=self._voice_recognition_loop, daemon=True)
        voice_thread.start()
        
        self._create_voice_feedback_widget(root_widget)
    
    def setup_voice_commands(self):
        """Definiert Sprachbefehle"""
        self.voice_commands = {
            "öffnen": self._voice_open_file,
            "speichern": self._voice_save_file,
            "analyse starten": self._voice_start_analysis,
            "weiter": self._voice_next_step,
            "zurück": self._voice_previous_step,
            "hilfe": self._voice_show_help,
            "einstellungen": self._voice_open_settings,
            "beenden": self._voice_exit_app,
            "vorlesen": self._voice_read_current,
            "pause": self._voice_pause_reading,
            "wiederholung": self._voice_repeat_last,
            "vergrößern": self._voice_zoom_in,
            "verkleinern": self._voice_zoom_out,
            "kontrast": self._voice_toggle_contrast
        }
    
    def _voice_recognition_loop(self):
        """Hauptschleife für Spracherkennung"""
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
        
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
        
        while self.voice_control_active:
            try:
                with microphone as source:
                    # Kurzes Timeout für kontinuierliches Listening
                    audio = recognizer.listen(source, timeout=1, phrase_time_limit=3)
                
                # Spracherkennung
                text = recognizer.recognize_google(audio, language='de-DE').lower()
                self._process_voice_command(text)
                
            except sr.WaitTimeoutError:
                pass  # Normal bei kontinuierlichem Listening
            except sr.UnknownValueError:
                pass  # Nicht verstanden
            except Exception as e:
                print(f"Voice Recognition Error: {e}")
                time.sleep(1)
    
    def _process_voice_command(self, command_text):
        """Verarbeitet erkannten Sprachbefehl"""
        for command, action in self.voice_commands.items():
            if command in command_text:
                try:
                    action()
                    self._announce_command_executed(command)
                except Exception as e:
                    print(f"Fehler bei Sprachbefehl '{command}': {e}")
                break
    
    def _announce_command_executed(self, command):
        """Bestätigt ausgeführten Befehl"""
        announcement = f"Befehl '{command}' ausgeführt"
        self._speak_text(announcement)
    
    def setup_color_correction(self, widget):
        """Richtet Farbkorrektur für Farbenblindheit ein"""
        cb_type = self.settings.get("color_blindness_type", "none")
        
        if cb_type == "none":
            return widget
        
        # Color correction matrices
        correction_matrices = {
            "protanopia": np.array([  # Rot-Blindheit
                [0.567, 0.433, 0],
                [0.558, 0.442, 0],
                [0, 0.242, 0.758]
            ]),
            "deuteranopia": np.array([  # Grün-Blindheit
                [0.625, 0.375, 0],
                [0.7, 0.3, 0],
                [0, 0.3, 0.7]
            ]),
            "tritanopia": np.array([  # Blau-Blindheit
                [0.95, 0.05, 0],
                [0, 0.433, 0.567],
                [0, 0.475, 0.525]
            ])
        }
        
        if cb_type in correction_matrices:
            self.color_correction = correction_matrices[cb_type]
            self._apply_color_correction_to_widget(widget)
        
        return widget
    
    def _apply_color_correction_to_widget(self, widget):
        """Wendet Farbkorrektur auf Widget an"""
        # Implementation für verschiedene Widget-Typen
        if hasattr(widget, 'configure'):
            try:
                # Beispiel für Button-Farbkorrektur
                if isinstance(widget, (ctk.CTkButton, tk.Button)):
                    original_color = widget.cget('fg_color')
                    if original_color:
                        corrected_color = self._correct_color(original_color)
                        widget.configure(fg_color=corrected_color)
            except Exception as e:
                print(f"Farbkorrektur-Fehler: {e}")
    
    def _correct_color(self, color_value):
        """Korrigiert einzelne Farbwerte"""
        # Vereinfachte Farbkorrektur - in Praxis komplexer
        if isinstance(color_value, str) and color_value.startswith('#'):
            # Hex to RGB conversion und Korrektur
            rgb = tuple(int(color_value[i:i+2], 16) for i in (1, 3, 5))
            corrected_rgb = np.dot(self.color_correction, rgb)
            corrected_rgb = np.clip(corrected_rgb, 0, 255).astype(int)
            return f"#{corrected_rgb[0]:02x}{corrected_rgb[1]:02x}{corrected_rgb[2]:02x}"
        return color_value
    
    def create_magnifier_window(self, parent):
        """Erstellt Lupen-Fenster für Vergrößerung"""
        if self.magnifier_window and self.magnifier_window.winfo_exists():
            return
        
        self.magnifier_window = ctk.CTkToplevel(parent)
        self.magnifier_window.title("Bildschirmlupe")
        self.magnifier_window.geometry("300x300")
        self.magnifier_window.attributes('-topmost', True)
        
        # Magnifier Canvas
        self.magnifier_canvas = tk.Canvas(
            self.magnifier_window, 
            width=280, 
            height=250,
            bg='white'
        )
        self.magnifier_canvas.pack(pady=10)
        
        # Zoom Controls
        controls_frame = ctk.CTkFrame(self.magnifier_window)
        controls_frame.pack(fill="x", padx=10, pady=5)
        
        zoom_label = ctk.CTkLabel(controls_frame, text="Vergrößerung:")
        zoom_label.pack(side="left", padx=5)
        
        self.zoom_slider = ctk.CTkSlider(
            controls_frame,
            from_=1.0,
            to=5.0,
            number_of_steps=40,
            command=self._update_magnification
        )
        self.zoom_slider.pack(side="left", fill="x", expand=True, padx=5)
        self.zoom_slider.set(self.settings.get("magnification_level", 2.0))
        
        # Magnifier Update Loop starten
        self._start_magnifier_update()
    
    def _start_magnifier_update(self):
        """Startet Magnifier Update Loop"""
        def update_magnifier():
            if self.magnifier_window and self.magnifier_window.winfo_exists():
                self._update_magnifier_content()
                self.magnifier_window.after(100, update_magnifier)
        
        update_magnifier()
    
    def _update_magnifier_content(self):
        """Aktualisiert Magnifier-Inhalt"""
        try:
            # Mausposition ermitteln
            x, y = self.magnifier_window.winfo_pointerx(), self.magnifier_window.winfo_pointery()
            
            # Screenshot-Bereich um Mausposition
            zoom_level = self.zoom_slider.get()
            capture_size = int(100 / zoom_level)
            
            # Vereinfachte Darstellung - in Praxis Screenshot-API verwenden
            self.magnifier_canvas.delete("all")
            self.magnifier_canvas.create_text(
                140, 125,
                text=f"Lupe aktiv\nZoom: {zoom_level:.1f}x\nPosition: {x}, {y}",
                justify="center",
                font=("Arial", int(12 * zoom_level))
            )
            
        except Exception as e:
            print(f"Magnifier Update Error: {e}")
    
    def _update_magnification(self, value):
        """Aktualisiert Vergrößerungslevel"""
        self.settings["magnification_level"] = float(value)
        self.save_advanced_settings()
    
    def setup_dyslexia_support(self, widget):
        """Richtet Dyslexie-Unterstützung ein"""
        if not self.settings.get("dyslexia_support", False):
            return widget
        
        # Dyslexie-freundliche Schriftart
        dyslexia_font = ctk.CTkFont(
            family="OpenDyslexic",  # Falls installiert
            size=14,
            weight="normal"
        )
        
        # Fallback auf Arial bei fehlender Schriftart
        try:
            if hasattr(widget, 'configure'):
                widget.configure(font=dyslexia_font)
        except:
            widget.configure(font=ctk.CTkFont(family="Arial", size=14))
        
        # Zusätzliche Dyslexie-Optimierungen
        if hasattr(widget, 'configure'):
            # Erhöhter Zeilenabstand
            widget.configure(text_color="#2c3e50")  # Besserer Kontrast
        
        return widget
    
    def create_cognitive_load_reducer(self, parent):
        """Erstellt Interface zur Reduzierung kognitiver Belastung"""
        if not self.settings.get("cognitive_load_reduction", False):
            return None
        
        # Simplified Interface Mode
        if self.settings.get("simplified_interface", False):
            self._apply_simplified_interface(parent)
        
        # Attention Indicators
        if self.settings.get("attention_indicators", False):
            self._setup_attention_indicators(parent)
        
        return parent
    
    def _apply_simplified_interface(self, widget):
        """Wendet vereinfachtes Interface an"""
        # Reduzierte Farben und weniger visuelle Ablenkungen
        if hasattr(widget, 'configure'):
            widget.configure(
                fg_color="#f8f9fa",  # Sehr helles Grau
                border_width=1,
                corner_radius=5
            )
    
    def _setup_attention_indicators(self, parent):
        """Richtet Aufmerksamkeitsindikatoren ein"""
        # Fokus-Rahmen für wichtige Elemente
        self.attention_frame = ctk.CTkFrame(
            parent,
            border_width=3,
            border_color="#ff6b6b"
        )
        
        # Pulsierender Effekt für wichtige Aktionen
        def pulse_attention():
            colors = ["#ff6b6b", "#ff8e8e", "#ffb3b3", "#ff8e8e"]
            for color in colors:
                self.attention_frame.configure(border_color=color)
                parent.update()
                time.sleep(0.2)
        
        self.pulse_function = pulse_attention
    
    def setup_motor_assistance(self, widget):
        """Richtet motorische Unterstützung ein"""
        if not self.settings.get("motor_assistance", False):
            return widget
        
        # Vergrößerte Klickbereiche
        if hasattr(widget, 'configure'):
            # Minimale Button-Größe nach WCAG
            widget.configure(
                width=max(44, widget.cget('width') if widget.cget('width') else 120),
                height=max(44, widget.cget('height') if widget.cget('height') else 35)
            )
        
        # Hover-Verzögerung für stabilere Interaktion
        widget.bind("<Enter>", lambda e: self._delayed_hover(e.widget))
        widget.bind("<Leave>", self._cancel_delayed_hover)
        
        # Dwell-Click für Maus-alternative Bedienung
        widget.bind("<Button-1>", self._handle_dwell_click)
        
        return widget
    
    def _delayed_hover(self, widget):
        """Verzögerter Hover-Effekt"""
        def apply_hover():
            time.sleep(0.5)  # 500ms Verzögerung
            if hasattr(widget, 'configure'):
                widget.configure(fg_color="#4a90e2")
        
        self.hover_thread = threading.Thread(target=apply_hover, daemon=True)
        self.hover_thread.start()
    
    def _cancel_delayed_hover(self, event):
        """Bricht verzögerten Hover ab"""
        if hasattr(self, 'hover_thread'):
            # Thread kann nicht direkt abgebrochen werden
            pass
    
    def _handle_dwell_click(self, event):
        """Behandelt Dwell-Click (langes Drücken)"""
        widget = event.widget
        
        def dwell_action():
            time.sleep(1.0)  # 1 Sekunde für Dwell-Click
            if hasattr(widget, 'invoke'):
                widget.invoke()
        
        threading.Thread(target=dwell_action, daemon=True).start()
    
    def create_switch_navigation(self, parent):
        """Erstellt Switch-Navigation für Ein-Taste-Bedienung"""
        if not self.settings.get("switch_navigation", False):
            return
        
        self.switch_elements = []
        self.current_switch_index = 0
        
        # Alle fokussierbaren Elemente sammeln
        self._collect_focusable_elements(parent)
        
        # Switch-Navigation Setup
        parent.bind("<KeyPress-space>", self._switch_select)
        parent.bind("<KeyPress-Return>", self._switch_activate)
        
        # Auto-Scanning starten
        self._start_auto_scanning()
    
    def _collect_focusable_elements(self, parent):
        """Sammelt alle fokussierbaren Elemente"""
        for child in parent.winfo_children():
            if isinstance(child, (ctk.CTkButton, ctk.CTkEntry, ctk.CTkCheckBox)):
                self.switch_elements.append(child)
            self._collect_focusable_elements(child)
    
    def _start_auto_scanning(self):
        """Startet automatisches Scanning"""
        def auto_scan():
            while self.settings.get("switch_navigation", False):
                if self.switch_elements:
                    # Aktuelles Element hervorheben
                    current_element = self.switch_elements[self.current_switch_index]
                    self._highlight_switch_element(current_element)
                    
                    time.sleep(2)  # 2 Sekunden pro Element
                    
                    # Nächstes Element
                    self.current_switch_index = (self.current_switch_index + 1) % len(self.switch_elements)
        
        threading.Thread(target=auto_scan, daemon=True).start()
    
    def _highlight_switch_element(self, element):
        """Hebt Switch-Element hervor"""
        if hasattr(element, 'configure'):
            # Alle anderen Elemente normal
            for el in self.switch_elements:
                if hasattr(el, 'configure'):
                    el.configure(border_width=1, border_color="#cccccc")
            
            # Aktuelles Element hervorheben
            element.configure(border_width=4, border_color="#ff6b6b")
            element.focus_set()
    
    def _switch_select(self, event):
        """Switch-Auswahl bestätigen"""
        if self.switch_elements:
            current_element = self.switch_elements[self.current_switch_index]
            current_element.focus_set()
            self._speak_text(f"Element {self.current_switch_index + 1} ausgewählt")
    
    def _switch_activate(self, event):
        """Switch-Element aktivieren"""
        if self.switch_elements:
            current_element = self.switch_elements[self.current_switch_index]
            if hasattr(current_element, 'invoke'):
                current_element.invoke()
                self._speak_text("Aktiviert")
    
    def _speak_text(self, text):
        """Spricht Text aus"""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            
            # Geschwindigkeit anpassen
            rate = self.settings.get("reading_speed", 200)
            engine.setProperty('rate', rate)
            
            engine.say(text)
            engine.runAndWait()
        except Exception as e:
            print(f"TTS Error: {e}")
    
    def create_advanced_settings_dialog(self, parent):
        """Erstellt erweiterte Einstellungen-Dialog"""
        settings_window = ctk.CTkToplevel(parent)
        settings_window.title("Erweiterte Barrierefreiheit")
        settings_window.geometry("600x700")
        settings_window.transient(parent)
        settings_window.grab_set()
        
        # Scrollable Frame
        scrollable_frame = ctk.CTkScrollableFrame(settings_window)
        scrollable_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Voice Control Section
        voice_frame = ctk.CTkFrame(scrollable_frame)
        voice_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(voice_frame, text="🎙️ Sprachsteuerung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.voice_control_var = tk.BooleanVar(value=self.settings.get("voice_control", False))
        ctk.CTkCheckBox(
            voice_frame,
            text="Sprachsteuerung aktivieren",
            variable=self.voice_control_var
        ).pack(anchor="w", padx=10, pady=5)
        
        self.voice_commands_var = tk.BooleanVar(value=self.settings.get("voice_commands_enabled", True))
        ctk.CTkCheckBox(
            voice_frame,
            text="Sprachbefehle aktivieren",
            variable=self.voice_commands_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Reading Speed
        ctk.CTkLabel(voice_frame, text="Vorlesegeschwindigkeit (WPM):").pack(anchor="w", padx=10, pady=5)
        self.reading_speed_slider = ctk.CTkSlider(
            voice_frame,
            from_=100,
            to=300,
            number_of_steps=200
        )
        self.reading_speed_slider.pack(fill="x", padx=10, pady=5)
        self.reading_speed_slider.set(self.settings.get("reading_speed", 200))
        
        # Color Blindness Section
        color_frame = ctk.CTkFrame(scrollable_frame)
        color_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(color_frame, text="🎨 Farbenblindheit-Unterstützung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.color_blindness_var = tk.StringVar(value=self.settings.get("color_blindness_type", "none"))
        ctk.CTkOptionMenu(
            color_frame,
            values=["none", "protanopia", "deuteranopia", "tritanopia"],
            variable=self.color_blindness_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Motor Assistance Section
        motor_frame = ctk.CTkFrame(scrollable_frame)
        motor_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(motor_frame, text="🖱️ Motorische Unterstützung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.motor_assistance_var = tk.BooleanVar(value=self.settings.get("motor_assistance", False))
        ctk.CTkCheckBox(
            motor_frame,
            text="Motorische Unterstützung aktivieren",
            variable=self.motor_assistance_var
        ).pack(anchor="w", padx=10, pady=5)
        
        self.switch_navigation_var = tk.BooleanVar(value=self.settings.get("switch_navigation", False))
        ctk.CTkCheckBox(
            motor_frame,
            text="Switch-Navigation (Ein-Taste-Bedienung)",
            variable=self.switch_navigation_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Cognitive Support Section
        cognitive_frame = ctk.CTkFrame(scrollable_frame)
        cognitive_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(cognitive_frame, text="🧠 Kognitive Unterstützung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        self.dyslexia_var = tk.BooleanVar(value=self.settings.get("dyslexia_support", False))
        ctk.CTkCheckBox(
            cognitive_frame,
            text="Dyslexie-Unterstützung",
            variable=self.dyslexia_var
        ).pack(anchor="w", padx=10, pady=5)
        
        self.cognitive_load_var = tk.BooleanVar(value=self.settings.get("cognitive_load_reduction", False))
        ctk.CTkCheckBox(
            cognitive_frame,
            text="Reduzierung kognitiver Belastung",
            variable=self.cognitive_load_var
        ).pack(anchor="w", padx=10, pady=5)
        
        self.simplified_interface_var = tk.BooleanVar(value=self.settings.get("simplified_interface", False))
        ctk.CTkCheckBox(
            cognitive_frame,
            text="Vereinfachtes Interface",
            variable=self.simplified_interface_var
        ).pack(anchor="w", padx=10, pady=5)
        
        self.attention_indicators_var = tk.BooleanVar(value=self.settings.get("attention_indicators", False))
        ctk.CTkCheckBox(
            cognitive_frame,
            text="Aufmerksamkeitsindikatoren",
            variable=self.attention_indicators_var
        ).pack(anchor="w", padx=10, pady=5)
        
        # Visual Assistance Section
        visual_frame = ctk.CTkFrame(scrollable_frame)
        visual_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(visual_frame, text="👁️ Visuelle Unterstützung", font=ctk.CTkFont(size=16, weight="bold")).pack(pady=5)
        
        # Magnification Level
        ctk.CTkLabel(visual_frame, text="Vergrößerungslevel:").pack(anchor="w", padx=10, pady=5)
        self.magnification_slider = ctk.CTkSlider(
            visual_frame,
            from_=1.0,
            to=5.0,
            number_of_steps=40
        )
        self.magnification_slider.pack(fill="x", padx=10, pady=5)
        self.magnification_slider.set(self.settings.get("magnification_level", 1.0))
        
        # Magnifier Button
        ctk.CTkButton(
            visual_frame,
            text="Bildschirmlupe öffnen",
            command=lambda: self.create_magnifier_window(parent)
        ).pack(pady=5)
        
        # Buttons
        button_frame = ctk.CTkFrame(settings_window)
        button_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="Speichern",
            command=lambda: self._save_advanced_settings_dialog(settings_window)
        ).pack(side="right", padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="Abbrechen",
            command=settings_window.destroy
        ).pack(side="right", padx=5)
        
        # Test Button
        ctk.CTkButton(
            button_frame,
            text="Einstellungen testen",
            command=self._test_advanced_settings
        ).pack(side="left", padx=5)
    
    def _save_advanced_settings_dialog(self, dialog):
        """Speichert Einstellungen aus Dialog"""
        self.settings.update({
            "voice_control": self.voice_control_var.get(),
            "voice_commands_enabled": self.voice_commands_var.get(),
            "reading_speed": int(self.reading_speed_slider.get()),
            "color_blindness_type": self.color_blindness_var.get(),
            "motor_assistance": self.motor_assistance_var.get(),
            "switch_navigation": self.switch_navigation_var.get(),
            "dyslexia_support": self.dyslexia_var.get(),
            "cognitive_load_reduction": self.cognitive_load_var.get(),
            "simplified_interface": self.simplified_interface_var.get(),
            "attention_indicators": self.attention_indicators_var.get(),
            "magnification_level": self.magnification_slider.get()
        })
        
        self.save_advanced_settings()
        dialog.destroy()
        messagebox.showinfo("Gespeichert", "Erweiterte Barrierefreiheits-Einstellungen wurden gespeichert.")
    
    def _test_advanced_settings(self):
        """Testet erweiterte Einstellungen"""
        test_text = "Dies ist ein Test der erweiterten Barrierefreiheits-Einstellungen."
        self._speak_text(test_text)
        messagebox.showinfo("Test", "Sprachausgabe-Test gestartet.")
    
    # Voice Command Implementations
    def _voice_open_file(self):
        """Sprachbefehl: Datei öffnen"""
        print("Voice Command: Datei öffnen")
    
    def _voice_save_file(self):
        """Sprachbefehl: Datei speichern"""
        print("Voice Command: Datei speichern")
    
    def _voice_start_analysis(self):
        """Sprachbefehl: Analyse starten"""
        print("Voice Command: Analyse starten")
    
    def _voice_next_step(self):
        """Sprachbefehl: Nächster Schritt"""
        print("Voice Command: Nächster Schritt")
    
    def _voice_previous_step(self):
        """Sprachbefehl: Vorheriger Schritt"""
        print("Voice Command: Vorheriger Schritt")
    
    def _voice_show_help(self):
        """Sprachbefehl: Hilfe anzeigen"""
        print("Voice Command: Hilfe anzeigen")
    
    def _voice_open_settings(self):
        """Sprachbefehl: Einstellungen öffnen"""
        print("Voice Command: Einstellungen öffnen")
    
    def _voice_exit_app(self):
        """Sprachbefehl: App beenden"""
        print("Voice Command: App beenden")
    
    def _voice_read_current(self):
        """Sprachbefehl: Aktuellen Inhalt vorlesen"""
        print("Voice Command: Vorlesen")
    
    def _voice_pause_reading(self):
        """Sprachbefehl: Vorlesen pausieren"""
        print("Voice Command: Vorlesen pausieren")
    
    def _voice_repeat_last(self):
        """Sprachbefehl: Letzte Ansage wiederholen"""
        print("Voice Command: Wiederholen")
    
    def _voice_zoom_in(self):
        """Sprachbefehl: Vergrößern"""
        current_level = self.settings.get("magnification_level", 1.0)
        new_level = min(5.0, current_level + 0.5)
        self.settings["magnification_level"] = new_level
        print(f"Voice Command: Vergrößert auf {new_level}x")
    
    def _voice_zoom_out(self):
        """Sprachbefehl: Verkleinern"""
        current_level = self.settings.get("magnification_level", 1.0)
        new_level = max(1.0, current_level - 0.5)
        self.settings["magnification_level"] = new_level
        print(f"Voice Command: Verkleinert auf {new_level}x")
    
    def _voice_toggle_contrast(self):
        """Sprachbefehl: Kontrast umschalten"""
        print("Voice Command: Kontrast umschalten")
    
    def _create_voice_feedback_widget(self, parent):
        """Erstellt Voice Feedback Widget"""
        self.voice_feedback_frame = ctk.CTkFrame(parent)
        self.voice_feedback_frame.pack(side="bottom", fill="x", padx=10, pady=5)
        
        self.voice_status_label = ctk.CTkLabel(
            self.voice_feedback_frame,
            text="🎙️ Sprachsteuerung aktiv - Sagen Sie 'Hilfe' für verfügbare Befehle",
            font=ctk.CTkFont(size=12)
        )
        self.voice_status_label.pack(pady=5)

# Global Instance
advanced_accessibility = AdvancedAccessibility()

def create_accessible_widget_advanced(widget_class, parent, **kwargs):
    """Erstellt erweitert barrierefreies Widget"""
    widget = widget_class(parent, **kwargs)
    
    # Erweiterte Accessibility Features anwenden
    advanced_accessibility.setup_color_correction(widget)
    advanced_accessibility.setup_dyslexia_support(widget)
    advanced_accessibility.setup_motor_assistance(widget)
    
    return widget

def setup_advanced_accessibility(root):
    """Richtet erweiterte Barrierefreiheit für ganze App ein"""
    advanced_accessibility.setup_voice_control(root)
    advanced_accessibility.create_cognitive_load_reducer(root)
    advanced_accessibility.create_switch_navigation(root)
    
    # Globale Tastenkombinationen
    root.bind("<Control-Alt-v>", lambda e: advanced_accessibility.create_advanced_settings_dialog(root))
    root.bind("<Control-Alt-m>", lambda e: advanced_accessibility.create_magnifier_window(root))
    root.bind("<Control-Alt-h>", lambda e: advanced_accessibility._voice_show_help())

if __name__ == "__main__":
    # Test der erweiterten Accessibility Features
    ctk.set_appearance_mode("light")
    
    root = ctk.CTk()
    root.title("Erweiterte Barrierefreiheit Test")
    root.geometry("800x600")
    
    # Advanced Accessibility Setup
    setup_advanced_accessibility(root)
    
    # Test Widgets
    main_frame = ctk.CTkFrame(root)
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Accessible Widgets with advanced features
    label = create_accessible_widget_advanced(
        ctk.CTkLabel,
        main_frame,
        text="Erweiterte Barrierefreiheit Test",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    label.pack(pady=10)
    
    button = create_accessible_widget_advanced(
        ctk.CTkButton,
        main_frame,
        text="Test Button",
        command=lambda: print("Advanced accessible button clicked")
    )
    button.pack(pady=10)
    
    # Settings Button
    settings_btn = create_accessible_widget_advanced(
        ctk.CTkButton,
        main_frame,
        text="🔧 Erweiterte Barrierefreiheits-Einstellungen",
        command=lambda: advanced_accessibility.create_advanced_settings_dialog(root)
    )
    settings_btn.pack(pady=20)
    
    # Info Text
    info_text = ctk.CTkTextbox(main_frame, height=100)
    info_text.pack(fill="x", pady=10)
    info_text.insert("0.0", 
        "Erweiterte Barrierefreiheits-Features:\n"
        "• Sprachsteuerung (Ctrl+Alt+V für Einstellungen)\n"
        "• Bildschirmlupe (Ctrl+Alt+M)\n"
        "• Switch-Navigation\n"
        "• Dyslexie-Unterstützung\n"
        "• Farbenblindheit-Korrektur\n"
        "• Motorische Unterstützung"
    )
    
    root.mainloop()
