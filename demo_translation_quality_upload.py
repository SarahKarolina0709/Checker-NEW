#!/usr/bin/env python3
"""
Demo der Translation Quality Framework mit File Upload Funktionalität
Zeigt die neuen Features für Dateipaar-Upload und Batch-Analyse
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog
import customtkinter as ctk

# Füge den aktuellen Ordner zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importiere das Translation Quality Framework
try:
    from translation_quality_workflow import create_translation_quality_gui
except ImportError as e:
    print(f"❌ Import-Fehler: {e}")
    print("Bitte stellen Sie sicher, dass translation_quality_workflow.py im gleichen Ordner ist.")
    sys.exit(1)

def create_demo_files():
    """Erstelle Demo-Dateien zum Testen der Upload-Funktionalität"""
    
    # Erstelle Demo-Ordner falls nicht vorhanden
    demo_dir = "demo_translation_files"
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
    
    # Demo Ausgangstexte (Englisch)
    source_texts = [
        {
            "filename": "source_1_welcome.txt",
            "content": """Welcome to our revolutionary translation quality system. 
This innovative platform combines artificial intelligence with linguistic expertise to deliver unparalleled translation accuracy. 
Our comprehensive quality framework evaluates six critical criteria: accuracy, fluency, terminology consistency, style appropriateness, cultural adaptation, and technical compliance.
We ensure that every translation meets the highest professional standards."""
        },
        {
            "filename": "source_2_technical.txt", 
            "content": """The system architecture implements a multi-layered quality assessment protocol.
Advanced natural language processing algorithms analyze semantic coherence, syntactic accuracy, and lexical appropriateness.
The framework incorporates machine learning models trained on extensive multilingual corpora to identify translation errors and inconsistencies.
Performance metrics include precision, recall, and F1-scores across various linguistic dimensions."""
        },
        {
            "filename": "source_3_business.txt",
            "content": """Our client portfolio spans diverse industries including technology, healthcare, finance, and legal services.
Each project undergoes rigorous quality assurance procedures tailored to specific domain requirements.
We maintain strict confidentiality protocols and adhere to international translation standards such as ISO 17100.
Customer satisfaction rates exceed 98% across all service categories."""
        }
    ]
    
    # Demo Übersetzungen (Deutsch) - mit absichtlichen Qualitätsunterschieden
    translation_texts = [
        {
            "filename": "translation_1_welcome.txt",
            "content": """Willkommen bei unserem revolutionären Übersetzungsqualitätssystem.
Diese innovative Plattform kombiniert künstliche Intelligenz mit linguistischer Expertise, um unvergleichliche Übersetzungsgenauigkeit zu liefern.
Unser umfassendes Qualitäts-Framework evaluiert sechs kritische Kriterien: Genauigkeit, Flüssigkeit, Terminologie-Konsistenz, Stil-Angemessenheit, kulturelle Anpassung und technische Compliance.
Wir stellen sicher, dass jede Übersetzung den höchsten professionellen Standards entspricht."""
        },
        {
            "filename": "translation_2_technical.txt",
            "content": """Die Systemarchitektur implementiert ein mehrschichtiges Qualitätsbewertungsprotokoll.
Fortgeschrittene Verarbeitung natürlicher Sprache Algorithmen analysieren semantische Kohärenz, syntaktische Genauigkeit und lexikalische Angemessenheit.
Das Framework inkorporiert Maschinen-Lern-Modelle trainiert auf extensive multilinguale Korpora um Übersetzungsfehler und Inkonsistenzen zu identifizieren.
Performance-Metriken beinhalten Präzision, Recall und F1-Scores über verschiedene linguistische Dimensionen."""
        },
        {
            "filename": "translation_3_business.txt", 
            "content": """Unser Kundenstamm umfasst verschiedene Branchen wie Technologie, Gesundheitswesen, Finanzwesen und Rechtsdienstleistungen.
Jedes Projekt durchläuft strenge Qualitätssicherungsverfahren, die auf spezifische Domänenanforderungen zugeschnitten sind.
Wir halten strenge Vertraulichkeitsprotokolle ein und halten uns an internationale Übersetzungsstandards wie ISO 17100.
Die Kundenzufriedenheitsraten überschreiten 98% in allen Servicekategorien."""
        }
    ]
    
    # Schreibe Demo-Dateien
    for source_text in source_texts:
        filepath = os.path.join(demo_dir, source_text["filename"])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(source_text["content"])
    
    for trans_text in translation_texts:
        filepath = os.path.join(demo_dir, trans_text["filename"])
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(trans_text["content"])
    
    print(f"✅ Demo-Dateien erstellt in: {demo_dir}/")
    return demo_dir

def show_demo_instructions():
    """Zeige Anweisungen für die Demo"""
    instructions = """
🌍 TRANSLATION QUALITY FRAMEWORK - DEMO ANLEITUNG
================================================================

📂 FILE UPLOAD FEATURES:
1. Zwei getrennte Upload-Manager:
   - Welcome Screen: Allgemeine Projektdateien
   - Quality Check: Spezielle Dateipaar-Uploads (Ausgangstext + Übersetzung)

🔄 WORKFLOW SCHRITTE:
1. Ausgangstexte hochladen (📄 Button)
2. Übersetzungen hochladen (🌍 Button)  
3. Dateipaare erstellen (🔗 Button)
4. Automatische Paarung nach Index oder Dateinamen
5. Qualitätsanalyse starten:
   - Einzelanalyse: 🚀 Run Quality Check
   - Batch-Analyse: 📊 Analyze All File Pairs

📋 UNTERSTÜTZTE DATEIFORMATE:
- TXT: Direkte Textextraktion
- PDF: PyPDF2-basierte Extraktion
- DOCX: python-docx-basierte Extraktion

🎯 QUALITÄTSKRITERIEN (6):
1. Richtigkeit (Accuracy)
2. Flüssigkeit (Fluency) 
3. Terminologie (Terminology)
4. Stil (Style)
5. Kulturelle Anpassung (Cultural)
6. Technische Aspekte (Technical)

⚡ WORKFLOW-SCHRITTE (6):
1. Eingangsprüfung
2. Formatprüfung
3. Inhaltsprüfung
4. Qualitätskontrolle
5. Technische Validierung
6. Feedback & Rückmeldungen

💡 DEMO-TIPPS:
- Demo-Dateien wurden automatisch erstellt
- Verschiedene Qualitätslevel zum Testen
- Batch-Analyse für mehrere Dateipaare
- Detaillierte Ergebnisberichte mit Scores
================================================================
    """
    print(instructions)

def main():
    """Hauptfunktion für die Demo"""
    print("🌍 Translation Quality Framework - File Upload Demo")
    print("=" * 60)
    
    # Erstelle Demo-Dateien
    demo_dir = create_demo_files()
    
    # Zeige Anweisungen
    show_demo_instructions()
    
    # Frage ob GUI gestartet werden soll
    response = input("\n🚀 Möchten Sie die GUI starten? (j/n): ").lower()
    
    if response in ['j', 'ja', 'y', 'yes', '']:
        print("Starte Translation Quality Framework GUI...")
        
        try:
            # Starte die GUI
            create_translation_quality_gui()
        except Exception as e:
            print(f"❌ Fehler beim Starten der GUI: {e}")
    else:
        print("Demo beendet. Demo-Dateien sind verfügbar in:", demo_dir)

if __name__ == "__main__":
    main()
