# 🚀 SCHNELLE LÖSUNG: PDF mit OCR konvertieren

## Option 1: Online-OCR (kostenlos, 5 Minuten)
1. Gehen Sie zu: https://www.ilovepdf.com/de/ocr-pdf
2. Laden Sie Ihr PDF hoch: `HR-Auszug Marinetrans Germany GmbH.pdf`
3. Sprache: Deutsch auswählen
4. Konvertieren → Herunterladen
5. Neue Datei in Checker hochladen → Text wird jetzt erkannt!

## Option 2: Adobe Acrobat (falls vorhanden)
1. PDF in Adobe öffnen
2. Werkzeuge → Text erkennen → In dieser Datei
3. Sprache: Deutsch
4. Speichern → In Checker hochladen

## Option 3: Windows PDF-Reader (kostenlos)
1. PDF im Edge-Browser öffnen
2. "Als Word speichern" → erzeugt DOCX mit Text
3. DOCX in Checker hochladen (funktioniert bereits!)

## Option 4: Poppler installieren (15 Minuten)
Falls Sie häufig gescannte PDFs haben:

### Schritt 1: Poppler herunterladen
https://github.com/oschwartz10612/poppler-windows/releases/latest
→ `poppler-XX.XX.X.zip` herunterladen

### Schritt 2: Entpacken
Entpacken nach: `C:\Program Files\poppler\`

### Schritt 3: PATH setzen
1. Windows-Suche: "Umgebungsvariablen bearbeiten"
2. Systemvariablen → PATH → Bearbeiten → Neu
3. Eintrag: `C:\Program Files\poppler\Library\bin`
4. OK → OK → Neustart

### Schritt 4: Testen
```powershell
cd c:\Users\sarah\Desktop\Checker
.\.venv\Scripts\python.exe test_pdf_extraction.py
```

Sollte zeigen: `✅ OCR funktioniert`

## 🎯 EMPFEHLUNG
- **Jetzt sofort**: Option 1 (Online-OCR, 5 Min) → PDF konvertieren
- **Langfristig**: Option 4 (Poppler, 15 Min) → für zukünftige PDFs

## Status nach Konvertierung
Nach OCR-Konvertierung:
- ✅ Quelle: X Zeichen (statt 0)
- ✅ Ziel: Y Zeichen  
- ✅ Analyse funktioniert
