import py_compile
import os
import traceback

def check_syntax(file_path):
    print(f"Checking syntax of {file_path}...")
    try:
        py_compile.compile(file_path, doraise=True)
        print("File syntax is correct!")
        return True
    except py_compile.PyCompileError as e:
        print(f"Syntax error found:")
        print(e)
        return False
    except Exception as e:
        print(f"Other error: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    file_path = r"c:\Users\sarah\Desktop\Checker\fixed_pruefung_workflow_corrected.py"
    check_syntax(file_path)
