import os
from datetime import datetime
from collections import defaultdict
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors

# Placeholder for resource_path if you have a logo, or define it if not available globally
# For simplicity, assuming resource_path is available or logo is handled directly
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        # pylint: disable=no-member
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def exportiere_reduziertes_pdf():
    # Dummy-Implementierung
    print("Dummy: exportiere_reduziertes_pdf aufgerufen")
    pass

def exportiere_score_pdf():
    # Dummy-Implementierung
    print("Dummy: exportiere_score_pdf aufgerufen")
    pass

def exportiere_ki_pdf(bericht, dateiname="ki_bericht.pdf"):
    # Ensure directory exists
    try:
        export_dir = os.path.dirname(dateiname)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
    except Exception as e:
        print(f"Fehler beim Erstellen des Verzeichnisses für KI PDF: {e}")

    c = canvas.Canvas(dateiname, pagesize=A4)
    c.setFont("Helvetica", 12)
    
    width, height = A4
    y_position = height - 50
    x_margin = 50
    line_height = 14

    for line in bericht.splitlines():
        if y_position < 50: # New page if not enough space
            c.showPage()
            c.setFont("Helvetica", 12)
            y_position = height - 50
        c.drawString(x_margin, y_position, line)
        y_position -= line_height
        
    c.save()
    try:
        os.startfile(dateiname)
    except Exception as e:
        print(f"Konnte PDF nicht automatisch öffnen: {e}")

def pdf_export_sortiert(matches, dateiname="checker_score_bericht.pdf"):
    # Dummy-Implementierung
    print(f"Dummy: pdf_export_sortiert aufgerufen für {dateiname}")
    pass

def exportiere_bericht_pdf(matches, ki_text, pruefstufe, language_code, fachgebiet, dateiname="Uebersetzerbericht.pdf", logo_path=None):
    try:
        export_dir = os.path.dirname(dateiname)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
    except Exception as e:
        print(f"Fehler beim Erstellen des Verzeichnisses für Bericht PDF: {e}")

    c = canvas.Canvas(dateiname, pagesize=A4)
    width, height = A4
    y = height - 50
    x_margin = 50
    line_height = 14
    max_line_width = width - 2 * x_margin

    # Logo (optional)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            # Adjust logo size and position as needed
            c.drawImage(logo, x_margin, y - 40, width=80, height=40, preserveAspectRatio=True, anchor='nw')
            title_x_offset = 100 # Shift title if logo is present
        except Exception as e:
            print(f"Logo konnte nicht geladen werden: {e}")
            title_x_offset = 0
    else:
        title_x_offset = 0


    # Überschrift
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x_margin + title_x_offset, y, f"Übersetzungs-Fehlerbericht")
    y -= 18 
    c.setFont("Helvetica", 11) 
    c.drawString(x_margin + title_x_offset, y, f"(Stufe: {pruefstufe}, Sprache: {language_code}, Fachgebiet: {fachgebiet})")
    y -= 25
    
    c.setFont("Helvetica-Bold", 14)
    c.drawString(x_margin, y, "Fehlerübersicht nach Regeltyp:")
    y -= (line_height + 6)
    c.setFont("Helvetica", 10) # Smaller font for details

    fehler_gesamt = defaultdict(list)
    for match in matches:
        # Group by ruleId or category, ensure unique messages per group if needed
        rule_display = f"{match.ruleId} ({match.category})"
        # Simple way to avoid exact duplicate messages under the same rule
        if match.message not in fehler_gesamt[rule_display]:
             fehler_gesamt[rule_display].append(match.message)

    for regel, fehler_messages in fehler_gesamt.items():
        if y < 70: # New page
            c.showPage()
            c.setFont("Helvetica", 10)
            y = height - 50
        
        c.setFont("Helvetica-Bold", 11)
        c.drawString(x_margin, y, f"Regel: {regel}")
        y -= line_height
        c.setFont("Helvetica", 10)
        for msg in fehler_messages:
            if y < 50: # New page
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
            # Basic text wrapping (can be improved with ReportLab's Paragraphs for complex text)
            # For simplicity, just draw string. For long messages, consider text objects or paragraphs.
            c.drawString(x_margin + 15, y, f"- {msg[:100]}{'...' if len(msg) > 100 else ''}") # Truncate long messages
            y -= line_height
        y -= (line_height / 2) # Extra space between rule groups

    # KI Text Section
    if y < 150 and ki_text.strip(): # Check if enough space for KI section header and some content
        c.showPage()
        y = height - 50
        
    if ki_text.strip():
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, y, "KI-Analyse Ergebnis:")
        y -= (line_height + 6)
        c.setFont("Helvetica", 10)
        for line in ki_text.splitlines():
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
            # Again, simple drawString. Consider Paragraphs for better formatting.
            c.drawString(x_margin, y, line[:120]) # Truncate long lines
            y -= line_height

    c.save()
    try:
        os.startfile(dateiname)
    except Exception as e:
        print(f"Konnte PDF nicht automatisch öffnen: {e}")

def exportiere_umfassende_pruefung_pdf(pruefstufe, language_code, fachgebiet, konsistenz_ki, ki_ergebnis, zusammenfassung, glossar_check, tonfall, kulturell, stilistische_hinweise, dateiname="Umfassende_Pruefung.pdf", logo_path=None):
    try:
        export_dir = os.path.dirname(dateiname)
        if export_dir and not os.path.exists(export_dir):
            os.makedirs(export_dir)
    except Exception as e:
        print(f"Fehler beim Erstellen des Verzeichnisses für umfassende PDF: {e}")

    c = canvas.Canvas(dateiname, pagesize=A4)
    width, height = A4
    y = height - 50
    x_margin = 50
    line_height = 14

    # Logo (optional)
    if logo_path and os.path.exists(logo_path):
        try:
            logo = ImageReader(logo_path)
            c.drawImage(logo, x_margin, y - 40, width=80, height=40, preserveAspectRatio=True, anchor='nw')
            title_x_offset = 100
        except Exception as e:
            print(f"Logo konnte nicht geladen werden: {e}")
            title_x_offset = 0
    else:
        title_x_offset = 0
        
    c.setFont("Helvetica-Bold", 18)
    c.drawString(x_margin + title_x_offset, y, f"Umfassende KI-Prüfung")
    y -= 18
    c.setFont("Helvetica", 11)
    c.drawString(x_margin + title_x_offset, y, f"(Stufe: {pruefstufe}, Sprache: {language_code}, Fachgebiet: {fachgebiet})")
    y -= 25

    sections = {
        "Konsistenzprüfung (KI)": konsistenz_ki,
        "KI-Analyse (Qualität & Vergleich)": ki_ergebnis,
        "Automatische Zusammenfassung": zusammenfassung,
        "Glossar-Check": glossar_check,
        "Tonfall-/Register-Prüfung": tonfall,
        "Kulturelle Anpassungen": kulturell,
        "Stilistische Hinweise": stilistische_hinweise
    }

    for title, content in sections.items():
        if not content or content.strip() == "N/A für diese Stufe": # Skip empty or N/A sections
            continue

        if y < 100: # Check for new page before starting a new section
            c.showPage()
            y = height - 50
        
        c.setFont("Helvetica-Bold", 14)
        c.drawString(x_margin, y, title)
        y -= (line_height + 6)
        c.setFont("Helvetica", 10)
        
        # Ensure content is a string before splitting; if it's a list, join it.
        if isinstance(content, list):
            content_str = "\n".join(content)
        else:
            content_str = str(content) # Ensure it's a string

        for line in content_str.splitlines():
            if y < 50:
                c.showPage()
                c.setFont("Helvetica", 10)
                y = height - 50
            c.drawString(x_margin + 10, y, line[:120]) # Truncate long lines
            y -= line_height
        y -= line_height # Extra space after section

    c.save()
    try:
        os.startfile(dateiname)
    except Exception as e:
        print(f"Konnte PDF nicht automatisch öffnen: {e}")

