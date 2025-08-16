#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 GUI FUZZY DIALOG DEBUG TEST
Test ob _show_duplicate_warning_dialog wirklich aufgerufen wird
"""

import sys
import os
sys.path.append(os.getcwd())

def test_dialog_integration():
    """Test the actual GUI dialog integration"""
    print("🎯 GUI DIALOG INTEGRATION TEST")
    print("=" * 50)
    
    try:
        # Import without starting GUI
        from welcome_screen import WelcomeScreen
        print("✅ WelcomeScreen imported successfully")
        
        # Check if dialog method exists
        if hasattr(WelcomeScreen, '_show_duplicate_warning_dialog'):
            print("✅ _show_duplicate_warning_dialog method exists")
        else:
            print("❌ _show_duplicate_warning_dialog method NOT FOUND!")
            return False
        
        # Check if _add_customer method exists
        if hasattr(WelcomeScreen, '_add_customer'):
            print("✅ _add_customer method exists")
        else:
            print("❌ _add_customer method NOT FOUND!")
            return False
        
        # Try to find dialog call in source code
        try:
            with open('welcome_screen.py', 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Look for dialog calls
            dialog_calls = []
            lines = source_code.split('\n')
            for i, line in enumerate(lines, 1):
                if '_show_duplicate_warning_dialog' in line:
                    dialog_calls.append((i, line.strip()))
            
            print(f"\n🔍 DIALOG CALLS IN SOURCE CODE:")
            if dialog_calls:
                for line_num, line in dialog_calls:
                    print(f"   Line {line_num}: {line}")
            else:
                print("   ❌ NO DIALOG CALLS FOUND IN SOURCE!")
                return False
        
        except Exception as e:
            print(f"⚠️ Could not read source code: {e}")
        
        # Look for fuzzy match handling
        fuzzy_matches = []
        for i, line in enumerate(lines, 1):
            if 'similar_customers' in line and ('if' in line or 'and' in line or 'not success' in line):
                fuzzy_matches.append((i, line.strip()))
        
        print(f"\n🔍 FUZZY MATCH HANDLING:")
        if fuzzy_matches:
            for line_num, line in fuzzy_matches:
                print(f"   Line {line_num}: {line}")
        else:
            print("   ❌ NO FUZZY MATCH HANDLING FOUND!")
        
        return True
        
    except Exception as e:
        print(f"❌ GUI integration test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def analyze_add_customer_method():
    """Analyze the _add_customer method implementation"""
    print(f"\n🔍 _ADD_CUSTOMER METHOD ANALYSIS")
    print("=" * 50)
    
    try:
        with open('welcome_screen.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        # Find _add_customer method
        lines = source_code.split('\n')
        add_customer_lines = []
        in_add_customer = False
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            if 'def _add_customer(' in line:
                in_add_customer = True
                indent_level = len(line) - len(line.lstrip())
                add_customer_lines.append((i, line))
                continue
            
            if in_add_customer:
                current_indent = len(line) - len(line.lstrip())
                
                # Check if we're still in the method
                if line.strip() and current_indent <= indent_level:
                    # We've left the method
                    break
                
                add_customer_lines.append((i, line))
        
        if add_customer_lines:
            print("✅ FOUND _add_customer METHOD:")
            for line_num, line in add_customer_lines:
                print(f"   {line_num:3}: {line}")
        else:
            print("❌ _add_customer METHOD NOT FOUND!")
            return False
        
        # Check for critical elements
        method_text = '\n'.join([line for _, line in add_customer_lines])
        
        critical_checks = [
            ('customer_manager.add_customer', 'CustomerManager integration'),
            ('similar_customers', 'Similar customers handling'),
            ('_show_duplicate_warning_dialog', 'Dialog call'),
            ('not success', 'Error handling'),
            ('return', 'Return statements')
        ]
        
        print(f"\n🎯 CRITICAL ELEMENTS CHECK:")
        for check, description in critical_checks:
            if check in method_text:
                print(f"   ✅ {description}: FOUND")
            else:
                print(f"   ❌ {description}: MISSING")
        
        return True
        
    except Exception as e:
        print(f"❌ Add customer analysis error: {e}")
        return False

def find_dialog_definition():
    """Find the _show_duplicate_warning_dialog definition"""
    print(f"\n🔍 DIALOG DEFINITION ANALYSIS")
    print("=" * 50)
    
    try:
        with open('welcome_screen.py', 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        lines = source_code.split('\n')
        dialog_definition = []
        in_dialog_method = False
        indent_level = 0
        
        for i, line in enumerate(lines, 1):
            if 'def _show_duplicate_warning_dialog(' in line:
                in_dialog_method = True
                indent_level = len(line) - len(line.lstrip())
                dialog_definition.append((i, line))
                continue
            
            if in_dialog_method:
                current_indent = len(line) - len(line.lstrip())
                
                # Check if we're still in the method (or empty line)
                if line.strip() and current_indent <= indent_level:
                    break
                
                dialog_definition.append((i, line))
                
                # Stop after reasonable number of lines
                if len(dialog_definition) > 100:
                    dialog_definition.append((i+1, "   # ... (truncated)"))
                    break
        
        if dialog_definition:
            print("✅ FOUND _show_duplicate_warning_dialog METHOD:")
            print("   First 20 lines:")
            for line_num, line in dialog_definition[:20]:
                print(f"   {line_num:3}: {line}")
            
            if len(dialog_definition) > 20:
                print(f"   ... and {len(dialog_definition)-20} more lines")
            
            # Check if dialog creates actual widgets
            dialog_text = '\n'.join([line for _, line in dialog_definition])
            
            widget_checks = [
                ('CTkToplevel', 'Dialog window'),
                ('CTkLabel', 'Labels'),
                ('CTkButton', 'Buttons'),
                ('grab_set', 'Modal dialog'),
                ('mainloop', 'Dialog loop')
            ]
            
            print(f"\n🎯 DIALOG WIDGET CHECK:")
            for check, description in widget_checks:
                if check in dialog_text:
                    print(f"   ✅ {description}: FOUND")
                else:
                    print(f"   ❌ {description}: MISSING")
            
            return True
        else:
            print("❌ _show_duplicate_warning_dialog METHOD NOT FOUND!")
            return False
        
    except Exception as e:
        print(f"❌ Dialog definition analysis error: {e}")
        return False

if __name__ == "__main__":
    print("🎯 COMPREHENSIVE GUI FUZZY DIALOG DEBUG")
    print("=" * 60)
    
    results = []
    
    print("Step 1: Testing dialog integration...")
    results.append(test_dialog_integration())
    
    print("\nStep 2: Analyzing _add_customer method...")
    results.append(analyze_add_customer_method())
    
    print("\nStep 3: Finding dialog definition...")
    results.append(find_dialog_definition())
    
    print(f"\n🎯 DIAGNOSIS SUMMARY:")
    print("=" * 60)
    
    if all(results):
        print("✅ ALL COMPONENTS FOUND!")
        print("💡 LIKELY ISSUE: Dialog is created but not displayed properly")
        print("\n🔧 DEBUGGING STEPS:")
        print("   1. Add print statements to _add_customer method")
        print("   2. Add print statements to _show_duplicate_warning_dialog")
        print("   3. Check if dialog.mainloop() is called")
        print("   4. Verify parent window reference")
        
    elif not results[0]:
        print("❌ INTEGRATION ISSUE: Methods not found or not called")
        
    elif not results[1]:
        print("❌ ADD_CUSTOMER ISSUE: Method missing critical components")
        
    elif not results[2]:
        print("❌ DIALOG ISSUE: Dialog method not properly implemented")
    
    else:
        print("⚠️ MIXED RESULTS: Some components working, others not")
    
    print(f"\n" + "=" * 60)
