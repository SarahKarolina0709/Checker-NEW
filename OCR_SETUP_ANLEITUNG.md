# OCR-Setup für gescannte PDFs

## Problem
Ihr PDF "HR-Auszug Marinetrans Germany GmbH.pdf" ist **gescannt** (enthält nur Bilder, keinen extrahierbaren Text). Deshalb werden 0 Zeichen extrahiert.

## Lösung: OCR-Installation

### Methode 1: Tesseract + pdf2image (EMPFOHLEN)

#### Schritt 1: Poppler installieren
1. Download: https://github.com/oschwartz10612/poppler-windows/releases/latest
2. `poppler-xx.xx.x.zip` herunterladen
3. Entpacken nach `C:\Program Files\poppler` (oder beliebigen Pfad)
4. **Pfad zu System-PATH hinzufügen:**
   - Windows-Suche: "Umgebungsvariablen"
   - System → Erweitert → Umgebungsvariablen
   - PATH bearbeiten → Neu:  `C:\Program Files\poppler\Library\bin`
   - OK → Neu starten

#### Schritt 2: Testen
```powershell
cd c:\Users\sarah\Desktop\Checker
.\.venv\Scripts\python.exe -c "from pdf2image import convert_from_path; print('Poppler OK!')"
```

### Methode 2: pymupdf4llm (Alternat)
```powershell
.\.venv\Scripts\python.exe -m pip install pymupdf4llm
```

Dann in `quality_gui_main_app.py`:
```python
import pymupdf4llm
text = pymupdf4llm.to_markdown(pdf_path)
```

### Methode 3: Externe Tools
- **Adobe Acrobat** → Text exportieren
- **Online-OCR**: https://www.onlineocr.net/
- **ABBYY FineReader** (kostenpflichtig, sehr gut)

## Status-Check
Nach Installation testen:
```powershell
.\.venv\Scripts\python.exe test_ocr.py
```

## Alternative Workflow
1. PDFs extern mit OCR konvertieren (z.B. Adobe Acrobat)
2. Als Text-PDF neu speichern
3. In Checker hochladen → funktioniert ohne zusätzliche Tools
