#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print('🔍 Testing folder open UI issue...')

try:
    import customtkinter as ctk
    ctk.set_appearance_mode('light')
    
    root = ctk.CTk()
    root.geometry('1000x700')
    root.title('Folder Open UI Test')
    
    from welcome_screen import WelcomeScreen
    
    class MockApp:
        pass
    
    screen = WelcomeScreen(root, MockApp())
    
    def test_folder_open():
        print('🎯 Testing folder open button click...')
        
        try:
            # First select a customer
            screen._select_customer_by_name('MaxMuster')
            print('✅ Customer selected: MaxMuster')
            
            # Wait for UI update, then click folder button
            root.after(1000, lambda: click_folder_button())
            
        except Exception as e:
            print(f'❌ Error in customer selection: {e}')
            import traceback
            traceback.print_exc()
    
    def click_folder_button():
        print('🔍 Attempting to click folder button...')
        
        try:
            if hasattr(screen, 'folder_btn') and screen.folder_btn:
                state = screen.folder_btn.cget('state')
                text = screen.folder_btn.cget('text')
                print(f'📂 Folder button before click: "{text}" - state: {state}')
                
                if state == 'normal':
                    print('🖱️ Simulating button click...')
                    # Call the actual method that would be called by button click
                    screen._open_current_customer_folder()
                    print('✅ Button click simulated')
                    
                    # Wait a moment then check UI state
                    root.after(2000, check_ui_after_click)
                else:
                    print('❌ Button is disabled, cannot click')
                    root.after(1000, root.destroy)
            else:
                print('❌ Folder button not found')
                root.after(1000, root.destroy)
                
        except Exception as e:
            print(f'❌ Error clicking folder button: {e}')
            import traceback
            traceback.print_exc()
            root.after(1000, root.destroy)
    
    def check_ui_after_click():
        print('🔍 Checking UI state after folder button click...')
        
        try:
            # Check if button still exists and is visible
            if hasattr(screen, 'folder_btn') and screen.folder_btn:
                try:
                    text = screen.folder_btn.cget('text')
                    state = screen.folder_btn.cget('state')
                    print(f'📂 Folder button after click: "{text}" - state: {state}')
                    print('✅ Button still exists and accessible')
                except Exception as e:
                    print(f'❌ Button exists but error getting properties: {e}')
            else:
                print('❌ Folder button no longer exists!')
                
            # Check if remove button still exists
            if hasattr(screen, 'remove_btn') and screen.remove_btn:
                try:
                    text = screen.remove_btn.cget('text')
                    state = screen.remove_btn.cget('state')
                    print(f'🗑️ Remove button after click: "{text}" - state: {state}')
                    print('✅ Remove button still exists and accessible')
                except Exception as e:
                    print(f'❌ Remove button exists but error getting properties: {e}')
            else:
                print('❌ Remove button no longer exists!')
                
            # Check main container
            if hasattr(screen, 'main_container') and screen.main_container:
                children = screen.main_container.winfo_children()
                print(f'📋 Main container has {len(children)} children')
                for i, child in enumerate(children):
                    print(f'  Child {i}: {type(child).__name__}')
            else:
                print('❌ Main container not found!')
                
        except Exception as e:
            print(f'❌ Error checking UI state: {e}')
            import traceback
            traceback.print_exc()
        
        print('🏁 UI test completed')
        root.after(2000, root.destroy)
    
    root.after(500, test_folder_open)
    root.mainloop()
    
    print('✅ Folder open UI test completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
