# PowerShell Cleanup Script for Checker Project
# This script will archive documentation and delete obsolete files.

# --- ARCHIVE ---
# Create archive directory if it doesn't exist
$archiveDir = ".\archive"
if (-not (Test-Path $archiveDir)) {
    New-Item -ItemType Directory -Path $archiveDir
    Write-Host "Created archive directory."
}

# Move all markdown files to the archive
Get-ChildItem -Path . -Filter *.md | ForEach-Object {
    Move-Item -Path $_.FullName -Destination $archiveDir
    Write-Host "Archived $($_.Name)"
}

# --- DELETE ---
# List of specific files and patterns to delete
$filesToDelete = @(
    # Backups
    "checker_app_BACKUP_20250713_023925.py",
    "checker_app_broken_backup.py",
    "ctk_patch.py.old",
    "upload_section_backup.py",
    "ultra_modern_welcome_screen_simplified.py.backup",

    # Old/Test Scripts
    "accessibility_extensions.py",
    "advanced_accessibility.py",
    "advanced_gui_optimizer.py",
    "advanced_performance_monitor.py",
    "advanced_search_system.py",
    "advanced_visual_effects.py",
    "analyze_dependencies.py",
    "analyze_duplicates.py",
    "analyze_duplicate_files.py",
    "animation_engine.py",
    "base_ui_components.py",
    "basispfad_konfigurator.py",
    "calendar_cleanup_summary.py",
    "calendar_demo.py",
    "calendar_extensions.py",
    "calendar_fix_analysis.py",
    "check_pdf2image.py",
    "check_tkinterdnd.py",
    "cleanup_customer_files.py",
    "cleanup_script.py",
    "cleanup_script_automated.py",
    "create_demo_customers.py",
    "create_file_icon.py",
    "create_fixed_template.py",
    "create_simple_icon.py",
    "create_upload_icon.py",
    "column_resize_summary.py",
    "cleanup_duplicates.bat",
    "cleanup_duplicates.ps1",

    # Logs and Reports
    "analyzer_test_complete.txt",
    "analyzer_test_results.txt",
    "angebots_display_test.txt",
    "angebots_test.txt",
    "coverage.xml",
    ".coverage"
)

# Delete specific files
foreach ($file in $filesToDelete) {
    if (Test-Path $file) {
        Remove-Item -Path $file -Force
        Write-Host "Deleted $file"
    }
}

# Delete files by pattern
Get-ChildItem -Path . -Filter "final_*.py" | Remove-Item -Force -Verbose
Get-ChildItem -Path . -Filter "test_*.py" | Remove-Item -Force -Verbose
Get-ChildItem -Path . -Filter "debug_*.py" | Remove-Item -Force -Verbose
Get-ChildItem -Path . -Filter "demo_*.py" | Remove-Item -Force -Verbose
Get-ChildItem -Path . -Filter "*.log" | Remove-Item -Force -Verbose
Get-ChildItem -Path . -Filter "pylint_results*.txt" | Remove-Item -Force -Verbose

# Delete directories
$dirsToDelete = @(
    "__pycache__",
    "htmlcov"
)
foreach ($dir in $dirsToDelete) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force -Path $dir
        Write-Host "Deleted directory $dir"
    }
}

Write-Host "Project cleanup complete."
