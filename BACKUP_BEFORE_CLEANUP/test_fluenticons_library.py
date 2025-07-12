#!/usr/bin/env python3
"""
Test script to explore the FluentIcons library capabilities
and see how we can integrate it with our CustomTkinter app.
"""

import sys
import os

def test_fluenticons_import():
    """Test importing FluentIcons and explore its API"""
    try:
        import FluentIcons
        print(f"✅ FluentIcons imported successfully")
        print(f"Version: {getattr(FluentIcons, '__version__', 'unknown')}")
        print(f"Available attributes: {[attr for attr in dir(FluentIcons) if not attr.startswith('_')]}")
        return FluentIcons
    except ImportError as e:
        print(f"❌ Failed to import FluentIcons: {e}")
        return None

def test_fluenticons_submodules():
    """Test importing various FluentIcons submodules"""
    modules_to_test = [
        'FluentIcons.icons',
        'FluentIcons.common',
        'FluentIcons.qml',
        'FluentIcons.qfluenticons'
    ]
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[''])
            print(f"✅ {module_name} imported successfully")
            print(f"   Attributes: {[attr for attr in dir(module) if not attr.startswith('_')][:10]}...")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")

def test_icon_availability():
    """Test what icons are available in FluentIcons"""
    try:
        from FluentIcons import FluentIcon
        print(f"✅ FluentIcon class imported")
        
        # Check if it has common icons we need
        test_icons = ['Home', 'Settings', 'Add', 'Delete', 'Edit', 'Save', 'Open']
        for icon_name in test_icons:
            if hasattr(FluentIcon, icon_name):
                icon = getattr(FluentIcon, icon_name)
                print(f"   ✅ {icon_name}: {icon}")
            else:
                print(f"   ❌ {icon_name}: not found")
                
    except ImportError as e:
        print(f"❌ Failed to import FluentIcon: {e}")

def test_icon_rendering():
    """Test if we can render icons as images for Tkinter"""
    try:
        from FluentIcons import FluentIcon, getIconColor, Theme
        print(f"✅ FluentIcon rendering modules imported")
        
        # Try to get an icon as an image
        try:
            from FluentIcons.common.icon import drawIcon
            print(f"✅ drawIcon function available")
        except ImportError:
            print(f"❌ drawIcon function not available")
            
        # Check available themes
        try:
            themes = [Theme.LIGHT, Theme.DARK]
            print(f"✅ Themes available: {themes}")
        except:
            print(f"❌ Theme constants not available")
            
    except ImportError as e:
        print(f"❌ Failed to import icon rendering modules: {e}")

def test_qt_integration():
    """Test if FluentIcons is designed for Qt"""
    try:
        from FluentIcons import qfluenticons
        print(f"✅ qfluenticons module available - this is likely a Qt-based library")
        
        # Check if it requires Qt
        try:
            from FluentIcons.common.icon import FluentIconBase
            print(f"✅ FluentIconBase available")
        except ImportError:
            print(f"❌ FluentIconBase not available")
            
    except ImportError as e:
        print(f"❌ qfluenticons not available: {e}")

def main():
    """Run all tests"""
    print("🔍 Testing FluentIcons Library Integration")
    print("=" * 50)
    
    # Test basic import
    fluent_icons = test_fluenticons_import()
    if not fluent_icons:
        return
    
    print("\n📦 Testing submodules...")
    test_fluenticons_submodules()
    
    print("\n🎯 Testing icon availability...")
    test_icon_availability()
    
    print("\n🎨 Testing icon rendering...")
    test_icon_rendering()
    
    print("\n⚙️ Testing Qt integration...")
    test_qt_integration()
    
    print("\n" + "=" * 50)
    print("✨ Test completed!")

if __name__ == "__main__":
    main()
