#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print('🔍 Testing REAL GUI folder open issue...')

try:
    import customtkinter as ctk
    ctk.set_appearance_mode('light')
    
    root = ctk.CTk()
    root.geometry('1200x800')
    root.title('REAL GUI Folder Open Test')
    
    from welcome_screen import WelcomeScreen
    
    class MockApp:
        pass
    
    screen = WelcomeScreen(root, MockApp())
    
    # Create instructions label
    instructions = ctk.CTkLabel(
        root,
        text="ANWEISUNGEN:\n1. Wähle einen Kunden aus\n2. Klicke auf 'Kundenordner öffnen'\n3. Schaue ob die UI kaputt geht",
        font=ctk.CTkFont(size=14, weight="bold"),
        fg_color="lightblue",
        corner_radius=10,
        width=300,
        height=100
    )
    instructions.place(x=10, y=10)
    
    # Keep the window open for manual testing
    root.mainloop()
    
    print('✅ REAL GUI test completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
