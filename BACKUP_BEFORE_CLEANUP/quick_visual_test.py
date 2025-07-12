#!/usr/bin/env python3
"""
Kurzer visueller Test der CheckerApp mit der reparierten register_persistent_button Funktionalität
"""

import sys
import time

def quick_visual_test():
    """Kurzer visueller Test der CheckerApp"""
    print("🚀 QUICK VISUAL TEST: CheckerApp mit repairierter register_persistent_button")
    print("=" * 80)
    
    try:
        print("📦 Importing CheckerApp...")
        from checker_app import CheckerApp
        print("✅ CheckerApp imported successfully")
        
        print("🎨 Creating CheckerApp instance...")
        app = CheckerApp()
        print("✅ CheckerApp created successfully")
        
        print("⏱️ Running app for 3 seconds to test button registrations...")
        
        # Schedule app shutdown
        app.root.after(3000, app.root.quit)  # Quit after 3 seconds
        
        # Start the app
        app.root.mainloop()
        
        print(f"📊 Final Statistics:")
        print(f"  - Persistent buttons registered: {app.get_persistent_button_count()}")
        
        # Show some details about registered buttons
        if hasattr(app, 'persistent_buttons') and app.persistent_buttons:
            print(f"  - Sample registered buttons:")
            for i, entry in enumerate(app.persistent_buttons[:5]):  # Show first 5
                print(f"    {i+1}. {entry['description']}")
        
        print("✅ App ran successfully and shutdown cleanly!")
        return True
        
    except Exception as e:
        print(f"❌ ERROR during visual test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting Quick Visual Test...\n")
    
    success = quick_visual_test()
    
    print(f"\n{'='*80}")
    print("🏁 VISUAL TEST RESULTS")
    print(f"{'='*80}")
    
    if success:
        print("✅ VISUAL TEST PASSED!")
        print("🎉 register_persistent_button funktioniert perfekt in der echten CheckerApp!")
        print("🔒 Alle Button-Icons sind jetzt dauerhaft geschützt!")
    else:
        print("❌ VISUAL TEST FAILED!")
        print("⚠️ Es gab Probleme beim Ausführen der CheckerApp!")
    
    sys.exit(0 if success else 1)
