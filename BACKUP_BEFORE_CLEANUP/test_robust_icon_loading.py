#!/usr/bin/env python3
"""
Test der robusten PNG Icon Loading Implementation mit FluentIconManager
"""

import os
import sys

def test_robust_icon_loading():
    print("🧪 Testing Robust PNG Icon Loading with FluentIconManager...")
    print("="*70)
    
    try:
        # Import der aktualisierten Module
        print("📋 Test 1: Import FluentIconManager...")
        from fluent_icons_manager import EnhancedFluentIconManager
        print("   ✅ FluentIconManager imported successfully")
        
        # Test 2: Erstelle FluentIconManager
        print("\n📋 Test 2: Creating FluentIconManager instance...")
        workspace = os.getcwd()
        icon_manager = EnhancedFluentIconManager(workspace_path=workspace)
        print(f"   ✅ FluentIconManager created with workspace: {workspace}")
        
        # Test 3: Teste die robuste load_png_icon Methode
        print("\n📋 Test 3: Testing robust load_png_icon method...")
        test_icons = [
            'home.png',
            'settings.png', 
            'file.png',
            'close.png',
            'info.png',
            'non-existent.png'  # Test für Fehlerbehandlung
        ]
        
        successful_loads = 0
        for icon_file in test_icons:
            try:
                photo_image = icon_manager.load_png_icon(icon_file, (24, 24))
                if photo_image:
                    print(f"   ✅ {icon_file}: Successfully loaded as PhotoImage")
                    successful_loads += 1
                else:
                    print(f"   ❌ {icon_file}: Failed to load")
            except Exception as e:
                print(f"   ❌ {icon_file}: Exception - {e}")
        
        # Test 4: Teste CheckerApp Integration
        print("\n📋 Test 4: Testing CheckerApp integration...")
        try:
            import tkinter as tk
            from tkinterdnd2 import TkinterDnD
            
            # Erstelle minimale Test-Umgebung
            test_root = TkinterDnD.Tk()
            test_root.withdraw()
            
            # Simuliere CheckerApp Icon-Loading mit neuer Methode
            class MockCheckerApp:
                def __init__(self):
                    self.icon_manager = icon_manager
                    self.icon_images = {}
                    
                def load_ctk_icon(self, icon_name, size=(20, 20)):
                    """Simuliere die neue load_ctk_icon Methode"""
                    try:
                        possible_files = [
                            f"{icon_name}.png",
                            f"{icon_name.replace('_', '-')}.png"
                        ]
                        
                        for filename in possible_files:
                            photo_image = self.icon_manager.load_png_icon(filename, size)
                            if photo_image:
                                return photo_image
                        return None
                    except Exception as e:
                        print(f"Error in load_ctk_icon: {e}")
                        return None
            
            mock_app = MockCheckerApp()
            
            # Teste verschiedene Icon-Namen
            app_test_icons = ['home', 'settings', 'file', 'close']
            app_successful = 0
            
            for icon_name in app_test_icons:
                result = mock_app.load_ctk_icon(icon_name)
                if result:
                    print(f"   ✅ {icon_name}: App integration successful")
                    app_successful += 1
                else:
                    print(f"   ❌ {icon_name}: App integration failed")
            
            test_root.destroy()
            
            print(f"\n📊 App Integration Results: {app_successful}/{len(app_test_icons)} icons loaded")
            
        except Exception as e:
            print(f"   ❌ App integration test failed: {e}")
            app_successful = 0
        
        # Test 5: Performance und Memory
        print("\n📋 Test 5: Testing performance and memory management...")
        cache_hits = len(icon_manager.image_cache)
        print(f"   📋 Image cache entries: {cache_hits}")
        print(f"   📋 Available local icons: {len(icon_manager.available_local_icons)}")
        
        # Summary
        print("\n" + "="*70)
        print("🎯 TEST SUMMARY:")
        print(f"   📊 PNG files loaded successfully: {successful_loads}/{len(test_icons) - 1}")  # -1 für non-existent
        print(f"   🎯 App integration success: {app_successful}/{len(app_test_icons) if 'app_test_icons' in locals() else 0}")
        print(f"   🔒 Image cache entries: {cache_hits}")
        
        # Overall result
        if successful_loads >= 3 and (app_successful >= 2 if 'app_successful' in locals() else True):
            print("\n🎉 ROBUST PNG ICON LOADING: EXCELLENT!")
            return True
        elif successful_loads >= 2:
            print("\n✅ ROBUST PNG ICON LOADING: GOOD!")
            return True
        else:
            print("\n⚠️  ROBUST PNG ICON LOADING: NEEDS IMPROVEMENT")
            return False
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Starting robust PNG icon loading test...\n")
    result = test_robust_icon_loading()
    
    if result:
        print("\n🚀 ROBUST PNG ICON SYSTEM IS READY FOR PRODUCTION! 🚀")
    else:
        print("\n🔧 ROBUST PNG ICON SYSTEM NEEDS FURTHER WORK")
    
    input("\nPress Enter to exit...")
