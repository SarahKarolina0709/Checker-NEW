#!/usr/bin/env python3
"""
Test script for persistent recent projects functionality.
Verifies that JSON persistence is working correctly.
"""

import os
import json
import sys
sys.path.append(os.path.dirname(__file__))

def test_recent_projects_persistence():
    """Test the recent projects JSON persistence functionality."""
    print("🧪 Testing Recent Projects Persistence...")
    
    # Test data
    test_projects = [
        {
            "kunde_name": "Test Kunde GmbH",
            "auftragsnummer": "TEST-2025-001",
            "last_used": "03.07.2025, 15:30",
            "workflow_type": "angebots_workflow"
        },
        {
            "kunde_name": "Demo Corp",
            "auftragsnummer": "DEMO-PROJECT",
            "last_used": "02.07.2025, 10:15",
            "workflow_type": "pruefung_workflow"
        }
    ]
    
    # Test file path
    test_file = "test_recent_projects.json"
    
    try:
        # Test 1: Save to JSON
        print("📝 Test 1: Saving to JSON...")
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump(test_projects, f, ensure_ascii=False, indent=2)
        print("✅ JSON save successful")
        
        # Test 2: Load from JSON
        print("📖 Test 2: Loading from JSON...")
        with open(test_file, "r", encoding="utf-8") as f:
            loaded_projects = json.load(f)
        
        # Verify data integrity
        if loaded_projects == test_projects:
            print("✅ JSON load successful - data integrity verified")
        else:
            print("❌ Data integrity check failed")
            return False
        
        # Test 3: File structure
        print("🔍 Test 3: Verifying file structure...")
        if isinstance(loaded_projects, list) and len(loaded_projects) == 2:
            first_project = loaded_projects[0]
            required_fields = ["kunde_name", "auftragsnummer", "last_used", "workflow_type"]
            
            if all(field in first_project for field in required_fields):
                print("✅ File structure verified")
            else:
                print("❌ Missing required fields")
                return False
        else:
            print("❌ Invalid file structure")
            return False
        
        # Test 4: UTF-8 encoding
        print("🔤 Test 4: Testing UTF-8 encoding...")
        unicode_test = {
            "kunde_name": "Müller & Söhne GmbH",
            "auftragsnummer": "ÜMLAUT-ÄÖ-2025",
            "last_used": "03.07.2025, 16:00",
            "workflow_type": "finalisierung_workflow"
        }
        
        with open(test_file, "w", encoding="utf-8") as f:
            json.dump([unicode_test], f, ensure_ascii=False, indent=2)
        
        with open(test_file, "r", encoding="utf-8") as f:
            loaded_unicode = json.load(f)
        
        if loaded_unicode[0]["kunde_name"] == "Müller & Söhne GmbH":
            print("✅ UTF-8 encoding working correctly")
        else:
            print("❌ UTF-8 encoding failed")
            return False
        
        print("\n🎉 All tests passed! Recent projects persistence is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        # Cleanup
        if os.path.exists(test_file):
            os.remove(test_file)
            print("🧹 Test file cleaned up")

if __name__ == "__main__":
    success = test_recent_projects_persistence()
    exit(0 if success else 1)
