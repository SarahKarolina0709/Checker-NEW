"""
Script to ensure the bottom bar stays on top of other UI elements
"""

def ensure_buttons_visible():
    with open('fixed_pruefung_workflow_corrected.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        
        # Add additional lift() calls after each update_idletasks() for bottom_bar
        if 'bottom_bar.update_idletasks()' in line:
            next_line = lines[lines.index(line) + 1] if lines.index(line) + 1 < len(lines) else ""
            if 'bottom_bar.lift()' not in next_line:
                modified_lines.append('                bottom_bar.lift()  # Ensure bottom bar stays on top\n')
                
        # Add additional lift() calls for buttons
        if 'self.start_button.pack(side="right"' in line:
            modified_lines.append('                self.start_button.lift()  # Ensure button stays on top\n')
            
        if 'self.export_button.pack(side="right"' in line:
            modified_lines.append('                self.export_button.lift()  # Ensure button stays on top\n')
    
    with open('fixed_pruefung_workflow_corrected.py', 'w', encoding='utf-8') as f:
        f.writelines(modified_lines)
    
    print("Button visibility enhancements added")

if __name__ == "__main__":
    ensure_buttons_visible()
