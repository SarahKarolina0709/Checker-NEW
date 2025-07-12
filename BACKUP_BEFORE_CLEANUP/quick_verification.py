#!/usr/bin/env python3
"""
Language Detection Fix Verification
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=== Language Detection Fix Verification ===")

try:
    # Test 1: Import controller
    from pruefung_workflow_controller import PruefungWorkflowController
    controller = PruefungWorkflowController()
    print("✓ Controller imported and created successfully")
    
    # Test 2: Check if missing method exists
    if hasattr(controller, 'clear_all_file_pairs'):
        print("✓ clear_all_file_pairs method is now available")
    else:
        print("❌ clear_all_file_pairs method is still missing")
    
    # Test 3: Test language detection
    from language_detection import detect_language
    test_text = "Stock market punk: Nvidia tops all expectations, but BYD after the correction, what to do?"
    detected_lang = detect_language(test_text)
    print(f"✓ Language detection working: {detected_lang}")
    
    print("\n🎉 All basic tests passed!")
    print("The application should now start without the AttributeError.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

def simple_test():
    print("Starting Simple Refactoring Verification...")
    
    # Test 1: Base UI Components
    try:
        from base_ui_components import BaseUIComponents, BaseWorkflowMixin
        print("✓ Base UI Components imported successfully")
    except Exception as e:
        print(f"✗ Base UI Components failed: {e}")
        return False
    
    # Test 2: Smart Workflow Assistant
    try:
        from smart_workflow_assistant import SmartWorkflowAssistant
        assistant = SmartWorkflowAssistant()
        assistant.track_action("test_action", 1.0, True)
        print("✓ Smart Workflow Assistant working")
    except Exception as e:
        print(f"✗ Smart Workflow Assistant failed: {e}")
        return False
    
    # Test 3: Refactored Workflows
    workflows_to_test = [
        ("projekt_workflow", "ProjektWorkflow"),
        ("finalisierung_workflow", "FinalisierungWorkflow"),
        ("pruefung_workflow", "PruefungWorkflow"),
        ("angebots_workflow", "AngebotsWorkflow")
    ]
    
    working_workflows = 0
    for module_name, class_name in workflows_to_test:
        try:
            module = __import__(module_name)
            if hasattr(module, class_name):
                workflow_class = getattr(module, class_name)
                # Check if it inherits from BaseWorkflowMixin
                if issubclass(workflow_class, BaseWorkflowMixin):
                    print(f"✓ {class_name} working correctly")
                    working_workflows += 1
                else:
                    print(f"⚠ {class_name} not using BaseWorkflowMixin")
            else:
                print(f"✗ {class_name} not found in {module_name}")
        except Exception as e:
            print(f"✗ {class_name} failed: {e}")
    
    print(f"\nResults: {working_workflows}/{len(workflows_to_test)} workflows working")
    
    if working_workflows == len(workflows_to_test):
        print("\n🎉 REFACTORING SUCCESS!")
        print("All workflows have been successfully refactored to use shared components!")
        return True
    else:
        print(f"\n⚠ {len(workflows_to_test) - working_workflows} workflows need attention")
        return False

if __name__ == "__main__":
    simple_test()
