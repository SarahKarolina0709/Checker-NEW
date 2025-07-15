#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload-Test für die Checker-Anwendung
"""

import os
import sys

def test_upload_function():
    """Testet die Upload-Funktion direkt."""
    print("🧪 Direkter Upload-Test gestartet...\n")
    
    # Test-Datei erstellen
    test_file = "test_upload_file.txt"
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Test-Inhalt für Upload-Test\n")
        f.write("Diese Datei sollte im 01_Ausgangstext Ordner landen.\n")
    
    print(f"📄 Test-Datei erstellt: {test_file}")
    print(f"📄 Datei existiert: {os.path.exists(test_file)}")
    print(f"📄 Dateigröße: {os.path.getsize(test_file)} Bytes")
    
    # Simulation der Upload-Parameter
    files = [os.path.abspath(test_file)]
    test_customer = {
        'id': 1,
        'name': 'Test Firma GmbH',
        'code': 'TST',
        'email': 'info@testfirma.de',
        'contact': 'Max Mustermann'
    }
    
    project_paths = {
        'current_directory': os.getcwd()
    }
    
    print(f"📋 Upload-Parameter:")
    print(f"   Dateien: {files}")
    print(f"   Kunde: {test_customer}")
    print(f"   Projekt-Pfad: {project_paths}")
    
    # Upload-Funktion simulieren
    from datetime import datetime
    import shutil
    
    def clean_folder_name(name):
        invalid_chars = '<>:"/\\|?*&'
        clean_name = ''.join(c if c not in invalid_chars else '_' for c in name)
        clean_name = '_'.join(clean_name.split())
        return clean_name.strip('_')[:50] or "Kunde"
    
    def copy_files_to_workflow(files, customer, base_path):
        try:
            print(f"\n🔄 Upload-Simulation gestartet...")
            
            # Ordnerstruktur erstellen
            customer_name_clean = clean_folder_name(customer['name'])
            customer_folder = os.path.join(base_path, customer_name_clean)
            
            today = datetime.now()
            date_folder = os.path.join(customer_folder, today.strftime("%Y-%m-%d"))
            ausgangstext_folder = os.path.join(date_folder, "01_Ausgangstext")
            
            print(f"📂 Kundenordner: {customer_folder}")
            print(f"📅 Datumsordner: {date_folder}")
            print(f"📝 Ausgangstext-Ordner: {ausgangstext_folder}")
            
            # Ordner erstellen
            os.makedirs(ausgangstext_folder, exist_ok=True)
            print(f"✅ Ordner erstellt: {os.path.exists(ausgangstext_folder)}")
            
            # Dateien kopieren
            copied_count = 0
            for file_path in files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    destination = os.path.join(ausgangstext_folder, file_name)
                    
                    print(f"📋 Kopiere {file_name} nach {destination}")
                    shutil.copy2(file_path, destination)
                    copied_count += 1
                    
                    print(f"✅ Kopiert: {os.path.exists(destination)}")
                    
                    # Dateiinhalt prüfen
                    if os.path.exists(destination):
                        with open(destination, 'r', encoding='utf-8') as f:
                            content = f.read()
                        print(f"📄 Dateiinhalt in Ziel:\n{content}")
            
            return {'success': True, 'copied_count': copied_count}
            
        except Exception as e:
            import traceback
            print(f"❌ Fehler: {e}")
            print(f"🔍 Traceback: {traceback.format_exc()}")
            return {'success': False, 'error': str(e)}
    
    # Test ausführen
    result = copy_files_to_workflow(files, test_customer, project_paths['current_directory'])
    
    print(f"\n📊 Test-Ergebnis:")
    print(f"   Erfolgreich: {result['success']}")
    if result['success']:
        print(f"   Kopierte Dateien: {result['copied_count']}")
    else:
        print(f"   Fehler: {result.get('error', 'Unbekannt')}")
    
    # Aufräumen
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"\n🧹 Test-Datei gelöscht: {test_file}")
    
    print(f"\n✅ Upload-Test abgeschlossen!")

if __name__ == "__main__":
    test_upload_function()
