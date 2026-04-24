"""
Test-Skript für PDF-Text-Extraktion und OCR

Überprüft alle verfügbaren PDF-Extraktionsmethoden und gibt
einen detaillierten Bericht über die Erfolgsquote.
"""

import os
import sys

PDF_PATH = r"C:\Users\sarah\Desktop\Texte\HR-Auszug Marinetrans Germany GmbH.pdf"

def test_pdfplumber():
    """Test pdfplumber Text-Extraktion"""
    try:
        import pdfplumber
        with pdfplumber.open(PDF_PATH) as pdf:
            text = pdf.pages[0].extract_text()
            return ("✅ pdfplumber installiert", len(text) if text else 0)
    except ImportError:
        return ("❌ pdfplumber nicht installiert", 0)
    except Exception as e:
        return (f"⚠️ pdfplumber Fehler: {str(e)[:50]}", 0)

def test_pypdf():
    """Test pypdf Text-Extraktion"""
    try:
        import pypdf
        with open(PDF_PATH, 'rb') as f:
            reader = pypdf.PdfReader(f)
            text = reader.pages[0].extract_text()
            return ("✅ pypdf installiert", len(text) if text else 0)
    except ImportError:
        return ("❌ pypdf nicht installiert", 0)
    except Exception as e:
        return (f"⚠️ pypdf Fehler: {str(e)[:50]}", 0)

def test_pypdf2():
    """Test PyPDF2 Text-Extraktion"""
    try:
        import PyPDF2
        with open(PDF_PATH, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            text = reader.pages[0].extract_text()
            return ("✅ PyPDF2 installiert", len(text) if text else 0)
    except ImportError:
        return ("❌ PyPDF2 nicht installiert", 0)
    except Exception as e:
        return (f"⚠️ PyPDF2 Fehler: {str(e)[:50]}", 0)

def test_pymupdf():
    """Test PyMuPDF Text-Extraktion"""
    try:
        import fitz
        doc = fitz.open(PDF_PATH)
        text = doc[0].get_text()
        doc.close()
        return ("✅ PyMuPDF installiert", len(text) if text else 0)
    except ImportError:
        return ("❌ PyMuPDF nicht installiert", 0)
    except Exception as e:
        return (f"⚠️ PyMuPDF Fehler: {str(e)[:50]}", 0)

def test_tesseract():
    """Test Tesseract OCR"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        return (f"✅ Tesseract {version}", 0)
    except ImportError:
        return ("❌ pytesseract nicht installiert", 0)
    except Exception as e:
        return (f"⚠️ Tesseract nicht gefunden: {str(e)[:50]}", 0)

def test_pdf2image():
    """Test pdf2image (braucht Poppler)"""
    try:
        from pdf2image import convert_from_path
        # Nur 1 Seite testen
        images = convert_from_path(PDF_PATH, first_page=1, last_page=1)
        return (f"✅ pdf2image + Poppler OK ({len(images)} Seiten)", len(images))
    except ImportError:
        return ("❌ pdf2image nicht installiert", 0)
    except Exception as e:
        if "poppler" in str(e).lower():
            return ("⚠️ pdf2image: Poppler fehlt!", 0)
        return (f"⚠️ pdf2image Fehler: {str(e)[:50]}", 0)

def test_ocr_full():
    """Test vollständige OCR mit Tesseract"""
    try:
        import pytesseract
        from PIL import Image
        from pdf2image import convert_from_path
        
        images = convert_from_path(PDF_PATH, first_page=1, last_page=1, dpi=300)
        if images:
            text = pytesseract.image_to_string(images[0], lang='deu+eng')
            return (f"✅ OCR funktioniert", len(text) if text else 0)
    except Exception as e:
        return (f"⚠️ OCR fehlgeschlagen: {str(e)[:50]}", 0)

if __name__ == "__main__":
    print("=" * 70)
    print("PDF-EXTRAKTION TEST".center(70))
    print("=" * 70)
    print()
    
    if not os.path.exists(PDF_PATH):
        print(f"❌ PDF nicht gefunden: {PDF_PATH}")
        sys.exit(1)
    
    print(f"📄 PDF: {os.path.basename(PDF_PATH)}")
    print(f"📊 Größe: {os.path.getsize(PDF_PATH) / 1024:.1f} KB")
    print()
    
    print("TEXT-EXTRAKTION (ohne OCR):")
    print("-" * 70)
    
    tests = [
        ("pdfplumber", test_pdfplumber),
        ("pypdf", test_pypdf),
        ("PyPDF2", test_pypdf2),
        ("PyMuPDF", test_pymupdf),
    ]
    
    success_count = 0
    for name, test_func in tests:
        status, chars = test_func()
        print(f"  {name:15} → {status}")
        if chars > 0:
            print(f"                    Text gefunden: {chars} Zeichen")
            success_count += 1
    
    print()
    print("OCR-KOMPONENTEN:")
    print("-" * 70)
    
    tesseract_status, _ = test_tesseract()
    print(f"  Tesseract OCR   → {tesseract_status}")
    
    pdf2image_status, _ = test_pdf2image()
    print(f"  pdf2image       → {pdf2image_status}")
    
    print()
    print("VOLLSTÄNDIGER OCR-TEST:")
    print("-" * 70)
    
    ocr_status, ocr_chars = test_ocr_full()
    print(f"  OCR (komplett)  → {ocr_status}")
    if ocr_chars > 0:
        print(f"                    Text extrahiert: {ocr_chars} Zeichen")
    
    print()
    print("=" * 70)
    print("ZUSAMMENFASSUNG:")
    print("=" * 70)
    
    if success_count > 0:
        print(f"✅ {success_count} Methode(n) können Text extrahieren")
    else:
        print("⚠️ KEINE Text-Extraktion möglich → PDF ist gescannt!")
        print()
        print("LÖSUNG: OCR benötigt")
        print("  1. Poppler installieren (siehe OCR_SETUP_ANLEITUNG.md)")
        print("  2. Oder: PDF extern mit OCR konvertieren")
    
    if ocr_chars > 0:
        print(f"✅ OCR funktioniert ({ocr_chars} Zeichen extrahiert)")
    elif "Poppler" in pdf2image_status:
        print("⚠️ OCR fast bereit → Nur noch Poppler installieren!")
        print("   Download: https://github.com/oschwartz10612/poppler-windows/releases/")
    else:
        print("❌ OCR nicht verfügbar")
    
    print()
