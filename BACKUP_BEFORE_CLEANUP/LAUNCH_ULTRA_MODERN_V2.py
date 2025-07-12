"""
Launch Script für die Checker-App mit Ultra-Modern Welcome Screen v2.0
"""

import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    """Startet die Checker-App mit dem neuen Ultra-Modern Welcome Screen"""
    print("=" * 70)
    print("🚀 Checker-App - Ultra-Modern Welcome Screen v2.0")
    print("=" * 70)
    print("Starte die Anwendung mit verbessertem Design...")
    print()
    
    try:
        # Import and run the main app
        from checker_app import CheckerApp
        
        # Create and run the app
        app = CheckerApp()
        
        print("✅ Checker-App erfolgreich gestartet!")
        print("📱 Neues Ultra-Modern Welcome Screen v2.0 aktiv")
        print("🎨 Verbesserte Icons und Benutzerführung")
        print()
        print("Features des neuen Designs:")
        print("• 🎯 Verbesserte Benutzerführung mit kategorisierten Workflows")
        print("• 🎨 Modernere Icons und Typografie")
        print("• 📱 Responsive Design mit Card-basiertem Layout")
        print("• ✨ Micro-Animationen und Hover-Effekte")
        print("• 🔧 Erweiterte Werkzeug-Sektion")
        print("• 💡 Hilfreiche Tipps und Schnellzugriffe")
        print()
        
        # Run the application
        app.root.mainloop()
        
    except ImportError as e:
        print(f"❌ Import-Fehler: {e}")
        print("Stelle sicher, dass alle Abhängigkeiten installiert sind:")
        print("pip install customtkinter pillow tkinterdnd2")
        
    except Exception as e:
        print(f"❌ Fehler beim Starten der Anwendung: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        print("\n👋 Checker-App beendet")

if __name__ == "__main__":
    main()
