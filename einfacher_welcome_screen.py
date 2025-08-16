#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🏠 EINFACHER WELCOME SCREEN REPARATUR
===================================

Direkte, einfache Version ohne komplexe Module.
"""

import customtkinter as ctk
from design_system import get_color, get_font
from design_system import DesignSystem
import sys
import os

# Force light mode
ctk.set_appearance_mode("light")

class EinfacherWelcomeScreen:
    """🏠 Einfache Welcome Screen Version"""
    
    def __init__(self, root):
        self.root = root
        self.root.configure(fg_color=get_color('white'))
        
        # Erstelle Hauptcontainer
        self.main_frame = ctk.CTkFrame(root, fg_color=get_color('white'))
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        self._create_header()
        self._create_three_containers()
    
    def _create_header(self):
        """📋 Header erstellen"""
        header_frame = ctk.CTkFrame(self.main_frame, fg_color=get_color('primary'), height=80)
        header_frame.pack(fill="x", pady=(0, 20))
        
        title = ctk.CTkLabel(
            header_frame,
            text="Checker - Welcome Screen",
            font=ctk.CTkFont(*get_font('heading_lg')),
            text_color=get_color('white')
        )
        title.pack(expand=True)
    
    def _create_three_containers(self):
        """📦 Die drei Hauptcontainer erstellen"""
        # Container-Frame für die drei Bereiche
        container_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        container_frame.pack(fill="both", expand=True)
        
        # Grid konfigurieren
        container_frame.grid_columnconfigure(0, weight=1)
        container_frame.grid_columnconfigure(1, weight=1)
        container_frame.grid_columnconfigure(2, weight=1)
        container_frame.grid_rowconfigure(0, weight=1)
        
        # Die drei Hauptbereiche
        self._create_customer_card(container_frame, 0)
        self._create_upload_card(container_frame, 1)
        self._create_workflow_card(container_frame, 2)
    
    def _create_customer_card(self, parent, column):
        """👤 Kundenmanagement Card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=get_color('white'),
            border_width=DesignSystem.get_component_property('borders', 'width_medium'),
            border_color=get_color('surface_border')
        )
        card.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(
            card,
            text="Kundenmanagement",
            font=ctk.CTkFont(*get_font('heading_md')),
            text_color=get_color('gray_700')
        )
        header.pack(pady=20)
        
        # Content
        content = ctk.CTkLabel(
            card,
            text="• Kunden erstellen\n• Kunden auswählen\n• Projekte verwalten\n• 39 Kunden verfügbar",
            font=ctk.CTkFont(*get_font('body_md')),
            text_color=get_color('gray_500'),
            justify="left"
        )
        content.pack(pady=10)
        
        # Button
        btn = ctk.CTkButton(
            card,
            text="Kunde hinzufügen",
            font=ctk.CTkFont(*get_font('button_md')),
            width=DesignSystem.get_component_property('buttons','min_width_md'),
            fg_color=get_color('button_primary'),
            hover_color=get_color('button_primary_hover'),
            text_color=get_color('button_primary_text')
        )
        btn.pack(pady=20)
    
    def _create_upload_card(self, parent, column):
        """📁 Upload Card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=get_color('white'),
            border_width=DesignSystem.get_component_property('borders', 'width_medium'),
            border_color=get_color('surface_border')
        )
        card.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(
            card,
            text="Upload System",
            font=ctk.CTkFont(*get_font('heading_md')),
            text_color=get_color('gray_700')
        )
        header.pack(pady=20)
        
        # Content
        content = ctk.CTkLabel(
            card,
            text="• Dateien hochladen\n• Drag & Drop\n• Automatische Organisation\n• Projektstruktur",
            font=ctk.CTkFont(*get_font('body_md')),
            text_color=get_color('gray_500'),
            justify="left"
        )
        content.pack(pady=10)
        
        # Button
        btn = ctk.CTkButton(
            card,
            text="Dateien hochladen",
            font=ctk.CTkFont(*get_font('button_md')),
            width=DesignSystem.get_component_property('buttons','min_width_md'),
            fg_color=get_color('success'),
            hover_color=get_color('success_hover'),
            text_color=get_color('white')
        )
        btn.pack(pady=20)
    
    def _create_workflow_card(self, parent, column):
        """🎯 Workflow Card"""
        card = ctk.CTkFrame(
            parent,
            fg_color=get_color('white'),
            border_width=DesignSystem.get_component_property('borders', 'width_medium'),
            border_color=get_color('surface_border')
        )
        card.grid(row=0, column=column, sticky="nsew", padx=10, pady=10)
        
        # Header
        header = ctk.CTkLabel(
            card,
            text="Workflow-Auswahl",
            font=ctk.CTkFont(*get_font('heading_md')),
            text_color=get_color('gray_700')
        )
        header.pack(pady=20)
        
        # Content
        content = ctk.CTkLabel(
            card,
            text="Verfügbare Prüfungsworkflows:",
            font=ctk.CTkFont(*get_font('body_md')),
            text_color=get_color('gray_500')
        )
        content.pack(pady=10)
        
        # Workflow Buttons
        workflows = [
            ("Übersetzungsqualität", "quality_gui_main_app.py"),
            ("Modular System", "modern_translation_quality_gui_modular.py"),
            ("Legacy System", "modern_translation_quality_gui.py")
        ]
        
        for workflow_name, workflow_file in workflows:
            btn = ctk.CTkButton(
                card,
                text=workflow_name,
                font=ctk.CTkFont(*get_font('button_md')),
                width=DesignSystem.get_component_property('buttons','min_width_md'),
                fg_color=get_color('warning'),
                hover_color=get_color('warning_hover'),
                text_color=get_color('white'),
                command=lambda f=workflow_file: self._start_workflow(f)
            )
            btn.pack(pady=5, padx=20, fill="x")
    
    def _start_workflow(self, workflow_file):
        """🚀 Workflow starten"""
        try:
            import subprocess
            subprocess.Popen([sys.executable, workflow_file])
            print(f"✅ Workflow gestartet: {workflow_file}")
        except Exception as e:
            print(f"❌ Error starting workflow: {e}")

def main():
    """🚀 Start the Simple Welcome Screen"""
    print("🏠 EINFACHER WELCOME SCREEN - REPARATUR")
    print("=" * 50)
    print("Startet eine vereinfachte aber funktionierende Version")
    print("mit den drei Hauptbereichen:")
    print("👤 Kundenmanagement")
    print("📁 Upload System") 
    print("🎯 Workflow-Auswahl")
    print()

    try:
        # Create main window
        root = ctk.CTk()
        root.title("Checker - Einfacher Welcome Screen")
        root.geometry("1400x800")
        root.minsize(1000, 600)

        # Center window
        root.update_idletasks()
        width = 1400
        height = 800
        x = (root.winfo_screenwidth() // 2) - (width // 2)
        y = (root.winfo_screenheight() // 2) - (height // 2)
        root.geometry(f"{width}x{height}+{x}+{y}")

        print("✅ Fenster erstellt und zentriert")

        # Create Welcome Screen
        welcome_screen = EinfacherWelcomeScreen(root)
        print("✅ Welcome Screen initialisiert")

        # Force window to front
        root.lift()
        root.focus_force()
        root.attributes('-topmost', True)
        root.after(100, lambda: root.attributes('-topmost', False))

        print("\n🎉 EINFACHER WELCOME SCREEN GESTARTET!")
        print("Du solltest jetzt die drei Container sehen:")
        print("👤 Links: Kundenmanagement")
        print("📁 Mitte: Upload System")
        print("🎯 Rechts: Workflow-Auswahl")
        print("\nSchließe mit Alt+F4 oder dem X-Button")

        # Start GUI loop
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        import traceback
        traceback.print_exc()
        input("Drücke Enter zum Beenden...")

if __name__ == "__main__":
    main()
