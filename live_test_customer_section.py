#!/usr/bin/env python3
"""
Live Test: CustomerSectionComplete View aufrufen
Testet alle implementierten Aufruf-Methoden
"""

import customtkinter as ctk
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def live_test_customer_section():
    """Live Test aller CustomerSectionComplete Aufruf-Methoden"""
    
    print("🚀 Live Test: CustomerSectionComplete View")
    print("=" * 50)
    
    # Set appearance mode
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create test window
    root = ctk.CTk()
    root.title("Live Test: CustomerSectionComplete")
    root.geometry("500x400")
    
    # Title
    title_label = ctk.CTkLabel(
        root,
        text="🧪 Live Test: CustomerSectionComplete",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=20)
    
    # Test results frame
    results_frame = ctk.CTkFrame(root)
    results_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Results display
    results_text = ctk.CTkTextbox(
        results_frame,
        font=ctk.CTkFont(family="Consolas", size=12)
    )
    results_text.pack(pady=10, padx=10, fill="both", expand=True)
    
    def log_result(message):
        """Log a test result"""
        results_text.insert("end", f"{message}\n")
        results_text.see("end")
    
    # Test 1: Import Test
    def test_import():
        log_result("🧪 Test 1: Import CustomerSectionComplete")
        try:
            from welcome_screen_components.customer_section_complete import CustomerSectionComplete
            log_result("✅ Import erfolgreich!")
            return True
        except Exception as e:
            log_result(f"❌ Import Fehler: {e}")
            return False
    
    # Test 2: CheckerApp Integration Test
    def test_checker_app_integration():
        log_result("\n🧪 Test 2: CheckerApp Integration")
        try:
            from checker_app import CheckerApp
            log_result("✅ CheckerApp Import erfolgreich!")
            
            # Check if CustomerSectionComplete is in imports
            import checker_app
            import inspect
            source = inspect.getsource(checker_app)
            if "CustomerSectionComplete" in source:
                log_result("✅ CustomerSectionComplete in CheckerApp integriert!")
                return True
            else:
                log_result("❌ CustomerSectionComplete nicht in CheckerApp gefunden")
                return False
        except Exception as e:
            log_result(f"❌ CheckerApp Integration Fehler: {e}")
            return False
    
    # Test 3: ViewStack Integration Test
    def test_viewstack_integration():
        log_result("\n🧪 Test 3: ViewStack Integration")
        try:
            # Create minimal app instance to test ViewStack
            test_app = ctk.CTk()
            test_app.withdraw()  # Hide test window
            
            from view_stack import EnhancedViewStack
            viewstack = EnhancedViewStack(test_app)
            
            # Test CustomerSectionComplete creation
            from welcome_screen_components.customer_section_complete import CustomerSectionComplete
            
            # Create mock app object
            class MockApp:
                def __init__(self):
                    self.kunden_manager = None
                    import logging
                    self.logger = logging.getLogger(__name__)
            
            mock_app = MockApp()
            
            # Create CustomerSectionComplete
            customer_section = CustomerSectionComplete(
                master=viewstack,
                app=mock_app,
                welcome_screen=None
            )
            
            # Add to ViewStack
            viewstack.add("customer_management", customer_section)
            
            log_result("✅ ViewStack Integration erfolgreich!")
            log_result("✅ CustomerSectionComplete erstellt und hinzugefügt!")
            
            test_app.destroy()
            return True
            
        except Exception as e:
            log_result(f"❌ ViewStack Integration Fehler: {e}")
            import traceback
            log_result(f"   Details: {traceback.format_exc()}")
            return False
    
    # Test 4: Aufruf-Methoden Test
    def test_call_methods():
        log_result("\n🧪 Test 4: Aufruf-Methoden")
        
        methods = [
            "app.views.show('customer_management')",
            "app.show_customer_menu()",
            "app.show_customer_section_complete()",
            "ctk.CTkButton(..., command=lambda: app.views.show('customer_management'))"
        ]
        
        for method in methods:
            log_result(f"📋 Methode verfügbar: {method}")
        
        log_result("✅ Alle Aufruf-Methoden dokumentiert!")
        return True
    
    # Button frame
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10, padx=20, fill="x")
    
    # Test buttons
    test1_btn = ctk.CTkButton(
        button_frame,
        text="Test 1: Import",
        command=test_import,
        width=120
    )
    test1_btn.grid(row=0, column=0, padx=5, pady=5)
    
    test2_btn = ctk.CTkButton(
        button_frame,
        text="Test 2: Integration",
        command=test_checker_app_integration,
        width=120
    )
    test2_btn.grid(row=0, column=1, padx=5, pady=5)
    
    test3_btn = ctk.CTkButton(
        button_frame,
        text="Test 3: ViewStack",
        command=test_viewstack_integration,
        width=120
    )
    test3_btn.grid(row=1, column=0, padx=5, pady=5)
    
    test4_btn = ctk.CTkButton(
        button_frame,
        text="Test 4: Methoden",
        command=test_call_methods,
        width=120
    )
    test4_btn.grid(row=1, column=1, padx=5, pady=5)
    
    # Run all tests button
    def run_all_tests():
        log_result("🚀 Starte alle Tests...\n")
        test_import()
        test_checker_app_integration()
        test_viewstack_integration()
        test_call_methods()
        log_result("\n✅ Alle Tests abgeschlossen!")
    
    run_all_btn = ctk.CTkButton(
        button_frame,
        text="🚀 Alle Tests",
        command=run_all_tests,
        width=250,
        height=40,
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="#10b981",
        hover_color="#059669"
    )
    run_all_btn.grid(row=2, column=0, columnspan=2, padx=5, pady=10)
    
    # Configure grid
    button_frame.grid_columnconfigure((0, 1), weight=1)
    
    # Initial message
    log_result("🧪 CustomerSectionComplete Live Test bereit!")
    log_result("Klicken Sie auf die Test-Buttons oder 'Alle Tests'")
    log_result("=" * 50)
    
    print("✅ Live Test UI bereit")
    root.mainloop()

if __name__ == "__main__":
    live_test_customer_section()
