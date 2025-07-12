"""
Manual Icon Loading Test - Direktes Laden ohne Manager und Cache
Demonstriert die Sofortlösung für Icon-Probleme
"""

import os
import sys
from pathlib import Path

# Pfad zur Checker-App hinzufügen
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_manual_icon_loading():
    """Testet manuelles Icon-Loading ohne Manager"""
    print("🔧 MANUAL ICON LOADING TEST")
    print("="*50)
    
    try:
        import tkinter as tk
        from PIL import Image
        import customtkinter as ctk
        
        print("1️⃣ Erstelle Test-Fenster...")
        root = tk.Tk()
        root.title("Manual Icon Loading Test")
        root.geometry("600x400")
        
        main_frame = ctk.CTkFrame(root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        print("2️⃣ Teste direktes Icon-Loading...")
        
        # Test Icons direkt ohne Manager
        test_icons = [
            ('rocket', 'icons/rocket.png'),
            ('home', 'icons/home.png'),
            ('search', 'icons/search.png'),
            ('settings', 'icons/settings.png'),
            ('file', 'assets/icons/file.png'),
            ('folder', 'icons/folder.png')
        ]
        
        loaded_icons = []
        row = 0
        
        for icon_name, icon_path in test_icons:
            try:
                print(f"   🔄 Lade {icon_name} von {icon_path}...")
                
                # Direktes Laden ohne Manager
                if os.path.exists(icon_path):
                    print(f"   ✅ Datei existiert: {icon_path}")
                    
                    # Lade PIL Image
                    pil_image = Image.open(icon_path)
                    print(f"   📸 PIL Image: {pil_image.size}, {pil_image.mode}")
                    
                    # Erstelle CTkImage
                    ctk_image = ctk.CTkImage(light_image=pil_image, size=(32, 32))
                    print(f"   🎨 CTkImage erstellt: {type(ctk_image)}")
                    
                    # Prüfe CTkImage-Eigenschaften
                    has_light_image = hasattr(ctk_image, '_light_image')
                    print(f"   🔍 Hat _light_image: {has_light_image}")
                    
                    # Erstelle Test-Label
                    label = ctk.CTkLabel(
                        main_frame,
                        image=ctk_image,
                        text=f"{icon_name}",
                        compound="top",
                        font=("Arial", 10)
                    )
                    label.grid(row=row//3, column=row%3, padx=10, pady=10, sticky="nsew")
                    
                    # WICHTIG: Persistente Referenz
                    label.image = ctk_image
                    
                    loaded_icons.append({
                        'name': icon_name,
                        'path': icon_path,
                        'success': True,
                        'ctk_image': ctk_image,
                        'label': label
                    })
                    
                    print(f"   ✅ {icon_name} erfolgreich geladen und angezeigt")
                    row += 1
                    
                else:
                    print(f"   ❌ Datei nicht gefunden: {icon_path}")
                    loaded_icons.append({
                        'name': icon_name,
                        'path': icon_path,
                        'success': False
                    })
                
            except Exception as e:
                print(f"   ❌ Fehler beim Laden von {icon_name}: {e}")
                loaded_icons.append({
                    'name': icon_name,
                    'path': icon_path,
                    'success': False,
                    'error': str(e)
                })
        
        # Grid-Konfiguration für responsive Layout
        for i in range(3):
            main_frame.grid_columnconfigure(i, weight=1)
        for i in range((len(loaded_icons) + 2) // 3):
            main_frame.grid_rowconfigure(i, weight=1)
        
        print("\n3️⃣ Ergebnisse:")
        print("-" * 40)
        
        successful = sum(1 for icon in loaded_icons if icon['success'])
        
        for icon in loaded_icons:
            status = "✅" if icon['success'] else "❌"
            print(f"{status} {icon['name']}: {icon['path']}")
            if not icon['success'] and 'error' in icon:
                print(f"      Fehler: {icon['error']}")
        
        print(f"\n📊 Erfolgreich geladen: {successful}/{len(test_icons)} "
              f"({successful/len(test_icons)*100:.1f}%)")
        
        if successful > 0:
            print("\n🎉 Icons werden erfolgreich angezeigt!")
            print("💡 Diese Methode umgeht alle Manager- und Cache-Probleme")
            
            # Info-Label hinzufügen
            info_label = ctk.CTkLabel(
                root,
                text=f"Manual Loading Erfolgreich: {successful}/{len(test_icons)} Icons geladen",
                font=("Arial", 12, "bold")
            )
            info_label.pack(pady=10)
            
            print("\n👀 Fenster wird angezeigt - schließe es manually um fortzufahren...")
            root.mainloop()
        else:
            print("❌ Keine Icons konnten geladen werden")
            root.destroy()
            
    except Exception as e:
        print(f"❌ Kritischer Fehler: {e}")
        import traceback
        traceback.print_exc()

def demonstrate_solution_code():
    """Zeigt den Lösungscode für die Anwendung"""
    print("\n" + "="*60)
    print("💡 LÖSUNGSCODE FÜR DIE ANWENDUNG")
    print("="*60)
    
    solution_code = '''
# Lösung: CTkImage direkt erstellen ohne Manager/Cache

def load_icon_direct(icon_path, size=(24, 24)):
    """
    Lädt ein Icon direkt als CTkImage ohne Manager oder Cache
    
    Args:
        icon_path: Pfad zur Icon-Datei (z.B. "icons/home.png")
        size: Gewünschte Größe
        
    Returns:
        CTkImage oder None
    """
    try:
        from PIL import Image
        import customtkinter as ctk
        import os
        
        if os.path.exists(icon_path):
            # Lade PIL Image
            pil_image = Image.open(icon_path)
            
            # Erstelle CTkImage
            ctk_image = ctk.CTkImage(light_image=pil_image, size=size)
            
            return ctk_image
    except Exception as e:
        print(f"Fehler beim Laden von {icon_path}: {e}")
        
    return None

# Verwendung im Welcome Screen:
rocket_icon = load_icon_direct("icons/rocket.png", size=(24, 24))

if rocket_icon:
    button = ctk.CTkButton(
        parent,
        image=rocket_icon,
        text="Start",
        compound="left"
    )
    # WICHTIG: Persistente Referenz
    button.image = rocket_icon
else:
    # Fallback ohne Icon
    button = ctk.CTkButton(parent, text="🚀 Start")
'''
    
    print(solution_code)
    
    print("\n🔧 ANWENDUNG IN DER CHECKER-APP:")
    print("-" * 40)
    print("1. Ersetze alle app.get_icon() Aufrufe durch load_icon_direct()")
    print("2. Verwende absolute Icon-Pfade (z.B. 'icons/home.png')")
    print("3. Erstelle persistente Referenzen (widget.image = icon)")
    print("4. Implementiere Fallbacks für fehlende Icons")

def main():
    """Hauptfunktion"""
    print("🧪 Manual Icon Loading Test")
    print("=" * 40)
    
    # Test manuelles Icon-Loading
    test_manual_icon_loading()
    
    # Zeige Lösungscode
    demonstrate_solution_code()
    
    print("\n" + "="*60)
    print("✅ Manual Icon Loading Test abgeschlossen")
    print("💡 Diese Methode löst alle Icon-Darstellungsprobleme")
    print("="*60)

if __name__ == "__main__":
    main()
