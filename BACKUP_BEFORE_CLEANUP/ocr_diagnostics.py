import os
from PIL import Image, ImageDraw, ImageFont
import pytesseract
from pdf2image import convert_from_path
from reportlab.pdfgen import canvas as reportlab_canvas
from reportlab.lib.pagesizes import letter

# --- Configuration (IMPORTANT: Uncomment and set these if Tesseract/Poppler are not in your PATH) ---
# Tesseract OCR executable path
# Example for Windows:
TESSERACT_CMD_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# Example for Linux/macOS (if not in PATH):
# TESSERACT_CMD_PATH = r'/usr/local/bin/tesseract' # or /opt/homebrew/bin/tesseract
TESSERACT_CMD_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# Poppler configuration now handled automatically by poppler_config.py
# Use get_poppler_path_for_pdf2image() instead of hardcoded paths
from poppler_config import get_poppler_path_for_pdf2image

# --- Setup Tesseract Path if Configured ---
if TESSERACT_CMD_PATH:
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
else:
    print("INFO: TESSERACT_CMD_PATH not set in script; relying on Tesseract being in system PATH.")

# --- Helper Functions ---
def create_dummy_image(filename="dummy_ocr_test_image.png", text="Test 123"):
    """Creates a simple image with text."""
    try:
        img = Image.new('RGB', (400, 100), color = (255, 255, 255))
        d = ImageDraw.Draw(img)
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()
        
        # Calculate text position for centering
        text_bbox = d.textbbox((0,0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        x = (img.width - text_width) / 2
        y = (img.height - text_height) / 2
        
        d.text((x,y), text, fill=(0,0,0), font=font)
        img.save(filename)
        print(f"SUCCESS: Dummy image '{filename}' created.")
        return True
    except Exception as e:
        print(f"ERROR: Could not create dummy image '{filename}': {e}")
        return False

def create_dummy_pdf(filename="dummy_ocr_test_pdf.pdf", text="PDF Test Content 456"):
    """Creates a simple one-page PDF with text."""
    try:
        c = reportlab_canvas.Canvas(filename, pagesize=letter)
        c.setFont("Helvetica", 20)
        c.drawString(100, 750, text)
        c.save()
        print(f"SUCCESS: Dummy PDF '{filename}' created.")
        return True
    except Exception as e:
        print(f"ERROR: Could not create dummy PDF '{filename}': {e}")
        return False

def test_image_ocr(image_path="dummy_ocr_test_image.png"):
    print(f"\n--- Testing Image OCR on '{image_path}' ---")
    if not os.path.exists(image_path):
        print(f"INFO: Image '{image_path}' not found. Attempting to create it.")
        if not create_dummy_image(image_path):
            print("Skipping image OCR test as dummy image creation failed.")
            return

    try:
        text_from_image = pytesseract.image_to_string(Image.open(image_path))
        if text_from_image:
            print(f"SUCCESS: OCR from image successful. Extracted text (partial): '{text_from_image.strip()[:50]}...'")
        else:
            print("WARNING: OCR from image returned empty text. Tesseract might be working but found no text.")
    except pytesseract.TesseractNotFoundError:
        print("ERROR: Tesseract executable not found by pytesseract.")
        print("Please ensure Tesseract OCR is installed AND in your system PATH,")
        print("OR uncomment and set TESSERACT_CMD_PATH in this script (and in your project's file_operations.py).")
    except Exception as e:
        print(f"ERROR: An error occurred during image OCR: {e}")

def test_pdf_ocr(pdf_path="dummy_ocr_test_pdf.pdf"):
    print(f"\n--- Testing PDF to Image Conversion (Poppler) and OCR on '{pdf_path}' ---")
    if not os.path.exists(pdf_path):
        print(f"INFO: PDF '{pdf_path}' not found. Attempting to create it.")
        if not create_dummy_pdf(pdf_path):
            print("Skipping PDF OCR test as dummy PDF creation failed.")
            return
            
    try:
        # Auto-detect Poppler path using our configuration manager
        poppler_path = get_poppler_path_for_pdf2image()
        images_from_pdf = convert_from_path(pdf_path, poppler_path=poppler_path)
        if images_from_pdf:
            print(f"SUCCESS: PDF to image conversion successful ({len(images_from_pdf)} page(s) converted).")
            print("Attempting OCR on the first page...")
            try:
                text_from_pdf_image = pytesseract.image_to_string(images_from_pdf[0])
                if text_from_pdf_image:
                    print(f"SUCCESS: OCR from PDF's first page successful. Extracted text (partial): '{text_from_pdf_image.strip()[:50]}...'")
                else:
                    print("WARNING: OCR from PDF image returned empty text. Tesseract might be working but found no text on the page.")
            except pytesseract.TesseractNotFoundError:
                print("ERROR: Tesseract executable not found by pytesseract during PDF page OCR.")
                print("Ensure Tesseract is installed AND in PATH, or TESSERACT_CMD_PATH is set.")
            except Exception as e_ocr:
                print(f"ERROR: An error occurred during OCR of the PDF page: {e_ocr}")
        else:
            print("WARNING: PDF to image conversion returned no images. PDF might be empty or Poppler had an issue.")
    except Exception as e: # Catches pdf2image exceptions like PopplerNotInstalledError
        print(f"ERROR: An error occurred during PDF to image conversion (pdf2image): {e}")
        print("This often means Poppler is not installed, not in PATH, or Poppler configuration failed.")
        print("Run 'python poppler_config.py' for installation guidance.")
        print("Please ensure Poppler is installed and its 'bin' directory is in PATH or configured.")

if __name__ == "__main__":
    print("Starting OCR Diagnostics...")
    print("This script will test if Tesseract and Poppler are correctly set up for OCR.")
    
    if TESSERACT_CMD_PATH:
        print(f"INFO: Using Tesseract command path: {TESSERACT_CMD_PATH}")
    else:
        print("INFO: TESSERACT_CMD_PATH not set in script; relying on Tesseract being in system PATH.")
          # Display Poppler configuration status
    from poppler_config import POPPLER_CONFIG
    if POPPLER_CONFIG and POPPLER_CONFIG.is_configured:
        status = POPPLER_CONFIG.get_status_info()
        print(f"INFO: Using Poppler: {status['path'] or 'System PATH'} ({status['method']})")
    else:
        print("INFO: Poppler configuration not found; relying on system PATH or will fail.")

    # Test 1: Image OCR
    test_image_ocr()

    # Test 2: PDF to Image conversion (Poppler) and then OCR (Tesseract)
    test_pdf_ocr()

    print("\n--- Diagnostics Complete ---")
    print("If you see 'SUCCESS' messages, your basic setup is likely working.")
    print("If you see 'ERROR' messages, please check the installation and PATH for Tesseract and/or Poppler,")
    print("or run 'python poppler_config.py' for automatic Poppler setup guidance.")
    print("Remember to also apply similar path configurations in your main project's 'file_operations.py' if needed.")

