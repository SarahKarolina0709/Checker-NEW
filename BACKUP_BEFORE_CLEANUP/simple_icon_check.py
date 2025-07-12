"""
Einfacher Icon-Test für die Checker-App.
Testet alle verfügbaren Icons ohne vollständige App-Initialisierung.
"""

import os

def simple_icon_test():
    """Führt einen einfachen Test aller Icon-Dateien durch"""
    
    print("🔍 EINFACHER ICON-TEST GESTARTET")
    print("="*60)
    
    # 1. Teste alle verfügbaren Icon-Dateien
    print("\n1. VERFÜGBARE ICON-DATEIEN:")
    print("-" * 40)
    
    icons_dir = "icons"
    available_files = []
    
    if os.path.exists(icons_dir):
        for file in os.listdir(icons_dir):
            if file.endswith('.png'):
                available_files.append(file)
    else:
        print(f"   ❌ Icons-Ordner nicht gefunden: {icons_dir}")
        return
    
    available_files.sort()
    
    print(f"   📁 Icons-Ordner: {os.path.abspath(icons_dir)}")
    print(f"   📊 Gesamt: {len(available_files)} Icon-Dateien gefunden\n")
    
    # Zeige alle Icons in Kategorien
    categories = {
        'Dateien & Dokumente': [],
        'Navigation': [],
        'Aktionen': [],
        'UI-Elemente': [],
        'Kommunikation': [],
        'Sicherheit': [],
        'System': [],
        'Medien': [],
        'Sonstige': []
    }
    
    # Kategorisierung
    for file in available_files:
        icon_name = file.replace('.png', '')
        
        if any(keyword in icon_name for keyword in ['file', 'doc', 'pdf', 'txt', 'image']):
            categories['Dateien & Dokumente'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['arrow', 'home', 'folder', 'menu']):
            categories['Navigation'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['check', 'done', 'plus', 'close', 'edit', 'save', 'export', 'import', 'upload', 'download']):
            categories['Aktionen'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['settings', 'theme', 'options', 'help', 'info', 'about']):
            categories['UI-Elemente'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['mail', 'speech', 'share', 'connect']):
            categories['Kommunikation'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['lock', 'key', 'padlock', 'security']):
            categories['Sicherheit'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['workflow', 'analytics', 'clock', 'restart', 'play', 'quit', 'error', 'success']):
            categories['System'].append(icon_name)
        elif any(keyword in icon_name for keyword in ['picture', 'photo', 'media']):
            categories['Medien'].append(icon_name)
        else:
            categories['Sonstige'].append(icon_name)
    
    # Zeige Kategorien
    for category, icons in categories.items():
        if icons:  # Nur nicht-leere Kategorien anzeigen
            print(f"📁 {category} ({len(icons)} Icons):")
            print("-" * (len(category) + 15))
            
            # Zeige Icons in 3 Spalten
            for i in range(0, len(icons), 3):
                row_icons = icons[i:i+3]
                row_text = "   ".join(f"{icon:<20}" for icon in row_icons)
                print(f"   {row_text}")
            print()
    
    # 2. Teste wichtige Icon-Mappings
    print("\n2. WICHTIGE ICON-MAPPINGS:")
    print("-" * 40)
    
    important_mappings = [
        ('rocket', 'Für Launch/Start-Funktionen'),
        ('quality', 'Für Qualitätsprüfungen'),
        ('pdf-file', 'Für PDF-Dokumente'),
        ('doc-file', 'Für Word-Dokumente'),
        ('txt-file', 'Für Text-Dateien'),
        ('upload', 'Für Datei-Upload'),
        ('download', 'Für Datei-Download'),
        ('import', 'Für Daten-Import'),
        ('link', 'Für Verbindungen'),
        ('chain', 'Für Verkettungen'),
        ('user', 'Für Benutzer-Profile'),
        ('settings', 'Für Einstellungen'),
        ('workflow', 'Für Workflow-Prozesse'),
        ('analytics', 'Für Datenanalyse'),
        ('check-mark', 'Für Bestätigungen'),
        ('trash-can', 'Für Löschfunktionen'),
    ]
    
    available_names = [f.replace('.png', '') for f in available_files]
    
    for icon_name, description in important_mappings:
        if icon_name in available_names:
            status = "✅"
        else:
            status = "❌"
        
        print(f"   {status} {icon_name:<15} | {description}")
    
    # 3. Fehlende Icons identifizieren
    print("\n3. FEHLENDE WICHTIGE ICONS:")
    print("-" * 40)
    
    missing_icons = [icon for icon, desc in important_mappings if icon.replace('.png', '') not in available_names]
    
    if missing_icons:
        print("   💡 Folgende wichtige Icons fehlen noch:")
        for icon in missing_icons:
            print(f"      - {icon}.png")
    else:
        print("   🎉 Alle wichtigen Icons sind vorhanden!")
    
    # 4. Zusammenfassung
    print("\n4. ZUSAMMENFASSUNG:")
    print("="*60)
    print(f"   📁 Gefundene Icon-Dateien: {len(available_files)}")
    print(f"   ✅ Verfügbare wichtige Icons: {len(important_mappings) - len(missing_icons)}")
    print(f"   ❌ Fehlende wichtige Icons: {len(missing_icons)}")
    
    success_rate = ((len(important_mappings) - len(missing_icons)) / len(important_mappings)) * 100
    print(f"   📊 Verfügbarkeitsrate: {success_rate:.1f}%")
    
    if success_rate >= 90:
        print("\n   🎉 AUSGEZEICHNET! Fast alle Icons sind verfügbar.")
    elif success_rate >= 75:
        print("\n   👍 GUT! Die meisten wichtigen Icons sind verfügbar.")
    elif success_rate >= 50:
        print("\n   ⚠️  OKAY! Es fehlen noch einige wichtige Icons.")
    else:
        print("\n   ❌ VERBESSERUNG NÖTIG! Viele wichtige Icons fehlen.")
    
    print("\n" + "="*60)
    print("🔍 EINFACHER ICON-TEST ABGESCHLOSSEN")

if __name__ == "__main__":
    simple_icon_test()
