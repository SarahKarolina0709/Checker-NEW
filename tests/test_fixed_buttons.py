#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print('✅ Testing FIXED customer button states...')

try:
    import customtkinter as ctk
    ctk.set_appearance_mode('light')
    
    root = ctk.CTk()
    root.geometry('1000x700')
    root.title('FIXED Button States Test')
    
    from welcome_screen import WelcomeScreen
    
    class MockApp:
        pass
    
    screen = WelcomeScreen(root, MockApp())
    
    def test_fixed_buttons():
        print('🔍 Testing FIXED button existence and states...')
        
        # Check button existence and initial states
        buttons_to_check = [
            ('folder_btn', 'Kundenordner öffnen'),
            ('remove_btn', 'Entfernen')
        ]
        
        for attr, desc in buttons_to_check:
            if hasattr(screen, attr):
                widget = getattr(screen, attr)
                if widget:
                    try:
                        state = widget.cget('state')
                        text = widget.cget('text')
                        print(f'📋 Found {attr}: "{text}" - state: {state}')
                    except Exception as e:
                        print(f'❌ {desc}: error getting info: {e}')
                else:
                    print(f'⚠️ {desc}: is None')
            else:
                print(f'❌ {desc}: does not exist')
        
        # Test customer selection and button state changes
        root.after(1500, lambda: test_customer_selection())
    
    def test_customer_selection():
        print('🎯 Testing customer selection with FIXED button update...')
        
        try:
            # Select customer using the fixed method
            screen._select_customer_by_name('MaxMuster')
            print('✅ Customer selected: MaxMuster')
            
            # Check current_customer attribute
            current = getattr(screen, 'current_customer', None)
            print(f'🔍 Current customer attribute: {current}')
            
            # Wait a bit for UI updates, then check button states
            root.after(500, lambda: check_final_states())
            
        except Exception as e:
            print(f'❌ Error in customer selection: {e}')
            import traceback
            traceback.print_exc()
            root.after(1000, root.destroy)
    
    def check_final_states():
        print('🎯 Checking FINAL button states after FIXED customer selection...')
        
        # Check folder button
        if hasattr(screen, 'folder_btn') and screen.folder_btn:
            state = screen.folder_btn.cget('state')
            text = screen.folder_btn.cget('text')
            print(f'📂 Folder button FINAL state: "{text}" - {state}')
        
        # Check remove button
        if hasattr(screen, 'remove_btn') and screen.remove_btn:
            state = screen.remove_btn.cget('state')
            text = screen.remove_btn.cget('text')
            print(f'🗑️ Remove button FINAL state: "{text}" - {state}')
        
        print('✅ FIXED customer button test completed!')
        root.after(2000, root.destroy)
    
    root.after(500, test_fixed_buttons)
    root.mainloop()
    
    print('✅ FIXED customer button test completed successfully!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
