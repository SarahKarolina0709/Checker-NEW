"""
TkinterDnD Installation and Configuration Check

This script checks if tkinterdnd2 is properly installed and provides
instructions for fixing drag & drop support in the Checker app.
"""

import sys
import subprocess
import importlib.util

def check_tkinterdnd2():
    """Check if tkinterdnd2 is properly installed."""
    print("=" * 60)
    print("TKINTERDND2 INSTALLATION CHECK")
    print("=" * 60)
    
    # Check if tkinterdnd2 can be imported
    try:
        import tkinterdnd2
        from tkinterdnd2 import TkinterDnD
        print("✓ tkinterdnd2 is installed and can be imported")
        
        # Check version if available
        if hasattr(tkinterdnd2, '__version__'):
            print(f"✓ Version: {tkinterdnd2.__version__}")
        
        # Test basic TkinterDnD functionality
        try:
            # This should not raise an error if properly configured
            test_root = TkinterDnD.Tk()
            test_root.withdraw()  # Hide the test window
            test_root.destroy()
            print("✓ TkinterDnD.Tk() can be created successfully")
            return True
            
        except Exception as e:
            print(f"✗ Error creating TkinterDnD.Tk(): {e}")
            return False
            
    except ImportError as e:
        print(f"✗ tkinterdnd2 is not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error with tkinterdnd2: {e}")
        return False

def provide_installation_instructions():
    """Provide installation instructions for tkinterdnd2."""
    print("\n" + "=" * 60)
    print("INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Install tkinterdnd2 using pip:")
    print("   pip install tkinterdnd2")
    
    print("\n2. If you're using conda:")
    print("   conda install -c conda-forge tkinterdnd2")
    
    print("\n3. If you're using a virtual environment, activate it first:")
    print("   # Windows")
    print("   .\\venv\\Scripts\\activate")
    print("   pip install tkinterdnd2")
    
    print("\n4. For development/testing:")
    print("   pip install tkinterdnd2[dev]")
    
    print("\n5. Verify installation:")
    print("   python -c \"import tkinterdnd2; print('tkinterdnd2 installed successfully')\"")

def check_current_environment():
    """Check current Python environment details."""
    print("\n" + "=" * 60)
    print("CURRENT ENVIRONMENT")
    print("=" * 60)
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("⚠ Running in system Python (consider using virtual environment)")
    
    # Check pip version
    try:
        import pip
        print(f"pip version: {pip.__version__}")
    except ImportError:
        print("⚠ pip not available")

def install_tkinterdnd2():
    """Attempt to install tkinterdnd2 automatically."""
    print("\n" + "=" * 60)
    print("AUTOMATIC INSTALLATION")
    print("=" * 60)
    
    try:
        print("Attempting to install tkinterdnd2...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "tkinterdnd2"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✓ tkinterdnd2 installed successfully!")
            print("\nInstallation output:")
            print(result.stdout)
            return True
        else:
            print("✗ Installation failed!")
            print("Error output:")
            print(result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("✗ Installation timed out (>2 minutes)")
        return False
    except Exception as e:
        print(f"✗ Installation error: {e}")
        return False

def check_checker_app_compatibility():
    """Check if the checker app files are properly configured."""
    print("\n" + "=" * 60)
    print("CHECKER APP COMPATIBILITY")
    print("=" * 60)
    
    # Check if improved_drag_drop.py exists
    try:
        import improved_drag_drop
        print("✓ improved_drag_drop.py found")
        
        # Check if it has the get_improved_dnd_manager function
        if hasattr(improved_drag_drop, 'get_improved_dnd_manager'):
            print("✓ get_improved_dnd_manager function available")
        else:
            print("✗ get_improved_dnd_manager function not found")
            
    except ImportError:
        print("✗ improved_drag_drop.py not found")
    
    # Check if checker_app.py exists and has TkinterDnD support
    try:
        with open('checker_app.py', 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'TkinterDnD' in content:
            print("✓ checker_app.py has TkinterDnD references")
        else:
            print("✗ checker_app.py missing TkinterDnD references")
            
        if '_has_native_dnd' in content:
            print("✓ checker_app.py has native DnD flag support")
        else:
            print("✗ checker_app.py missing native DnD flag")
            
    except FileNotFoundError:
        print("✗ checker_app.py not found in current directory")
    except Exception as e:
        print(f"✗ Error checking checker_app.py: {e}")

def main():
    """Main function to run all checks."""
    print("Checking TkinterDnD support for Checker App...")
    
    # Check current environment
    check_current_environment()
    
    # Check if tkinterdnd2 is installed
    is_installed = check_tkinterdnd2()
    
    if not is_installed:
        provide_installation_instructions()
        
        # Ask if user wants automatic installation
        try:
            response = input("\nWould you like to try automatic installation? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                success = install_tkinterdnd2()
                if success:
                    # Re-check after installation
                    print("\nRe-checking installation...")
                    is_installed = check_tkinterdnd2()
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled by user.")
    
    # Check app compatibility
    check_checker_app_compatibility()
    
    # Final recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if is_installed:
        print("✓ tkinterdnd2 is properly installed")
        print("✓ The Checker app should now support drag & drop")
        print("\nNext steps:")
        print("1. Restart the Checker app")
        print("2. Test drag & drop functionality")
        print("3. Check the console for any remaining errors")
    else:
        print("✗ tkinterdnd2 is not properly installed")
        print("\nTo fix the drag & drop error:")
        print("1. Install tkinterdnd2: pip install tkinterdnd2")
        print("2. Restart your development environment")
        print("3. Restart the Checker app")
        print("4. Verify that the error is resolved")
    
    print("\nIf problems persist:")
    print("- Check virtual environment activation")
    print("- Try: pip install --upgrade tkinterdnd2")
    print("- Consider using conda instead of pip")
    print("- Check for conflicting tkinter installations")

if __name__ == "__main__":
    main()
