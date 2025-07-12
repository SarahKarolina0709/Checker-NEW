#!/usr/bin/env python3
"""
Demo: CustomerSectionComplete direkt aufrufen
Zeigt verschiedene Methoden zum Starten der Customer View
"""

import customtkinter as ctk
import sys
from pathlib import Path

# Add project directory to path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

def demo_customer_section_calls():
    """Demonstriert verschiedene Wege zum Aufrufen der CustomerSectionComplete"""
    
    print("🎯 CustomerSectionComplete Aufruf-Demo")
    print("=" * 50)
    
    # Set appearance mode
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create demo window
    root = ctk.CTk()
    root.title("CustomerSection Aufruf Demo")
    root.geometry("600x500")
    
    # Title
    title_label = ctk.CTkLabel(
        root,
        text="🏢 CustomerSectionComplete Aufruf-Methoden",
        font=ctk.CTkFont(size=20, weight="bold")
    )
    title_label.pack(pady=20)
    
    # Methods container
    methods_frame = ctk.CTkScrollableFrame(root, height=350)
    methods_frame.pack(pady=10, padx=20, fill="both", expand=True)
    
    # Method 1: Direct ViewStack call
    method1_frame = ctk.CTkFrame(methods_frame)
    method1_frame.pack(pady=10, padx=10, fill="x")
    
    method1_title = ctk.CTkLabel(
        method1_frame,
        text="📋 Methode 1: Direkter ViewStack Aufruf",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    method1_title.pack(pady=(10, 5), padx=10, anchor="w")
    
    method1_code = ctk.CTkTextbox(
        method1_frame,
        height=60,
        font=ctk.CTkFont(family="Consolas", size=12)
    )
    method1_code.pack(pady=5, padx=10, fill="x")
    method1_code.insert("0.0", """# Direkt über ViewStack
app.views.show("customer_management")""")
    method1_code.configure(state="disabled")
    
    # Method 2: Button integration
    method2_frame = ctk.CTkFrame(methods_frame)
    method2_frame.pack(pady=10, padx=10, fill="x")
    
    method2_title = ctk.CTkLabel(
        method2_frame,
        text="🔘 Methode 2: Button Integration",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    method2_title.pack(pady=(10, 5), padx=10, anchor="w")
    
    method2_code = ctk.CTkTextbox(
        method2_frame,
        height=100,
        font=ctk.CTkFont(family="Consolas", size=12)
    )
    method2_code.pack(pady=5, padx=10, fill="x")
    method2_code.insert("0.0", """# Button mit direktem Aufruf
btn = ctk.CTkButton(
    parent,
    text="🏢 Kundenverwaltung öffnen",
    command=lambda: app.views.show("customer_management")
)""")
    method2_code.configure(state="disabled")
    
    # Method 3: Menu integration
    method3_frame = ctk.CTkFrame(methods_frame)
    method3_frame.pack(pady=10, padx=10, fill="x")
    
    method3_title = ctk.CTkLabel(
        method3_frame,
        text="📱 Methode 3: Über show_customer_menu()",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    method3_title.pack(pady=(10, 5), padx=10, anchor="w")
    
    method3_code = ctk.CTkTextbox(
        method3_frame,
        height=80,
        font=ctk.CTkFont(family="Consolas", size=12)
    )
    method3_code.pack(pady=5, padx=10, fill="x")
    method3_code.insert("0.0", """# Über bestehende Menu-Methode (automatisch)
app.show_customer_menu()
# -> Priorität 1: CustomerSectionComplete""")
    method3_code.configure(state="disabled")
    
    # Method 4: Direct method call
    method4_frame = ctk.CTkFrame(methods_frame)
    method4_frame.pack(pady=10, padx=10, fill="x")
    
    method4_title = ctk.CTkLabel(
        method4_frame,
        text="🎯 Methode 4: Direkte Methode",
        font=ctk.CTkFont(size=16, weight="bold"),
        anchor="w"
    )
    method4_title.pack(pady=(10, 5), padx=10, anchor="w")
    
    method4_code = ctk.CTkTextbox(
        method4_frame,
        height=80,
        font=ctk.CTkFont(family="Consolas", size=12)
    )
    method4_code.pack(pady=5, padx=10, fill="x")
    method4_code.insert("0.0", """# Über neue Helper-Methode
app.show_customer_section_complete()
# -> Direkt zur CustomerSectionComplete""")
    method4_code.configure(state="disabled")
    
    # Status info
    status_frame = ctk.CTkFrame(root, fg_color="transparent")
    status_frame.pack(pady=10, fill="x")
    
    status_label = ctk.CTkLabel(
        status_frame,
        text="✅ CustomerSectionComplete ist bereits integriert und einsatzbereit!",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color="green"
    )
    status_label.pack()
    
    # Test instructions
    instruction_label = ctk.CTkLabel(
        root,
        text="💡 Starten Sie checker_app.py und klicken Sie auf 'Kunden' im Menü",
        font=ctk.CTkFont(size=12),
        text_color="gray"
    )
    instruction_label.pack(pady=5)
    
    print("✅ Demo UI bereit - verschiedene Aufruf-Methoden werden angezeigt")
    
    root.mainloop()

if __name__ == "__main__":
    demo_customer_section_calls()
