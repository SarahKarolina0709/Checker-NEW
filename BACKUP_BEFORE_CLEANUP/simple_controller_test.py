import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from pruefung_workflow_controller import PruefungWorkflowController
    controller = PruefungWorkflowController()
    tabs = controller.get_tab_configurations()
    print("SUCCESS: Controller works correctly!")
    print(f"Found {len(tabs)} tab configurations")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
