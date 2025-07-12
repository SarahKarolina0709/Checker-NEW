#!/usr/bin/env python3
"""
ViewStack Debug Test - Teste ViewStack Integration systematisch
"""

import customtkinter as ctk
from checker_app import CheckerApp
import time

def test_viewstack_integration():
    """Teste ViewStack Integration systematisch."""
    print("=== VIEWSTACK INTEGRATION DEBUG TEST ===")
    
    try:
        # Erstelle App
        print("1. App wird erstellt...")
        app = CheckerApp()
        
        # Prüfe ViewStack-Existenz
        print(f"2. ViewStack verfügbar: {hasattr(app, 'views')}")
        if hasattr(app, 'views'):
            print(f"   ViewStack Type: {type(app.views).__name__}")
            # Korrekte Zugriffe auf ViewStack-Methoden
            all_views = app.views.get_views()
            current_view = app.views.get_current_view()
            print(f"   ViewStack verfügbare Views: {list(all_views.keys())}")
            print(f"   Current View: {current_view}")
        
        # Teste Customer Menu Aufruf
        print("\n3. Teste Customer Menu Aufruf...")
        app.show_customer_menu()
        
        # Prüfe ViewStack nach Customer Menu
        print("\n4. ViewStack Status nach Customer Menu:")
        if hasattr(app, 'views'):
            available_views = list(app.views.get_views().keys())
            current_view = app.views.get_current_view()
            
            print(f"   Verfügbare Views: {available_views}")
            print(f"   Current View: {current_view}")
            
            # Prüfe ob Customer Management View existiert
            customer_views = [v for v in available_views if 'customer' in v.lower()]
            print(f"   Customer-bezogene Views: {customer_views}")
            
            # Teste direkte View-Navigation
            print("\n5. Teste direkte View-Navigation...")
            if customer_views:
                target_view = customer_views[0]
                print(f"   Navigiere zu: {target_view}")
                try:
                    app.views.show(target_view)
                    new_current = app.views.get_current_view()
                    print(f"   Neue Current View: {new_current}")
                    print(f"   ✅ Navigation erfolgreich: {new_current == target_view}")
                except Exception as e:
                    print(f"   ❌ Navigation fehlgeschlagen: {e}")
            
            # Teste Welcome vs. Customer View
            print("\n6. Teste View-Wechsel Welcome -> Customer:")
            try:
                print("   Gehe zu Welcome...")
                app.views.show('welcome')
                print(f"   Current nach Welcome: {app.views.get_current_view()}")
                
                if customer_views:
                    print(f"   Gehe zu Customer View ({customer_views[0]})...")
                    app.views.show(customer_views[0])
                    final_view = app.views.get_current_view()
                    print(f"   Final Current View: {final_view}")
                    
                    if final_view == customer_views[0]:
                        print("   ✅ ViewStack funktioniert korrekt!")
                    else:
                        print("   ❌ ViewStack-Problem: View wird nicht korrekt angezeigt")
                        
            except Exception as e:
                print(f"   ❌ View-Wechsel fehlgeschlagen: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n=== VIEWSTACK TEST ABGESCHLOSSEN ===")
        
    except Exception as e:
        print(f"❌ Fehler im ViewStack Test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_viewstack_integration()
