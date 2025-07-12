"""
PDF2Image Dependency Checker and Installer

This script checks for pdf2image and related dependencies, and provides
automated installation and configuration for PDF OCR functionality.
"""

import sys
import subprocess
import importlib.util
import os

def check_pdf2image():
    """Check if pdf2image is properly installed."""
    print("=" * 60)
    print("PDF2IMAGE DEPENDENCY CHECK")
    print("=" * 60)
    
    # Check if pdf2image can be imported
    try:
        import pdf2image
        from pdf2image import convert_from_path
        print("✓ pdf2image is installed and can be imported")
        
        # Check version if available
        if hasattr(pdf2image, '__version__'):
            print(f"✓ Version: {pdf2image.__version__}")
        
        return True
        
    except ImportError as e:
        print(f"✗ pdf2image is not installed: {e}")
        return False
    except Exception as e:
        print(f"✗ Error with pdf2image: {e}")
        return False

def check_poppler():
    """Check if Poppler is available for pdf2image."""
    print("\n" + "=" * 60)
    print("POPPLER DEPENDENCY CHECK")
    print("=" * 60)
    
    try:
        import pdf2image
        from pdf2image import convert_from_path
        
        # Try to create a test conversion (will fail if Poppler missing)
        # We'll just check if the function exists and imports work
        print("✓ pdf2image convert_from_path function available")
        
        # Check if poppler_config module exists
        try:
            import poppler_config
            config = poppler_config.POPPLER_CONFIG
            if config and config.is_configured:
                print(f"✓ Poppler configured at: {config.path}")
                return True
            else:
                print("⚠ Poppler configuration not found")
                return False
        except ImportError:
            print("⚠ poppler_config module not found")
            return False
            
    except ImportError:
        print("✗ pdf2image not available - cannot check Poppler")
        return False
    except Exception as e:
        print(f"✗ Error checking Poppler: {e}")
        return False

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

def install_pdf2image():
    """Attempt to install pdf2image automatically."""
    print("\n" + "=" * 60)
    print("AUTOMATIC INSTALLATION")
    print("=" * 60)
    
    try:
        print("Attempting to install pdf2image...")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "pdf2image"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✓ pdf2image installed successfully!")
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

def install_poppler_windows():
    """Provide instructions for installing Poppler on Windows."""
    print("\n" + "=" * 60)
    print("POPPLER INSTALLATION (WINDOWS)")
    print("=" * 60)
    
    print("Poppler ist erforderlich für PDF-Verarbeitung mit pdf2image.")
    print("\nOption 1 - Conda (empfohlen):")
    print("   conda install -c conda-forge poppler")
    
    print("\nOption 2 - Manueller Download:")
    print("   1. Download von: https://github.com/oschwartz10612/poppler-windows/releases/")
    print("   2. Entpacken Sie das Archiv")
    print("   3. Fügen Sie den bin-Ordner zu Ihrem System-PATH hinzu")
    
    print("\nOption 3 - Chocolatey:")
    print("   choco install poppler")
    
    print("\nNach der Installation:")
    print("   - Starten Sie Ihre Entwicklungsumgebung neu")
    print("   - Führen Sie diesen Checker erneut aus")

def provide_installation_instructions():
    """Provide comprehensive installation instructions."""
    print("\n" + "=" * 60)
    print("INSTALLATION INSTRUCTIONS")
    print("=" * 60)
    
    print("\n1. Install pdf2image using pip:")
    print("   pip install pdf2image")
    
    print("\n2. If you're using conda:")
    print("   conda install -c conda-forge pdf2image")
    
    print("\n3. For virtual environments:")
    print("   # Windows")
    print("   .\\venv\\Scripts\\activate")
    print("   pip install pdf2image")
    
    print("\n4. For complete PDF OCR support, also install:")
    print("   pip install pytesseract")
    print("   # And install Tesseract OCR engine separately")
    
    print("\n5. Verify installation:")
    print("   python -c \"import pdf2image; print('pdf2image installed successfully')\"")

def check_file_operations_integration():
    """Check if file_operations.py can use pdf2image."""
    print("\n" + "=" * 60)
    print("FILE OPERATIONS INTEGRATION")
    print("=" * 60)
    
    try:
        # Import file_operations and check PDF2IMAGE_ENABLED flag
        import file_operations
        
        if hasattr(file_operations, 'PDF2IMAGE_ENABLED'):
            if file_operations.PDF2IMAGE_ENABLED:
                print("✓ file_operations.py: PDF2IMAGE_ENABLED = True")
                print("✓ PDF OCR functionality is available")
            else:
                print("✗ file_operations.py: PDF2IMAGE_ENABLED = False")
                print("✗ PDF OCR functionality is disabled")
        else:
            print("⚠ file_operations.py: PDF2IMAGE_ENABLED flag not found")
        
        # Check if OCR_ENABLED
        if hasattr(file_operations, 'OCR_ENABLED'):
            print(f"OCR_ENABLED: {file_operations.OCR_ENABLED}")
        
        # Check if PYTESSERACT_ENABLED
        if hasattr(file_operations, 'PYTESSERACT_ENABLED'):
            print(f"PYTESSERACT_ENABLED: {file_operations.PYTESSERACT_ENABLED}")
            
    except ImportError:
        print("✗ file_operations.py not found or cannot be imported")
    except Exception as e:
        print(f"✗ Error checking file_operations.py: {e}")

def test_pdf_conversion():
    """Test PDF conversion functionality."""
    print("\n" + "=" * 60)
    print("PDF CONVERSION TEST")
    print("=" * 60)
    
    try:
        from pdf2image import convert_from_path
        print("✓ pdf2image convert_from_path imported successfully")
        
        # We won't actually convert a file, just test that the function is available
        print("✓ PDF conversion function is ready to use")
        print("Note: Actual conversion requires a PDF file and proper Poppler configuration")
        
    except ImportError as e:
        print(f"✗ Cannot import pdf2image: {e}")
    except Exception as e:
        print(f"✗ Error testing PDF conversion: {e}")

def main():
    """Main function to run all checks."""
    print("Checking pdf2image dependencies for Checker App PDF OCR...")
    
    # Check current environment
    check_current_environment()
    
    # Check if pdf2image is installed
    pdf2image_installed = check_pdf2image()
    
    # Check Poppler availability
    poppler_available = check_poppler()
    
    # Check file operations integration
    check_file_operations_integration()
    
    # Test PDF conversion
    test_pdf_conversion()
    
    if not pdf2image_installed:
        provide_installation_instructions()
        
        # Ask if user wants automatic installation
        try:
            response = input("\nWould you like to try automatic installation? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                success = install_pdf2image()
                if success:
                    # Re-check after installation
                    print("\nRe-checking installation...")
                    pdf2image_installed = check_pdf2image()
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled by user.")
    
    if pdf2image_installed and not poppler_available:
        install_poppler_windows()
    
    # Final recommendations
    print("\n" + "=" * 60)
    print("RECOMMENDATIONS")
    print("=" * 60)
    
    if pdf2image_installed and poppler_available:
        print("✓ pdf2image and Poppler are properly configured")
        print("✓ PDF OCR functionality should work")
        print("\nNext steps:")
        print("1. Restart the Checker app")
        print("2. Test PDF OCR functionality")
        print("3. Check the console for any remaining warnings")
    elif pdf2image_installed:
        print("✓ pdf2image is installed")
        print("⚠ Poppler may need configuration")
        print("\nTo complete setup:")
        print("1. Install Poppler (see instructions above)")
        print("2. Restart your development environment")
        print("3. Restart the Checker app")
    else:
        print("✗ pdf2image is not properly installed")
        print("\nTo fix the PDF OCR warning:")
        print("1. Install pdf2image: pip install pdf2image")
        print("2. Install Poppler for your system")
        print("3. Restart your development environment")
        print("4. Restart the Checker app")
        print("5. Verify that the warning is resolved")
    
    print("\nIf problems persist:")
    print("- Check virtual environment activation")
    print("- Try: pip install --upgrade pdf2image")
    print("- Consider using conda instead of pip")
    print("- Check for conflicting PIL/Pillow installations")
    print("- Ensure Poppler is in your system PATH")

if __name__ == "__main__":
    main()
