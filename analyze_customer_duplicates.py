#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 CUSTOMER CODE DUPLICATE ANALYSIS
====================================

Analysiert Duplikate zwischen verschiedenen Customer-Management-Implementierungen.
"""

import os
import re
from pathlib import Path

def analyze_customer_functions(file_path):
    """Analysiere Customer-Funktionen in einer Datei"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Finde alle Customer-related Funktionen
        functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):', content)
        customer_functions = [f for f in functions if 'customer' in f.lower() or 'kunde' in f.lower()]
        
        # Finde alle Klassen
        classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', content)
        customer_classes = [c for c in classes if 'customer' in c.lower() or 'kunde' in c.lower()]
        
        # Analysiere Code-Größe
        lines = content.split('\n')
        non_empty_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
        
        return {
            'file': file_path,
            'total_lines': len(lines),
            'code_lines': len(non_empty_lines),
            'all_functions': functions,
            'customer_functions': customer_functions,
            'customer_classes': customer_classes,
            'has_add_customer': any('add' in f.lower() and 'customer' in f.lower() for f in functions),
            'has_customer_exists': any('exist' in f.lower() and 'customer' in f.lower() for f in functions),
            'has_customer_manager': 'customer_manager' in content.lower() or 'CustomerManager' in content
        }
        
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e)
        }

def find_duplicate_patterns():
    """Finde duplicate Patterns zwischen Customer-Implementierungen"""
    
    customer_files = [
        'welcome_screen.py',
        'welcome_screen_customer.py', 
        'customer_manager.py',
        'sections/customer_section.py',
        'src/managers/kunden_manager.py'
    ]
    
    print("🔍 CUSTOMER CODE DUPLICATE ANALYSIS")
    print("=" * 60)
    
    analyses = []
    
    for file_path in customer_files:
        if os.path.exists(file_path):
            analysis = analyze_customer_functions(file_path)
            analyses.append(analysis)
            
            print(f"\n📁 {file_path}")
            print("-" * 40)
            
            if 'error' in analysis:
                print(f"❌ Error: {analysis['error']}")
                continue
                
            print(f"Lines: {analysis['total_lines']} total, {analysis['code_lines']} code")
            print(f"Classes: {analysis['customer_classes']}")
            print(f"Customer Functions: {analysis['customer_functions']}")
            print(f"Has add_customer: {'✅' if analysis['has_add_customer'] else '❌'}")
            print(f"Has customer_exists: {'✅' if analysis['has_customer_exists'] else '❌'}")
            print(f"Uses CustomerManager: {'✅' if analysis['has_customer_manager'] else '❌'}")
        else:
            print(f"\n📁 {file_path}")
            print("❌ File not found")
    
    # Analysiere Duplikate
    print(f"\n🚨 DUPLICATE ANALYSIS")
    print("=" * 60)
    
    # Finde gemeinsame Funktionsnamen
    all_customer_functions = []
    for analysis in analyses:
        if 'customer_functions' in analysis:
            all_customer_functions.extend(analysis['customer_functions'])
    
    from collections import Counter
    function_counts = Counter(all_customer_functions)
    duplicates = {func: count for func, count in function_counts.items() if count > 1}
    
    if duplicates:
        print("🔍 Duplicate Functions found:")
        for func, count in duplicates.items():
            print(f"   • {func}: {count} implementations")
            
            # Zeige in welchen Dateien
            for analysis in analyses:
                if 'customer_functions' in analysis and func in analysis['customer_functions']:
                    print(f"     → {os.path.basename(analysis['file'])}")
    else:
        print("✅ No duplicate function names found")
    
    # Analysiere Implementierungs-Pattern
    print(f"\n📊 IMPLEMENTATION PATTERNS")
    print("-" * 40)
    
    add_customer_files = [a['file'] for a in analyses if a.get('has_add_customer')]
    exists_check_files = [a['file'] for a in analyses if a.get('has_customer_exists')]
    manager_usage_files = [a['file'] for a in analyses if a.get('has_customer_manager')]
    
    print(f"Files with add_customer logic: {len(add_customer_files)}")
    for f in add_customer_files:
        print(f"   • {os.path.basename(f)}")
    
    print(f"\nFiles with customer_exists logic: {len(exists_check_files)}")
    for f in exists_check_files:
        print(f"   • {os.path.basename(f)}")
    
    print(f"\nFiles using CustomerManager: {len(manager_usage_files)}")
    for f in manager_usage_files:
        print(f"   • {os.path.basename(f)}")
    
    # Empfehlungen
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 60)
    
    if len(add_customer_files) > 1:
        print("🚨 MULTIPLE ADD_CUSTOMER IMPLEMENTATIONS FOUND!")
        print("   → Consolidate to single implementation in CustomerManager")
        print("   → Use CustomerManager from all UI modules")
    
    if len(exists_check_files) > 1:
        print("🚨 MULTIPLE CUSTOMER_EXISTS IMPLEMENTATIONS FOUND!")
        print("   → Consolidate to single implementation in CustomerManager")
    
    if duplicates:
        print("🚨 DUPLICATE FUNCTIONS DETECTED!")
        print("   → Review and merge similar implementations")
        print("   → Extract common logic to CustomerManager")
    
    if len(manager_usage_files) < len([a for a in analyses if 'customer_functions' in a and a['customer_functions']]):
        print("⚠️  NOT ALL MODULES USE CUSTOMERMANAGER!")
        print("   → Migrate remaining modules to use CustomerManager")
        print("   → Remove redundant customer logic from UI modules")

if __name__ == "__main__":
    find_duplicate_patterns()
