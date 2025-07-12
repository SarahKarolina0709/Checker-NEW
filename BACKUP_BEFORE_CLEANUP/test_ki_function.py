#!/usr/bin/env python3
"""
Test the KI module functions directly to see where the issue is.
"""

import sys
import os

# Add the current directory to the path so we can import ki_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ki_module import ki_qualitaetspruefung

def test_ki_function():
    """Test the ki_qualitaetspruefung function directly."""
    print("Testing ki_qualitaetspruefung function...")
    
    # Simple test text
    test_text = "This is a simple test translation. Dies ist eine einfache Testübersetzung."
    
    print(f"Input text: {test_text}")
    print("Calling ki_qualitaetspruefung...")
    
    try:
        result = ki_qualitaetspruefung(test_text)
        print(f"Result: {result}")
        
        if "Allgemeiner Fehler" in result or "timed out" in result:
            print("❌ KI function failed with timeout/error")
            return False
        else:
            print("✅ KI function worked successfully!")
            return True
            
    except Exception as e:
        print(f"❌ Exception in KI function: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ki_function()
    sys.exit(0 if success else 1)
