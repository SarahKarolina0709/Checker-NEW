#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modern Upload Component für Checker Pro Suite
Verbesserte Upload-UX mit Progress-Anzeige, Drag & Drop und Toast-Nachrichten
"""

import customtkinter as ctk
from ui_theme import UITheme
import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
from typing import List, Callable, Optional

class ModernUploadZone(ctk.CTkFrame):
    """Moderne Upload-Zone mit verbesserter UX."""
    
    def __init__(self, parent, upload_callback: Callable[[List[str]], None], **kwargs):
        """
        Initialisiert die moderne Upload-Zone.
        
        Args:
            parent: Parent-Widget
            upload_callback: Callback-Funktion für erfolgreiche Uploads
        """
        # Theme-Styling anwenden
        style = UITheme.create_frame_style('surface')
        style.update(kwargs)
        super().__init__(parent, **style)
        
        self.upload_callback = upload_callback
        self.is_uploading = False
        self.uploaded_files = []
        
        self._create_upload_interface()
        self._bind_drag_drop_events()
    
    def _create_upload_interface(self):
        """Erstellt die Upload-Benutzeroberfläche."""
        # Hauptcontainer
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('md'))
        
        # Upload-Icon und Text
        self._create_upload_header(main_container)
        
        # Haupt-Upload-Button
        self._create_main_upload_button(main_container)
        
        # Alternative Upload-Methoden
        self._create_alternative_methods(main_container)
        
        # Progress-Anzeige (initial versteckt)
        self._create_progress_indicator(main_container)
        
        # Status-Anzeige
        self._create_status_display(main_container)
    
    def _create_upload_header(self, parent):
        """Erstellt Header mit Icon und Beschreibung."""
        header_frame = ctk.CTkFrame(parent, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, UITheme.get_spacing('md')))
        
        # Upload-Icon
        self.upload_icon = ctk.CTkLabel(
            header_frame,
            text="📁",
            font=UITheme.get_font('icon_large'),
            text_color=UITheme.get_color('primary')
        )
        self.upload_icon.pack(pady=(0, UITheme.get_spacing('sm')))
        
        # Beschreibungstext
        self.description_label = ctk.CTkLabel(
            header_frame,
            text="📁 Dateien hochladen\n\nDateien hier ablegen oder Button klicken",
            font=UITheme.get_font('body'),
            text_color=UITheme.get_color('text_secondary'),
            justify="center"
        )
        self.description_label.pack()
    
    def _create_main_upload_button(self, parent):
        """Erstellt den Haupt-Upload-Button."""
        self.main_upload_btn = ctk.CTkButton(
            parent,
            text="📂 DATEIEN AUSWÄHLEN",
            height=50,
            **UITheme.create_button_style('primary'),
            command=self._open_file_dialog
        )
        self.main_upload_btn.pack(fill="x", pady=UITheme.get_spacing('md'))
    
    def _create_alternative_methods(self, parent):
        """Erstellt alternative Upload-Methoden."""
        alt_frame = ctk.CTkFrame(parent, fg_color="transparent")
        alt_frame.pack(fill="x", pady=UITheme.get_spacing('sm'))
        
        # Zwischenablage-Button
        clipboard_btn = ctk.CTkButton(
            alt_frame,
            text="📋 Zwischenablage",
            width=120,
            height=35,
            **UITheme.create_button_style('purple'),
            command=self._upload_from_clipboard
        )
        clipboard_btn.pack(side="left", padx=(0, UITheme.get_spacing('sm')))
        
        # Ordner-Button
        folder_btn = ctk.CTkButton(
            alt_frame,
            text="📁 Ordner",
            width=80,
            height=35,
            **UITheme.create_button_style('secondary'),
            command=self._select_folder
        )
        folder_btn.pack(side="left", padx=(0, UITheme.get_spacing('sm')))
        
        # Hilfe-Button
        help_btn = ctk.CTkButton(
            alt_frame,
            text="❓",
            width=40,
            height=35,
            **UITheme.create_button_style('neutral'),
            command=self._show_upload_help
        )
        help_btn.pack(side="right")
    
    def _create_progress_indicator(self, parent):
        """Erstellt Progress-Anzeige."""
        self.progress_frame = ctk.CTkFrame(parent, **UITheme.create_frame_style('surface'))
        # Initial versteckt
        
        # Progress-Bar
        self.progress_bar = ctk.CTkProgressBar(
            self.progress_frame,
            progress_color=UITheme.get_color('primary'),
            fg_color=UITheme.get_color('border')
        )
        self.progress_bar.pack(fill="x", padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('sm'))
        
        # Progress-Text
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="",
            font=UITheme.get_font('caption'),
            text_color=UITheme.get_color('text_secondary')
        )
        self.progress_label.pack(pady=(0, UITheme.get_spacing('sm')))
    
    def _create_status_display(self, parent):
        """Erstellt Status-Anzeige."""
        self.status_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.status_frame.pack(fill="x", pady=UITheme.get_spacing('sm'))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="💡 Tipp: Drag & Drop funktioniert auch!",
            font=UITheme.get_font('caption'),
            text_color=UITheme.get_color('text_muted')
        )
        self.status_label.pack()
    
    def _bind_drag_drop_events(self):
        """Bindet Drag & Drop Events."""
        # Maus-Events für visuelles Feedback
        self.bind("<Enter>", self._on_mouse_enter)
        self.bind("<Leave>", self._on_mouse_leave)
        
        # Keyboard-Shortcuts werden über das Hauptfenster verwaltet
        # Keine bind_all Verwendung für CustomTkinter-Kompatibilität
        print("ℹ️ Keyboard-Shortcuts werden über Hauptanwendung verwaltet")
    
    def _on_mouse_enter(self, event):
        """Mouse-Enter Event."""
        if not self.is_uploading:
            self.configure(border_color=UITheme.get_color('primary'))
    
    def _on_mouse_leave(self, event):
        """Mouse-Leave Event."""
        if not self.is_uploading:
            self.configure(border_color=UITheme.get_color('border'))
    
    def _open_file_dialog(self):
        """Öffnet Datei-Dialog."""
        if self.is_uploading:
            return
        
        try:
            files = filedialog.askopenfilenames(
                title="Dateien für Upload auswählen",
                filetypes=[
                    ("Alle unterstützten", "*.pdf;*.docx;*.xlsx;*.pptx;*.txt;*.png;*.jpg;*.jpeg"),
                    ("PDF Dateien", "*.pdf"),
                    ("Word Dateien", "*.docx"),
                    ("Excel Dateien", "*.xlsx"),
                    ("PowerPoint", "*.pptx"),
                    ("Text Dateien", "*.txt"),
                    ("Bilder", "*.png;*.jpg;*.jpeg"),
                    ("Alle Dateien", "*.*")
                ]
            )
            
            if files:
                self._process_files(list(files))
        except Exception as e:
            self._show_error(f"Fehler beim Öffnen des Datei-Dialogs: {e}")
    
    def _upload_from_clipboard(self):
        """Upload aus Zwischenablage."""
        if self.is_uploading:
            return
        
        try:
            # Hier würde die Zwischenablage-Logik implementiert
            self._update_status("📋 Zwischenablage wird geprüft...", "info")
            # Placeholder - echte Implementierung folgt
            self._update_status("💡 Tipp: Drag & Drop funktioniert auch!", "default")
        except Exception as e:
            self._show_error(f"Fehler beim Lesen der Zwischenablage: {e}")
    
    def _select_folder(self):
        """Ordner-Auswahl."""
        if self.is_uploading:
            return
        
        try:
            folder = filedialog.askdirectory(title="Ordner für Upload auswählen")
            if folder:
                # Alle unterstützten Dateien im Ordner finden
                supported_files = []
                for root, dirs, files in os.walk(folder):
                    for file in files:
                        if any(file.lower().endswith(ext) for ext in ['.pdf', '.docx', '.xlsx', '.pptx', '.txt', '.png', '.jpg', '.jpeg']):
                            supported_files.append(os.path.join(root, file))
                
                if supported_files:
                    result = messagebox.askyesno(
                        "Ordner-Upload",
                        f"📁 {len(supported_files)} unterstützte Datei(en) im Ordner gefunden.\n\nAlle Dateien hochladen?"
                    )
                    if result:
                        self._process_files(supported_files)
                else:
                    messagebox.showwarning("Keine Dateien", "Keine unterstützten Dateien im ausgewählten Ordner gefunden.")
        except Exception as e:
            self._show_error(f"Fehler beim Ordner-Upload: {e}")
    
    def _show_upload_help(self):
        """Zeigt Upload-Hilfe."""
        help_text = """
🎯 UPLOAD-METHODEN:

1️⃣ HAUPTBUTTON (Empfohlen):
   • Klicken Sie "DATEIEN AUSWÄHLEN"
   • Wählen Sie eine oder mehrere Dateien
   • Bestätigen Sie die Auswahl

2️⃣ ORDNER-UPLOAD:
   • Klicken Sie "Ordner"
   • Wählen Sie einen Ordner
   • Alle unterstützten Dateien werden gefunden

3️⃣ ZWISCHENABLAGE:
   • Kopieren Sie Dateien im Explorer (Strg+C)
   • Klicken Sie "Zwischenablage"
   • Bestätigen Sie den Upload

4️⃣ DRAG & DROP:
   • Ziehen Sie Dateien direkt in diese Zone
   • Lassen Sie die Dateien los

✅ UNTERSTÜTZTE FORMATE:
PDF, Word, Excel, PowerPoint, Text, PNG, JPG

⚠️ WICHTIG:
Wählen Sie zuerst einen Kunden aus!
        """
        messagebox.showinfo("Upload-Hilfe", help_text)
    
    def _process_files(self, files: List[str]):
        """Verarbeitet ausgewählte Dateien."""
        if not files or self.is_uploading:
            return
        
        # Upload in separatem Thread für bessere UX
        upload_thread = threading.Thread(target=self._upload_files_async, args=(files,))
        upload_thread.daemon = True
        upload_thread.start()
    
    def _upload_files_async(self, files: List[str]):
        """Asynchroner Upload mit Progress-Anzeige."""
        try:
            self.is_uploading = True
            self._show_progress()
            
            # Upload simulieren mit Progress
            total_files = len(files)
            for i, file_path in enumerate(files):
                if not os.path.exists(file_path):
                    continue
                
                # Progress aktualisieren
                progress = (i + 1) / total_files
                self._update_progress(progress, f"Lade hoch: {os.path.basename(file_path)} ({i+1}/{total_files})")
                
                # Upload-Simulation (200ms pro Datei)
                time.sleep(0.2)
            
            # Upload abschließen
            self._upload_complete(files)
            
        except Exception as e:
            self._upload_failed(str(e))
        finally:
            self.is_uploading = False
            self._hide_progress()
    
    def _show_progress(self):
        """Zeigt Progress-Anzeige."""
        self.progress_frame.pack(fill="x", pady=UITheme.get_spacing('md'))
        self.main_upload_btn.configure(state="disabled", text="🔄 Wird hochgeladen...")
        self._update_status("📤 Upload läuft...", "info")
    
    def _hide_progress(self):
        """Versteckt Progress-Anzeige."""
        self.progress_frame.pack_forget()
        self.main_upload_btn.configure(state="normal", text="📂 DATEIEN AUSWÄHLEN")
    
    def _update_progress(self, progress: float, text: str):
        """Aktualisiert Progress-Bar und -Text."""
        def update():
            self.progress_bar.set(progress)
            self.progress_label.configure(text=text)
        
        self.after(0, update)
    
    def _upload_complete(self, files: List[str]):
        """Upload erfolgreich abgeschlossen."""
        def complete():
            self.uploaded_files.extend(files)
            self._update_status(f"✅ {len(files)} Datei(en) erfolgreich hochgeladen!", "success")
            if self.upload_callback:
                self.upload_callback(files)
        
        self.after(0, complete)
    
    def _upload_failed(self, error: str):
        """Upload fehlgeschlagen."""
        def failed():
            self._update_status(f"❌ Upload fehlgeschlagen: {error}", "error")
        
        self.after(0, failed)
    
    def _update_status(self, text: str, status_type: str = "default"):
        """Aktualisiert Status-Text."""
        color_map = {
            "default": UITheme.get_color('text_muted'),
            "info": UITheme.get_color('info'),
            "success": UITheme.get_color('success'),
            "error": UITheme.get_color('error'),
            "warning": UITheme.get_color('warning')
        }
        
        color = color_map.get(status_type, color_map["default"])
        self.status_label.configure(text=text, text_color=color)
        
        # Status nach 5 Sekunden zurücksetzen (außer bei Fehlern)
        if status_type != "error":
            self.after(5000, lambda: self._update_status("💡 Tipp: Drag & Drop funktioniert auch!", "default"))
    
    def _show_error(self, message: str):
        """Zeigt Fehlermeldung."""
        self._update_status(f"❌ {message}", "error")
        messagebox.showerror("Upload-Fehler", message)
    
    def get_uploaded_files(self) -> List[str]:
        """Gibt Liste der hochgeladenen Dateien zurück."""
        return self.uploaded_files.copy()
    
    def clear_uploaded_files(self):
        """Löscht Liste der hochgeladenen Dateien."""
        self.uploaded_files.clear()
        self._update_status("🗑️ Upload-Liste geleert", "info")

# === TOAST-NOTIFICATION SYSTEM ===

class ToastNotification(ctk.CTkToplevel):
    """Toast-Benachrichtigung für bessere UX."""
    
    def __init__(self, parent, message: str, notification_type: str = "info", duration: int = 3000):
        super().__init__(parent)
        
        self.message = message
        self.notification_type = notification_type
        self.duration = duration
        
        self._setup_window()
        self._create_content()
        self._position_window()
        self._auto_dismiss()
    
    def _setup_window(self):
        """Konfiguriert das Toast-Fenster."""
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.configure(fg_color=UITheme.get_color('surface'))
    
    def _create_content(self):
        """Erstellt Toast-Inhalt."""
        # Icon basierend auf Typ
        icon_map = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        # Farbe basierend auf Typ
        color_map = {
            "info": UITheme.get_color('info'),
            "success": UITheme.get_color('success'),
            "warning": UITheme.get_color('warning'),
            "error": UITheme.get_color('error')
        }
        
        icon = icon_map.get(self.notification_type, "ℹ️")
        color = color_map.get(self.notification_type, UITheme.get_color('info'))
        
        # Container
        container = ctk.CTkFrame(
            self,
            fg_color=color,
            corner_radius=UITheme.get_radius('medium'),
            border_width=1,
            border_color=UITheme.get_color('border')
        )
        container.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Inhalt
        content = ctk.CTkFrame(container, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=UITheme.get_spacing('md'), pady=UITheme.get_spacing('sm'))
        
        # Icon und Text
        label = ctk.CTkLabel(
            content,
            text=f"{icon} {self.message}",
            font=UITheme.get_font('body_small'),
            text_color=UITheme.get_color('text_inverse')
        )
        label.pack()
    
    def _position_window(self):
        """Positioniert Toast am oberen rechten Bildschirmrand."""
        self.update_idletasks()
        
        # Fenstergröße
        width = self.winfo_reqwidth()
        height = self.winfo_reqheight()
        
        # Bildschirmgröße
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Position berechnen (oberer rechter Rand)
        x = screen_width - width - 20
        y = 50
        
        self.geometry(f"{width}x{height}+{x}+{y}")
    
    def _auto_dismiss(self):
        """Automatisches Ausblenden nach festgelegter Zeit."""
        self.after(self.duration, self.destroy)

def show_toast(parent, message: str, notification_type: str = "info", duration: int = 3000):
    """Zeigt eine Toast-Benachrichtigung."""
    try:
        toast = ToastNotification(parent, message, notification_type, duration)
        return toast
    except Exception as e:
        print(f"Toast-Fehler: {e}")
        return None
