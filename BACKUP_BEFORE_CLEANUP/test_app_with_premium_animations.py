#!/usr/bin/env python3
"""
Script to test the improved animations in the main checker app.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from checker_app import CheckerApp
    print("🚀 Starting Checker App with improved premium animations...")
    print("✨ Look for:")
    print("   - Smooth workflow card entrance animations")
    print("   - Elegant hover effects with scale and glow")
    print("   - Premium button animations")
    print("   - Refined click effects")
    
    app = CheckerApp()
    app.run()
    
except Exception as e:
    print(f"❌ Error starting app: {e}")
    import traceback
    traceback.print_exc()
