#!/usr/bin/env python3
"""
Test script to verify container heights and visibility
"""
import customtkinter as ctk
from ui_theme import UITheme

class ContainerHeightTest:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Container Height Test")
        self.root.geometry("1400x950")
        
        # Light mode
        ctk.set_appearance_mode("Light")
        
        self.create_test_containers()
        
    def create_test_containers(self):
        """Create test containers with the same styles as the app"""
        
        # Main container
        main_container = ctk.CTkFrame(self.root, fg_color="#F5F5F5")
        main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Content frame with three columns
        content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True)
        
        # Configure grid
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        content_frame.grid_columnconfigure(2, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)
        
        # Test containers
        # Customer container (left)
        customer_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_CUSTOMER
        )
        customer_container.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=(0, 15))
        
        # Add test content
        ctk.CTkLabel(
            customer_container,
            text="Customer Container\nHeight: 720px",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Upload container (middle)
        upload_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_UPLOAD
        )
        upload_container.grid(row=0, column=1, sticky="nsew", padx=(5, 5), pady=(0, 15))
        
        # Add test content
        ctk.CTkLabel(
            upload_container,
            text="Upload Container\nHeight: 720px",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Workflow container (right)
        workflow_container = ctk.CTkFrame(
            content_frame,
            **UITheme.CONTAINER_STYLE_WORKFLOW
        )
        workflow_container.grid(row=0, column=2, sticky="nsew", padx=(10, 0), pady=(0, 15))
        
        # Add test content
        ctk.CTkLabel(
            workflow_container,
            text="Workflow Container\nHeight: 720px",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=20)
        
        # Add test content to show fullness
        for i, (container, name) in enumerate([
            (customer_container, "Customer"),
            (upload_container, "Upload"),
            (workflow_container, "Workflow")
        ]):
            for j in range(15):  # Add multiple items to test height
                ctk.CTkLabel(
                    container,
                    text=f"{name} Item {j+1}",
                    font=ctk.CTkFont(size=12)
                ).pack(pady=2)
                
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    test = ContainerHeightTest()
    test.run()
