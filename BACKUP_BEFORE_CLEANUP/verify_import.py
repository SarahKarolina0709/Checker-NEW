"""
Simple script to verify that the corrected_pruefung_workflow.py can be imported
"""
try:
    from corrected_pruefung_workflow import PruefungWorkflow
    print("✓ Successfully imported PruefungWorkflow from corrected_pruefung_workflow")
    
    # Check if the required methods exist
    methods = [
        'select_text_a',
        'select_text_b',
        '_update_dynamic_content'
    ]
    
    all_methods_exist = True
    for method in methods:
        if hasattr(PruefungWorkflow, method) and callable(getattr(PruefungWorkflow, method)):
            print(f"✓ Method {method} exists")
        else:
            print(f"✗ Method {method} does not exist")
            all_methods_exist = False
    
    if all_methods_exist:
        print("\n✓ All required methods exist in the PruefungWorkflow class")
    else:
        print("\n✗ Some methods are missing in the PruefungWorkflow class")
        
except ImportError as e:
    print(f"✗ Error importing PruefungWorkflow: {str(e)}")
except Exception as e:
    import traceback
    print(f"✗ Unexpected error: {str(e)}")
    traceback.print_exc()
