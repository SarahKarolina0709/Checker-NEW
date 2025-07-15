#!/usr/bin/env python3
"""
Script to identify and safely remove duplicate Python files.
This script will analyze file content, not just names, to find true duplicates.
"""

import os
import hashlib
import shutil
import json
from pathlib import Path
from collections import defaultdict
import argparse
from typing import Dict, List, Set, Tuple

class DuplicateFileFinder:
    def __init__(self, directory: str):
        self.directory = Path(directory)
        self.file_hashes: Dict[str, List[Path]] = defaultdict(list)
        self.file_sizes: Dict[int, List[Path]] = defaultdict(list)
        
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file content."""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except (IOError, OSError) as e:
            print(f"Error reading {file_path}: {e}")
            return ""
    
    def scan_python_files(self) -> None:
        """Scan all Python files and group by hash and size."""
        print(f"Scanning Python files in {self.directory}...")
        
        python_files = list(self.directory.rglob("*.py"))
        print(f"Found {len(python_files)} Python files")
        
        for file_path in python_files:
            if file_path.is_file():
                try:
                    file_size = file_path.stat().st_size
                    self.file_sizes[file_size].append(file_path)
                    
                    file_hash = self.calculate_file_hash(file_path)
                    if file_hash:
                        self.file_hashes[file_hash].append(file_path)
                        
                except (OSError, IOError) as e:
                    print(f"Error processing {file_path}: {e}")
    
    def find_duplicates_by_content(self) -> Dict[str, List[Path]]:
        """Find files with identical content (same hash)."""
        duplicates = {}
        for file_hash, file_paths in self.file_hashes.items():
            if len(file_paths) > 1:
                duplicates[file_hash] = file_paths
        return duplicates
    
    def find_duplicates_by_size_and_name(self) -> List[Tuple[str, List[Path]]]:
        """Find potential duplicates by size and similar names."""
        potential_duplicates = []
        
        for size, file_paths in self.file_sizes.items():
            if len(file_paths) > 1:
                # Group by similar names
                name_groups = defaultdict(list)
                for path in file_paths:
                    base_name = path.stem.lower()
                    # Remove common suffixes
                    for suffix in ['_backup', '_old', '_copy', '_v2', '_final', '_test', '_demo']:
                        base_name = base_name.replace(suffix, '')
                    name_groups[base_name].append(path)
                
                for base_name, paths in name_groups.items():
                    if len(paths) > 1:
                        potential_duplicates.append((base_name, paths))
        
        return potential_duplicates
    
    def analyze_duplicates(self) -> Dict:
        """Analyze and categorize all duplicates."""
        content_duplicates = self.find_duplicates_by_content()
        name_size_duplicates = self.find_duplicates_by_size_and_name()
        
        analysis = {
            'content_duplicates': {},
            'potential_duplicates': [],
            'statistics': {
                'total_python_files': len(list(self.directory.rglob("*.py"))),
                'content_duplicate_groups': len(content_duplicates),
                'potential_duplicate_groups': len(name_size_duplicates)
            }
        }
        
        # Convert Path objects to strings for JSON serialization
        for file_hash, paths in content_duplicates.items():
            analysis['content_duplicates'][file_hash] = [str(p) for p in paths]
        
        for base_name, paths in name_size_duplicates:
            analysis['potential_duplicates'].append({
                'base_name': base_name,
                'files': [str(p) for p in paths]
            })
        
        return analysis

class SafeRemover:
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.backup_dir = Path("duplicate_backups")
        
    def create_backup_dir(self):
        """Create backup directory if it doesn't exist."""
        if not self.dry_run:
            self.backup_dir.mkdir(exist_ok=True)
    
    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before deletion."""
        if self.dry_run:
            return file_path
            
        backup_path = self.backup_dir / file_path.name
        counter = 1
        while backup_path.exists():
            name_parts = file_path.stem, counter, file_path.suffix
            backup_path = self.backup_dir / f"{name_parts[0]}_{name_parts[1]}{name_parts[2]}"
            counter += 1
            
        shutil.copy2(file_path, backup_path)
        return backup_path
    
    def remove_duplicates(self, duplicates: Dict[str, List[str]], strategy: str = "keep_main") -> List[str]:
        """Remove duplicate files based on strategy."""
        removed_files = []
        
        for file_hash, file_paths in duplicates.items():
            paths = [Path(p) for p in file_paths]
            
            if strategy == "keep_main":
                # Keep the file in the main directory or with the simplest name
                to_keep = self._choose_file_to_keep(paths)
                to_remove = [p for p in paths if p != to_keep]
            elif strategy == "keep_first":
                # Keep the first file alphabetically
                paths.sort()
                to_keep = paths[0]
                to_remove = paths[1:]
            else:
                continue
            
            print(f"\nDuplicate group (hash: {file_hash[:8]}...):")
            print(f"  Keeping: {to_keep}")
            
            for file_path in to_remove:
                if self.dry_run:
                    print(f"  [DRY RUN] Would remove: {file_path}")
                else:
                    try:
                        backup_path = self.backup_file(file_path)
                        file_path.unlink()
                        print(f"  Removed: {file_path} (backed up to {backup_path})")
                        removed_files.append(str(file_path))
                    except Exception as e:
                        print(f"  Error removing {file_path}: {e}")
        
        return removed_files
    
    def _choose_file_to_keep(self, paths: List[Path]) -> Path:
        """Choose which file to keep based on priority rules."""
        # Priority: main checker_app.py > files without suffixes > shortest path
        
        # 1. Keep main checker_app.py if present
        for path in paths:
            if path.name == "checker_app.py" and "backup" not in str(path).lower():
                return path
        
        # 2. Keep files without common duplicate suffixes
        clean_files = []
        for path in paths:
            name_lower = path.stem.lower()
            if not any(suffix in name_lower for suffix in 
                      ['backup', 'copy', 'old', 'temp', 'test', 'demo', '_v2', '_2']):
                clean_files.append(path)
        
        if clean_files:
            # Return the one with shortest path or simplest name
            return min(clean_files, key=lambda p: (len(str(p)), len(p.stem)))
        
        # 3. Fallback: return shortest path
        return min(paths, key=lambda p: len(str(p)))

def main():
    parser = argparse.ArgumentParser(description="Find and remove duplicate Python files")
    parser.add_argument("--directory", "-d", default=".", help="Directory to scan")
    parser.add_argument("--dry-run", action="store_true", default=True, 
                       help="Only show what would be deleted (default)")
    parser.add_argument("--execute", action="store_true", 
                       help="Actually delete files (creates backups)")
    parser.add_argument("--strategy", choices=["keep_main", "keep_first"], 
                       default="keep_main", help="Strategy for choosing which file to keep")
    parser.add_argument("--report-only", action="store_true", 
                       help="Only generate analysis report")
    
    args = parser.parse_args()
    
    # Set execution mode
    dry_run = not args.execute
    
    print("🔍 Duplicate Python File Finder & Remover")
    print("=" * 50)
    print(f"Directory: {os.path.abspath(args.directory)}")
    print(f"Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"Strategy: {args.strategy}")
    print()
    
    # Initialize finder
    finder = DuplicateFileFinder(args.directory)
    finder.scan_python_files()
    
    # Analyze duplicates
    analysis = finder.analyze_duplicates()
    
    # Save analysis report
    report_file = "duplicate_analysis_report.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Analysis Report:")
    print(f"  Total Python files: {analysis['statistics']['total_python_files']}")
    print(f"  Content duplicate groups: {analysis['statistics']['content_duplicate_groups']}")
    print(f"  Potential duplicate groups: {analysis['statistics']['potential_duplicate_groups']}")
    print(f"  Report saved to: {report_file}")
    
    if args.report_only:
        print("\n📋 Content Duplicates (identical files):")
        for file_hash, files in analysis['content_duplicates'].items():
            print(f"  Group {file_hash[:8]}...:")
            for file in files:
                print(f"    - {file}")
        
        print("\n⚠️  Potential Duplicates (similar names/sizes):")
        for group in analysis['potential_duplicates']:
            print(f"  {group['base_name']}:")
            for file in group['files']:
                print(f"    - {file}")
        return
    
    # Remove duplicates if any found
    if analysis['content_duplicates']:
        print(f"\n🗑️  Removing duplicates...")
        
        remover = SafeRemover(dry_run=dry_run)
        remover.create_backup_dir()
        
        removed_files = remover.remove_duplicates(
            analysis['content_duplicates'], 
            args.strategy
        )
        
        if removed_files:
            print(f"\n✅ Successfully removed {len(removed_files)} duplicate files")
            if not dry_run:
                print(f"💾 Backups saved to: {remover.backup_dir}")
        else:
            print("\n✅ No files were removed")
    else:
        print("\n✅ No content duplicates found!")
    
    # Show potential duplicates for manual review
    if analysis['potential_duplicates']:
        print(f"\n⚠️  Found {len(analysis['potential_duplicates'])} groups of potential duplicates")
        print("These require manual review:")
        for group in analysis['potential_duplicates']:
            print(f"  {group['base_name']}:")
            for file in group['files']:
                print(f"    - {file}")

if __name__ == "__main__":
    main()
