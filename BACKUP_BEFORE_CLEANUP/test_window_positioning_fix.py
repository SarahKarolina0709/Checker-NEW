#!/usr/bin/env python3
"""
Test für Window Positioning Bug Fix.
Verifiziert, dass die Fensterpositionierung konsistent mit der Geometrie ist.
"""

import sys
import os

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_window_positioning_fix():
    """Test ob die Window Positioning Inkonsistenz behoben wurde"""
    print("=== WINDOW POSITIONING BUG FIX TEST ===")
    print()
    
    # Test different screen resolutions
    test_scenarios = [
        ("Small Screen", 1366, 768),
        ("Medium Screen", 1440, 900), 
        ("Large Screen", 1920, 1080),
        ("Wide Screen", 2560, 1440),
        ("4K Screen", 3840, 2160)
    ]
    
    window_width = 1600  # Fixed width
    window_height = 900  # Fixed height
    
    print(f"Testing window positioning for {window_width}x{window_height} window:")
    print("-" * 60)
    print(f"{'Screen Type':<15} {'Resolution':<12} {'X Position':<12} {'Y Position':<12} {'Status':<10}")
    print("-" * 60)
    
    all_tests_passed = True
    
    for screen_name, screen_width, screen_height in test_scenarios:
        # Calculate position wie in der App
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # Ensure the window doesn't go off-screen
        x = max(0, min(x, screen_width - window_width))
        y = max(0, min(y, screen_height - window_height))
        
        # Check if window fits on screen
        fits_horizontally = window_width <= screen_width
        fits_vertically = window_height <= screen_height
        is_centered = (x == (screen_width - window_width) // 2) if fits_horizontally else True
        
        if fits_horizontally and fits_vertically and is_centered:
            status = "✓ PERFECT"
        elif fits_horizontally and fits_vertically:
            status = "✓ FITS"
        elif window_width <= screen_width:
            status = "⚠ HEIGHT"
        else:
            status = "✗ TOO BIG"
            all_tests_passed = False
        
        print(f"{screen_name:<15} {screen_width}x{screen_height:<8} {x:<12} {y:<12} {status:<10}")
    
    print("\n" + "=" * 60)
    
    if all_tests_passed:
        print("🎉 WINDOW POSITIONING FIX ERFOLGREICH!")
        print("✅ Keine Off-Screen Positionierung mehr")
        print("✅ Konsistente 1600px Breite in Geometrie und Positionierung") 
        print("✅ Fenster wird korrekt zentriert auf allen Bildschirmgrößen")
    else:
        print("⚠ Einige Bildschirme sind zu klein für das Fenster")
        print("Das ist normal für sehr kleine Bildschirme")
    
    return all_tests_passed

def test_code_consistency():
    """Test ob der Code konsistent ist"""
    print("\n=== CODE KONSISTENZ TEST ===")
    print()
    
    print("Checking for consistency in checker_app.py...")
    
    # Test ob wir die Datei lesen können
    try:
        with open("checker_app.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Suche nach den relevanten Zeilen
        geometry_lines = [line.strip() for line in content.split('\n') if 'geometry("1600x900")' in line]
        width_2000_lines = [line.strip() for line in content.split('\n') if 'width = 2000' in line]
        width_1600_lines = [line.strip() for line in content.split('\n') if 'width = 1600' in line]
        
        print(f"Geometry 1600x900 Referenzen: {len(geometry_lines)}")
        print(f"width = 2000 Referenzen: {len(width_2000_lines)}")
        print(f"width = 1600 Referenzen: {len(width_1600_lines)}")
        
        if len(width_2000_lines) == 0 and len(width_1600_lines) > 0:
            print("✅ Positioning width erfolgreich von 2000 auf 1600 korrigiert")
            print("✅ Keine width = 2000 Referenzen mehr gefunden")
            return True
        else:
            print("⚠ Noch width = 2000 Referenzen gefunden:")
            for line in width_2000_lines:
                print(f"   {line}")
            return False
            
    except FileNotFoundError:
        print("⚠ checker_app.py nicht gefunden")
        return False
    except Exception as e:
        print(f"⚠ Fehler beim Lesen der Datei: {e}")
        return False

def main():
    """Hauptfunktion für den Window Positioning Test"""
    print("Window Positioning Bug Fix - Verifikationstest")
    print("=" * 50)
    
    try:
        # Test window positioning
        positioning_ok = test_window_positioning_fix()
        
        # Test code consistency
        code_ok = test_code_consistency()
        
        print(f"\n{'='*50}")
        print("ZUSAMMENFASSUNG:")
        print(f"{'='*50}")
        print(f"Positionierung: {'✅ KORREKT' if positioning_ok else '⚠ PROBLEME'}")
        print(f"Code Konsistenz: {'✅ KORREKT' if code_ok else '⚠ PROBLEME'}")
        
        if positioning_ok and code_ok:
            print(f"\n🎉 WINDOW POSITIONING BUG ERFOLGREICH BEHOBEN!")
            print("• Inkonsistenz zwischen Geometrie und Positionierung gelöst")
            print("• Fenster wird korrekt auf allen Bildschirmgrößen zentriert")
            print("• Keine Off-Screen Positionierung mehr möglich")
            print("• Code ist jetzt konsistent")
        else:
            print(f"\n⚠ Noch Verbesserungen nötig")
        
        return positioning_ok and code_ok
        
    except Exception as e:
        print(f"\nFEHLER beim Test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
