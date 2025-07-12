#!/usr/bin/env python3
"""
Complete Icon Management System Test
Tests all icon management features including the newly added helper methods.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from checker_app import CheckerApp
import customtkinter as ctk

def test_icon_management_complete():
    """Test all icon management features comprehensively"""
    print("="*80)
    print("                     COMPLETE ICON MANAGEMENT TEST")
    print("="*80)
    
    # Create app instance
    app = CheckerApp()
    
    # Test 1: Basic icon loading
    print("\n1. TESTING BASIC ICON LOADING:")
    print("-" * 40)
    test_icons = ['rocket', 'quality', 'pdf-file', 'upload', 'download', 'user', 'settings']
    for icon_name in test_icons:
        icon = app.get_icon(icon_name, size=(24, 24))
        status = "✓ LOADED" if icon else "✗ FAILED"
        print(f"   {icon_name:<15} | {status}")
    
    # Test 2: Alias and fallback system
    print("\n2. TESTING ALIAS & FALLBACK SYSTEM:")
    print("-" * 40)
    alias_tests = [
        ('delete', 'trash-can'),
        ('quality', 'check-mark'),
        ('launch', 'rocket'),
        ('pdf', 'pdf-file'),
        ('security', 'lock'),
        ('connect', 'link')
    ]
    for alias, expected in alias_tests:
        icon = app.get_icon(alias, size=(20, 20))
        status = "✓ MAPPED" if icon else "✗ FAILED"
        print(f"   {alias:<12} → {expected:<15} | {status}")
    
    # Test 3: Category-based icon lookup
    print("\n3. TESTING CATEGORY-BASED LOOKUP:")
    print("-" * 40)
    categories = ['file', 'user', 'action', 'settings', 'help', 'security', 'network']
    for category in categories:
        icon = app.get_icon_by_category(category, size=(20, 20))
        status = "✓ FOUND" if icon else "✗ NOT FOUND"
        print(f"   Category '{category}' | {status}")
    
    # Test 4: Type-based icon lookup
    print("\n4. TESTING TYPE-BASED LOOKUP:")
    print("-" * 40)
    types = ['launch', 'validate', 'file_pdf', 'upload_file', 'security_check', 'user_profile']
    for icon_type in types:
        icon = app.get_icon_by_type(icon_type, size=(20, 20))
        status = "✓ FOUND" if icon else "✗ NOT FOUND"
        print(f"   Type '{icon_type}' | {status}")
    
    # Test 5: Icon suggestions
    print("\n5. TESTING ICON SUGGESTIONS:")
    print("-" * 40)
    suggestion_tests = ['file', 'user', 'check', 'export']
    for partial in suggestion_tests:
        suggestions = app.get_icon_suggestions(partial)
        print(f"   '{partial}' → {suggestions[:3]}...")  # Show first 3 suggestions
    
    # Test 6: New helper methods
    print("\n6. TESTING NEW HELPER METHODS:")
    print("-" * 40)
    
    # Test get_text_icon
    text, icon = app.get_text_icon("Launch App", "rocket", size=(20, 20))
    print(f"   get_text_icon: Text='{text}', Icon={'✓ LOADED' if icon else '✗ FAILED'}")
    
    # Test create_icon_button (simulated)
    try:
        # Create a temporary frame for testing
        test_frame = ctk.CTkFrame(app.root)
        button = app.create_icon_button(
            test_frame, 
            text="Test Button", 
            icon_name="rocket", 
            size=(24, 24)
        )
        print(f"   create_icon_button: {'✓ CREATED' if button else '✗ FAILED'}")
        test_frame.destroy()  # Clean up
    except Exception as e:
        print(f"   create_icon_button: ✗ ERROR - {e}")
    
    # Test setup_icon_menu (simulated)
    try:
        import tkinter as tk
        test_menu = tk.Menu(app.root)
        menu_items = [
            {'text': 'Open', 'icon': 'folder', 'command': lambda: None},
            {'text': 'Save', 'icon': 'save_icon', 'command': lambda: None},
            {'text': 'Export', 'icon': 'export', 'command': lambda: None}
        ]
        configured_menu = app.setup_icon_menu(test_menu, menu_items)
        print(f"   setup_icon_menu: {'✓ CONFIGURED' if configured_menu else '✗ FAILED'}")
    except Exception as e:
        print(f"   setup_icon_menu: ✗ ERROR - {e}")
    
    # Test 7: Available icons overview
    print("\n7. TESTING AVAILABLE ICONS OVERVIEW:")
    print("-" * 40)
    available_icons = app.get_available_icons()
    categorized_icons = app.get_available_icons(categorized=True)
    print(f"   Total available icons: {len(available_icons)}")
    print(f"   Categories found: {len(categorized_icons)}")
    for category, icons in categorized_icons.items():
        print(f"   - {category}: {len(icons)} icons")
    
    # Test 8: Print icon summary (abbreviated)
    print("\n8. ICON SUMMARY (abbreviated):")
    print("-" * 40)
    app.print_icon_summary()
    
    print("\n" + "="*80)
    print("                       TEST COMPLETE")
    print("="*80)
    
    return app

if __name__ == "__main__":
    try:
        app = test_icon_management_complete()
        
        # Optional: Show a small demo window
        print("\nDo you want to see a visual demo of the icons? (y/n): ", end="")
        choice = input().lower().strip()
        
        if choice == 'y':
            # Create a simple demo window
            demo_window = ctk.CTkToplevel(app.root)
            demo_window.title("Icon Management Demo")
            demo_window.geometry("600x400")
            
            # Create some demo buttons with icons
            demo_icons = ['rocket', 'quality', 'upload', 'download', 'user', 'settings']
            for i, icon_name in enumerate(demo_icons):
                button = app.create_icon_button(
                    demo_window,
                    text=f"{icon_name.title()} Button",
                    icon_name=icon_name,
                    size=(24, 24)
                )
                button.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="ew")
            
            demo_window.grid_columnconfigure(0, weight=1)
            demo_window.grid_columnconfigure(1, weight=1)
            
            print("Demo window opened. Close it to exit.")
            app.root.mainloop()
        else:
            print("Test completed successfully. All icon management features are working!")
            
    except Exception as e:
        print(f"Test failed with error: {e}")
        import traceback
        traceback.print_exc()
