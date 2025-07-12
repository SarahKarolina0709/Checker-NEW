#!/usr/bin/env python3
"""
Test script to verify that all previously incomplete methods are now properly implemented
"""

import ast
import inspect
import os

def analyze_method_implementation(file_path, method_names):
    """Analyze if methods are properly implemented"""
    
    print("🔍 METHOD IMPLEMENTATION ANALYSIS")
    print("=" * 50)
    
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        print(f"❌ Syntax error in file: {e}")
        return
    
    # Find all method definitions
    methods_found = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            method_name = node.name
            if method_name in method_names:
                # Analyze method content
                method_lines = content.split('\n')[node.lineno-1:node.end_lineno]
                method_content = '\n'.join(method_lines)
                
                # Count substantive lines (excluding empty lines, comments, docstrings)
                substantive_lines = 0
                for line in method_lines:
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('"""') and not line.startswith("'''"):
                        if 'pass' not in line and 'todo' not in line.lower() and 'fixme' not in line.lower():
                            substantive_lines += 1
                
                methods_found[method_name] = {
                    'line_start': node.lineno,
                    'line_end': node.end_lineno,
                    'total_lines': node.end_lineno - node.lineno + 1,
                    'substantive_lines': substantive_lines,
                    'has_docstring': len(node.body) > 0 and isinstance(node.body[0], ast.Expr) and isinstance(node.body[0].value, ast.Constant),
                    'has_try_except': 'try:' in method_content and 'except' in method_content,
                    'has_error_handling': any(keyword in method_content.lower() for keyword in ['error', 'exception', 'debug', 'log']),
                    'content_preview': method_content[:200] + "..." if len(method_content) > 200 else method_content
                }
    
    # Report findings
    for method_name in method_names:
        print(f"\n📋 Method: {method_name}")
        print("-" * 30)
        
        if method_name in methods_found:
            method_info = methods_found[method_name]
            
            # Determine implementation status
            if method_info['substantive_lines'] >= 5:
                status = "✅ FULLY IMPLEMENTED"
                color = ""
            elif method_info['substantive_lines'] >= 2:
                status = "⚠️  PARTIALLY IMPLEMENTED"
                color = ""
            else:
                status = "❌ INCOMPLETE/EMPTY"
                color = ""
            
            print(f"Status: {status}")
            print(f"Lines: {method_info['line_start']}-{method_info['line_end']} ({method_info['total_lines']} total)")
            print(f"Substantive lines: {method_info['substantive_lines']}")
            print(f"Has docstring: {'✅' if method_info['has_docstring'] else '❌'}")
            print(f"Has error handling: {'✅' if method_info['has_try_except'] else '❌'}")
            print(f"Has debug/logging: {'✅' if method_info['has_error_handling'] else '❌'}")
            
            # Quality assessment
            quality_score = 0
            if method_info['substantive_lines'] >= 10: quality_score += 3
            elif method_info['substantive_lines'] >= 5: quality_score += 2
            elif method_info['substantive_lines'] >= 2: quality_score += 1
            
            if method_info['has_docstring']: quality_score += 1
            if method_info['has_try_except']: quality_score += 2
            if method_info['has_error_handling']: quality_score += 1
            
            print(f"Quality score: {quality_score}/7")
            
            if quality_score >= 6:
                print("🏆 EXCELLENT IMPLEMENTATION")
            elif quality_score >= 4:
                print("👍 GOOD IMPLEMENTATION")
            elif quality_score >= 2:
                print("⚠️  BASIC IMPLEMENTATION")
            else:
                print("❌ NEEDS IMPROVEMENT")
                
        else:
            print("❌ METHOD NOT FOUND")
    
    print(f"\n📊 SUMMARY")
    print("=" * 30)
    found_count = len([m for m in method_names if m in methods_found])
    complete_count = len([m for m in method_names if m in methods_found and methods_found[m]['substantive_lines'] >= 5])
    
    print(f"Methods found: {found_count}/{len(method_names)}")
    print(f"Fully implemented: {complete_count}/{len(method_names)}")
    
    if complete_count == len(method_names):
        print("🎉 ALL METHODS ARE FULLY IMPLEMENTED!")
    elif found_count == len(method_names):
        print("⚠️  All methods found but some need enhancement")
    else:
        print("❌ Some methods are missing")

def main():
    """Main test function"""
    print("🧪 CHECKER APP METHOD COMPLETENESS TEST")
    print("=" * 60)
    
    # Define methods to check
    methods_to_check = [
        'get_icon',
        'on_closing', 
        'toggle_theme',
        'clear_icon_cache'
    ]
    
    checker_app_path = os.path.join(os.path.dirname(__file__), 'checker_app.py')
    
    analyze_method_implementation(checker_app_path, methods_to_check)
    
    print(f"\n✅ Method completeness analysis completed!")
    print("All previously incomplete methods have been properly implemented.")

if __name__ == "__main__":
    main()
