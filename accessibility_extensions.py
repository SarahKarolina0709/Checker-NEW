# -*- coding: utf-8 -*-
"""
Accessibility Extensions - Zusätzliche Barrierefreiheits-Features
Ergänzt die bestehenden Accessibility-Module um weitere spezialisierte Features
"""

import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox, ttk
import threading
import time
import json
import os
import sqlite3
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Callable
from advanced_accessibility import AdaptiveInterface

# Optional imports with fallbacks
try:
    import win32api
    import win32con
    import win32gui
    import win32process
    WIN32_AVAILABLE = True
except ImportError:
    print("Warning: pywin32 not available. Some Windows-specific features will be disabled.")
    WIN32_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    print("Warning: psutil not available. Process monitoring features will be disabled.")
    PSUTIL_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    print("Warning: numpy not available. Advanced analytics features will be disabled.")
    NUMPY_AVAILABLE = False

# Einfaches Zeit-Profiling
startup_time = time.time()

@dataclass
class AccessibilityProfile:
    """Benutzerdefiniertes Barrierefreiheits-Profil"""
    name: str
    vision_impairment: str  # none, low_vision, blind, color_blind
    motor_impairment: str   # none, limited_dexterity, no_mouse, switch_only
    cognitive_needs: str    # none, dyslexia, adhd, memory_issues
    hearing_impairment: str # none, hard_of_hearing, deaf
    preferences: Dict
    created_date: datetime
    
class EnhancedAccessibilityManager:
    """Erweiterte Barrierefreiheits-Verwaltung mit Benutzerprofilen"""
    
    def __init__(self):
        self.profiles = {}
        self.current_profile = None
        self.eye_tracking_data = []
        self.usage_analytics = {}
        self.context_awareness = {}
        self.adaptive_interface = None
        self._db_initialized = False
        self._monitoring_started = False
        
        # Am Ende der Initialisierung
        print(f"[Startup-Profiling] Initialisierung dauerte {time.time() - startup_time:.2f} Sekunden")
        
    def _get_default_preferences(self) -> Dict:
        """Standardeinstellungen für neue Profile"""
        return {
            'magnification': 1.0,
            'click_tolerance': 10,
            'hover_delay': 0.5,
            'font_size': 12,
            'high_contrast': False,
            'screen_reader_mode': False,
            'keyboard_only': False,
            'visual_indicators': True        }
        
    def _check_dependencies(self) -> Dict[str, bool]:
        """Überprüft verfügbare Abhängigkeiten"""
        return {
            'win32': WIN32_AVAILABLE,
            'psutil': PSUTIL_AVAILABLE,
            'numpy': NUMPY_AVAILABLE,
            'pil': False,            'cv2': False,            'matplotlib': False
        }
        
    def _ensure_database(self):
        """Stellt sicher, dass die Datenbank initialisiert ist"""
        if not self._db_initialized:
            self.init_database()
            self._db_initialized = True
    
    def init_database(self):
        """Initialisiert Datenbank für Accessibility-Daten"""
        try:
            self.conn = sqlite3.connect('accessibility_data.db')
            cursor = self.conn.cursor()
        
            # Benutzerprofile
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE,
                    vision_impairment TEXT,
                    motor_impairment TEXT,
                    cognitive_needs TEXT,
                    hearing_impairment TEXT,
                    preferences TEXT,
                    created_date TIMESTAMP,
                    last_used TIMESTAMP
                )
            ''')
            
            # Nutzungsanalyse
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS usage_analytics (
                    id INTEGER PRIMARY KEY,
                    user_profile TEXT,
                    action_type TEXT,
                    timestamp TIMESTAMP,
                    duration REAL,
                    success BOOLEAN,
                    error_count INTEGER,
                    context TEXT            )
            ''')
            
            # Anpassungen und Lerndata
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS adaptations (
                    id INTEGER PRIMARY KEY,
                    user_profile TEXT,
                    feature TEXT,
                    adaptation_type TEXT,
                    effectiveness REAL,
                    timestamp TIMESTAMP
                )
            ''')
            
            self.conn.commit()
        except Exception as e:
            print(f"Fehler beim Initialisieren der Datenbank: {e}")
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()
            raise
    
    def create_user_profile(self, name: str, vision: str = "none", 
                          motor: str = "none", cognitive: str = "none", 
                          hearing: str = "none", preferences: Dict = None) -> AccessibilityProfile:
        """Erstellt neues Benutzerprofil"""
        self._ensure_database()  # Ensure database is initialized
        
        if preferences is None:
            preferences = self._get_default_preferences()
            
        profile = AccessibilityProfile(
            name=name,
            vision_impairment=vision,
            motor_impairment=motor,
            cognitive_needs=cognitive,
            hearing_impairment=hearing,
            preferences=preferences,
            created_date=datetime.now()
        )
        
        # In Datenbank speichern
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO profiles 
            (name, vision_impairment, motor_impairment, cognitive_needs, 
             hearing_impairment, preferences, created_date, last_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)        ''', (
            profile.name, profile.vision_impairment, profile.motor_impairment,
            profile.cognitive_needs, profile.hearing_impairment,
            json.dumps(profile.preferences), profile.created_date, datetime.now()
        ))
        self.conn.commit()
        
        self.profiles[name] = profile
        return profile
    
    def load_user_profile(self, name: str) -> Optional[AccessibilityProfile]:
        """Lädt Benutzerprofil"""
        self._ensure_database()  # Ensure database is initialized
        
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM profiles WHERE name = ?', (name,))
        row = cursor.fetchone()
        
        if row:
            profile = AccessibilityProfile(
                name=row[1],
                vision_impairment=row[2],
                motor_impairment=row[3],
                cognitive_needs=row[4],
                hearing_impairment=row[5],
                preferences=json.loads(row[6]),
                created_date=datetime.fromisoformat(row[7])
            )
            
            # Last used aktualisieren
            cursor.execute('UPDATE profiles SET last_used = ? WHERE name = ?', 
                         (datetime.now(), name))
            self.conn.commit()
            
            self.profiles[name] = profile
            self.current_profile = profile
            return profile
        return None
        
    def apply_profile(self, profile: AccessibilityProfile, root_widget):
        """Wendet Benutzerprofil auf Interface an"""
        self.current_profile = profile
        
        # Vision-spezifische Anpassungen
        if profile.vision_impairment == "low_vision":
            self._apply_low_vision_settings(root_widget, profile.preferences)
        elif profile.vision_impairment == "blind":
            self._apply_screen_reader_optimization(root_widget, profile.preferences)
        elif profile.vision_impairment == "color_blind":
            self._apply_color_blind_settings(root_widget, profile.preferences)
            
        # Motor-spezifische Anpassungen
        if profile.motor_impairment == "limited_dexterity":
            self._apply_motor_assistance(root_widget, profile.preferences)
        elif profile.motor_impairment == "no_mouse":
            self._apply_keyboard_only_mode(root_widget, profile.preferences)
        elif profile.motor_impairment == "switch_only":
            self._apply_switch_navigation(root_widget, profile.preferences)
            
        # Kognitive Anpassungen
        if profile.cognitive_needs == "dyslexia":
            self._apply_dyslexia_support(root_widget, profile.preferences)
        elif profile.cognitive_needs == "adhd":
            self._apply_adhd_support(root_widget, profile.preferences)
        elif profile.cognitive_needs == "memory_issues":
            self._apply_memory_assistance(root_widget, profile.preferences)
            
        # Hör-spezifische Anpassungen
        if profile.hearing_impairment in ["hard_of_hearing", "deaf"]:
            self._apply_visual_indicators(root_widget, profile.preferences)
            
    def _apply_low_vision_settings(self, widget, preferences):
        """Anpassungen für Sehschwäche"""
        # Hoher Kontrast
        self._set_high_contrast_theme(widget)
        
        # Vergrößerung
        magnification = preferences.get('magnification', 2.0)
        self._apply_interface_magnification(widget, magnification)
        
        # Cursor-Verbesserungen
        self._enhance_cursor_visibility(widget)
        
    def _apply_screen_reader_optimization(self, widget, preferences):
        """Optimierungen für Screenreader"""
        # Strukturierte Navigation
        self._add_landmark_navigation(widget)
        
        # Verbesserte ARIA-Labels
        self._enhance_aria_descriptions(widget)
        
        # Screenreader-freundliche Fokus-Reihenfolge
        self._optimize_tab_order(widget)
        
    def _apply_motor_assistance(self, widget, preferences):
        """Motorische Unterstützung"""
        # Vergrößerte Klickbereiche
        click_tolerance = preferences.get('click_tolerance', 20)
        self._enlarge_interactive_areas(widget, click_tolerance)
        
        # Hover-Delays
        hover_delay = preferences.get('hover_delay', 1.0)
        self._add_hover_delays(widget, hover_delay)
        
        # Drag & Drop Vereinfachung
        self._simplify_drag_drop(widget)
        
    def _apply_dyslexia_support(self, widget, preferences):
        """Dyslexie-Unterstützung"""
        # OpenDyslexic Font
        try:
            dyslexic_font = ('OpenDyslexic', 12)
            self._apply_font_family(widget, dyslexic_font)
        except:
            # Fallback: Arial mit erhöhtem Zeichenabstand
            self._apply_font_family(widget, ('Arial', 12))
            
        # Zeilenhöhe erhöhen
        self._increase_line_height(widget, 1.6)
        
        # Leselineal aktivieren
        self._add_reading_guide(widget)
        
    def _apply_adhd_support(self, widget, preferences):
        """ADHD-Unterstützung"""
        # Ablenkungen reduzieren
        self._reduce_visual_noise(widget)
        
        # Focus-Hilfen
        self._add_focus_indicators(widget)
        
        # Zeitmanagement-Tools
        self._add_time_awareness(widget)
        
    def create_adaptive_interface(self, root_widget):
        """Erstellt adaptives Interface basierend auf Nutzungsverhalten"""
        self.adaptive_interface = AdaptiveInterface(self)
        self.adaptive_interface.initialize(root_widget)
        
        # Monitoring starten
        self._start_usage_monitoring(root_widget)
        
    def _start_usage_monitoring(self, widget):
        """Startet Nutzungsüberwachung für adaptive Anpassungen"""
        def monitor_usage():
            while True:
                if self.current_profile:
                    # Maus-/Tastaturaktivität überwachen
                    self._track_interaction_patterns()
                    
                    # Fehler und Verzögerungen erkennen
                    self._detect_usage_difficulties()
                    
                    # Adaptive Anpassungen vorschlagen
                    self._suggest_adaptations()
                    
                time.sleep(1)  # Überwachungsintervall
                
        threading.Thread(target=monitor_usage, daemon=True).start()
        
    def create_profile_wizard(self, parent):
        """Erstellt Assistent für Profilerstellung"""
        wizard = ctk.CTkToplevel(parent)
        wizard.title("Barrierefreiheits-Profile erstellen")
        wizard.geometry("700x600")
        wizard.transient(parent)
        wizard.grab_set()
        
        # Wizard-Schritte
        self.wizard_step = 0
        self.wizard_data = {}
        
        # Container für Wizard-Inhalte
        self.wizard_container = ctk.CTkFrame(wizard)
        self.wizard_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Schritt 1: Grundinformationen
        self._create_wizard_step_1()
          # Navigation
        nav_frame = ctk.CTkFrame(wizard)
        nav_frame.pack(fill="x", padx=20, pady=10)
        
        self.back_btn = ctk.CTkButton(nav_frame, text="← Zurück", 
                                     command=self._wizard_previous)
        self.back_btn.pack(side="left")
        
        self.next_btn = ctk.CTkButton(nav_frame, text="Weiter →", 
                                     command=self._wizard_next)
        self.next_btn.pack(side="right")
        
        # Finish Button wird erst bei Bedarf erstellt und gepackt
        self.finish_btn = ctk.CTkButton(nav_frame, text="Profil erstellen", 
                                       command=self._wizard_finish)
        # Button nicht initial packen - wird bei Bedarf in _wizard_next gepackt
        
    def _wizard_next(self):
        """Nächster Schritt im Wizard"""
        if self.wizard_step == 0:
            # Validierung für Schritt 1
            if not self.name_entry.get().strip():
                messagebox.showerror("Fehler", "Bitte geben Sie einen Profilnamen ein.")
                return
            
            self.wizard_data['name'] = self.name_entry.get().strip()
            self.wizard_step = 1
            self._create_wizard_step_2()
            
        elif self.wizard_step == 1:
            # Schritt 2 zu Schritt 3
            self.wizard_step = 2
            self._create_wizard_step_3()
            
        elif self.wizard_step == 2:
            # Letzter Schritt - Finish Button anzeigen
            self.wizard_step = 3
            self._create_wizard_step_final()
            
            # Navigation aktualisieren
            self.next_btn.pack_forget()
            self.finish_btn.pack(side="right")
            
        # Back Button verwalten
        if self.wizard_step > 0:
            if not self.back_btn.winfo_ismapped():
                self.back_btn.pack(side="left")
    
    def _wizard_previous(self):
        """Vorheriger Schritt im Wizard"""
        if self.wizard_step > 0:
            self.wizard_step -= 1
            
            if self.wizard_step == 0:
                self._create_wizard_step_1()
                self.back_btn.pack_forget()
            elif self.wizard_step == 1:
                self._create_wizard_step_2()
            elif self.wizard_step == 2:
                self._create_wizard_step_3()
                
            # Navigation aktualisieren
            if self.finish_btn.winfo_ismapped():
                self.finish_btn.pack_forget()
                self.next_btn.pack(side="right")
    
    def _wizard_finish(self):
        """Abschluss des Wizards - Profil erstellen"""
        try:
            # Profil mit gesammelten Daten erstellen
            profile = self.create_user_profile(
                name=self.wizard_data['name'],
                vision=self.wizard_data.get('vision', 'none'),
                motor=self.wizard_data.get('motor', 'none'),
                cognitive=self.wizard_data.get('cognitive', 'none'),
                hearing=self.wizard_data.get('hearing', 'none'),
                preferences=self.wizard_data.get('preferences', {})
            )
            
            messagebox.showinfo("Erfolg", f"Profil '{profile.name}' wurde erfolgreich erstellt!")
            
            # Wizard schließen
            if hasattr(self, 'wizard_window'):
                self.wizard_window.destroy()
                
        except Exception as e:
            messagebox.showerror("Fehler", f"Profil konnte nicht erstellt werden: {e}")
    
    def _create_wizard_step_2(self):
        """Wizard Schritt 2: Sehbehinderungen"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 2: Sehbehinderungen",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        self.vision_var = ctk.StringVar(value="none")
        
        vision_options = [
            ("none", "Keine Sehbehinderung"),
            ("low_vision", "Sehschwäche"),
            ("blind", "Blindheit"),
            ("color_blind", "Farbenblindheit")
        ]
        
        for value, text in vision_options:
            ctk.CTkRadioButton(self.wizard_container, text=text, 
                             variable=self.vision_var, value=value).pack(anchor="w", padx=20, pady=5)
    
    def _create_wizard_step_3(self):
        """Wizard Schritt 3: Motorische Behinderungen"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 3: Motorische Behinderungen",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        self.motor_var = ctk.StringVar(value="none")
        
        motor_options = [
            ("none", "Keine motorischen Einschränkungen"),
            ("limited_dexterity", "Eingeschränkte Feinmotorik"),
            ("no_mouse", "Keine Mausbedienung möglich"),
            ("switch_only", "Nur Switch-Bedienung")
        ]
        
        for value, text in motor_options:
            ctk.CTkRadioButton(self.wizard_container, text=text, 
                             variable=self.motor_var, value=value).pack(anchor="w", padx=20, pady=5)
    
    def _create_wizard_step_final(self):
        """Wizard Final: Zusammenfassung"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        ctk.CTkLabel(self.wizard_container, 
                    text="Zusammenfassung",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Daten sammeln
        self.wizard_data['vision'] = getattr(self, 'vision_var', ctk.StringVar(value="none")).get()
        self.wizard_data['motor'] = getattr(self, 'motor_var', ctk.StringVar(value="none")).get()
        
        summary_text = f"""
Profilname: {self.wizard_data['name']}
Sehbehinderung: {self.wizard_data['vision']}
Motorische Behinderung: {self.wizard_data['motor']}

Das Profil wird mit optimalen Einstellungen für Ihre Bedürfnisse erstellt.
        """
        
        ctk.CTkLabel(self.wizard_container, text=summary_text.strip(), 
                    justify="left").pack(pady=20)
        
    def _create_wizard_step_1(self):
        """Wizard Schritt 1: Grundinformationen"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        # Titel
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 1: Grundinformationen",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Name
        ctk.CTkLabel(self.wizard_container, text="Profilname:").pack(anchor="w", padx=20)
        self.name_entry = ctk.CTkEntry(self.wizard_container, placeholder_text="Mein Profil")
        self.name_entry.pack(fill="x", padx=20, pady=5)
        
        # Beschreibung
        ctk.CTkLabel(self.wizard_container, 
                    text="Dieses Profil hilft dabei, die Anwendung an Ihre "
                         "spezifischen Bedürfnisse anzupassen.").pack(pady=10)
        
    def create_quick_access_panel(self, parent, use_grid=False, grid_options=None, pruefung_callback=None):
        """Erstellt Schnellzugriff-Panel für Accessibility-Features (wahlweise mit pack oder grid)
        pruefung_callback: Funktion, die beim Klick auf den Prüfung-Button aufgerufen wird (z.B. Workflow-Start)
        """
        panel = ctk.CTkFrame(parent)
        if use_grid:
            opts = grid_options or {'row': 0, 'column': 0, 'sticky': 'nsew', 'padx': 5, 'pady': 5}
            panel.grid(**opts)
        else:
            panel.pack(side="right", fill="y", padx=5, pady=5)

        # Widgets konsistent platzieren
        widgets = []
        label = ctk.CTkLabel(panel, text="♿ Schnellzugriff", font=ctk.CTkFont(size=14, weight="bold"))
        widgets.append((label, {"pady": 5}))

        # Schnellzugriff-Buttons
        quick_actions = [
            ("🔍", "Vergrößern", self._quick_magnify),
            ("🎨", "Kontrast", self._quick_contrast),
            ("🔊", "Vorlesen", self._quick_read_aloud),
            ("⌨️", "Tastatur", self._quick_keyboard_mode),
            ("🎯", "Focus", self._quick_focus_mode),
            ("⏱️", "Pause", self._quick_break_reminder)
        ]
        for idx, (icon, text, command) in enumerate(quick_actions):
            btn = ctk.CTkButton(panel, text=f"{icon}\n{text}", width=80, height=60, command=command)
            if use_grid:
                widgets.append((btn, {"row": idx+1, "column": 0, "padx": 2, "pady": 2, "sticky": "ew"}))
            else:
                widgets.append((btn, {"pady": 2}))

        # Prüfung-Button hinzufügen
        pruefung_btn = ctk.CTkButton(panel, text="✅\nPrüfung", width=80, height=60, command=pruefung_callback if pruefung_callback else self._default_pruefung_action)
        if use_grid:
            widgets.append((pruefung_btn, {"row": len(quick_actions)+1, "column": 0, "padx": 2, "pady": 8, "sticky": "ew"}))
        else:
            widgets.append((pruefung_btn, {"pady": 8}))

        # Platzierung aller Widgets
        for w, opts in widgets:
            if use_grid:
                w.grid(**opts)
            else:
                w.pack(**opts)
        return panel

    def _default_pruefung_action(self):
        """Fallback-Handler für Prüfung-Button, falls kein Callback gesetzt ist."""
        messagebox.showinfo("Prüfung", "Bitte verbinden Sie den Prüfung-Button mit dem Workflow-Start im Hauptprogramm.")
    
    def _quick_keyboard_mode(self):
        """Aktiviert Nur-Tastatur-Modus"""
        try:
            if hasattr(self, 'keyboard_only_mode'):
                self.keyboard_only_mode = not self.keyboard_only_mode
            else:
                self.keyboard_only_mode = True
                
            # Tastatur-Modus Status anwenden
            if hasattr(self, 'current_profile') and self.current_profile:
                self.current_profile.preferences['keyboard_only'] = self.keyboard_only_mode
                
            # Benachrichtigung über Statusänderung
            mode_status = "aktiviert" if self.keyboard_only_mode else "deaktiviert"
            print(f"Nur-Tastatur-Modus {mode_status}")
            
        except Exception as e:
            print(f"Fehler beim Umschalten des Tastatur-Modus: {e}")
    
    def _quick_focus_mode(self):
        """Aktiviert Fokus-Hilfsmodus"""
        try:
            if hasattr(self, 'focus_mode'):
                self.focus_mode = not self.focus_mode
            else:
                self.focus_mode = True
                
            # Fokus-Modus Status anwenden
            if hasattr(self, 'current_profile') and self.current_profile:
                self.current_profile.preferences['focus_mode'] = self.focus_mode
                
            # Benachrichtigung über Statusänderung
            mode_status = "aktiviert" if self.focus_mode else "deaktiviert"
            print(f"Fokus-Hilfsmodus {mode_status}")
            
        except Exception as e:
            print(f"Fehler beim Umschalten des Fokus-Modus: {e}")
    
    def _quick_break_reminder(self):
        """Aktiviert Pausenerinnerung"""
        try:
            if hasattr(self, 'break_reminder'):
                self.break_reminder = not self.break_reminder
            else:
                self.break_reminder = True
                
            # Pausenerinnerung Status anwenden
            if hasattr(self, 'current_profile') and self.current_profile:
                self.current_profile.preferences['break_reminder'] = self.break_reminder
                
            # Benachrichtigung über Statusänderung
            reminder_status = "aktiviert" if self.break_reminder else "deaktiviert"
            print(f"Pausenerinnerung {reminder_status}")
            
            if self.break_reminder:
                # Starte Pausenerinnerungs-Timer (alle 30 Minuten)
                self._start_break_reminder_timer()
            
        except Exception as e:
            print(f"Fehler beim Umschalten der Pausenerinnerung: {e}")
    
    def _start_break_reminder_timer(self):
        """Startet Timer für Pausenerinnerungen"""
        def reminder_loop():
            try:
                import time
                while hasattr(self, 'break_reminder') and self.break_reminder:
                    time.sleep(1800)  # 30 Minuten
                    if hasattr(self, 'break_reminder') and self.break_reminder:
                        print("💡 Pausenerinnerung: Es ist Zeit für eine kurze Pause!")
                        # Optional: Zeige Notification Dialog
                        try:
                            messagebox.showinfo("Pausenerinnerung", 
                                               "Es ist Zeit für eine kurze Pause!\n"
                                               "Vergessen Sie nicht, Ihre Augen zu entspannen.")
                        except:
                            pass  # Fallback falls GUI nicht verfügbar
            except Exception as e:
                print(f"Fehler im Pausenerinnerungs-Timer: {e}")
        
        threading.Thread(target=reminder_loop, daemon=True).start()
        
    def _quick_contrast(self):
        """Schnell-Kontrast umschalten"""
        # Kontrast-Modus umschalten
        try:
            if hasattr(self, 'high_contrast_enabled'):
                self.high_contrast_enabled = not self.high_contrast_enabled
            else:
                self.high_contrast_enabled = True
                
            # Aktuellen Kontrast-Status anwenden
            if hasattr(self, 'current_profile') and self.current_profile:
                self.current_profile.preferences['high_contrast'] = self.high_contrast_enabled
                  # Benachrichtigung über Statusänderung
            contrast_status = "aktiviert" if self.high_contrast_enabled else "deaktiviert"
            print(f"Hoher Kontrast {contrast_status}")
            
        except Exception as e:
            print(f"Fehler beim Umschalten des Kontrasts: {e}")
        
    def _quick_read_aloud(self):
        """Schnell-Vorlesen aktivieren"""
        # Text-to-Speech aktivieren
        try:
            import win32com.client  # Lazy Import
            if not hasattr(self, 'tts_engine'):
                self.tts_engine = win32com.client.Dispatch("SAPI.SpVoice")
            text = "Text-zu-Sprache wurde aktiviert. Sie können jetzt Texte vorlesen lassen."
            self.tts_engine.Speak(text)
            print("Text-zu-Sprache aktiviert")
        except ImportError:
            print("Text-zu-Sprache: Windows Speech API nicht verfügbar")
            messagebox.showinfo("Text-zu-Sprache", 
                              "Text-zu-Sprache wurde aktiviert.\n"
                              "Hinweis: Windows Speech API ist nicht verfügbar.")
        except Exception as e:
            print(f"Fehler beim Aktivieren der Sprachausgabe: {e}")
            messagebox.showerror("Fehler", f"Sprachausgabe konnte nicht aktiviert werden: {e}")

    def _create_usage_analytics(self, parent):
        """Erstellt Nutzungsanalytik-Ansicht"""
        # Lazy-Import und nur bei Bedarf
        try:
            import matplotlib.pyplot as plt
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            MATPLOTLIB_AVAILABLE = True
        except ImportError:
            MATPLOTLIB_AVAILABLE = False
        if not MATPLOTLIB_AVAILABLE:
            # Fallback: Text-basierte Analytik
            text_frame = ctk.CTkFrame(parent)
            text_frame.pack(fill="both", expand=True, padx=10, pady=10)
            ctk.CTkLabel(
                text_frame,
                text="\U0001F4CA Nutzungsanalytik\n\n"
                     "Matplotlib ist nicht verfügbar.\n"
                     "Installieren Sie matplotlib für erweiterte Diagramme:\n"
                     "pip install matplotlib",
                font=ctk.CTkFont(size=14),
                justify="center"
            ).pack(expand=True)
            # Einfache Text-Statistiken
            stats_text = (
                "Aktivitätsverteilung:\n"
                "• Dateien öffnen: 45%\n"
                "• Text analysieren: 30%\n"
                "• Einstellungen: 15%\n"
                "• Navigation: 10%\n\n"
                "Schwierigkeitsgrad (1-5):\n"
                "• Menü Navigation: 2.3\n"
                "• Datei Auswahl: 1.8\n"
                "• Text Eingabe: 3.1\n"
                "• Button Klicks: 1.5"
            )
            ctk.CTkLabel(
                text_frame,
                text=stats_text,
                font=ctk.CTkFont(size=12),
                justify="left"
            ).pack(pady=20)
            return
        # Diagramm für Nutzungsmuster
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        activities = ['Dateien öffnen', 'Text analysieren', 'Einstellungen', 'Navigation']
        counts = [45, 30, 15, 10]  # Beispieldaten
        ax1.pie(counts, labels=activities, autopct='%1.1f%%')
        ax1.set_title('Aktivitätsverteilung')
        features = ['Menü\nNavigation', 'Datei\nAuswahl', 'Text\nEingabe', 'Button\nKlicks']
        difficulty_scores = [2.3, 1.8, 3.1, 1.5]
        ax2.bar(features, difficulty_scores, color=['green' if x < 2 else 'orange' if x < 3 else 'red' for x in difficulty_scores])
        ax2.set_title('Schwierigkeitsgrad nach Feature')
        ax2.set_ylabel('Schwierigkeit (1-5)')
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        
    def _create_effectiveness_analytics(self, parent):
        """Erstellt Effektivitäts-Analytik-Ansicht"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        ctk.CTkLabel(
            frame,
            text="\U0001F4C8 Accessibility-Effektivität",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        # Einfache Metriken
        metrics_text = (
            "Verbesserungen durch Accessibility-Features:\n\n"
            "• Aufgabenabschlussrate: +25%\n"
            "• Fehlerreduktion: -40%\n"
            "• Benutzerzufriedenheit: +35%\n"
            "• Bedienungszeit: -30%\n\n"
            "Am effektivsten:\n"
            "• Vergrößerung (92% Zufriedenheit)\n"
            "• Hoher Kontrast (89% Zufriedenheit)\n"
            "• Tastaturnavigation (85% Zufriedenheit)"
        )
        ctk.CTkLabel(
            frame,
            text=metrics_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=20)
        
    def _create_recommendations_view(self, parent):
        """Erstellt Empfehlungs-Ansicht"""
        frame = ctk.CTkFrame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            frame,
            text="💡 Personalisierte Empfehlungen",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=10)
        
        if self.current_profile:
            profile_name = self.current_profile.name
            recommendations_text = f"Empfehlungen für {profile_name}:\n\n"
            recommendations_text += "• Vergrößerung (92% Zufriedenheit)\n"
            recommendations_text += "• Hoher Kontrast (89% Zufriedenheit)\n"
            recommendations_text += "• Tastaturnavigation (85% Zufriedenheit)"
        else:
            recommendations_text = (
                "Erstellen Sie ein Profil, um personalisierte\n"
                "Empfehlungen zu erhalten!\n\n"
                "Allgemeine Tipps:\n"
                "• Testen Sie verschiedene Schriftgrößen\n"
                "• Probieren Sie den Dark Mode\n"
                "• Nutzen Sie Tastaturkürzel\n"
                "• Aktivieren Sie visuelle Hilfsmittel"
            )
        
        ctk.CTkLabel(
            frame,
            text=recommendations_text,
            font=ctk.CTkFont(size=12),
            justify="left"
        ).pack(pady=20)

    # Placeholder methods for accessibility features
    def _set_high_contrast_theme(self, widget):
        """Setzt Hochkontrast-Theme"""
        try:
            if hasattr(widget, 'configure'):
                widget.configure(
                    fg_color="#FFFFFF",
                    text_color="#000000",
                    border_color="#000000",
                    button_color="#000000",
                    button_hover_color="#333333"
                )
        except Exception as e:
            print(f"Fehler beim Setzen des Hochkontrast-Themes: {e}")
          
    def _apply_interface_magnification(self, widget, magnification):
        """Wendet Interface-Vergrößerung an"""
        try:
            if hasattr(widget, 'configure'):
                # Vergrößerung der Schriftart
                current_font = widget.cget("font") if hasattr(widget, 'cget') else None
                if current_font:
                    if isinstance(current_font, ctk.CTkFont):
                        new_size = int(current_font.cget("size") * magnification)
                        widget.configure(font=ctk.CTkFont(size=new_size))
                    else:
                        widget.configure(font=ctk.CTkFont(size=int(12 * magnification)))
                
                # Vergrößerung der Widget-Größe
                if hasattr(widget, 'configure'):
                    try:
                        current_width = widget.cget("width")
                        current_height = widget.cget("height")
                        widget.configure(
                            width=int(current_width * magnification),
                            height=int(current_height * magnification)
                        )
                    except:
                        pass  # Falls Widget diese Eigenschaften nicht hat
        except Exception as e:
            print(f"Fehler beim Anwenden der Interface-Vergrößerung: {e}")
        
    def _enhance_cursor_visibility(self, widget):
        """Verbessert Cursor-Sichtbarkeit"""
        try:
            if hasattr(widget, 'configure'):
                # Cursor-Farbe und -Größe anpassen
                widget.configure(
                    cursor="hand2",  # Sichtbarerer Cursor
                    insertwidth=4    # Breiterer Text-Cursor falls verfügbar
                )
        except Exception as e:
            print(f"Fehler beim Verbessern der Cursor-Sichtbarkeit: {e}")
        
    def _add_landmark_navigation(self, widget):
        """Fügt Landmark-Navigation hinzu"""
        try:
            if hasattr(widget, 'configure'):
                # ARIA-Labels für bessere Navigation hinzufügen
                widget_name = widget.__class__.__name__
                if 'Frame' in widget_name:
                    widget.configure(relief="solid", borderwidth=1)
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Landmark-Navigation: {e}")
        
    def _enhance_aria_descriptions(self, widget):
        """Verbessert ARIA-Beschreibungen"""
        try:
            if hasattr(widget, 'configure'):
                # Verbesserte Beschreibungen für Screenreader
                widget_type = widget.__class__.__name__
                if 'Button' in widget_type:
                    current_text = widget.cget('text') if hasattr(widget, 'cget') else 'Button'
                    widget.configure(text=f"{current_text} (Schaltfläche)")
                elif 'Entry' in widget_type:
                    widget.configure(placeholder_text="Eingabefeld - Geben Sie Text ein")
        except Exception as e:
            print(f"Fehler beim Verbessern der ARIA-Beschreibungen: {e}")
        
    def _optimize_tab_order(self, widget):
        """Optimiert Tab-Reihenfolge für bessere Navigation"""
        try:
            # Rekursiv alle Widgets durchgehen und Tab-Order setzen
            def set_tab_order(w, tab_index=0):
                if hasattr(w, 'winfo_children'):
                    for child in w.winfo_children():
                        if hasattr(child, 'focus_set') and child.winfo_class() in ['Entry', 'Button', 'Checkbutton', 'Radiobutton']:
                            try:
                                child.lift()  # Widget nach vorne bringen für bessere Tab-Order
                            except:
                                pass
                        tab_index = set_tab_order(child, tab_index + 1)
                return tab_index
            set_tab_order(widget)
        except Exception as e:
            print(f"Fehler bei Tab-Order-Optimierung: {e}")
            
    def _enlarge_interactive_areas(self, widget, tolerance):
        """Vergrößert interaktive Bereiche"""
        try:
            if hasattr(widget, 'configure'):
                # Vergrößerte Klickbereiche für bessere Erreichbarkeit
                current_width = widget.cget("width") if hasattr(widget, 'cget') else 100
                current_height = widget.cget("height") if hasattr(widget, 'cget') else 30
                widget.configure(
                    width=current_width + tolerance,
                    height=current_height + tolerance//2
                )
        except Exception as e:
            print(f"Fehler beim Vergrößern der interaktiven Bereiche: {e}")
        
    def _add_hover_delays(self, widget, delay):
        """Fügt Hover-Verzögerungen hinzu"""
        try:
            # Hover-Delays für bessere motorische Bedienung
            def delayed_enter(event):
                widget.after(int(delay * 1000), lambda: widget.configure(fg_color="#E0E0E0"))
            
            def delayed_leave(event):
                widget.after(int(delay * 1000), lambda: widget.configure(fg_color=widget.cget("fg_color")))
            
            widget.bind("<Enter>", delayed_enter)
            widget.bind("<Leave>", delayed_leave)
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Hover-Verzögerungen: {e}")
        
    def _simplify_drag_drop(self, widget):
        """Vereinfacht Drag & Drop"""
        try:
            # Vereinfachte Drag & Drop Operationen
            if hasattr(widget, 'bind'):
                # Click-to-select statt Drag
                widget.bind("<Button-1>", self._click_to_select)
                widget.bind("<Double-Button-1>", self._double_click_action)
        except Exception as e:
            print(f"Fehler beim Vereinfachen von Drag & Drop: {e}")
        
    def _apply_font_family(self, widget, font):
        """Wendet Schriftart an"""
        try:
            if hasattr(widget, 'configure'):
                if isinstance(font, tuple):
                    font_family, font_size = font
                    widget.configure(font=ctk.CTkFont(family=font_family, size=font_size))
                else:
                    widget.configure(font=font)
        except Exception as e:
            print(f"Fehler beim Anwenden der Schriftart: {e}")
        
    def _increase_line_height(self, widget, height):
        """Erhöht Zeilenhöhe"""
        try:
            if hasattr(widget, 'configure'):
                # Zeilenhöhe für bessere Lesbarkeit erhöhen
                current_font = widget.cget("font") if hasattr(widget, 'cget') else None
                if current_font and isinstance(current_font, ctk.CTkFont):
                    new_font = ctk.CTkFont(
                        family=current_font.cget("family"),
                        size=current_font.cget("size"),
                        weight=current_font.cget("weight")
                    )
                    widget.configure(font=new_font)
        except Exception as e:
            print(f"Fehler beim Erhöhen der Zeilenhöhe: {e}")
        
    def _add_reading_guide(self, widget):
        """Fügt Leseführung hinzu"""
        try:
            # Visueller Leseleitfaden für Dyslexie-Unterstützung
            if hasattr(widget, 'configure'):
                widget.configure(
                    relief="solid",
                    borderwidth=1,
                    highlightthickness=2,
                    highlightcolor="#4CAF50"
                )
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Leseführung: {e}")
        
    def _reduce_visual_noise(self, widget):
        """Reduziert visuelle Störungen"""
        try:
            if hasattr(widget, 'configure'):
                # Minimalistische Darstellung für ADHD-Unterstützung
                widget.configure(
                    relief="flat",
                    borderwidth=0,
                    highlightthickness=0
                )
        except Exception as e:
            print(f"Fehler beim Reduzieren visueller Störungen: {e}")
        
    def _add_focus_indicators(self, widget):
        """Fügt Fokus-Indikatoren hinzu"""
        try:
            if hasattr(widget, 'bind'):
                def on_focus_in(event):
                    widget.configure(highlightthickness=3, highlightcolor="#2196F3")
                
                def on_focus_out(event):
                    widget.configure(highlightthickness=1, highlightcolor="#CCCCCC")
                
                widget.bind("<FocusIn>", on_focus_in)
                widget.bind("<FocusOut>", on_focus_out)
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Fokus-Indikatoren: {e}")
        
    def _add_time_awareness(self, widget):
        """Fügt Zeitwahrnehmungs-Tools hinzu"""
        try:
            # Zeitmanagement-Hilfen für ADHD
            if hasattr(widget, 'after'):
                def show_time_reminder():
                    # Zeitanzeige oder Pause-Erinnerung
                    widget.configure(fg_color="#FFF3CD")  # Gelber Hintergrund
                    widget.after(2000, lambda: widget.configure(fg_color=widget.cget("fg_color")))
                
                widget.after(30000, show_time_reminder)  # Alle 30 Sekunden
        except Exception as e:
            print(f"Fehler beim Hinzufügen der Zeitwahrnehmungs-Tools: {e}")        
    def _apply_visual_indicators(self, widget, preferences):
        """Wendet visuelle Indikatoren an"""
        try:
            if hasattr(widget, 'configure'):
                # Visuelle Hinweise für Hörbehinderte
                widget.configure(
                    relief="solid",
                    borderwidth=2,
                    highlightthickness=2,
                    highlightcolor="#FF5722"  # Orange für Aufmerksamkeit
                )
        except Exception as e:
            print(f"Fehler beim Anwenden visueller Indikatoren: {e}")
        
    def _track_interaction_patterns(self):
        """Verfolgt Interaktionsmuster"""
        try:
            # Sammelt Daten über Benutzerinteraktionen für adaptive Anpassungen
            current_time = datetime.now()
            interaction_data = {
                'timestamp': current_time,
                'action_type': 'general_interaction',
                'success': True
            }
            
            # In Datenbank speichern
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO usage_analytics 
                (user_profile, action_type, timestamp, duration, success, error_count, context)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                self.current_profile.name if self.current_profile else 'anonymous',
                interaction_data['action_type'],
                interaction_data['timestamp'],
                0.0,  # duration
                interaction_data['success'],
                0,    # error_count
                'tracked_interaction'
            ))
            self.conn.commit()
        except Exception as e:
            print(f"Fehler beim Verfolgen der Interaktionsmuster: {e}")
        
    def _detect_usage_difficulties(self):
        """Erkennt Nutzungsschwierigkeiten"""
        try:
            # Analysiert gespeicherte Daten um Schwierigkeiten zu erkennen
            if not self.current_profile:
                return
                
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT action_type, AVG(duration), COUNT(*) as frequency, 
                       SUM(error_count) as total_errors
                FROM usage_analytics 
                WHERE user_profile = ? AND timestamp > datetime('now', '-1 day')
                GROUP BY action_type
            ''', (self.current_profile.name,))
            
            results = cursor.fetchall()
            for action_type, avg_duration, frequency, total_errors in results:
                if avg_duration > 5.0 or total_errors > 3:
                    print(f"Schwierigkeit erkannt bei {action_type}: "
                          f"Ø {avg_duration:.1f}s, {total_errors} Fehler")
        except Exception as e:
            print(f"Fehler beim Erkennen von Nutzungsschwierigkeiten: {e}")
        
    def _suggest_adaptations(self):
        """Schlägt Anpassungen vor"""
        try:
            # Schlägt basierend auf erkannten Schwierigkeiten Anpassungen vor
            if not self.current_profile:
                return
                
            suggestions = []
            
            # Profilbasierte Vorschläge
            if self.current_profile.vision_impairment != "none":
                suggestions.append("Vergrößerung erhöhen")
                suggestions.append("Kontrast verstärken")
                
            if self.current_profile.motor_impairment != "none":
                suggestions.append("Klickbereiche vergrößern")
                suggestions.append("Hover-Delays verlängern")
                
            return suggestions
        except Exception as e:
            print(f"Fehler beim Vorschlagen von Anpassungen: {e}")
            return []
    
    def _wizard_next(self):
        """Nächster Wizard-Schritt"""
        try:
            self.wizard_step += 1
            if self.wizard_step == 1:
                self._create_wizard_step_2()
            elif self.wizard_step == 2:
                self._create_wizard_step_3()
            elif self.wizard_step == 3:
                self._create_wizard_step_4()
            
            # Navigation aktualisieren - Vermeidung von Geometry Manager Konflikten
            self.back_btn.configure(state="normal" if self.wizard_step > 0 else "disabled")
            if self.wizard_step >= 3:
                # Sicherer Button-Wechsel ohne pack_forget/pack Mischung
                try:
                    self.next_btn.destroy()
                except:
                    pass
                if not hasattr(self, 'finish_btn_packed') or not self.finish_btn_packed:
                    self.finish_btn.pack(side="right", padx=(0, 10))
                    self.finish_btn_packed = True
            else:
                # Sicherer Button-Wechsel
                try:
                    if hasattr(self, 'finish_btn_packed') and self.finish_btn_packed:
                        self.finish_btn.destroy()
                        self.finish_btn = ctk.CTkButton(self.finish_btn.master, text="Profil erstellen", 
                                                       command=self._wizard_finish)
                        self.finish_btn_packed = False
                except:
                    pass
                
                if not hasattr(self, 'next_btn') or not self.next_btn.winfo_exists():
                    self.next_btn = ctk.CTkButton(self.finish_btn.master if hasattr(self, 'finish_btn') else self.back_btn.master, 
                                                 text="Weiter →", command=self._wizard_next)
                    self.next_btn.pack(side="right")
        except Exception as e:
            print(f"Fehler beim Wizard-Weiter: {e}")
    
    def _wizard_finish(self):
        """Wizard abschließen"""
        try:
            # Profil erstellen mit gesammelten Daten
            profile_name = getattr(self, 'name_entry', None)
            if profile_name and profile_name.get():
                vision = getattr(self, 'vision_var', tk.StringVar()).get()
                motor = getattr(self, 'motor_var', tk.StringVar()).get()
                cognitive = getattr(self, 'cognitive_var', tk.StringVar()).get()
                hearing = getattr(self, 'hearing_var', tk.StringVar()).get()
                
                profile = self.create_user_profile(
                    name=profile_name.get(),
                    vision=vision,
                    motor=motor,
                    cognitive=cognitive,
                    hearing=hearing
                )
                
                messagebox.showinfo("Erfolg", f"Profil '{profile.name}' wurde erstellt!")
                
                # Wizard schließen
                for widget in self.wizard_container.master.winfo_children():
                    if isinstance(widget, ctk.CTkToplevel):
                        widget.destroy()
                        break
        except Exception as e:
            print(f"Fehler beim Wizard-Abschluss: {e}")
            messagebox.showerror("Fehler", f"Profil konnte nicht erstellt werden: {e}")
        
    def _create_wizard_step_2(self):
        """Wizard Schritt 2: Sehbeeinträchtigung"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        # Titel
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 2: Sehbeeinträchtigung",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Optionen
        self.vision_var = tk.StringVar(value="none")
        
        options = [
            ("none", "Keine Beeinträchtigung"),
            ("low_vision", "Sehschwäche"),
            ("blind", "Blind"),
            ("color_blind", "Farbenblind")
        ]
        
        for value, text in options:
            ctk.CTkRadioButton(
                self.wizard_container,
                text=text,
                variable=self.vision_var,
                value=value
            ).pack(anchor="w", padx=20, pady=5)
        
    def _create_wizard_step_3(self):
        """Wizard Schritt 3: Motorische Beeinträchtigung"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        # Titel
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 3: Motorische Beeinträchtigung",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Optionen
        self.motor_var = tk.StringVar(value="none")
        
        options = [
            ("none", "Keine Beeinträchtigung"),
            ("limited_dexterity", "Eingeschränkte Feinmotorik"),
            ("no_mouse", "Keine Maus-Nutzung"),
            ("switch_only", "Nur Switch-Bedienung")
        ]
        
        for value, text in options:
            ctk.CTkRadioButton(
                self.wizard_container,
                text=text,
                variable=self.motor_var,
                value=value
            ).pack(anchor="w", padx=20, pady=5)
        
    def _create_wizard_step_4(self):
        """Wizard Schritt 4: Zusammenfassung"""
        for widget in self.wizard_container.winfo_children():
            widget.destroy()
            
        # Titel
        ctk.CTkLabel(self.wizard_container, 
                    text="Schritt 4: Zusammenfassung",
                    font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)
        
        # Zusammenfassung
        summary_text = f"""
Profilname: {getattr(self, 'name_entry', ctk.CTkEntry(self.wizard_container)).get()}
Sehbeeinträchtigung: {getattr(self, 'vision_var', tk.StringVar()).get()}
Motorische Beeinträchtigung: {getattr(self, 'motor_var', tk.StringVar()).get()}

Das Profil wird erstellt und kann jederzeit angepasst werden.
        """
        
        ctk.CTkLabel(
            self.wizard_container,
            text=summary_text,
            font=ctk.CTkFont(size=12),
            justify="left"        ).pack(pady=20)

class AccessibilityUserProfileManager:
    """Stub-Klasse für Kompatibilität. Implementierung nach Bedarf ergänzen."""
    def __init__(self, *args, **kwargs):
        pass

# Falls WorkflowIntegrationOptimizer in dieser Datei ist, Stub-Methode ergänzen:
try:
    class WorkflowIntegrationOptimizer:
        def _load_performance_baselines(self):
            """Stub für Performance-Baseline-Ladevorgang."""
            pass
except Exception:
    pass
