#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print('🔍 Testing BLUE button style when active...')

try:
    import customtkinter as ctk
    ctk.set_appearance_mode('light')
    
    root = ctk.CTk()
    root.geometry('1000x700')
    root.title('Blue Button Style Test')
    
    from welcome_screen import WelcomeScreen
    
    class MockApp:
        pass
    
    screen = WelcomeScreen(root, MockApp())
    
    def test_button_colors():
        print('🎯 Testing button color changes...')
        
        try:
            # Check initial button state (should be disabled/gray)
            if hasattr(screen, 'folder_btn') and screen.folder_btn:
                initial_state = screen.folder_btn.cget('state')
                initial_fg = screen.folder_btn.cget('fg_color')
                print(f'📂 Initial folder button: state={initial_state}, fg_color={initial_fg}')
            
            # Select customer (should make button blue)
            screen._select_customer_by_name('MaxMuster')
            print('✅ Customer selected: MaxMuster')
            
            # Wait for UI updates, then check button colors
            root.after(500, lambda: check_button_colors())
            
        except Exception as e:
            print(f'❌ Error in button color test: {e}')
            import traceback
            traceback.print_exc()
            root.after(1000, root.destroy)
    
    def check_button_colors():
        print('🎨 Checking button colors after customer selection...')
        
        try:
            # Check folder button color
            if hasattr(screen, 'folder_btn') and screen.folder_btn:
                final_state = screen.folder_btn.cget('state')
                final_fg = screen.folder_btn.cget('fg_color')
                final_text_color = screen.folder_btn.cget('text_color')
                text = screen.folder_btn.cget('text')
                
                print(f'📂 Final folder button: "{text}"')
                print(f'   State: {final_state}')
                print(f'   fg_color: {final_fg}')
                print(f'   text_color: {final_text_color}')
                
                # Check if it's blue (primary color)
                if 'normal' in str(final_state).lower():
                    print('✅ Button is ACTIVE (normal state)')
                    if final_fg and ('#1F4E79' in str(final_fg) or '#2563EB' in str(final_fg)):
                        print('✅ Button is BLUE (primary color)!')
                    else:
                        print(f'⚠️ Button color might not be blue: {final_fg}')
                else:
                    print('❌ Button is still disabled')
            
            # Check remove button too
            if hasattr(screen, 'remove_btn') and screen.remove_btn:
                remove_state = screen.remove_btn.cget('state')
                remove_fg = screen.remove_btn.cget('fg_color')
                remove_text = screen.remove_btn.cget('text')
                
                print(f'🗑️ Remove button: "{remove_text}" - state={remove_state}, fg_color={remove_fg}')
                
        except Exception as e:
            print(f'❌ Error checking button colors: {e}')
            import traceback
            traceback.print_exc()
        
        print('🏁 Button color test completed')
        root.after(3000, root.destroy)
    
    root.after(500, test_button_colors)
    root.mainloop()
    
    print('✅ Blue button style test completed!')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
