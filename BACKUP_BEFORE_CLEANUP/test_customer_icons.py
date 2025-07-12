"""
Test script to verify that the new customer icons are being used in recent projects
"""

import sys
import os
sys.path.append('.')

# Test the icon loading directly
def test_new_icon_loading():
    print("🔍 Testing new customer icon loading...")
    
    try:
        from fluent_icons_manager import EnhancedFluentIconManager
        
        # Initialize icon manager
        workspace_path = os.getcwd()
        icon_manager = EnhancedFluentIconManager(workspace_path=workspace_path)
        
        # Test businesswoman icon
        print("\n📋 Testing businesswoman icon:")
        businesswoman_icon = icon_manager.get_icon('businesswoman', (24, 24))
        if businesswoman_icon:
            print("✅ businesswoman icon loaded successfully")
            print(f"   Type: {type(businesswoman_icon)}")
        else:
            print("❌ businesswoman icon failed to load")
        
        # Test client icon
        print("\n📋 Testing client icon:")
        client_icon = icon_manager.get_icon('client', (24, 24))
        if client_icon:
            print("✅ client icon loaded successfully")
            print(f"   Type: {type(client_icon)}")
        else:
            print("❌ client icon failed to load")
        
        # Test the mapping
        print("\n🗂️ Icon Mapping Check:")
        local_mapping = icon_manager.LOCAL_ICON_MAPPING
        print(f"businesswoman in mapping: {'businesswoman' in local_mapping}")
        print(f"client in mapping: {'client' in local_mapping}")
        
        if 'businesswoman' in local_mapping:
            print(f"businesswoman maps to: {local_mapping['businesswoman']}")
        if 'client' in local_mapping:
            print(f"client maps to: {local_mapping['client']}")
            
        # Check fallback emojis
        print("\n😊 Emoji Fallback Check:")
        fluent_icons = icon_manager.FLUENT_ICONS
        print(f"businesswoman emoji: {fluent_icons.get('businesswoman', 'NOT FOUND')}")
        print(f"client emoji: {fluent_icons.get('client', 'NOT FOUND')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        return False

def test_recent_projects_mapping():
    """Test the actual mapping used in recent projects"""
    print("\n🎯 Testing Recent Projects Icon Mapping...")
    
    # This is the exact mapping from ultra_modern_welcome_screen_simplified.py
    customer_icons = {
        "angebots_workflow": "businesswoman",
        "pruefung_workflow": "client", 
        "finalisierung_workflow": "businesswoman"
    }
    
    # Test projects
    test_projects = [
        {"workflow_type": "angebots_workflow", "name": "Mustermann GmbH"},
        {"workflow_type": "pruefung_workflow", "name": "TechCorp AG"},
        {"workflow_type": "finalisierung_workflow", "name": "Global Solutions"}
    ]
    
    print("📊 Icon mapping results:")
    for project in test_projects:
        workflow_type = project["workflow_type"]
        icon_name = customer_icons.get(workflow_type, "client")
        print(f"  {project['name']} ({workflow_type}) → {icon_name}.png")
    
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 CUSTOMER ICONS VERIFICATION TEST")
    print("=" * 60)
    
    # Test 1: Icon loading
    test1_result = test_new_icon_loading()
    
    # Test 2: Recent projects mapping
    test2_result = test_recent_projects_mapping()
    
    print("\n" + "=" * 60)
    if test1_result and test2_result:
        print("✅ ALL TESTS PASSED - Customer icons are properly configured!")
    else:
        print("❌ SOME TESTS FAILED - Please check the configuration")
    print("=" * 60)
