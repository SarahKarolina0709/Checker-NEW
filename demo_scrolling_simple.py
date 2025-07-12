"""
Einfacher Test zur Demonstration des vertikalen Scrollings
"""

import customtkinter as ctk
from ui_theme import UITheme

def create_scrolling_demo():
    """Erstellt ein Demo-Fenster mit vertikalem Scrolling"""
    
    # Haupt-Fenster
    root = ctk.CTk()
    root.title("Vertikales Scrolling Demo")
    root.geometry("1200x800")
    
    # Theme konfigurieren
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Main container
    main_container = ctk.CTkFrame(root, fg_color="#FAFBFC")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Grid für drei Spalten
    main_container.grid_columnconfigure(0, weight=1)
    main_container.grid_columnconfigure(1, weight=1)
    main_container.grid_columnconfigure(2, weight=1)
    main_container.grid_rowconfigure(0, weight=1)
    
    # Customer Container (links)
    customer_container = ctk.CTkFrame(main_container, **UITheme.CONTAINER_STYLE_CUSTOMER)
    customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
    customer_container.grid_columnconfigure(0, weight=1)
    customer_container.grid_rowconfigure(1, weight=1)
    customer_container.grid_propagate(False)
    
    # Header
    header_label = ctk.CTkLabel(
        customer_container,
        text="📊 Customer Section (Scrollable)",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=UITheme.COLOR_TEXT_PRIMARY
    )
    header_label.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    
    # Scrollbarer Inhalt
    scrollable_frame = ctk.CTkScrollableFrame(
        customer_container,
        fg_color="transparent",
        scrollbar_button_color=UITheme.COLOR_ACCENT,
        scrollbar_button_hover_color=UITheme.COLOR_ACCENT_HOVER
    )
    scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
    scrollable_frame.grid_columnconfigure(0, weight=1)
    
    # Viele Inhalte hinzufügen
    for i in range(30):
        content_frame = ctk.CTkFrame(scrollable_frame, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
        content_frame.grid(row=i, column=0, sticky="ew", pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            content_frame,
            text=f"Customer Item {i+1} - Mehr Inhalt hier",
            font=ctk.CTkFont(size=12)
        )
        label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
    
    # Upload Container (mitte)
    upload_container = ctk.CTkFrame(main_container, **UITheme.CONTAINER_STYLE_UPLOAD)
    upload_container.grid(row=0, column=1, sticky="nsew", padx=5, pady=(0, 15))
    upload_container.grid_columnconfigure(0, weight=1)
    upload_container.grid_rowconfigure(1, weight=1)
    upload_container.grid_propagate(False)
    
    # Header
    header_label2 = ctk.CTkLabel(
        upload_container,
        text="📤 Upload Section (Scrollable)",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=UITheme.COLOR_TEXT_PRIMARY
    )
    header_label2.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    
    # Scrollbarer Inhalt
    upload_scrollable = ctk.CTkScrollableFrame(
        upload_container,
        fg_color="transparent",
        scrollbar_button_color=UITheme.COLOR_ACCENT,
        scrollbar_button_hover_color=UITheme.COLOR_ACCENT_HOVER
    )
    upload_scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
    upload_scrollable.grid_columnconfigure(0, weight=1)
    
    # Viele Inhalte hinzufügen
    for i in range(25):
        content_frame = ctk.CTkFrame(upload_scrollable, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
        content_frame.grid(row=i, column=0, sticky="ew", pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            content_frame,
            text=f"📁 File {i+1}.txt - Uploaded document",
            font=ctk.CTkFont(size=12)
        )
        label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
    
    # Workflow Container (rechts)
    workflow_container = ctk.CTkFrame(main_container, **UITheme.CONTAINER_STYLE_WORKFLOW)
    workflow_container.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
    workflow_container.grid_columnconfigure(0, weight=1)
    workflow_container.grid_rowconfigure(1, weight=1)
    workflow_container.grid_propagate(False)
    
    # Header
    header_label3 = ctk.CTkLabel(
        workflow_container,
        text="⚙️ Workflow Section (Scrollable)",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color=UITheme.COLOR_TEXT_PRIMARY
    )
    header_label3.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
    
    # Scrollbarer Inhalt
    workflow_scrollable = ctk.CTkScrollableFrame(
        workflow_container,
        fg_color="transparent",
        scrollbar_button_color=UITheme.COLOR_ACCENT,
        scrollbar_button_hover_color=UITheme.COLOR_ACCENT_HOVER
    )
    workflow_scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
    workflow_scrollable.grid_columnconfigure(0, weight=1)
    
    # Viele Inhalte hinzufügen
    for i in range(20):
        content_frame = ctk.CTkFrame(workflow_scrollable, fg_color=UITheme.COLOR_SURFACE_HOVER_LIGHT)
        content_frame.grid(row=i, column=0, sticky="ew", pady=5)
        content_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            content_frame,
            text=f"⚙️ Workflow Step {i+1} - Process documents",
            font=ctk.CTkFont(size=12)
        )
        label.grid(row=0, column=0, sticky="ew", padx=15, pady=10)
    
    # Status
    status_label = ctk.CTkLabel(
        root,
        text="✅ VERTIKALES SCROLLING DEMO - Probieren Sie das Scrolling in allen drei Sektionen!",
        font=ctk.CTkFont(size=14, weight="bold"),
        text_color=UITheme.COLOR_SUCCESS
    )
    status_label.pack(pady=10)
    
    print("🎯 VERTIKALES SCROLLING DEMO GESTARTET!")
    print("=" * 60)
    print("✅ Alle drei Container haben jetzt vertikales Scrolling")
    print("📏 Feste Höhe (600px) verhindert das Strecken der Container")
    print("🎨 Deutlich unterschiedliche Rahmenfarben für bessere Trennung")
    print("🖱️ Scrollbars sind mit Akzentfarben gestaltet")
    print("=" * 60)
    print("🔍 Testen Sie das Scrolling in jeder Sektion!")
    
    root.mainloop()

if __name__ == "__main__":
    create_scrolling_demo()
