"""
Manual cleanup script to remove duplicate Python files
This script safely removes test files, backup files, and obvious duplicates
"""
import os
import shutil
from datetime import datetime
import glob

def create_backup_folder():
    """Create a timestamped backup folder"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = f"REMOVED_DUPLICATES_{timestamp}"
    os.makedirs(backup_folder, exist_ok=True)
    return backup_folder

def move_to_backup(file_path, backup_folder):
    """Move file to backup folder"""
    try:
        filename = os.path.basename(file_path)
        backup_path = os.path.join(backup_folder, filename)
        # Handle name conflicts
        counter = 1
        while os.path.exists(backup_path):
            name, ext = os.path.splitext(filename)
            backup_path = os.path.join(backup_folder, f"{name}_{counter}{ext}")
            counter += 1
        
        shutil.move(file_path, backup_path)
        print(f"✅ Moved: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error moving {file_path}: {e}")
        return False

def main():
    print("🧹 Python Duplicate File Cleanup")
    print("=" * 50)

    # --- SAFETY CONFIGURATION ---
    # Add any file that should NEVER be deleted to this list.
    essential_files = [
        "checker_app.py",
        "ui_theme.py",
        "kunden_manager.py",
        "app_managers.py",
        "angebots_workflow.py",
        "finalisierung_workflow.py",
        "pruefung_workflow.py",
        "projekt_workflow.py",
        "visual_integration.py",
        "modern_customer_gui.py",
        "smart_upload_calendar.py",
        "upload_manager.py",
        "workflow_router.py",
        "notification_center.py",
        "manual_cleanup.py",
        "analyze_dependencies.py",
        "core/__init__.py",
        "core/memory_manager.py",
        "core/state_manager.py",
        "core/thread_manager.py",
        "core/workflow_factory.py",
        "ui_components/__init__.py",
        "ui_components/base_view.py",
        "ui_components/file_pair_view.py",
        "ui_components/modern_button.py",
        "ui_components/progress_view.py",
        "ui_components/pruefung_workflow_view.py",
        "ui_components/result_view.py",
        "ui_components/settings_view.py",
        "ui_components/smart_entry.py",
        "ui_components/source_view.py",
        "utils/__init__.py",
        "utils/file_operations.py",
        "utils/icon_manager.py",
        "utils/logging_config.py",
        "utils/memory_monitor.py",
        "utils/resource_path.py",
        "utils/thread_worker.py",
        "utils/ui_utils.py",
        "utils/view_stack.py",
        "workflows/__init__.py",
        "workflows/base_workflow.py",
        "workflows/finalisierung_workflow_logic.py",
        "workflows/pruefung_workflow_controller.py",
        "__init__.py"
    ]
    
    # Get initial count
    initial_files = glob.glob("**/*.py", recursive=True)
    print(f"📊 Initial Python files: {len(initial_files)}")
    
    # Create backup folder
    backup_folder = create_backup_folder()
    print(f"📁 Created backup folder: {backup_folder}")
    
    # Define patterns to remove
    patterns_to_remove = [
        # Test files
        "test_*.py",
        "*_test.py",
        # Demo files  
        "demo_*.py",
        "*_demo.py",
        # Backup files
        "*_backup.py",
        "*_old.py",
        "*_copy.py",
        # Broken/temporary files
        "*_broken.py",
        "*_minimal.py", 
        "*_simplified.py",
        "*_temp.py",
        # Version files
        "*_v2.py",
        "*_v3.py",
        "*_2.py",
        # Debugging files
        "debug_*.py",
        "*_debug.py",
        # Quick files
        "quick_*.py",
        "*_quick.py"
    ]
    
    removed_count = 0
    
    # Process each pattern
    for pattern in patterns_to_remove:
        files = glob.glob(pattern, recursive=True)
        if files:
            print(f"\n🔍 Pattern: {pattern} found {len(files)} files:")
            for file_path in files:
                print(f"  - {file_path}")

            try:
                # Ask for user confirmation
                response = input(f"Do you want to remove these {len(files)} files? (y/N): ")
                if response.lower() != 'y':
                    print("Skipping this group.")
                    continue
            except EOFError:
                print("\nNon-interactive mode detected. Skipping confirmation.")

            for file_path in files:
                # Skip essential files
                if os.path.basename(file_path) in essential_files:
                    print(f"⏭️  Skipping essential file: {file_path}")
                    continue
                    
                if move_to_backup(file_path, backup_folder):
                    removed_count += 1
    
    # Also handle specific directories with many test files
    test_dirs = ["tests", "BACKUP_BEFORE_CLEANUP"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            test_files = glob.glob(f"{test_dir}/**/*.py", recursive=True)
            if test_files:
                print(f"\n🗂️  Processing directory: {test_dir} ({len(test_files)} files)")
                try:
                    # Ask for user confirmation
                    response = input(f"Do you want to remove all {len(test_files)} files from '{test_dir}'? (y/N): ")
                    if response.lower() != 'y':
                        print("Skipping this directory.")
                        continue
                except EOFError:
                    print("\nNon-interactive mode detected. Skipping confirmation.")

                for file_path in test_files:
                    if os.path.basename(file_path) in essential_files:
                        print(f"⏭️  Skipping essential file in directory: {file_path}")
                        continue
                    if move_to_backup(file_path, backup_folder):
                        removed_count += 1
    
    # Final count
    final_files = glob.glob("**/*.py", recursive=True)
    print(f"\n📊 Results:")
    print(f"  Initial files: {len(initial_files)}")
    print(f"  Final files: {len(final_files)}")
    print(f"  Files removed: {removed_count}")
    print(f"  Backup location: {backup_folder}")
    
    print(f"\n✅ Cleanup completed successfully!")
    
    # Show remaining important files
    important_files = [f for f in final_files if not f.startswith(backup_folder)]
    important_files.sort()
    
    print(f"\n📋 Remaining important Python files ({len(important_files)}):")
    for file in important_files[:20]:  # Show first 20
        print(f"  - {file}")
    
    if len(important_files) > 20:
        print(f"  ... and {len(important_files) - 20} more files")

if __name__ == "__main__":
    main()
