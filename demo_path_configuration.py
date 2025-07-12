#!/usr/bin/env python3
"""
Demo der Kundenpfad-Konfiguration
Zeigt alle verfügbaren Optionen zur Pfad-Bestimmung.
"""

import os
import json

def demo_path_configuration():
    """Demonstriert die Kundenpfad-Konfiguration."""
    
    print("📁 Kundenpfad-Konfiguration Demo")
    print("=" * 50)
    
    # Aktuelle Konfiguration laden
    config_path = "kunden_config.json"
    
    print("\n1️⃣ AKTUELLE KONFIGURATION")
    print("-" * 30)
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            current_path = config.get("kunden_base_dir", "Checker_Projekte")
            abs_path = os.path.abspath(current_path)
            
            print(f"📋 Konfigurationsdatei: {config_path}")
            print(f"📂 Konfigurierter Pfad: {current_path}")
            print(f"📁 Absoluter Pfad: {abs_path}")
            print(f"✅ Pfad existiert: {'Ja' if os.path.exists(abs_path) else 'Nein'}")
            
            if os.path.exists(abs_path):
                print(f"📊 Inhalt: {len(os.listdir(abs_path))} Elemente")
            
        except Exception as e:
            print(f"❌ Fehler beim Lesen: {e}")
    else:
        print(f"📋 Konfigurationsdatei: Nicht vorhanden")
        print(f"📂 Standard-Pfad: Checker_Projekte")
    
    print("\n2️⃣ VERFÜGBARE KONFIGURATIONS-METHODEN")
    print("-" * 40)
    
    methods = [
        ("🖱️  Grafisches Menü", "Tools → Kundenpfad konfigurieren", "EMPFOHLEN"),
        ("📝 Konfigurationsdatei", "kunden_config.json bearbeiten", "Für Experten"),
        ("🔧 Programmatisch", "Über Code-Funktionen", "Für Entwickler")
    ]
    
    for icon, method, note in methods:
        print(f"{icon} {method}")
        print(f"   💡 {note}")
        print()
    
    print("\n3️⃣ PFAD-BEISPIELE")
    print("-" * 20)
    
    examples = [
        ("Relativer Pfad", "Checker_Projekte", "Standard, relativ zum Anwendungsverzeichnis"),
        ("Absoluter Pfad", r"C:\Projekte\Checker_Kunden", "Fester Windows-Pfad"),
        ("Benutzerdokumente", r"C:\Users\IhrName\Documents\Checker", "In Benutzerprofil"),
        ("Netzlaufwerk", r"\\Server\Projekte\Checker", "Für Teams"),
        ("Anderes Laufwerk", r"D:\Backup\Checker_Projekte", "Für Backup-Integration")
    ]
    
    for title, path, description in examples:
        print(f"📂 {title}:")
        print(f"   Pfad: {path}")
        print(f"   💡 {description}")
        print()
    
    print("\n4️⃣ KONFIGURATION ÜBER GUI")
    print("-" * 30)
    
    steps = [
        "Tools-Menü öffnen",
        "'Kundenpfad konfigurieren' wählen",
        "Neuen Pfad eingeben oder durchsuchen",
        "Optionen wählen (Ordner erstellen, Daten kopieren)",
        "'Übernehmen' klicken"
    ]
    
    for i, step in enumerate(steps, 1):
        print(f"{i}. {step}")
    
    print("\n   ✅ Vorteile der GUI-Methode:")
    advantages = [
        "Benutzerfreundlich",
        "Automatische Validierung",
        "Fehlerprüfung",
        "Daten-Kopierung",
        "Sofortige Anwendung"
    ]
    
    for advantage in advantages:
        print(f"   • {advantage}")
    
    print("\n5️⃣ MANUELLE KONFIGURATION")
    print("-" * 30)
    
    print("📝 kunden_config.json erstellen/bearbeiten:")
    print()
    
    manual_examples = [
        ('Standard', '{"kunden_base_dir": "Checker_Projekte"}'),
        ('Absolut', '{"kunden_base_dir": "C:\\\\Projekte\\\\Checker"}'),
        ('Netzwerk', '{"kunden_base_dir": "\\\\\\\\Server\\\\Projekte"}')
    ]
    
    for title, config in manual_examples:
        print(f"   📄 {title}:")
        print(f"   {config}")
        print()
    
    print("   ⚠️  Wichtig:")
    print("   • Backslashes escapen (\\\\)")
    print("   • Gültige JSON-Syntax")
    print("   • Anwendung neu starten")
    
    print("\n6️⃣ ORDNERSTRUKTUR")
    print("-" * 20)
    
    print("Nach der Konfiguration wird folgende Struktur erstellt:")
    print()
    print("📁 Ihr_Kundenpfad/")
    print("├── 📁 Kunde_1/")
    print("│   ├── 📁 Angebot/")
    print("│   ├── 📁 Pruefung/")
    print("│   ├── 📁 Finalisierung/")
    print("│   └── 📁 Ausgangstexte/")
    print("├── 📁 Kunde_2/")
    print("│   ├── 📁 Angebot/")
    print("│   ├── 📁 Pruefung/")
    print("│   ├── 📁 Finalisierung/")
    print("│   └── 📁 Ausgangstexte/")
    print("└── ...")
    
    print("\n7️⃣ SCHNELLSTART")
    print("-" * 15)
    
    print("🚀 Empfohlenes Vorgehen für neue Benutzer:")
    print()
    print("1. Checker-App starten")
    print("2. Tools → Kundenpfad konfigurieren")
    print("3. Gewünschten Pfad eingeben")
    print("4. ✅ 'Ordner erstellen' aktivieren")
    print("5. 'Übernehmen' klicken")
    print("6. Fertig! 🎉")
    
    print("\n💡 TIPP: Für den Anfang den Standard-Pfad verwenden!")
    print("   Der wird automatisch im Anwendungsverzeichnis erstellt.")

if __name__ == "__main__":
    demo_path_configuration()
