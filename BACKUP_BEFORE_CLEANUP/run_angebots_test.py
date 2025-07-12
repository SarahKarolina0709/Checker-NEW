"""Simple wrapper to run the verify_angebots_display.py script with error handling"""

import os
import traceback

try:
    # Print current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Print if the script exists
    script_path = "c:\\Users\\sarah\\Desktop\\Checker\\verify_angebots_display.py"
    print(f"Script exists: {os.path.exists(script_path)}")
    
    # Import and run the test function
    from verify_angebots_display import test_angebots_display
    
    print("Successfully imported test_angebots_display")
    test_angebots_display()
    
    # Check if the result file was created
    result_path = "angebots_display_test.txt"
    print(f"Result file exists: {os.path.exists(result_path)}")
    
    if os.path.exists(result_path):
        print(f"Result file size: {os.path.getsize(result_path)} bytes")
        
        # Read and print the first few lines
        with open(result_path, "r", encoding="utf-8") as f:
            print("\nFirst 5 lines of result file:")
            for i, line in enumerate(f):
                if i < 5:
                    print(line.strip())
                else:
                    break

except Exception as e:
    print(f"Error: {e}")
    traceback.print_exc()

print("Script execution completed.")
