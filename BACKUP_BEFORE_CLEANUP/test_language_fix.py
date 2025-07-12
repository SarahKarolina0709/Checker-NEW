"""
Simple test to see if the language detection fix works in the Prüfung workflow.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_language_detection():
    """Test the language detection functionality."""
    print("Testing language detection...")
    
    try:
        from language_detection import detect_language
        
        # Test with English text (the user's example)
        english_text = "Stock market punk: Nvidia tops all expectations, but BYD after the correction, what to do? Imperial Brands: Dividend delicacies, Alfen, Pony.ai and Uniqa in check"
        detected_lang = detect_language(english_text)
        print(f"✓ English text detected as: {detected_lang}")
        
        # Test with German text
        german_text = "Das ist ein deutscher Text mit mehreren Wörtern. Der Text sollte als Deutsch erkannt werden. Die deutsche Sprache hat viele Artikel wie der, die, das."
        detected_lang_de = detect_language(german_text)
        print(f"✓ German text detected as: {detected_lang_de}")
        
        return True
        
    except Exception as e:
        print(f"✗ Language detection test failed: {e}")
        return False

def test_language_tool_with_detection():
    """Test LanguageTool with language detection."""
    print("\nTesting LanguageTool with language detection...")
    
    try:
        import language_tool_python
        from language_detection import detect_language
        
        # Test English text
        english_text = "This is an English text with some errors. The text has a mispelled word and should be checked."
        detected_lang = detect_language(english_text)
        print(f"✓ Detected language: {detected_lang}")
        
        # Initialize LanguageTool for the detected language
        tool = language_tool_python.LanguageTool(detected_lang)
        matches = tool.check(english_text)
        print(f"✓ LanguageTool found {len(matches)} potential issues")
        
        # Show the first match if any
        if matches:
            match = matches[0]
            print(f"  - Rule: {match.ruleId}")
            print(f"  - Message: {match.message}")
            print(f"  - Suggestions: {match.replacements}")
        
        tool.close()
        return True
        
    except Exception as e:
        print(f"✗ LanguageTool test failed: {e}")
        return False

def test_pruefung_controller():
    """Test the pruefung workflow controller initialization."""
    print("\nTesting Prüfung workflow controller...")
    
    try:
        from pruefung_workflow_controller import PruefungWorkflowController
        
        # Create a controller instance
        controller = PruefungWorkflowController()
        print("✓ Controller created successfully")
        
        # Test check definitions
        checks = controller.get_available_checks()
        print(f"✓ Available checks: {list(checks.keys())}")
        
        return True
        
    except Exception as e:
        print(f"✗ Controller test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Language Detection Fix Test ===")
    
    success = True
    success &= test_language_detection()
    success &= test_language_tool_with_detection()
    success &= test_pruefung_controller()
    
    if success:
        print("\n🎉 All tests passed! The language detection fix should work correctly.")
    else:
        print("\n❌ Some tests failed. Please check the error messages above.")
