#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Umfassender Debug-Test für Upload-Problem
"""

import os
import shutil
from datetime import datetime

def debug_upload_problem():
    """Detaillierte Analyse des Upload-Problems."""
    print("🔍 Umfassender Upload-Debug gestartet...\n")
    
    # Test-Kunde
    test_customer = {
        'id': 999,
        'name': 'Debug Test GmbH & Co. KG',
        'code': 'DBG',
        'email': 'debug@test.de',
        'contact': 'Debug Manager'
    }
    
    # Test-Datei erstellen
    test_file = "debug_test_upload.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Debug Upload Test\n")
        f.write(f"Erstellt: {datetime.now()}\n")
        f.write("Diese Datei testet das Upload-System.\n")
    
    print(f"📄 Debug-Datei erstellt: {test_file}")
    
    # Funktion aus der Anwendung nachbauen
    def clean_folder_name(name):
        """Bereinigt einen Namen für die Verwendung als Ordnername."""
        print(f"🔧 Ordnername vor Bereinigung: '{name}'")
        
        # Ungültige Zeichen für Windows-Ordnernamen entfernen/ersetzen
        invalid_chars = '<>:"/\\|?*&'
        clean_name = ''.join(c if c not in invalid_chars else '_' for c in name)
        
        # Umlaute ersetzen
        umlaut_map = {'ä': 'ae', 'ö': 'oe', 'ü': 'ue', 'ß': 'ss', 
                     'Ä': 'AE', 'Ö': 'OE', 'Ü': 'UE'}
        for umlaut, replacement in umlaut_map.items():
            clean_name = clean_name.replace(umlaut, replacement)
        
        # Zusätzliche problematische Zeichen ersetzen
        replacements = {
            '.': '_',  
            ',': '_',  
            ';': '_',  
            '(': '_',  
            ')': '_',
            '[': '_',
            ']': '_',
            '{': '_',
            '}': '_'
        }
        
        for char, replacement in replacements.items():
            clean_name = clean_name.replace(char, replacement)
        
        # Mehrfache Leerzeichen und Unterstriche bereinigen
        clean_name = '_'.join(part for part in clean_name.split() if part)
        clean_name = '_'.join(part for part in clean_name.split('_') if part)
        
        # Führende/abschließende Unterstriche entfernen
        clean_name = clean_name.strip('_')
        
        # Maximale Länge begrenzen
        if len(clean_name) > 50:
            clean_name = clean_name[:50].rstrip('_')
        
        # Sicherstellen, dass der Name nicht leer ist
        if not clean_name:
            clean_name = "Kunde"
        
        print(f"🔧 Ordnername nach Bereinigung: '{clean_name}'")
        return clean_name
    
    def copy_files_to_customer_workflow_folder(files, customer, base_path):
        """Debug-Version der Upload-Funktion."""
        try:
            print(f"🔄 Upload gestartet für {len(files)} Datei(en)")
            print(f"👤 Aktueller Kunde: {customer}")
            print(f"📁 Basis-Pfad: {base_path}")
            
            # Kundenordner erstellen (Name bereinigen für Dateisystem)
            customer_name_clean = clean_folder_name(customer['name'])
            customer_folder = os.path.join(base_path, customer_name_clean)
            print(f"📂 Kundenordner: {customer_folder}")
            
            # Datumsordner erstellen (YYYY-MM-DD)
            today = datetime.now()
            date_folder_name = today.strftime("%Y-%m-%d")
            date_folder = os.path.join(customer_folder, date_folder_name)
            print(f"📅 Datumsordner: {date_folder}")
            
            # Workflow-Ordnerstruktur erstellen
            workflow_folders = {
                "01_Ausgangstext": "Hochgeladene Ausgangsdateien",
                "02_Angebot": "Angebotsdokumente und Kostenvoranschläge", 
                "03_Prüfung": "Qualitätsprüfung und Korrektur",
                "04_Finalisierung": "Finale Dokumente und Auslieferung"
            }
            
            # Alle Ordner erstellen
            ausgangstext_folder = os.path.join(date_folder, "01_Ausgangstext")
            print(f"📝 Ausgangstext-Ordner: {ausgangstext_folder}")
            
            for folder_name, description in workflow_folders.items():
                folder_path = os.path.join(date_folder, folder_name)
                print(f"🏗️ Erstelle Ordner: {folder_path}")
                os.makedirs(folder_path, exist_ok=True)
                print(f"✅ Ordner erstellt: {os.path.exists(folder_path)}")
                
                # Info-Datei in jeden Ordner
                info_file = os.path.join(folder_path, "_INFO.txt")
                if not os.path.exists(info_file):
                    with open(info_file, 'w', encoding='utf-8') as f:
                        f.write(f"📁 {folder_name}\n")
                        f.write(f"📝 {description}\n")
                        f.write(f"👥 Kunde: {customer['name']}\n")
                        f.write(f"📅 Erstellt: {today.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    print(f"📄 Info-Datei erstellt: {info_file}")
            
            # Dateien in Ausgangstext-Ordner kopieren
            copied_count = 0
            print(f"📋 Beginne Datei-Kopierung nach: {ausgangstext_folder}")
            print(f"📋 Ausgangstext-Ordner existiert: {os.path.exists(ausgangstext_folder)}")
            
            for i, file_path in enumerate(files):
                print(f"📄 Datei {i+1}/{len(files)}: {file_path}")
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    destination = os.path.join(ausgangstext_folder, file_name)
                    print(f"📋 Kopiere nach: {destination}")
                    
                    # Datei kopieren (überschreiben falls vorhanden)
                    shutil.copy2(file_path, destination)
                    copied_count += 1
                    print(f"✅ Kopiert: {os.path.exists(destination)}")
                    
                    # Dateiinhalt vergleichen
                    if os.path.exists(destination):
                        with open(file_path, 'r', encoding='utf-8') as f:
                            original_content = f.read()
                        with open(destination, 'r', encoding='utf-8') as f:
                            copied_content = f.read()
                        
                        content_match = original_content == copied_content
                        print(f"📄 Dateiinhalt übereinstimmend: {content_match}")
                        if not content_match:
                            print(f"⚠️ Original: {len(original_content)} Zeichen")
                            print(f"⚠️ Kopie: {len(copied_content)} Zeichen")
                    
                else:
                    print(f"❌ Datei nicht gefunden: {file_path}")
            
            print(f"📊 Upload-Ergebnis: {copied_count} kopiert")
            
            # Verzeichnisinhalt prüfen
            print(f"\n📂 Inhalt des Ausgangstext-Ordners:")
            if os.path.exists(ausgangstext_folder):
                files_in_folder = os.listdir(ausgangstext_folder)
                for file in files_in_folder:
                    file_path = os.path.join(ausgangstext_folder, file)
                    file_size = os.path.getsize(file_path)
                    print(f"   📄 {file} ({file_size} Bytes)")
            else:
                print("   ❌ Ordner existiert nicht!")
            
            return {
                'success': True,
                'copied_count': copied_count,
                'customer_folder': customer_name_clean,
                'date_folder': date_folder_name,
                'workflow_folder': "01_Ausgangstext",
                'full_path': ausgangstext_folder
            }
            
        except Exception as e:
            import traceback
            error_details = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            print(f"❌ Upload-Fehler: {error_details}")
            return {
                'success': False,
                'error': error_details,
                'copied_count': 0
            }
    
    # Test ausführen
    files = [os.path.abspath(test_file)]
    base_path = os.getcwd()
    
    result = copy_files_to_customer_workflow_folder(files, test_customer, base_path)
    
    print(f"\n📊 Final Test-Ergebnis:")
    print(f"   Erfolgreich: {result['success']}")
    if result['success']:
        print(f"   Kopierte Dateien: {result['copied_count']}")
        print(f"   Vollständiger Pfad: {result['full_path']}")
        
        # Nochmalige Prüfung der Datei
        target_file = os.path.join(result['full_path'], os.path.basename(test_file))
        print(f"\n🔍 Finale Prüfung:")
        print(f"   Zieldatei: {target_file}")
        print(f"   Existiert: {os.path.exists(target_file)}")
        if os.path.exists(target_file):
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"   Inhalt: {len(content)} Zeichen")
            print(f"   Erste Zeile: {content.split(chr(10))[0] if content else 'Leer'}")
    else:
        print(f"   Fehler: {result.get('error', 'Unbekannt')}")
    
    # Aufräumen
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n🧹 Debug-Datei gelöscht: {test_file}")
    
    print(f"\n✅ Debug-Test abgeschlossen!")
    print(f"🗂️ Erstellte Ordnerstruktur kann manuell überprüft werden")

if __name__ == "__main__":
    debug_upload_problem()
