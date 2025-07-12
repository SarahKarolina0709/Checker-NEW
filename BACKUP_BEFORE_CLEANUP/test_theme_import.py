#!/usr/bin/env python3
"""
Test theme import to verify PAD_XS is available
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("Testing theme import...")

try:
    from theme import Theme
    print("✅ Theme imported successfully")
    
    # Test all padding attributes
    print(f"PAD_XL = {Theme.PAD_XL}")
    print(f"PAD_L = {Theme.PAD_L}")
    print(f"PAD_M = {Theme.PAD_M}")
    print(f"PAD_S = {Theme.PAD_S}")
    print(f"PAD_XS = {Theme.PAD_XS}")
    
    print("✅ All padding attributes are available!")
    
except AttributeError as e:
    print(f"❌ AttributeError: {e}")
except ImportError as e:
    print(f"❌ ImportError: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
