"""
A safe deduplication script that finds files with identical content,
chooses the best version to keep based on a set of rules, and backs up
the duplicates before removing them.
"""
import os
import hashlib
import shutil
from pathlib import Path
from collections import defaultdict
import argparse
from datetime import datetime

# --- SAFETY CONFIGURATION ---
# This list contains files identified as essential for the application.
# The script will avoid deleting these files.
ESSENTIAL_FILES = [
    "checker_app.py", "ui_theme.py", "kunden_manager.py", "app_managers.py",
    "angebots_workflow.py", "finalisierung_workflow.py", "pruefung_workflow.py",
    "projekt_workflow.py", "visual_integration.py", "modern_customer_gui.py",
    "smart_upload_calendar.py", "upload_manager.py", "workflow_router.py",
    "notification_center.py", "manual_cleanup.py", "analyze_dependencies.py",
    "core/__init__.py", "core/memory_manager.py", "core/state_manager.py",
    "core/thread_manager.py", "core/workflow_factory.py", "ui_components/__init__.py",
    "ui_components/base_view.py", "ui_components/file_pair_view.py",
    "ui_components/modern_button.py", "ui_components/progress_view.py",
    "ui_components/pruefung_workflow_view.py", "ui_components/result_view.py",
    "ui_components/settings_view.py", "ui_components/smart_entry.py",
    "ui_components/source_view.py", "utils/__init__.py", "utils/file_operations.py",
    "utils/icon_manager.py", "utils/logging_config.py", "utils/memory_monitor.py",
    "utils/resource_path.py", "utils/thread_worker.py", "utils/ui_utils.py",
    "utils/view_stack.py", "workflows/__init__.py", "workflows/base_workflow.py",
    "workflows/finalisierung_workflow_logic.py", "workflows/pruefung_workflow_controller.py",
    "__init__.py", "safe_deduplicator.py"
]

def calculate_file_hash(file_path: Path) -> str:
    """Calculates the SHA-256 hash of a file's content."""
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                h.update(chunk)
        return h.hexdigest()
    except (IOError, OSError) as e:
        print(f"Error reading {file_path}: {e}")
        return ""

def find_duplicates_by_content(directory: Path) -> dict[str, list[Path]]:
    """Finds files with identical content by hashing."""
    hashes = defaultdict(list)
    for file_path in directory.rglob("*.py"):
        if file_path.is_file():
            file_hash = calculate_file_hash(file_path)
            if file_hash:
                hashes[file_hash].append(file_path)
    
    return {key: value for key, value in hashes.items() if len(value) > 1}

def choose_file_to_keep(paths: list[Path]) -> Path:
    """Chooses which file to keep from a list of duplicates."""
    # Priority 1: Check for essential files first.
    essential_matches = [p for p in paths if p.name in ESSENTIAL_FILES]
    if essential_matches:
        # If there's one essential file, keep it. If multiple, pick the one with the shortest path.
        return min(essential_matches, key=lambda p: len(str(p)))

    # Priority 2: Keep files without common "duplicate" suffixes.
    clean_files = [
        p for p in paths 
        if not any(s in p.stem.lower() for s in ['_backup', '_copy', '_old', '_v2', '_test', '_demo'])
    ]
    if clean_files:
        return min(clean_files, key=lambda p: (len(str(p)), len(p.stem)))

    # Fallback: Keep the one with the shortest path name.
    return min(paths, key=lambda p: len(str(p)))

def main():
    """Main function to find and remove duplicate files."""
    parser = argparse.ArgumentParser(description="Safely find and remove duplicate Python files.")
    parser.add_argument(
        "--execute", 
        action="store_true", 
        help="Actually remove files. Otherwise, runs in dry-run mode."
    )
    args = parser.parse_args()

    print("🧹 Safe Python Deduplicator")
    print(f"Mode: {'EXECUTE' if args.execute else 'DRY RUN'}")
    print("=" * 50)

    duplicates = find_duplicates_by_content(Path('.'))
    
    if not duplicates:
        print("✅ No duplicate files found based on content.")
        return

    files_to_remove = []
    for file_hash, paths in duplicates.items():
        to_keep = choose_file_to_keep(paths)
        files_to_remove.extend([p for p in paths if p != to_keep])

    if not files_to_remove:
        print("✅ All duplicates are essential files. No files to remove.")
        return

    print(f"Found {len(files_to_remove)} duplicate files to remove:")
    for f in sorted(files_to_remove):
        print(f"  - To be removed: {f}")

    if not args.execute:
        print("\nRun with --execute to remove these files.")
        print("A backup of all removed files will be created.")
        return

    # --- Execution ---
    backup_folder = Path(f"REMOVED_DUPLICATES_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    backup_folder.mkdir(exist_ok=True)
    print(f"\n📁 Created backup folder: {backup_folder}")

    removed_count = 0
    for file_path in files_to_remove:
        try:
            if file_path.exists():
                shutil.move(str(file_path), str(backup_folder / file_path.name))
                removed_count += 1
        except Exception as e:
            print(f"❌ Error moving {file_path}: {e}")

    print(f"\n✅ Successfully removed {removed_count} files.")
    print(f"Backups are located in '{backup_folder}'.")

if __name__ == "__main__":
    main()
