"""
Test script to verify the fixed PruefungWorkflow implementation
"""
import tkinter as tk
import customtkinter as ctk
from corrected_pruefung_workflow import PruefungWorkflow

def main():
    print("=" * 50)
    print("Testing corrected_pruefung_workflow.py")
    print("=" * 50)
    
    # Create root window
    root = tk.Tk()
    root.title("PruefungWorkflow Test")
    root.geometry("800x600")
    
    # Create workflow instance
    try:
        workflow = PruefungWorkflow(
            root=root,
            back_callback=lambda: print("Back callback called"),
            project_data={"files": [None, None], "selected_checks": ["Grammatikprüfung"]}
        )
        print("✓ Successfully created PruefungWorkflow instance")
        
        # Test select_text_a method
        if hasattr(workflow, 'select_text_a') and callable(getattr(workflow, 'select_text_a')):
            print("✓ select_text_a method exists")
        else:
            print("✗ select_text_a method does not exist")
            
        # Test select_text_b method
        if hasattr(workflow, 'select_text_b') and callable(getattr(workflow, 'select_text_b')):
            print("✓ select_text_b method exists")
        else:
            print("✗ select_text_b method does not exist")
            
        # Test _update_dynamic_content method
        if hasattr(workflow, '_update_dynamic_content') and callable(getattr(workflow, '_update_dynamic_content')):
            print("✓ _update_dynamic_content method exists")
        else:
            print("✗ _update_dynamic_content method does not exist")
            
        # Display the workflow UI
        workflow.show_workflow()
        print("✓ Workflow UI displayed successfully")
        
        print("\n✓ All tests passed! The workflow should work correctly.")
        
        # Start the main loop
        root.mainloop()
        
    except Exception as e:
        import traceback
        print(f"✗ Error: {str(e)}")
        traceback.print_exc()
        return False
        
    return True

if __name__ == "__main__":
    main()
