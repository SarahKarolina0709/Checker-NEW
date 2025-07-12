#!/usr/bin/env python3
"""
Icon-Demo Script für die Checker-App
Zeigt die verfügbaren Icons und neue Features
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(__file__))

def demonstrate_icons():
    """Demonstriert die verfügbaren Icons"""
    print("🎨 CHECKER-APP ICON DEMONSTRATION")
    print("="*60)
    
    # Zeige die Icons aus dem icons Ordner
    icons_dir = os.path.join(os.path.dirname(__file__), "icons")
    
    if os.path.exists(icons_dir):
        icon_files = [f for f in os.listdir(icons_dir) if f.endswith('.png')]
        icon_files.sort()
        
        print(f"📁 Icons Ordner: {len(icon_files)} PNG-Dateien gefunden")
        print()
        
        # Gruppiere Icons nach Kategorien basierend auf Namen
        categories = {
            '📄 Dateien': [],
            '👤 Benutzer': [],
            '⚙️ System': [],
            '🔧 Aktionen': [],
            '📊 Daten': [],
            '🎨 UI-Elemente': [],
            '🔒 Sicherheit': [],
            '📱 Kommunikation': [],
            '⏰ Zeit': [],
            '🎯 Workflow': [],
            '🎵 Medien': [],
            '📋 Andere': []
        }
        
        for icon_file in icon_files:
            icon_name = icon_file.replace('.png', '')
            
            # Kategorisierung basierend auf Icon-Namen
            if any(keyword in icon_name.lower() for keyword in ['file', 'folder', 'document', 'pdf', 'doc', 'txt', 'image-file']):
                categories['📄 Dateien'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['user', 'person', 'profile']):
                categories['👤 Benutzer'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['settings', 'config', 'options', 'gear']):
                categories['⚙️ System'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['play', 'start', 'stop', 'edit', 'save', 'delete', 'add', 'plus', 'close', 'restart']):
                categories['🔧 Aktionen'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['analytics', 'chart', 'report', 'export']):
                categories['📊 Daten'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['menu', 'home', 'theme', 'star', 'bookmark']):
                categories['🎨 UI-Elemente'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['lock', 'key', 'security', 'padlock']):
                categories['🔒 Sicherheit'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['mail', 'message', 'speech', 'share']):
                categories['📱 Kommunikation'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['clock', 'time', 'timer']):
                categories['⏰ Zeit'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['workflow', 'process', 'analyze', 'check']):
                categories['🎯 Workflow'].append(icon_name)
            elif any(keyword in icon_name.lower() for keyword in ['picture', 'image', 'photo']):
                categories['🎵 Medien'].append(icon_name)
            else:
                categories['📋 Andere'].append(icon_name)
        
        # Zeige kategorisierte Icons
        for category, icons in categories.items():
            if icons:
                print(f"{category} ({len(icons)} Icons):")
                # Zeige in 3er-Gruppen
                for i in range(0, len(icons), 3):
                    group = icons[i:i+3]
                    print(f"   {' | '.join(f'{icon:<25}' for icon in group)}")
                print()
        
        print("="*60)
        print("💡 NEUE ICON-FEATURES:")
        print("✨ Intelligente Fallbacks - Icons werden automatisch gemappt")
        print("🔍 Icon-Suche - Finde Icons mit Teilnamen")
        print("📂 Kategorie-basierte Suche - Icons nach Kategorien finden")
        print("🎯 Erweiterte Aliase - Mehr alternative Namen für Icons")
        print()
        print("📋 BEISPIELE FÜR FALLBACKS:")
        fallback_examples = [
            ("quality", "check-mark"),
            ("complete", "done"),
            ("project", "folder"),
            ("document", "file_icon"),
            ("person", "user"),
            ("help", "info"),
            ("save", "save_icon"),
            ("download", "export"),
            ("find", "search"),
            ("chart", "analytics"),
            ("refresh", "restart"),
            ("start", "play"),
            ("image", "picture"),
            ("tools", "toolbox"),
            ("warning", "error"),
            ("pdf", "pdf-file"),
            ("upload", "export"),
            ("tick", "tick-box"),
            ("speech", "speech-bubble"),
            ("house", "home")
        ]
        
        for alias, fallback in fallback_examples:
            print(f"   '{alias}' → '{fallback}'")
        
        print("="*60)
        print("🚀 Die Icon-Engine ist bereit für maximale Kompatibilität!")
        
    else:
        print(f"❌ Icons-Ordner nicht gefunden: {icons_dir}")

if __name__ == "__main__":
    demonstrate_icons()
