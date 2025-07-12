"""
Script to update button heights and styling in fixed_pruefung_workflow_corrected.py
"""

def update_file():
    # Read the entire file
    with open('fixed_pruefung_workflow_corrected.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace height=70 with height=80 for bottom bar identification
    content = content.replace('("height") == 70:', '("height") == 80:')
    
    # Write back to the file
    with open('fixed_pruefung_workflow_corrected.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("Height updated successfully")

if __name__ == "__main__":
    update_file()
