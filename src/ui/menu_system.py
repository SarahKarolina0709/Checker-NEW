"""
Menu System Module
=================

Contains all menu-related functionality extracted from checker_app.py
"""

import tkinter as tk
from tkinter import messagebox, filedialog
import os


class MenuSystem:
    """Handles all application menus and menu actions."""
    
    def __init__(self, app):
        """Initialize menu system with reference to main app."""
        self.app = app
        self.logger = getattr(app, 'logger', None)
        self.error_monitor = getattr(app, 'error_monitor', None)
        self.notification_center = getattr(app, 'notification_center', None)
        self.workflow_router = getattr(app, 'workflow_router', None)
        
    def show_file_menu(self):
        """Shows the file menu."""
        try:
            menu = tk.Menu(self.app.root, tearoff=0)
            menu.add_command(label="Neues Projekt", command=self.create_new_project)
            menu.add_command(label="Projekt öffnen", command=self.open_project)
            menu.add_command(label="Projekt speichern", command=self.save_project)
            menu.add_separator()
            menu.add_command(label="Dateien hochladen", command=self.show_upload_dialog)
            menu.add_command(label="Upload-Manager", command=self.show_upload_manager)
            menu.add_separator()
            menu.add_command(label="Beenden", command=self.exit_application)
            
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            if self.error_monitor:
                self.error_monitor.handle_error(e, "File Menu", "warning")

    def show_customer_menu(self):
        """
        Zeigt die moderne Kundenverwaltungsschnittstelle an.
        
        Optimierte Version mit zentralisiertem Logging und 
        sauberer Fehlerbehandlung ohne redundante Fallbacks.
        """
        try:
            if self.logger:
                self.logger.info("Öffne Kundenverwaltung")
            
            # Validiere grundlegende App-Komponenten
            if not hasattr(self.app, 'root') or not self.app.root:
                raise RuntimeError("App ist nicht korrekt initialisiert")
            
            # Verwende ViewStack wenn verfügbar, sonst direkte Anzeige
            if hasattr(self.app, 'views') and self.app.views:
                self.app._show_customer_menu_via_viewstack()
            else:
                if self.logger:
                    self.logger.warning("ViewStack nicht verfügbar - verwende direkte Anzeige")
                self.app._show_modern_customer_gui_optimized()
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Fehler beim Öffnen der Kundenverwaltung: {e}")
            if self.notification_center:
                self.notification_center.show_error(
                    "Kundenverwaltung", 
                    "Fehler beim Laden der Kundenverwaltung"
                )

    def show_workflow_menu(self):
        """Shows the workflow menu."""
        try:
            menu = tk.Menu(self.app.root, tearoff=0)
            menu.add_command(label="Angebotsanalyse", 
                           command=lambda: self._start_workflow("angebots_workflow"))
            menu.add_command(label="Dateiprüfung", 
                           command=lambda: self._start_workflow("pruefung_workflow"))
            menu.add_command(label="Finalisierung", 
                           command=lambda: self._start_workflow("finalisierung_workflow"))
            menu.add_command(label="Projektübersicht", 
                           command=lambda: self._start_workflow("projekt_workflow"))
            
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            if self.error_monitor:
                self.error_monitor.handle_error(e, "Workflow Menu", "warning")

    def show_tools_menu(self):
        """Shows the tools menu."""
        try:
            menu = tk.Menu(self.app.root, tearoff=0)
            menu.add_command(label="Einstellungen", command=self.show_settings)
            menu.add_command(label="Theme umschalten", command=self.toggle_theme)
            menu.add_separator()
            menu.add_command(label="Debug-Modus", command=self.toggle_debug_mode)
            menu.add_command(label="Systeminfo", command=self.show_system_info)
            menu.add_separator()
            menu.add_command(label="Icon-Cache leeren", command=self.clear_icon_cache)
            menu.add_command(label="Garbage Collection", command=self.force_gc)
            menu.add_command(label="Memory Debug", command=self.show_memory_debug_menu)
            
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            if self.error_monitor:
                self.error_monitor.handle_error(e, "Tools Menu", "warning")

    def show_help_menu(self):
        """Shows the help menu."""
        try:
            menu = tk.Menu(self.app.root, tearoff=0)
            menu.add_command(label="Hilfe", command=self.show_help)
            menu.add_command(label="Tastaturkürzel", command=self.show_keyboard_shortcuts)
            menu.add_separator()
            menu.add_command(label="Über", command=self.show_about)
            
            x, y = self.app.root.winfo_pointerxy()
            menu.post(x, y)
            
        except Exception as e:
            if self.error_monitor:
                self.error_monitor.handle_error(e, "Help Menu", "warning")

    # ===== MENU ACTION METHODS =====
    
    def create_new_project(self):
        """Creates a new project."""
        messagebox.showinfo("Neues Projekt", "Funktion wird in Kürze verfügbar sein.")

    def open_project(self):
        """Opens an existing project."""
        try:
            file_path = filedialog.askopenfilename(
                title="Projekt öffnen",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            if file_path and self.notification_center:
                self.notification_center.show_notification(
                    f"Projekt wird geladen: {os.path.basename(file_path)}", 
                    "info"
                )
        except Exception as e:
            if self.error_monitor:
                self.error_monitor.handle_error(e, "Open Project", "error")

    def save_project(self):
        """Saves the current project."""
        if self.notification_center:
            self.notification_center.show_notification("Projekt wurde gespeichert.", "success")

    def exit_application(self):
        """Exits the application."""
        self.app.on_closing()
    
    def show_upload_dialog(self):
        """Shows the upload dialog."""
        if hasattr(self.app, 'show_upload_dialog'):
            self.app.show_upload_dialog()
    
    def show_upload_manager(self):
        """Shows the upload manager."""
        if hasattr(self.app, 'show_upload_manager'):
            self.app.show_upload_manager()
    
    def show_settings(self):
        """Shows settings dialog."""
        if hasattr(self.app, 'show_settings'):
            self.app.show_settings()
    
    def toggle_theme(self):
        """Toggles application theme."""
        if hasattr(self.app, 'toggle_theme'):
            self.app.toggle_theme()
    
    def toggle_debug_mode(self):
        """Toggles debug mode."""
        if hasattr(self.app, 'toggle_debug_mode'):
            self.app.toggle_debug_mode()
    
    def show_system_info(self):
        """Shows system information."""
        if hasattr(self.app, 'show_system_info'):
            self.app.show_system_info()
    
    def clear_icon_cache(self):
        """Clears icon cache."""
        if hasattr(self.app, 'clear_icon_cache'):
            self.app.clear_icon_cache()
    
    def force_gc(self):
        """Forces garbage collection."""
        if hasattr(self.app, 'force_gc'):
            self.app.force_gc()
    
    def show_memory_debug_menu(self):
        """Shows memory debug menu."""
        if hasattr(self.app, 'show_memory_debug_menu'):
            self.app.show_memory_debug_menu()
    
    def show_help(self):
        """Shows help dialog."""
        if hasattr(self.app, 'show_help'):
            self.app.show_help()
        else:
            messagebox.showinfo("Hilfe", "Hilfe wird in Kürze verfügbar sein.")
    
    def show_keyboard_shortcuts(self):
        """Shows keyboard shortcuts."""
        shortcuts_text = """
Tastaturkürzel:

Strg+N  - Neues Projekt
Strg+O  - Projekt öffnen
Strg+S  - Projekt speichern
Strg+U  - Upload-Dialog
Strg+Q  - Beenden

F1      - Hilfe
F5      - Aktualisieren
F11     - Vollbild
"""
        messagebox.showinfo("Tastaturkürzel", shortcuts_text)
    
    def show_about(self):
        """Shows about dialog."""
        if hasattr(self.app, 'show_about'):
            self.app.show_about()
        else:
            messagebox.showinfo("Über", "Checker Application v2.0")
    
    # ===== PRIVATE METHODS =====
    
    def _start_workflow(self, workflow_name):
        """Starts a workflow via workflow router."""
        if self.workflow_router:
            self.workflow_router.start_workflow(workflow_name)
        else:
            messagebox.showinfo("Workflow", f"Workflow '{workflow_name}' wird gestartet...")
