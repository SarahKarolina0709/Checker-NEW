"""
Test für erweiterte Kundenerkennung mit Fuzzy Matching
"""

import os
import sys
import shutil
from datetime import datetime

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_fuzzy_customer_matching():
    """Test die erweiterte Kundenerkennung"""
    
    print("🔍 Test: Erweiterte Kundenerkennung mit Fuzzy Matching")
    print("=" * 60)
    
    try:
        from kunden_manager_v2 import KundenManagerV2
    except ImportError as e:
        print(f"❌ Fehler beim Import: {e}")
        return False
    
    # Verwende ein Test-Verzeichnis
    test_dir = "Fuzzy_Test_Projekte"
    
    # Aufräumen
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    print(f"📁 Erstelle Test-Verzeichnis: {test_dir}")
    
    # Initialisiere KundenManagerV2
    km = KundenManagerV2(test_dir)
    
    # Erstelle einige Test-Kunden
    test_kunden = [
        "Musterfirma_GmbH",
        "Tech_Solutions_AG", 
        "Innovate_Corp",
        "Digital_Dynamics_Ltd",
        "Green_Energy_Systems"
    ]
    
    print(f"\n🏗️  Erstelle {len(test_kunden)} Test-Kunden...")
    
    for kunde in test_kunden:
        result = km.erstelle_projekt_ordner(
            kundenname=kunde,
            projektname="Initial_Projekt",
            datum="2025-01-15"
        )
        if result:
            print(f"   ✅ {kunde}")
        else:
            print(f"   ❌ {kunde}")
    
    # Jetzt teste Fuzzy Matching
    print(f"\n🎯 Teste Fuzzy Matching...")
    
    test_suchen = [
        # Exakte Treffer
        ("Musterfirma_GmbH", "Exakte Übereinstimmung"),
        ("Tech_Solutions_AG", "Exakte Übereinstimmung"),
        
        # Ähnliche Namen (sollten gefunden werden)
        ("Musterfirma GmbH", "Ähnlich (Unterstrich vs Leerzeichen)"),
        ("musterfirma gmbh", "Ähnlich (Groß-/Kleinschreibung)"),
        ("Tech Solutions AG", "Ähnlich (Unterstriche entfernt)"),
        ("tech-solutions-ag", "Ähnlich (Bindestrich statt Unterstrich)"),
        ("Innovate Corp", "Ähnlich (Unterstrich entfernt)"),
        ("Digital Dynamics", "Ähnlich (Ltd weggelassen)"),
        ("Green Energy", "Ähnlich (Systems weggelassen)"),
        
        # Tippfehler (sollten eventuell gefunden werden)
        ("Musterfirma_GmBH", "Tippfehler"),
        ("Tech_Solution_AG", "Tippfehler (fehlende 's')"),
        ("Innovate_Crop", "Tippfehler (p statt r)"),
        
        # Komplett andere Namen (sollten nicht gefunden werden)
        ("Andere_Firma_GmbH", "Komplett anderer Name"),
        ("Unbekannt_Ltd", "Unbekannt"),
    ]
    
    print(f"\n📊 Teste {len(test_suchen)} Suchanfragen...")
    
    for suchbegriff, beschreibung in test_suchen:
        customer_check = km.customer_exists(suchbegriff)
        
        # Handle unterschiedliche Rückgabe-Formate
        if len(customer_check) == 3:
            exists, existing_customer, similarity_score = customer_check
        elif len(customer_check) == 2:
            exists, existing_customer = customer_check
            similarity_score = 0.0
        else:
            exists, existing_customer, similarity_score = False, None, 0.0
        
        status = "✅" if exists else "❌"
        score_text = f" (Score: {similarity_score:.1f}%)" if similarity_score > 0 else ""
        
        print(f"   {status} '{suchbegriff}' -> {beschreibung}")
        if exists:
            print(f"      🎯 Gefunden: '{existing_customer}'{score_text}")
        
        print()
    
    # Teste auch die Projektlistung
    print(f"\n📋 Teste Projektlisting...")
    
    for kunde in test_kunden[:3]:  # Teste nur die ersten 3
        projekte = km.liste_kundenprojekte(kunde)
        print(f"   📁 {kunde}: {len(projekte)} Projekte")
        for projekt in projekte:
            print(f"      • {projekt}")
    
    print(f"\n🌳 Aktuelle Ordnerstruktur:")
    print_ordnerstruktur(test_dir, max_depth=2)
    
    # Aufräumen
    cleanup = input(f"\n❓ Test-Verzeichnis '{test_dir}' löschen? (y/n): ").lower().strip()
    if cleanup == 'y':
        shutil.rmtree(test_dir)
        print("🧹 Test-Verzeichnis gelöscht")
    else:
        print(f"📁 Test-Verzeichnis bleibt erhalten: {test_dir}")
    
    print("\n🎉 Test abgeschlossen!")
    return True

def print_ordnerstruktur(directory, prefix="", max_depth=3, current_depth=0):
    """Zeigt die Ordnerstruktur hierarchisch an"""
    
    if current_depth > max_depth or not os.path.exists(directory):
        return
    
    try:
        items = sorted(os.listdir(directory))
        
        for i, item in enumerate(items):
            item_path = os.path.join(directory, item)
            is_last = i == len(items) - 1
            
            if os.path.isdir(item_path):
                print(f"{prefix}{'└── ' if is_last else '├── '}📁 {item}/")
                if current_depth < max_depth:
                    extension = "    " if is_last else "│   "
                    print_ordnerstruktur(item_path, prefix + extension, max_depth, current_depth + 1)
            else:
                print(f"{prefix}{'└── ' if is_last else '├── '}📄 {item}")
                
    except PermissionError:
        print(f"{prefix}❌ Zugriff verweigert")

if __name__ == "__main__":
    test_fuzzy_customer_matching()
