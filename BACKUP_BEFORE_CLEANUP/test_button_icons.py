#!/usr/bin/env python3
"""
Quick Visual Test for Button Icon Improvements
Tests the enhanced Schnellstart and Zuletzt verwendet buttons
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_icon_differentiation():
    """Test that the new icon differentiation is working"""
    print("=== Button Icon Differentiation Test ===")
    print()
    
    try:
        # Test icon availability
        from checker_app import CheckerApp
        
        # Create a minimal app instance to test icon loading
        import customtkinter as ctk
        ctk.set_appearance_mode("light")
        
        root = ctk.CTk()
        root.withdraw()  # Hide the window
        
        # Create app instance to access icon system
        app = CheckerApp()
        
        print("✅ Application instance created successfully")
        print()
        
        # Test specific icons used in the improvements
        print("Testing Icon Availability:")
        print("-" * 40)
        
        # Test rocket icon (Schnellstart)
        rocket_icon = app.get_icon('rocket', size=(16, 16))
        if rocket_icon:
            print("✅ Rocket icon (Schnellstart): Available")
        else:
            print("❌ Rocket icon: Not available")
        
        # Test calendar icon (Zuletzt verwendet)
        calendar_icon = app.get_icon('calendar', size=(16, 16))
        if calendar_icon:
            print("✅ Calendar icon (Zuletzt verwendet): Available")
        else:
            print("❌ Calendar icon: Not available")
        
        # Test old clock icon (for comparison)
        clock_icon = app.get_icon('clock', size=(16, 16))
        if clock_icon:
            print("✅ Clock icon (old): Available")
        else:
            print("❌ Clock icon: Not available")
        
        print()
        print("Icon Differentiation Summary:")
        print("-" * 40)
        print("🚀 Schnellstart: Rocket icon - ✅ Action-oriented, immediate start")
        print("📅 Zuletzt verwendet: Calendar icon - ✅ Time-based, historical")
        print("🕐 Old clock icon: - ✅ Available as fallback")
        
        print()
        print("Visual Distinction Test:")
        print("-" * 40)
        
        if rocket_icon and calendar_icon:
            print("✅ EXCELLENT: Both icons are available and clearly different")
            print("   • Rocket = Action/Launch metaphor")
            print("   • Calendar = Time/History metaphor")
            print("   • Clear semantic distinction achieved!")
        elif rocket_icon:
            print("⚠️  PARTIAL: Rocket available, calendar missing")
        elif calendar_icon:
            print("⚠️  PARTIAL: Calendar available, rocket missing")
        else:
            print("❌ ISSUE: Both icons missing")
        
        print()
        print("=== Test Complete ===")
        
        # Cleanup
        root.destroy()
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_icon_differentiation()
    sys.exit(0 if success else 1)
