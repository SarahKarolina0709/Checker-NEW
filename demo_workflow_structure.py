#!/usr/bin/env python3
"""
Demo: Workflow-Ordnerstruktur
============================

Demonstriert die neue automatische Workflow-Ordnerstruktur
für die Kundendateiverwaltung.

Ordnerstruktur:
Checker_Projekte/
├── [Kundenname]/
│   ├── 2025-07-14/
│   │   ├── 01_Ausgangstext/         (← Hochgeladene Dateien)
│   │   │   ├── _INFO.txt
│   │   │   ├── dokument1.pdf
│   │   │   └── vertrag.docx
│   │   ├── 02_Angebot/
│   │   │   └── _INFO.txt
│   │   ├── 03_Prüfung/
│   │   │   └── _INFO.txt
│   │   └── 04_Finalisierung/
│   │       └── _INFO.txt
│   └── 2025-07-15/
│       ├── 01_Ausgangstext/
│       ├── 02_Angebot/
│       ├── 03_Prüfung/
│       └── 04_Finalisierung/
"""

import os
from datetime import datetime, timedelta

def demo_workflow_structure():
    """Demonstriert die Workflow-Ordnerstruktur."""
    
    print("📁 Demo: Automatische Workflow-Ordnerstruktur")
    print("=" * 50)
    
    # Simulierte Kunden
    customers = [
        {"name": "Müller & Söhne GmbH", "code": "MUE"},
        {"name": "Tech Solutions AG", "code": "TEC"},
        {"name": "Bäcker's Werkstatt", "code": "BAE"}
    ]
    
    # Basis-Pfad
    base_path = "Checker_Projekte"
    
    # Workflow-Ordner
    workflow_folders = {
        "01_Ausgangstext": "Hochgeladene Ausgangsdateien",
        "02_Angebot": "Angebotsdokumente und Kostenvoranschläge", 
        "03_Prüfung": "Qualitätsprüfung und Korrektur",
        "04_Finalisierung": "Finale Dokumente und Auslieferung"
    }
    
    print(f"\n🏗️ Basis-Struktur:")
    print(f"📁 {base_path}/")
    
    for customer in customers:
        # Kundenname für Ordner bereinigen
        customer_folder = clean_folder_name(customer["name"])
        print(f"├── 📁 {customer_folder}/")
        
        # Verschiedene Datums-Ordner simulieren
        dates = [
            datetime.now().strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        ]
        
        for i, date in enumerate(dates[:2]):  # Nur erste 2 Datums-Ordner anzeigen
            print(f"│   ├── 📅 {date}/")
            
            for j, (folder_name, description) in enumerate(workflow_folders.items()):
                is_last_workflow = j == len(workflow_folders) - 1
                is_last_date = i == 1
                
                connector = "│   │   └──" if is_last_workflow else "│   │   ├──"
                if is_last_date and is_last_workflow:
                    connector = "│   │   └──"
                
                print(f"{connector} 📂 {folder_name}/")
                
                # Info-Datei anzeigen
                info_connector = "│   │       └──" if is_last_workflow else "│   │       ├──"
                if is_last_date and is_last_workflow:
                    info_connector = "│   │       └──"
                
                print(f"{info_connector} 📝 _INFO.txt")
                
                # Beispiel-Dateien für Ausgangstext
                if folder_name == "01_Ausgangstext":
                    files = ["dokument.pdf", "vertrag.docx", "rechnung.xlsx"]
                    for k, file in enumerate(files[:2]):
                        file_connector = "│   │       └──" if k == 1 else "│   │       ├──"
                        if is_last_date and is_last_workflow and k == 1:
                            file_connector = "│   │       └──"
                        print(f"{file_connector} 📄 {file}")

def clean_folder_name(name):
    """Bereinigt einen Namen für die Verwendung als Ordnername."""
    # Ungültige Zeichen für Windows-Ordnernamen entfernen
    invalid_chars = '<>:"/\\|?*'
    clean_name = ''.join(c for c in name if c not in invalid_chars)
    
    # Umlaute ersetzen
    umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                 'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'}
    for umlaut, replacement in umlaut_map.items():
        clean_name = clean_name.replace(umlaut, replacement)
    
    # Mehrfache Leerzeichen entfernen und durch Unterstrich ersetzen
    clean_name = '_'.join(clean_name.split())
    
    # Maximale Länge begrenzen
    if len(clean_name) > 50:
        clean_name = clean_name[:50]
    
    return clean_name

def demo_workflow_process():
    """Demonstriert den Workflow-Prozess."""
    
    print(f"\n{'🔄 WORKFLOW-PROZESS' : ^50}")
    print("=" * 50)
    
    steps = [
        {
            "step": "1. Upload",
            "folder": "01_Ausgangstext",
            "description": "Kunde lädt Ausgangsdateien hoch",
            "files": ["original.docx", "quelle.pdf", "brief.txt"]
        },
        {
            "step": "2. Angebot",
            "folder": "02_Angebot", 
            "description": "Kostenvoranschlag und Angebot erstellen",
            "files": ["angebot.pdf", "kostenvoranschlag.xlsx"]
        },
        {
            "step": "3. Prüfung",
            "folder": "03_Prüfung",
            "description": "Qualitätsprüfung und Korrektur",
            "files": ["korrektur_v1.docx", "prüfbericht.pdf", "korrektur_final.docx"]
        },
        {
            "step": "4. Finalisierung", 
            "folder": "04_Finalisierung",
            "description": "Finale Dokumente für Auslieferung",
            "files": ["final.pdf", "auslieferung.zip", "rechnung.pdf"]
        }
    ]
    
    for step_info in steps:
        print(f"\n📋 {step_info['step']}: {step_info['description']}")
        print(f"   📁 Ordner: {step_info['folder']}")
        print(f"   📄 Beispiel-Dateien:")
        for file in step_info['files']:
            print(f"      • {file}")

def demo_benefits():
    """Zeigt die Vorteile der Workflow-Struktur."""
    
    print(f"\n{'✨ VORTEILE' : ^50}")
    print("=" * 50)
    
    benefits = [
        {
            "title": "🎯 Automatische Organisation",
            "points": [
                "Kundenordner werden automatisch erstellt",
                "Datumsbasierte Sortierung für Verlauf",
                "Workflow-Ordner für jeden Arbeitsschritt"
            ]
        },
        {
            "title": "📅 Chronologische Struktur", 
            "points": [
                "Jeder Tag erhält eigenen Ordner",
                "Klare Trennung verschiedener Projekte",
                "Einfache Nachverfolgung des Verlaufs"
            ]
        },
        {
            "title": "🔄 Workflow-Integration",
            "points": [
                "Klar definierte Arbeitsschritte",
                "Strukturierte Dokumentenablage", 
                "Info-Dateien für jeden Ordner"
            ]
        },
        {
            "title": "💻 Systemkompatibilität",
            "points": [
                "Windows-kompatible Ordnernamen",
                "Automatische Umlaute-Bereinigung",
                "Begrenzte Ordnernamenlänge"
            ]
        }
    ]
    
    for benefit in benefits:
        print(f"\n{benefit['title']}")
        print("-" * len(benefit['title']))
        for point in benefit['points']:
            print(f"  ✓ {point}")

def demo_example_scenario():
    """Zeigt ein Beispiel-Szenario."""
    
    print(f"\n{'📖 BEISPIEL-SZENARIO' : ^50}")
    print("=" * 50)
    
    scenario = [
        "1. 👥 Kunde 'Müller & Söhne GmbH' wird ausgewählt",
        "2. 📤 3 Dokumente werden hochgeladen (PDF, Word, Excel)",
        "3. 🏗️ System erstellt automatisch:",
        "   📁 Checker_Projekte/Müller_und_Soehne_GmbH/",
        "   📅 └── 2025-07-14/",
        "   📂     ├── 01_Ausgangstext/ (← Dateien landen hier)",
        "   📂     ├── 02_Angebot/",
        "   📂     ├── 03_Prüfung/",
        "   📂     └── 04_Finalisierung/",
        "4. 📄 Hochgeladene Dateien werden in '01_Ausgangstext' kopiert",
        "5. 📝 Info-Dateien werden in jeden Ordner erstellt",
        "6. ✅ Benutzer erhält Bestätigung mit vollständigem Pfad"
    ]
    
    for step in scenario:
        print(step)

if __name__ == "__main__":
    demo_workflow_structure()
    demo_workflow_process()
    demo_benefits()
    demo_example_scenario()
    
    print(f"\n{'🎉' * 20}")
    print("Demo abgeschlossen!")
    print("Automatische Workflow-Ordnerstruktur bereit! 🚀")
