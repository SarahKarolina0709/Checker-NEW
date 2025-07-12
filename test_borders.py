#!/usr/bin/env python3
"""
Test script to verify container border colors are visible
"""
import customtkinter as ctk
from ui_theme import UITheme

def test_border_colors():
    """Test all three container border colors"""
    
    # Create test window
    root = ctk.CTk()
    root.title("Border Color Test")
    root.geometry("900x300")
    
    # Force light mode
    ctk.set_appearance_mode("Light")
    
    # Create main frame
    main_frame = ctk.CTkFrame(root, fg_color="#FAFBFC")
    main_frame.pack(fill="both", expand=True, padx=20, pady=20)
    
    # Configure grid
    main_frame.grid_columnconfigure(0, weight=1)
    main_frame.grid_columnconfigure(1, weight=1)
    main_frame.grid_columnconfigure(2, weight=1)
    
    # Test Customer container
    customer_frame = ctk.CTkFrame(main_frame, **UITheme.CONTAINER_STYLE_CUSTOMER)
    customer_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
    
    customer_label = ctk.CTkLabel(customer_frame, text="Customer Container\nBorder: Blue", font=("Arial", 14))
    customer_label.pack(expand=True)
    
    # Test Upload container
    upload_frame = ctk.CTkFrame(main_frame, **UITheme.CONTAINER_STYLE_UPLOAD)
    upload_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
    
    upload_label = ctk.CTkLabel(upload_frame, text="Upload Container\nBorder: Purple", font=("Arial", 14))
    upload_label.pack(expand=True)
    
    # Test Workflow container
    workflow_frame = ctk.CTkFrame(main_frame, **UITheme.CONTAINER_STYLE_WORKFLOW)
    workflow_frame.grid(row=0, column=2, sticky="nsew", padx=10, pady=10)
    
    workflow_label = ctk.CTkLabel(workflow_frame, text="Workflow Container\nBorder: Orange", font=("Arial", 14))
    workflow_label.pack(expand=True)
    
    # Show color information
    info_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    info_frame.grid(row=1, column=0, columnspan=3, sticky="ew", pady=10)
    
    info_label = ctk.CTkLabel(
        info_frame, 
        text=f"Border Colors:\nCustomer: {UITheme.CONTAINER_STYLE_CUSTOMER['border_color']}\n"
             f"Upload: {UITheme.CONTAINER_STYLE_UPLOAD['border_color']}\n"
             f"Workflow: {UITheme.CONTAINER_STYLE_WORKFLOW['border_color']}\n"
             f"Border Width: {UITheme.CONTAINER_STYLE_CUSTOMER['border_width']}px",
        font=("Arial", 11),
        justify="left"
    )
    info_label.pack()
    
    root.mainloop()

if __name__ == "__main__":
    test_border_colors()
