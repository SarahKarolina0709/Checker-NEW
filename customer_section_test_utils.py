#!/usr/bin/env python3
"""
Test Button für CustomerSectionComplete
Fügt einen Test-Button hinzu, um die Customer View direkt aufzurufen
"""

import customtkinter as ctk

def add_customer_test_button(app_instance, parent_frame):
    """
    Fügt einen Test-Button hinzu, um CustomerSectionComplete direkt aufzurufen
    
    Args:
        app_instance: Die CheckerApp Instanz
        parent_frame: Das Parent Frame für den Button
    """
    
    # Test Button Container
    test_container = ctk.CTkFrame(parent_frame, fg_color="transparent")
    test_container.pack(pady=10, padx=20, fill="x")
    
    # Test Button für CustomerSectionComplete
    customer_test_btn = ctk.CTkButton(
        test_container,
        text="🏢 CustomerSectionComplete testen",
        command=lambda: test_customer_section_complete(app_instance),
        height=45,
        font=ctk.CTkFont(size=16, weight="bold"),
        fg_color="#3b82f6",
        hover_color="#2563eb"
    )
    customer_test_btn.pack(pady=5, fill="x")
    
    # Direkter ViewStack Test Button
    viewstack_test_btn = ctk.CTkButton(
        test_container,
        text="📋 Direkt über ViewStack",
        command=lambda: direct_viewstack_call(app_instance),
        height=35,
        font=ctk.CTkFont(size=14),
        fg_color="#10b981",
        hover_color="#059669"
    )
    viewstack_test_btn.pack(pady=2, fill="x")
    
    # Menu Test Button
    menu_test_btn = ctk.CTkButton(
        test_container,
        text="📱 Über show_customer_menu()",
        command=lambda: menu_call_test(app_instance),
        height=35,
        font=ctk.CTkFont(size=14),
        fg_color="#f59e0b",
        hover_color="#d97706"
    )
    menu_test_btn.pack(pady=2, fill="x")
    
    return test_container

def test_customer_section_complete(app_instance):
    """Test die CustomerSectionComplete über die neue Helper-Methode"""
    try:
        print("🎯 Testing CustomerSectionComplete via show_customer_section_complete()")
        
        if hasattr(app_instance, 'show_customer_section_complete'):
            success = app_instance.show_customer_section_complete()
            if success:
                print("✅ CustomerSectionComplete erfolgreich aufgerufen!")
            else:
                print("❌ CustomerSectionComplete konnte nicht aufgerufen werden")
        else:
            print("❌ show_customer_section_complete() Methode nicht verfügbar")
            
    except Exception as e:
        print(f"❌ Fehler beim Testen der CustomerSectionComplete: {e}")

def direct_viewstack_call(app_instance):
    """Test direkten ViewStack Aufruf"""
    try:
        print("📋 Testing direct ViewStack call: app.views.show('customer_management')")
        
        if hasattr(app_instance, 'views') and app_instance.views:
            app_instance.views.show("customer_management")
            print("✅ ViewStack direkter Aufruf erfolgreich!")
        else:
            print("❌ ViewStack nicht verfügbar")
            
    except Exception as e:
        print(f"❌ Fehler beim direkten ViewStack Aufruf: {e}")

def menu_call_test(app_instance):
    """Test über bestehende Menu-Methode"""
    try:
        print("📱 Testing via show_customer_menu() - should prioritize CustomerSectionComplete")
        
        if hasattr(app_instance, 'show_customer_menu'):
            app_instance.show_customer_menu()
            print("✅ show_customer_menu() aufgerufen - sollte CustomerSectionComplete priorisieren")
        else:
            print("❌ show_customer_menu() Methode nicht verfügbar")
            
    except Exception as e:
        print(f"❌ Fehler beim Menu-Aufruf: {e}")

# Beispiel für die Integration in ein bestehendes UI
def create_customer_test_ui(app_instance):
    """Erstelle eine Test-UI für CustomerSectionComplete Aufrufe"""
    
    # Test Window
    test_window = ctk.CTkToplevel()
    test_window.title("CustomerSectionComplete Test")
    test_window.geometry("400x300")
    
    # Title
    title_label = ctk.CTkLabel(
        test_window,
        text="🧪 CustomerSectionComplete Tests",
        font=ctk.CTkFont(size=18, weight="bold")
    )
    title_label.pack(pady=20)
    
    # Add test buttons
    add_customer_test_button(app_instance, test_window)
    
    # Status
    status_label = ctk.CTkLabel(
        test_window,
        text="Klicken Sie auf einen Button, um die CustomerSectionComplete zu testen",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    status_label.pack(pady=20)
    
    return test_window

if __name__ == "__main__":
    print("🧪 CustomerSectionComplete Test Utilities")
    print("Dieses Modul stellt Test-Funktionen für CustomerSectionComplete bereit.")
    print("Verwenden Sie add_customer_test_button() in Ihrer App-UI.")
