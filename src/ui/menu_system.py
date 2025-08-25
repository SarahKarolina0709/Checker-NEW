"""
Menu System Module
=================

Contains all menu-related functionality extracted from checker_app.py
"""

import os

from tkinter import messagebox, filedialog
import tkinter as tk
try:
    import customtkinter as ctk
except Exception:
    ctk = None  # Fallback safeguard; CTk-Methoden prüfen Verfügbarkeit

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

    # ===== CustomTkinter CTk Dialog Menus (Design-System konform) =====

    def show_file_menu_ctk(self):
        """Zeigt das Datei-Menü als CTk Dialog (Design-System der App)."""
        if not ctk:
            return self.show_file_menu()
        try:
            dialog = ctk.CTkToplevel(self.app)
            dialog.title("Datei-Menü")
            dialog.geometry("300x200")
            dialog.transient(self.app)
            dialog.grab_set()
            dialog.resizable(False, False)

            # Zentrierung über App-Helfer wenn vorhanden
            if hasattr(self.app, "_center_dialog"):
                self.app._center_dialog(dialog, 300, 200)

            menu_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            menu_frame.pack(fill="both", expand=True, padx=20, pady=20)

            options = [
                ("Arbeitsverzeichnis öffnen", getattr(self.app, "_open_workspace_folder", None)),
                ("Projekt exportieren", getattr(self.app, "_export_project", None)),
                ("Anwendung neu starten", getattr(self.app, "_restart_application", None)),
                ("Beenden", getattr(self.app, "_exit_application", None)),
            ]

            for text, command in options:
                if not callable(command):
                    continue
                btn = ctk.CTkButton(
                    menu_frame,
                    text=text,
                    font=ctk.CTkFont(*self.app.get_typography("caption")) if hasattr(self.app, "get_typography") else None,
                    fg_color=self.app.get_color('anthracite_600') if hasattr(self.app, 'get_color') else None,
                    hover_color=self.app.get_color('anthracite_700') if hasattr(self.app, 'get_color') else None,
                    text_color=self.app.get_color('white') if hasattr(self.app, 'get_color') else None,
                    height=35,
                    corner_radius=self.app.get_component_value('borders.radius_md') if hasattr(self.app, 'get_component_value') else 8,
                    command=lambda cmd=command, dlg=dialog: self._execute_menu_command_adapter(cmd, dlg)
                )
                btn.pack(fill="x", pady=(0, 8))
        except Exception as e:
            if self.logger:
                self.logger.error(f"File menu (CTk) error: {e}")

    def show_settings_ctk(self):
        """Zeigt Einstellungen als CTk Dialog (Design-System der App)."""
        if not ctk:
            return self.show_tools_menu()
        try:
            dlg = ctk.CTkToplevel(self.app)
            dlg.title("Einstellungen")
            dlg.geometry("500x400")
            dlg.transient(self.app)
            dlg.grab_set()
            dlg.resizable(False, False)

            if hasattr(self.app, "_center_dialog"):
                self.app._center_dialog(dlg, 500, 400)

            main_frame = ctk.CTkFrame(dlg, fg_color="transparent")
            main_frame.pack(fill="both", expand=True, padx=20, pady=20)

            header_label = ctk.CTkLabel(
                main_frame,
                text="Anwendungseinstellungen",
                font=ctk.CTkFont(*self.app.get_typography("subheading")) if hasattr(self.app, 'get_typography') else None,
                text_color=self.app.get_color('primary') if hasattr(self.app, 'get_color') else None
            )
            header_label.pack(pady=(0, 20))

            path_section = ctk.CTkFrame(
                main_frame,
                fg_color=self.app.get_color('background') if hasattr(self.app, 'get_color') else None,
                border_width=1,
                border_color=self.app.get_color('border') if hasattr(self.app, 'get_color') else None
            )
            path_section.pack(fill="x", pady=(0, 15))

            path_content = ctk.CTkFrame(path_section, fg_color="transparent")
            path_content.pack(fill="x", padx=15, pady=15)

            path_title = ctk.CTkLabel(
                path_content,
                text="Kundenprojekte-Verzeichnis",
                font=ctk.CTkFont(*self.app.get_typography("body_bold")) if hasattr(self.app, 'get_typography') else None,
                text_color=self.app.get_color('text_primary') if hasattr(self.app, 'get_color') else None
            )
            path_title.pack(anchor="w", pady=(0, 10))

            current_path_frame = ctk.CTkFrame(path_content, fg_color="transparent")
            current_path_frame.pack(fill="x", pady=(0, 10))

            ctk.CTkLabel(
                current_path_frame,
                text="Aktueller Pfad:",
                font=ctk.CTkFont(*self.app.get_typography("caption")) if hasattr(self.app, 'get_typography') else None,
                text_color=self.app.get_color('text_secondary') if hasattr(self.app, 'get_color') else None
            ).pack(anchor="w")

            current_text = getattr(self.app, 'projects_base_path', '')
            self.app.current_path_display = ctk.CTkLabel(
                current_path_frame,
                text=current_text,
                font=ctk.CTkFont(*self.app.get_typography("caption")) if hasattr(self.app, 'get_typography') else None,
                text_color=self.app.get_color('primary') if hasattr(self.app, 'get_color') else None,
                fg_color=self.app.get_color('info_light') if hasattr(self.app, 'get_color') else None,
                corner_radius=self.app.get_component_value('borders.radius_sm') if hasattr(self.app, 'get_component_value') else 6,
                padx=10, pady=6
            )
            self.app.current_path_display.pack(fill="x", pady=(5, 0))

            change_btn = ctk.CTkButton(
                path_content,
                text="Verzeichnis ändern",
                font=ctk.CTkFont(*self.app.get_typography("body_bold")) if hasattr(self.app, 'get_typography') else None,
                fg_color=self.app.get_color('primary') if hasattr(self.app, 'get_color') else None,
                hover_color=self.app.get_color('primary_hover') if hasattr(self.app, 'get_color') else None,
                text_color=self.app.get_color('white') if hasattr(self.app, 'get_color') else None,
                height=40,
                corner_radius=self.app.get_component_value('borders.radius_md') if hasattr(self.app, 'get_component_value') else 8,
                command=lambda: getattr(self.app, "_change_projects_path", lambda *_: None)(dlg)
            )
            change_btn.pack(fill="x", pady=(10, 0))

            button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            button_frame.pack(fill="x", pady=(15, 0))

            close_btn = ctk.CTkButton(
                button_frame,
                text="Schließen",
                font=ctk.CTkFont(*self.app.get_typography("body_bold")) if hasattr(self.app, 'get_typography') else None,
                fg_color=self.app.get_color('primary') if hasattr(self.app, 'get_color') else None,
                hover_color=self.app.get_color('primary_hover') if hasattr(self.app, 'get_color') else None,
                text_color=self.app.get_color('white') if hasattr(self.app, 'get_color') else None,
                height=40,
                corner_radius=self.app.get_component_value('borders.radius_md') if hasattr(self.app, 'get_component_value') else 8,
                command=dlg.destroy
            )
            close_btn.pack(side="right")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Settings menu (CTk) error: {e}")

    def show_help_ctk(self):
        """Zeigt Hilfe-Menü als CTk Dialog (Design-System der App)."""
        if not ctk:
            return self.show_help_menu()
        try:
            dlg = ctk.CTkToplevel(self.app)
            dlg.title("Hilfe")
            dlg.geometry("400x300")
            dlg.transient(self.app)
            dlg.grab_set()
            dlg.resizable(False, False)

            if hasattr(self.app, "_center_dialog"):
                self.app._center_dialog(dlg, 400, 300)

            help_frame = ctk.CTkFrame(dlg, fg_color="transparent")
            help_frame.pack(fill="both", expand=True, padx=20, pady=20)

            help_options = [
                ("Benutzerhandbuch", getattr(self.app, "_show_user_manual", None)),
                ("Schnellstart-Guide", getattr(self.app, "_show_quick_start", None)),
                ("Tipps & Tricks", getattr(self.app, "_show_tips", None)),
                ("Problem melden", getattr(self.app, "_report_issue", None)),
                ("Über Checker Pro", getattr(self.app, "_show_about", None)),
            ]

            for text, command in help_options:
                if not callable(command):
                    continue
                btn = ctk.CTkButton(
                    help_frame,
                    text=text,
                    font=ctk.CTkFont(*self.app.get_typography("caption")) if hasattr(self.app, 'get_typography') else None,
                    fg_color=self.app.get_color('info') if hasattr(self.app, 'get_color') else None,
                    hover_color=self.app.get_color('info') if hasattr(self.app, 'get_color') else None,
                    text_color=self.app.get_color('white') if hasattr(self.app, 'get_color') else None,
                    height=35,
                    corner_radius=self.app.get_component_value('borders.radius_md') if hasattr(self.app, 'get_component_value') else 8,
                    command=lambda cmd=command, dlg=dlg: self._execute_menu_command_adapter(cmd, dlg)
                )
                btn.pack(fill="x", pady=(0, 8))
        except Exception as e:
            if self.logger:
                self.logger.error(f"Help menu (CTk) error: {e}")

    # ===== Adapter =====
    def _execute_menu_command_adapter(self, command, dlg):
        try:
            dlg.destroy()
            command()
        except Exception as e:
            if self.logger:
                self.logger.error(f"Menu command error: {e}")

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