with open('c:\\Users\\sarah\\Desktop\\Checker\\fixed_pruefung_workflow_corrected.py', 'r', encoding='utf-8') as f:
    content = f.read()

try:
    compile(content, 'fixed_pruefung_workflow_corrected.py', 'exec')
    print("No syntax errors found!")
except SyntaxError as e:
    print(f"Syntax error on line {e.lineno}: {e}")
except Exception as e:
    print(f"Other error: {e}")
