"""Simple test script to check the text analyzer functionality"""

from text_analyzer import analyze_text

def test_analyzer():
    with open("analyzer_test_results.txt", "w", encoding="utf-8") as log_file:
        # Test with a simple string
        test_text = "Dies ist ein Testtext. Er enthält mehrere Sätze und Wörter."
        
        log_file.write(f"Analyzing text: {test_text}\n")
        results = analyze_text(test_text)
        
        log_file.write("\nAnalysis Results:\n")
        for key, value in results.items():
            log_file.write(f"- {key}: {value}\n")
        
        # Now test with file content
        log_file.write("\n\nTesting with file content:\n")
        try:
            with open("test.txt", "r", encoding="utf-8") as f:
                file_text = f.read()
            
            log_file.write(f"Read {len(file_text)} characters from test.txt\n")
            file_results = analyze_text(file_text)
            
            log_file.write("\nFile Analysis Results:\n")
            for key, value in file_results.items():
                log_file.write(f"- {key}: {value}\n")
        
        except Exception as e:
            log_file.write(f"Error reading or analyzing file: {e}\n")

if __name__ == "__main__":
    test_analyzer()
    with open("analyzer_test_complete.txt", "w") as f:
        f.write("Test completed successfully")
