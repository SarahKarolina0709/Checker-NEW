"""
Simple Python script to find and analyze duplicate Python files
"""
import os
import hashlib
import json
from pathlib import Path
from collections import defaultdict

def get_file_hash(filepath):
    """Calculate SHA-256 hash of file content."""
    hasher = hashlib.sha256()
    try:
        with open(filepath, 'rb') as f:
            hasher.update(f.read())
        return hasher.hexdigest()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None

def find_duplicate_python_files():
    """Find all duplicate Python files in current directory."""
    current_dir = Path(".")
    py_files = list(current_dir.rglob("*.py"))
    
    print(f"Found {len(py_files)} Python files")
    
    # Group files by content hash
    hash_groups = defaultdict(list)
    file_info = {}
    
    for py_file in py_files:
        if py_file.is_file():
            file_hash = get_file_hash(py_file)
            if file_hash:
                hash_groups[file_hash].append(py_file)
                file_info[str(py_file)] = {
                    'size': py_file.stat().st_size,
                    'hash': file_hash
                }
    
    # Find duplicates
    duplicates = {}
    for file_hash, files in hash_groups.items():
        if len(files) > 1:
            duplicates[file_hash] = [str(f) for f in files]
    
    # Analyze similar named files
    similar_names = defaultdict(list)
    for py_file in py_files:
        base_name = py_file.stem.lower()
        # Remove common suffixes
        for suffix in ['_backup', '_old', '_copy', '_v2', '_final', '_test', '_demo', '_broken', '_minimal', '_simplified']:
            base_name = base_name.replace(suffix, '')
        similar_names[base_name].append(str(py_file))
    
    potential_duplicates = {name: files for name, files in similar_names.items() if len(files) > 1}
    
    # Generate report
    report = {
        'total_files': len(py_files),
        'duplicate_groups': len(duplicates),
        'exact_duplicates': duplicates,
        'potential_duplicates': potential_duplicates,
        'all_files': file_info
    }
    
    return report

if __name__ == "__main__":
    print("🔍 Analyzing Python files for duplicates...")
    print("=" * 50)
    
    report = find_duplicate_python_files()
    
    # Save report
    with open('duplicate_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"📊 Analysis Results:")
    print(f"  Total Python files: {report['total_files']}")
    print(f"  Exact duplicate groups: {report['duplicate_groups']}")
    print(f"  Potential duplicate groups: {len(report['potential_duplicates'])}")
    
    print(f"\n🔄 Exact Duplicates (identical content):")
    for i, (hash_val, files) in enumerate(report['exact_duplicates'].items(), 1):
        print(f"  Group {i} ({hash_val[:8]}...):")
        for file in files:
            print(f"    - {file}")
    
    print(f"\n⚠️  Potential Duplicates (similar names):")
    for base_name, files in report['potential_duplicates'].items():
        if len(files) > 1:
            print(f"  {base_name}:")
            for file in files:
                print(f"    - {file}")
    
    print(f"\n📄 Report saved to: duplicate_report.json")
