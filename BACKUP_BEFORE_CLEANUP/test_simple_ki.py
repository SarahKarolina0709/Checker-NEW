#!/usr/bin/env python3
"""
Test mit einfachem Text um das Ollama-Problem zu isolieren.
"""

import sys
import os

# Add the current directory to the path so we can import ki_module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ki_module import ki_qualitaetspruefung

def test_simple_ki():
    """Test the KI function with a very simple text."""
    print("Testing KI with simple text...")
    
    # Very simple test text
    simple_text = "Hello world. Hallo Welt."
    
    print(f"Input text: {simple_text}")
    print("Calling ki_qualitaetspruefung...")
    
    try:
        result = ki_qualitaetspruefung(simple_text)
        print(f"SUCCESS: {result}")
        return True
            
    except Exception as e:
        print(f"FAILED: {type(e).__name__}: {str(e)}")
        return False

if __name__ == "__main__":
    test_simple_ki()
