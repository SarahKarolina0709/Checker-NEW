#!/usr/bin/env python3
"""
Test script to verify Prüfung workflow functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_controller_methods():
    """Test if all required methods exist in PruefungWorkflowController"""
    print("Testing PruefungWorkflowController methods...")
    
    try:
        from pruefung_workflow_controller import PruefungWorkflowController
        
        # Create controller instance
        controller = PruefungWorkflowController()
        print("✓ Controller created successfully")
        
        # Check required methods
        required_methods = [
            'get_available_checks',
            'get_tab_configurations', 
            'add_file_pair',
            'clear_all_file_pairs',
            'select_all_checks',
            'deselect_all_checks',
            'start_checking_process',
            'stop_checking_process',
            'export_results_as_pdf',
            'remove_file_pair_by_id'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if hasattr(controller, method_name):
                method = getattr(controller, method_name)
                if callable(method):
                    print(f"✓ {method_name} - exists and callable")
                else:
                    print(f"✗ {method_name} - exists but not callable")
                    missing_methods.append(method_name)
            else:
                print(f"✗ {method_name} - missing")
                missing_methods.append(method_name)
        
        if missing_methods:
            print(f"\n❌ Missing or invalid methods: {missing_methods}")
            return False
        else:
            print(f"\n✅ All {len(required_methods)} required methods are present and callable!")
            return True
            
    except Exception as e:
        print(f"❌ Error importing or testing controller: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ui_integration():
    """Test if the UI components can be imported and instantiated"""
    print("\nTesting UI integration...")
    
    try:
        # Test if UI components can be imported
        from ui_components.pruefung_workflow_view import PruefungWorkflowView
        print("✓ PruefungWorkflowView imported successfully")
        
        # Test if workflow can be imported  
        from pruefung_workflow import PruefungWorkflow
        print("✓ PruefungWorkflow imported successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Error importing UI components: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("PRÜFUNG WORKFLOW FUNCTIONALITY TEST")
    print("=" * 60)
    
    success = True
    
    # Test controller methods
    success &= test_controller_methods()
    
    # Test UI integration
    success &= test_ui_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! Prüfung workflow should work correctly.")
    else:
        print("💥 SOME TESTS FAILED! Check the errors above.")
    print("=" * 60)
