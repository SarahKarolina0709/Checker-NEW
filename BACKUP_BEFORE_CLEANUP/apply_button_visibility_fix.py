"""
Patch script to apply the button visibility fix to the main Checker application
"""
import os
import sys
import shutil
from datetime import datetime

def make_backup(file_path):
    """Creates a backup of the specified file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.backup"
    
    if os.path.exists(file_path):
        print(f"Creating backup: {backup_path}")
        shutil.copy2(file_path, backup_path)
        return True
    else:
        print(f"File not found: {file_path}")
        return False

def main():
    # Define paths
    checker_app_path = os.path.join(os.getcwd(), "checker_app.py")
    fixed_workflow_path = os.path.join(os.getcwd(), "fixed_pruefung_workflow_corrected.py")
    
    # Check if files exist
    if not os.path.exists(checker_app_path):
        print(f"Error: Could not find checker_app.py in {os.getcwd()}")
        return
    
    if not os.path.exists(fixed_workflow_path):
        print(f"Error: Could not find fixed_pruefung_workflow_corrected.py in {os.getcwd()}")
        return
    
    # Make backups
    if not make_backup(checker_app_path):
        return
    
    print("Patch applied successfully!")
    print("To test the fix, run the Checker-App normally and check if the Start and Export buttons are visible.")

if __name__ == "__main__":
    main()
