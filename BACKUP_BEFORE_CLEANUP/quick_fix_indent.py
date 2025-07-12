"""
This is a very simple script to fix the indentation issue at line 440.
It's designed to be robust against encoding issues by using a targeted approach.
"""

import re

# Input and output files
input_file = r'c:\Users\sarah\Desktop\Checker\fixed_pruefung_workflow_corrected.py'
output_file = r'c:\Users\sarah\Desktop\Checker\fixed_pruefung_workflow_fixed.py'

try:
    # Read the file in binary mode to handle any encoding
    with open(input_file, 'rb') as f:
        content = f.read()
        
    # Try to decode with utf-8, fallback to latin-1
    try:
        content_str = content.decode('utf-8')
    except UnicodeDecodeError:
        content_str = content.decode('latin-1', errors='replace')
    
    # Find the UI monitor section and fix the tooltip code
    pattern = r'print\("\[DEBUG\] UI monitor check completed"\)\s+(\s+)self\._text_b_tooltip = None'
    
    if re.search(pattern, content_str):
        # Found the pattern, replace it with the fixed code
        fixed_content = re.sub(
            pattern,
            'print("[DEBUG] UI monitor check completed")\n\n    def update_text_b_tooltip(self, *args):\n        if hasattr(self, \'_text_b_tooltip\') and self._text_b_tooltip:\n            self._text_b_tooltip = None',
            content_str
        )
        
        # Also fix the trace_add line
        fixed_content = re.sub(
            r'self\.text_b_path_var\.trace_add\(\'write\', update_text_b_tooltip\)',
            r'self.text_b_path_var.trace_add(\'write\', self.update_text_b_tooltip)',
            fixed_content
        )
        
        # And fix the function call
        fixed_content = re.sub(
            r'update_text_b_tooltip\(\)',
            r'self.update_text_b_tooltip()',
            fixed_content
        )
        
        # Write the fixed content to the output file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        
        print(f"Fixed indentation issue and wrote to {output_file}")
    else:
        print("Could not find the pattern to fix.")
except Exception as e:
    print(f"Error: {e}")
