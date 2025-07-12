import language_tool_python
import os

def create_test_file():
    print("Creating test file...")
    # This text contains two obvious, repeating errors.
    base_text = "This is a test sentence with some errrors and misteaks. "
    # Repeat the text to create a long single line of text.
    long_text = base_text * 100
    file_path = os.path.abspath("long_line_test.txt")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(long_text)
    print(f"Test file 'long_line_test.txt' created. Length: {len(long_text)} chars.")
    return long_text, file_path

def run_languagetool_test(text):
    print("\nInitializing LanguageTool for 'en-US'...")
    tool = None
    try:
        # Set a remote server URL if you have one, otherwise it runs locally.
        tool = language_tool_python.LanguageTool('en-US')
        print("LanguageTool initialized.")
    except Exception as e:
        print(f"Failed to initialize LanguageTool: {e}")
        print("Please ensure Java is installed and accessible.")
        return

    print("\nRunning check on the long text...")
    matches = tool.check(text)
    print(f"\nCheck complete. Found {len(matches)} potential issues.")

    if matches:
        print("\n--- First 10 Matches ---")
        for i, m in enumerate(matches[:10]):
            # Manually calculate line and column from offset, robust for single-line text
            line_number = text.count('\n', 0, m.offset) + 1
            last_newline = text.rfind('\n', 0, m.offset) # Will be -1 for the first line
            column_number = m.offset - last_newline

            print(f"\nMatch {i+1}:")
            print(f"  Message: {m.message}")
            print(f"  File Position: Line {line_number}, Col {column_number} (Offset: {m.offset})")
            print(f"  Context: '...{m.context}...', Error Length: {m.errorLength}")
            print(f"  Replacements: {m.replacements}")
            print(f"  Rule ID: {m.ruleId}")

    # Close the tool to free up resources
    if tool:
        tool.close()
        print("\nLanguageTool closed.")


if __name__ == "__main__":
    long_text, file_path = create_test_file()
    run_languagetool_test(long_text)
