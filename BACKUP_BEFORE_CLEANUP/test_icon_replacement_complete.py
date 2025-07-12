"""
Final verification test: Ensure all old workflow icons are replaced with customer icons
"""

import sys
import os
sys.path.append('.')

def test_all_old_icons_replaced():
    """Test that no old workflow icons remain in the code"""
    print("🔍 Verifying complete icon replacement...")
    
    # Read the welcome screen file
    welcome_file = "ultra_modern_welcome_screen_simplified.py"
    
    with open(welcome_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for old workflow icons
    old_icons = [
        "euro-money-2",
        "spell-check", 
        "done"  # when used in workflow context
    ]
    
    print("\n📋 Checking for old workflow icons:")
    found_old_icons = False
    
    for old_icon in old_icons:
        if old_icon in content:
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if old_icon in line:
                    print(f"❌ Found '{old_icon}' on line {i}: {line.strip()}")
                    found_old_icons = True
    
    if not found_old_icons:
        print("✅ No old workflow icons found!")
    
    # Check for new customer icons
    print("\n📋 Checking for new customer icons:")
    new_icons = ["businesswoman", "client"]
    
    for new_icon in new_icons:
        count = content.count(new_icon)
        print(f"✅ '{new_icon}' appears {count} times")
    
    # Summary
    print("\n" + "=" * 50)
    if not found_old_icons:
        print("🎉 SUCCESS: All old workflow icons successfully replaced!")
        print("   • euro-money-2 (€) → businesswoman.png")
        print("   • spell-check (✓) → client.png") 
        print("   • done (✔️) → businesswoman.png")
    else:
        print("⚠️  WARNING: Some old icons still found - please review above")
    print("=" * 50)
    
    return not found_old_icons

if __name__ == "__main__":
    test_all_old_icons_replaced()
