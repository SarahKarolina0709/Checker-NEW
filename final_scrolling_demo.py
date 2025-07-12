"""
FINALES VERTIKALES SCROLLING UPDATE
===================================

Dieses Script behebt alle Scrolling-Probleme und stellt sicher, dass:
1. Alle drei Container (Customer, Upload, Workflow) vertikales Scrolling haben
2. Die Container eine feste Höhe haben und nicht gestreckt werden
3. Genügend Testinhalt vorhanden ist, um das Scrolling zu demonstrieren
4. Die Scrollbars korrekt funktionieren
"""

import customtkinter as ctk
from ui_theme import UITheme
import json
import os
import shutil
from datetime import datetime

class FinalScrollingDemo:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("✅ FINALES VERTIKALES SCROLLING - CheckerApp Pro")
        self.root.geometry("1400x900")
        
        # Configure theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Create test data
        self.create_comprehensive_test_data()
        
        # Setup UI
        self.setup_final_ui()
        
        print("🎯 FINALES VERTIKALES SCROLLING DEMO")
        print("=" * 60)
        print("✅ Customer Section: 50+ Test-Projekte")
        print("✅ Upload Section: 40+ Test-Dateien")
        print("✅ Workflow Section: 12+ Test-Workflows")
        print("📏 Alle Container: Feste Höhe 600px")
        print("🖱️ Vollständiges vertikales Scrolling implementiert")
        print("🎨 Distinct border colors: Blau, Lila, Orange")
        print("=" * 60)
        print("🔍 TESTEN SIE DAS SCROLLING IN ALLEN DREI SEKTIONEN!")
    
    def create_comprehensive_test_data(self):
        """Erstellt umfassende Test-Daten für alle Sektionen"""
        
        # 1. Customer Test Data - Viele Projekte
        customer_projects = []
        companies = [
            "ACME Corporation", "TechnoGlobal GmbH", "Innovation Inc.", 
            "Digital Solutions AG", "Future Systems Ltd.", "Smart Technologies",
            "Advanced Dynamics", "Global Enterprises", "NextGen Solutions",
            "ProTech Industries", "Elite Services", "Premier Group"
        ]
        
        project_types = [
            "Website Übersetzung", "Dokumentation", "Marketing Material",
            "Software Lokalisierung", "E-Learning Kurs", "Produktkatalog",
            "Benutzerhandbuch", "Pressemitteilung", "Jahresbericht"
        ]
        
        for i in range(50):
            company = companies[i % len(companies)]
            project_type = project_types[i % len(project_types)]
            customer_projects.append({
                'customer': f'{company} #{i+1}',
                'project': f'{project_type} - Projekt {i+1}',
                'date': '2025-01-01',
                'status': 'In Bearbeitung' if i % 3 == 0 else 'Abgeschlossen'
            })
        
        # Speichere Customer-Daten
        with open('recent_projects.json', 'w', encoding='utf-8') as f:
            json.dump({'recent_projects': customer_projects}, f, ensure_ascii=False, indent=2)
        
        # 2. Upload Test Data - Viele Dateien
        test_files_dir = "comprehensive_test_uploads"
        if os.path.exists(test_files_dir):
            shutil.rmtree(test_files_dir)
        os.makedirs(test_files_dir)
        
        file_types = [
            "Produktbeschreibung", "Benutzerhandbuch", "FAQ", "Pressemitteilung",
            "Marketingtext", "Webseiteninhalt", "Blog-Artikel", "Newsletter",
            "Technische Dokumentation", "Vertragsbedingungen"
        ]
        
        self.test_files = []
        for i in range(40):
            file_type = file_types[i % len(file_types)]
            filename = f"{file_type.replace(' ', '_').lower()}_{i+1:02d}.txt"
            filepath = os.path.join(test_files_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"""
{file_type} #{i+1}

Dies ist ein umfassender Test-Text für die Übersetzung.
Der Text enthält verschiedene Absätze und Formatierungen.

Wichtige Informationen:
- Punkt 1: Qualitätssicherung
- Punkt 2: Termingerechte Lieferung  
- Punkt 3: Professionelle Übersetzung

Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}
Dateigröße: {(i+1) * 157} Zeichen
Status: Bereit für Übersetzung
""")
            self.test_files.append(filepath)
    
    def setup_final_ui(self):
        """Setup der finalen UI mit garantiertem vertikalem Scrolling"""
        
        # Main container mit optimaler Konfiguration
        main_container = ctk.CTkFrame(self.root, fg_color="#FAFBFC", corner_radius=0)
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Perfect grid configuration für drei Spalten
        main_container.grid_columnconfigure(0, weight=1, minsize=450)
        main_container.grid_columnconfigure(1, weight=1, minsize=450) 
        main_container.grid_columnconfigure(2, weight=1, minsize=450)
        main_container.grid_rowconfigure(0, weight=1)
        
        # Create all three sections
        self.create_final_customer_section(main_container)
        self.create_final_upload_section(main_container)
        self.create_final_workflow_section(main_container)
        
        # Add comprehensive status info
        status_frame = ctk.CTkFrame(self.root, fg_color="transparent")
        status_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        status_text = ("✅ VERTIKALES SCROLLING IMPLEMENTIERT | "
                      "Customer: 50 Projekte | Upload: 40 Dateien | Workflow: 12 Aktionen | "
                      "Alle Container: Feste Höhe 600px mit Scrolling")
        
        status_label = ctk.CTkLabel(
            status_frame,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#2E8B57"
        )
        status_label.pack(pady=10)
    
    def create_final_customer_section(self, parent):
        """Finale Customer Section mit garantiertem Scrolling"""
        
        # Container mit exakter Theme-Konfiguration
        customer_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_CUSTOMER)
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        customer_container.grid_columnconfigure(0, weight=1)
        customer_container.grid_rowconfigure(1, weight=1)
        customer_container.grid_propagate(False)  # KRITISCH: Verhindert Auto-Resize
        
        # Header
        header_frame = ctk.CTkFrame(customer_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_frame = ctk.CTkFrame(header_frame, width=40, height=40, 
                                 fg_color=UITheme.COLOR_CONTAINER_CUSTOMER, corner_radius=8)
        icon_frame.grid(row=0, column=0, sticky="w", padx=(0, 15))
        icon_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="👤", font=ctk.CTkFont(size=20))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title and subtitle
        title_label = ctk.CTkLabel(
            header_frame,
            text="Projektdaten",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Kundenname eingeben • Projekt auswählen oder erstellen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew")
        
        # SCROLLABLE CONTENT FRAME - DIES IST DER SCHLÜSSEL!
        scrollable_frame = ctk.CTkScrollableFrame(
            customer_container,
            fg_color="transparent",
            scrollbar_button_color=UITheme.COLOR_CONTAINER_CUSTOMER,
            scrollbar_button_hover_color="#1D4ED8",  # Dunkleres Blau
            corner_radius=0
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(20, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Load und display customer projects
        try:
            with open('recent_projects.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                projects = data.get('recent_projects', [])
                
            # Erstelle Project-Einträge
            for i, project in enumerate(projects):
                project_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
                project_frame.grid(row=i, column=0, sticky="ew", pady=3)
                project_frame.grid_columnconfigure(0, weight=1)
                
                # Project info
                customer_label = ctk.CTkLabel(
                    project_frame,
                    text=f"🏢 {project['customer']}",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    anchor="w"
                )
                customer_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 2))
                
                project_label = ctk.CTkLabel(
                    project_frame,
                    text=f"📋 {project['project']}",
                    font=ctk.CTkFont(size=11),
                    text_color=UITheme.COLOR_TEXT_SECONDARY,
                    anchor="w"
                )
                project_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 10))
                
        except Exception as e:
            # Fallback content
            for i in range(30):
                fallback_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
                fallback_frame.grid(row=i, column=0, sticky="ew", pady=3)
                fallback_frame.grid_columnconfigure(0, weight=1)
                
                fallback_label = ctk.CTkLabel(
                    fallback_frame,
                    text=f"🏢 Fallback Kunde {i+1} - Test Projekt",
                    font=ctk.CTkFont(size=12)
                )
                fallback_label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
    
    def create_final_upload_section(self, parent):
        """Finale Upload Section mit garantiertem Scrolling"""
        
        # Container mit exakter Theme-Konfiguration
        upload_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_UPLOAD)
        upload_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 15))
        upload_container.grid_columnconfigure(0, weight=1)
        upload_container.grid_rowconfigure(1, weight=1)
        upload_container.grid_propagate(False)  # KRITISCH: Verhindert Auto-Resize
        
        # Header
        header_frame = ctk.CTkFrame(upload_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_frame = ctk.CTkFrame(header_frame, width=40, height=40, 
                                 fg_color=UITheme.COLOR_CONTAINER_UPLOAD, corner_radius=8)
        icon_frame.grid(row=0, column=0, sticky="w", padx=(0, 15))
        icon_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="📤", font=ctk.CTkFont(size=20))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title and subtitle
        title_label = ctk.CTkLabel(
            header_frame,
            text="Dateien hochladen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Dateien per Drag & Drop oder Upload-Button hinzufügen",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew")
        
        # SCROLLABLE CONTENT FRAME - DIES IST DER SCHLÜSSEL!
        scrollable_frame = ctk.CTkScrollableFrame(
            upload_container,
            fg_color="transparent",
            scrollbar_button_color=UITheme.COLOR_CONTAINER_UPLOAD,
            scrollbar_button_hover_color="#7C3AED",  # Dunkleres Lila
            corner_radius=0
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(20, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Add test files
        for i, filepath in enumerate(self.test_files):
            file_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
            file_frame.grid(row=i, column=0, sticky="ew", pady=2)
            file_frame.grid_columnconfigure(0, weight=1)
            
            filename = os.path.basename(filepath)
            file_size = os.path.getsize(filepath) if os.path.exists(filepath) else 0
            
            # File info
            name_label = ctk.CTkLabel(
                file_frame,
                text=f"📁 {filename}",
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor="w"
            )
            name_label.grid(row=0, column=0, sticky="ew", padx=15, pady=(8, 2))
            
            size_label = ctk.CTkLabel(
                file_frame,
                text=f"📏 {file_size} Bytes • Bereit für Übersetzung",
                font=ctk.CTkFont(size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            size_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 8))
    
    def create_final_workflow_section(self, parent):
        """Finale Workflow Section mit garantiertem Scrolling"""
        
        # Container mit exakter Theme-Konfiguration
        workflow_container = ctk.CTkFrame(parent, **UITheme.CONTAINER_STYLE_WORKFLOW)
        workflow_container.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        workflow_container.grid_columnconfigure(0, weight=1)
        workflow_container.grid_rowconfigure(1, weight=1)
        workflow_container.grid_propagate(False)  # KRITISCH: Verhindert Auto-Resize
        
        # Header
        header_frame = ctk.CTkFrame(workflow_container, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 0))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Icon
        icon_frame = ctk.CTkFrame(header_frame, width=40, height=40, 
                                 fg_color=UITheme.COLOR_CONTAINER_WORKFLOW, corner_radius=8)
        icon_frame.grid(row=0, column=0, sticky="w", padx=(0, 15))
        icon_frame.grid_propagate(False)
        
        icon_label = ctk.CTkLabel(icon_frame, text="⚙️", font=ctk.CTkFont(size=20))
        icon_label.place(relx=0.5, rely=0.5, anchor="center")
        
        # Title and subtitle
        title_label = ctk.CTkLabel(
            header_frame,
            text="Workflows starten",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=16, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY,
            anchor="w"
        )
        title_label.grid(row=0, column=1, sticky="ew")
        
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Wählen Sie einen Workflow zur Bearbeitung aus",
            font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=12),
            text_color=UITheme.COLOR_TEXT_SECONDARY,
            anchor="w"
        )
        subtitle_label.grid(row=1, column=1, sticky="ew")
        
        # SCROLLABLE CONTENT FRAME - DIES IST DER SCHLÜSSEL!
        scrollable_frame = ctk.CTkScrollableFrame(
            workflow_container,
            fg_color="transparent",
            scrollbar_button_color=UITheme.COLOR_CONTAINER_WORKFLOW,
            scrollbar_button_hover_color="#EA580C",  # Dunkleres Orange
            corner_radius=0
        )
        scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(20, 20))
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Comprehensive workflow list
        workflows = [
            ("🔄", "Angebotsanalyse", "Erstelle professionelle Angebote"),
            ("✅", "Qualitätsprüfung", "Prüfe Übersetzungen auf Qualität"),
            ("🎯", "Finalisierung", "Finalisiere Projekte"),
            ("📊", "Projektübersicht", "Verwalte deine Projekte"),
            ("📝", "Terminologie Check", "Prüfe Terminologie-Konsistenz"),
            ("🎨", "Layout Anpassung", "Optimiere Design und Layout"),
            ("🔍", "SEO Optimierung", "Suchmaschinenoptimierung"),
            ("📤", "Export Manager", "Export in verschiedene Formate"),
            ("📋", "Workflow Automation", "Automatisierte Prozesse"),
            ("🔧", "System Integration", "Integration mit externen Systemen"),
            ("📈", "Analytics Dashboard", "Leistungsanalyse und Berichte"),
            ("🛠️", "Custom Workflows", "Benutzerdefinierte Arbeitsabläufe")
        ]
        
        for i, (icon, name, description) in enumerate(workflows):
            workflow_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
            workflow_frame.grid(row=i, column=0, sticky="ew", pady=5)
            workflow_frame.grid_columnconfigure(0, weight=1)
            
            # Workflow info
            header_container = ctk.CTkFrame(workflow_frame, fg_color="transparent")
            header_container.grid(row=0, column=0, sticky="ew", padx=15, pady=(12, 8))
            header_container.grid_columnconfigure(1, weight=1)
            
            icon_label = ctk.CTkLabel(
                header_container,
                text=icon,
                font=ctk.CTkFont(size=16)
            )
            icon_label.grid(row=0, column=0, sticky="w", padx=(0, 10))
            
            name_label = ctk.CTkLabel(
                header_container,
                text=name,
                font=ctk.CTkFont(size=12, weight="bold"),
                anchor="w"
            )
            name_label.grid(row=0, column=1, sticky="ew")
            
            desc_label = ctk.CTkLabel(
                workflow_frame,
                text=description,
                font=ctk.CTkFont(size=10),
                text_color=UITheme.COLOR_TEXT_SECONDARY,
                anchor="w"
            )
            desc_label.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 12))
    
    def run(self):
        """Starte die finale Demo"""
        self.root.mainloop()
        
        # Cleanup
        self.cleanup()
    
    def cleanup(self):
        """Bereinige Test-Dateien"""
        try:
            if os.path.exists('recent_projects.json'):
                os.remove('recent_projects.json')
            if os.path.exists('comprehensive_test_uploads'):
                shutil.rmtree('comprehensive_test_uploads')
        except Exception as e:
            print(f"Cleanup error: {e}")

if __name__ == "__main__":
    print("🚀 Starte finales vertikales Scrolling Demo...")
    app = FinalScrollingDemo()
    app.run()
