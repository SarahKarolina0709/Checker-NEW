import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
import os
import platform
import subprocess
from datetime import datetime
import threading
import json
from tkinter import ttk
import time

from docx import Document
import PyPDF2
import language_tool_python
import ollama
from PIL import Image
import spacy
from rapidfuzz import fuzz

from theme_loader import lade_theme, lade_icons, get_effective_mode
from toolbar_setup import create_toolbar
from theme_zentrale import öffne_theme_zentrale
from tooltip import Tooltip

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from collections import defaultdict

import customtkinter as ctk

# >>> HIER FARBCODES DEFINIEREN <<<
PRIMARY = "#1e90ff"      # Blau für Hauptaktionen
PRIMARY_HOVER = "#1565c0"
SUCCESS = "#2e8b57"      # Grün für Erfolg
SUCCESS_HOVER = "#388e3c"
DANGER = "#e53935"       # Rot für Warnungen
DANGER_HOVER = "#b71c1c"
BG = "#f5f5f5"           # Heller Hintergrund für Light-Mode
FG = "#16191f"           # Dunkleres Anthrazit für Schrift im Light-Mode

REGEL_BESCHREIBUNG = {
    # Beispielregeln:
    "UPPERCASE_SENTENCE_START": "Großschreibung am Satzanfang",
    "COMMA_PARENTHESIS_WHITESPACE": "Komma oder Klammer Abstand",
    "EN_QUOTES": "Englische Anführungszeichen",
    # ... ergänze nach Bedarf ...
}

# ----- Theme und App-Fenster -----

root = TkinterDnD.Tk()  # DnD-fähiges Fenster
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")
root.title("Checker – KI-gestützte Übersetzungsprüfung")
root.geometry("960x720")

theme_mode = tk.StringVar(value="auto")
THEME = lade_theme()
MODE = get_effective_mode(theme_mode.get())
COLORS = THEME[MODE]
root.configure(bg=COLORS["bg"])

def apply_theme_live(mode_name, theme_dict):
    global COLORS, THEME, icons
    COLORS = theme_dict[mode_name]
    THEME = theme_dict
    root.configure(bg=COLORS["bg"])
    for widget in root.winfo_children():
        try:
            if isinstance(widget, tk.Entry):
                widget.configure(bg=COLORS["btn"], fg=COLORS["fg"], insertbackground=COLORS["fg"])
            elif isinstance(widget, tk.Text):
                widget.configure(bg=COLORS["btn"], fg=COLORS["fg"])
            elif isinstance(widget, tk.Label):
                widget.configure(bg=COLORS["bg"], fg=COLORS["fg"])
            elif isinstance(widget, tk.Button):
                widget.configure(bg=COLORS["btn"], fg=COLORS["fg"], activebackground=COLORS["btn_hover"])
            else:
                widget.configure(bg=COLORS["bg"])
        except Exception as e:
            print(f"⚠️ Widget konnte nicht aktualisiert werden: {e}")
    icons = lade_icons(mode_name, master=root)
    print(f"✅ Theme '{mode_name}' wurde live angewendet.")

# ----- Eingabevariablen -----
kundenname = tk.StringVar()
kundenordner_pfad = tk.StringVar()
kommentar_übersetzer = tk.StringVar()
ausgangsdatei = tk.StringVar()
uebersetzungsdatei = tk.StringVar()
referenzdatei = tk.StringVar()

# ----- Dateioperationen -----
def lade_ausgangsdatei():
    pfad = filedialog.askopenfilename(
        title="Ausgangstext wählen",
        filetypes=[("Textdateien", "*.txt *.docx *.pdf"), ("Alle Dateien", "*.*")]
    )
    if pfad:
        ausgangsdatei.set(pfad)
        label_ausgang.configure(text=os.path.basename(pfad))  # Dateiname anzeigen

def lade_uebersetzungsdatei():
    pfad = filedialog.askopenfilename(
        title="Übersetzung wählen",
        filetypes=[("Textdateien", "*.txt *.docx *.pdf"), ("Alle Dateien", "*.*")]
    )
    if pfad:
        uebersetzungsdatei.set(pfad)
        label_uebersetzung.configure(text=os.path.basename(pfad))  # Dateiname anzeigen

def lade_referenzdatei():
    pfad = filedialog.askopenfilename(
        title="Referenzübersetzung wählen",
        filetypes=[("Textdateien", "*.txt *.docx *.pdf"), ("Alle Dateien", "*.*")]
    )
    if pfad:
        referenzdatei.set(pfad)
        label_referenz.configure(text=os.path.basename(pfad))  # Dateiname anzeigen

def lese_datei(pfad):
    ext = os.path.splitext(pfad)[1].lower()
    if ext == ".docx":
        doc = Document(pfad)
        return "\n".join([para.text for para in doc.paragraphs])
    elif ext == ".pdf":
        text = ""
        with open(pfad, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() or ""
        return text
    else:
        with open(pfad, "r", encoding="utf-8") as f:
            return f.read()

# ----- Drag & Drop -----
def drop_ausgangsdatei(event):
    pfad = event.data.strip("{}")
    ausgangsdatei.set(pfad)
    label_ausgang.configure(text=os.path.basename(pfad))

def drop_uebersetzungsdatei(event):
    pfad = event.data.strip("{}")
    uebersetzungsdatei.set(pfad)
    label_uebersetzung.configure(text=os.path.basename(pfad))

# ----- Prüfungen -----
def pruefe_uebersetzung():
    pfad = uebersetzungsdatei.get()
    if not pfad:
        messagebox.showwarning("Fehler", "Bitte zuerst eine Übersetzungsdatei auswählen!")
        return
    try:
        text = lese_datei(pfad)
        print(f"📄 Geladener Text (Auszug):\n{text[:300]}")
    except Exception as e:
        root.after(0, lambda: messagebox.showerror("Fehler", f"Datei konnte nicht gelesen werden:\n{e}"))
        return

    try:
        tool = language_tool_python.LanguageTool(zielsprache.get())
        matches = tool.check(text)
        print(f"🔍 {len(matches)} Fehler gefunden.")
        if matches:
            root.after(0, lambda: zeige_sortierte_fehler(matches))
        else:
            root.after(0, lambda: zeige_ergebnis_im_textfeld("Keine Fehler gefunden!"))
    except Exception as e:
        root.after(0, lambda e=e: messagebox.showerror("Toolfehler", str(e)))

def pruefe_uebersetzung_threaded():
    def task():
        progress = show_progress("Prüfe Übersetzung...")
        try:
            pruefe_uebersetzung()
        finally:
            progress.destroy()
    threading.Thread(target=task).start()

def pruefe_uebersetzungsvergleich():
    pfad_ausgang = ausgangsdatei.get()
    pfad_uebersetzung = uebersetzungsdatei.get()
    if not pfad_ausgang or not pfad_uebersetzung:
        messagebox.showwarning("Fehler", "Bitte beide Dateien auswählen!")
        return
    try:
        text_ausgang = lese_datei(pfad_ausgang)
        text_uebersetzung = lese_datei(pfad_uebersetzung)
    except Exception as e:
        messagebox.showerror("Fehler", f"Dateien konnten nicht gelesen werden:\n{e}")
        return

    ausgang_zeilen = text_ausgang.splitlines()
    uebersetzung_zeilen = text_uebersetzung.splitlines()
    vergleichsergebnis = []
    max_len = max(len(ausgang_zeilen), len(uebersetzung_zeilen))
    for i in range(max_len):
        src = ausgang_zeilen[i] if i < len(ausgang_zeilen) else ""
        tgt = uebersetzung_zeilen[i] if i < len(uebersetzung_zeilen) else ""
        if not tgt.strip():
            vergleichsergebnis.append(f"Zeile {i+1}: Keine Übersetzung vorhanden für: {src}")
        elif src.strip() and src.strip() != tgt.strip():
            vergleichsergebnis.append(f"Zeile {i+1}: Unterschied:\n  Original: {src}\n  Übersetzung: {tgt}")

    if len(ausgang_zeilen) != len(uebersetzung_zeilen):
        vergleichsergebnis.append("⚠️ Unterschiedliche Zeilenzahl in Ausgangstext und Übersetzung!")

    if vergleichsergebnis:
        zeige_ergebnisfenster("Vergleich Ausgangstext vs. Übersetzung", "\n".join(vergleichsergebnis))
    else:
        zeige_ergebnisfenster("Vergleich", "Keine offensichtlichen Unterschiede gefunden.")

def pruefe_ki_qualitaet():
    pfad_ausgang = ausgangsdatei.get()
    pfad_uebersetzung = uebersetzungsdatei.get()
    if not pfad_ausgang or not pfad_uebersetzung:
        messagebox.showwarning("Fehler", "Bitte beide Dateien auswählen!")
        return
    try:
        text_ausgang = lese_datei(pfad_ausgang)
        text_uebersetzung = lese_datei(pfad_uebersetzung)  # <-- hier korrigiert!
    except Exception as e:
        messagebox.showerror("Fehler", f"Dateien konnten nicht gelesen werden:\n{e}")
        return

    ergebnis = ki_qualitaetspruefung_mit_vergleich(text_ausgang, text_uebersetzung)
    zeige_ergebnisfenster("KI-Qualitätsprüfung", ergebnis)

def pruefe_alle():
    progress = show_progress("Prüfung und PDF-Export läuft...")
    def task():
        try:
            pfad_ausgang = ausgangsdatei.get()
            pfad_uebersetzung = uebersetzungsdatei.get()
            if not pfad_ausgang or not pfad_uebersetzung:
                messagebox.showwarning("Fehler", "Bitte beide Dateien auswählen!")
                return
            try:
                text_ausgang = lese_datei(pfad_ausgang)
                text_uebersetzung = lese_datei(pfad_uebersetzung)
            except Exception as e:
                messagebox.showerror("Fehler", f"Dateien konnten nicht gelesen werden:\n{e}")
                return

            # LanguageTool prüft ausschließlich die Übersetzung (Zieldatei)
            tool = language_tool_python.LanguageTool('de-DE')
            matches = tool.check(text_uebersetzung)

            # Konsistenzprüfung: Sind alle Kernbegriffe aus dem Ausgangstext korrekt in der Übersetzung übernommen?
            konsistenz_fehler = pruefe_kernbegriffe_konsistenz(text_ausgang, text_uebersetzung)

            # KI-Vergleich: Prüft, ob die Übersetzung dem Ausgangstext entspricht (Bedeutung, Zahlen, Namen, Maßeinheiten)
            ki_ergebnis = ki_qualitaetspruefung_mit_vergleich(text_ausgang, text_uebersetzung)

            # Fehlende oder doppelte Abschnitte prüfen
            abschnitts_check = ki_abschnitts_check(text_ausgang, text_uebersetzung)

            # Kombiniertes Ergebnis im Textfeld anzeigen
            fehlertext = "LanguageTool-Fehler:\n" + ("\n".join(fehler_liste) if fehler_liste else "Keine Fehler gefunden.")
            gesamt = (
                f"{fehlertext}\n\n{'='*60}\n\n"
                f"Konsistenz Kernbegriffe (KI):\n{konsistenz_ki}\n\n"
                f"{'='*60}\n\nKI-Analyse:\n{ki_ergebnis}\n\n"
                f"{'='*60}\n\nFehlende oder doppelte Abschnitte (KI):\n{abschnitts_check}\n"
            )
            root.after(0, lambda: zeige_ergebnisfenster("Kombinierte Prüfung", gesamt))

            # PDF-Export automatisch nach Prüfung
            exportiere_bericht_pdf(matches, ki_ergebnis)
            root.after(0, lambda: update_status("PDF-Fehlerbericht für Übersetzer erstellt!", color="#2e8b57"))
        finally:
            progress.destroy()
    threading.Thread(target=task).start()

def umfassende_pruefung():
    win, update = show_progressbar("Umfassende Prüfung läuft...", max_value=100)
    def task():
        try:
            pfad_ausgang = ausgangsdatei.get()
            pfad_uebersetzung = uebersetzungsdatei.get()
            if not pfad_ausgang or not pfad_uebersetzung:
                messagebox.showwarning("Fehler", "Bitte beide Dateien auswählen!")
                return
            try:
                text_ausgang = lese_datei(pfad_ausgang)
                text_uebersetzung = lese_datei(pfad_uebersetzung)
            except Exception as e:
                messagebox.showerror("Fehler", f"Dateien konnten nicht gelesen werden:\n{e}")
                return

            # Schritt 1
            konsistenz_ki = ki_konsistenzpruefung(text_ausgang, text_uebersetzung)
            update(0.15)
            # Schritt 2
            ki_ergebnis = ki_qualitaetspruefung_mit_vergleich(text_ausgang, text_uebersetzung)
            update(0.30)
            # Schritt 3
            zusammenfassung = ki_automatische_zusammenfassung(text_ausgang, text_uebersetzung)
            update(0.45)
            # Schritt 4
            glossar = ["Begriff1", "Begriff2"]
            glossar_check = ki_glossar_check(text_ausgang, text_uebersetzung, glossar)
            update(0.60)
            # Schritt 5
            tonfall = ki_tonfall_pruefung(text_ausgang, text_uebersetzung)
            update(0.75)
            # Schritt 6
            kulturell = ki_kulturelle_anpassungen(text_ausgang, text_uebersetzung)
            update(0.90)
            # Schritt 7
            stilistische_hinweise = ki_stilistische_hinweise(text_ausgang, text_uebersetzung)
            update(1.0)

            gesamt = (
                "Umfassende Prüfung (KI & Konsistenz):\n\n"
                f"--- Konsistenz Kernbegriffe (KI):\n{konsistenz_ki}\n\n"
                f"--- KI-Analyse ---\n{ki_ergebnis}\n\n"
                f"--- Automatische Zusammenfassung ---\n{zusammenfassung}\n\n"
                f"--- Glossar-Check ---\n{glossar_check}\n\n"
                f"--- Tonfall-/Register-Prüfung ---\n{tonfall}\n\n"
                f"--- Kulturelle Anpassungen ---\n{kulturell}\n\n"
                f"--- Stilistische Hinweise ---\n{stilistische_hinweise}\n"
            )
            root.after(0, lambda: zeige_ergebnisfenster("Umfassende Prüfung", gesamt))
            exportiere_umfassende_pruefung_pdf(konsistenz_ki, ki_ergebnis, zusammenfassung, glossar_check, tonfall)
            root.after(0, lambda: update_status("Umfassender KI-Bericht exportiert!", color="#1e90ff"))
        finally:
            win.destroy()
    threading.Thread(target=task).start()

# ----- KI-Funktionen -----
# Lade das deutsche spaCy-Modell einmal beim Start
nlp_de = spacy.load("de_core_news_sm")

def finde_kernbegriffe(text):
    """Extrahiert Eigennamen (Personen, Organisationen, Orte) aus dem Text."""
    doc = nlp_de(text)
    begriffe = set()
    for ent in doc.ents:
        if ent.label_ in ("PER", "ORG", "LOC", "MISC"):
            begriffe.add(ent.text)
    return begriffe

def pruefe_kernbegriffe_konsistenz(original, uebersetzung, schwelle=85):
    """Prüft, ob Kernbegriffe aus dem Original konsistent in der Übersetzung vorkommen (mit Fuzzy-Matching)."""
    kernbegriffe = finde_kernbegriffe(original)
    fehler = []
    uebersetzer_worte = set(uebersetzung.split())
    for begriff in kernbegriffe:
        # Fuzzy-Matching: Gibt es ein sehr ähnliches Wort in der Übersetzung?
        gefunden = False
        for wort in uebersetzer_worte:
            if fuzz.ratio(begriff.lower(), wort.lower()) >= schwelle:
                gefunden = True
                break
        if not gefunden:
            fehler.append(f"Kernbegriff '{begriff}' fehlt oder wurde stark verändert.")
    return fehler

def ki_qualitaetspruefung(text, prompt=None):
    if prompt is None:
        prompt = (
            "Bewerte die Übersetzungsqualität und nenne Fehler. "
            "Achte besonders auf Bedeutungsunterschiede, wie z.B. Zeitangaben (20:00 Uhr vs. 8 pm), Maßeinheiten, Namen, Zahlen, Datumsformate usw. "
            "Gib konkrete Beispiele, falls solche Unterschiede vorkommen."
        )
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': text}
        ]
    )
    return response['message']['content']

def ki_qualitaetspruefung_mit_vergleich(original, uebersetzung, prompt=None):
    if prompt is None:
        prompt = (
            "Vergleiche den folgenden Ausgangstext mit der Übersetzung. "
            "Gib alle Unterschiede in folgender Markdown-Tabelle aus:\n"
            "| Kategorie | Original | Übersetzung | Bemerkung |\n"
            "|-----------|----------|-------------|-----------|\n"
            "Kategorien: Bedeutungsunterschiede, Zahlen, Namen, Maßeinheiten, Datumsformate. "
            "Ignoriere stilistische Unterschiede. "
            "Am Ende bewerte die Übersetzungsqualität in 1-2 Sätzen, aber gehe NICHT auf Stil oder Formulierung ein."
        )
    vergleichstext = (
        f"Ausgangstext:\n{original}\n\n"
        f"Übersetzung:\n{uebersetzung}"
    )
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_konsistenzpruefung(original, uebersetzung, prompt=None):
    if prompt is None:
        prompt = (
            "Vergleiche die im Ausgangstext vorkommenden Eigennamen, Fachbegriffe und Organisationen mit der Übersetzung. "
            "Liste alle Fälle auf, in denen ein Begriff unterschiedlich oder nicht konsistent übersetzt wurde. "
            "Ignoriere grammatikalisch notwendige Anpassungen (z.B. Kasus, Plural), aber melde echte Unterschiede wie z.B. 'Meyer' und 'Müller'. "
            "Gib die Ergebnisse als Liste aus. Wenn alles konsistent ist, schreibe: 'Alle Kernbegriffe wurden konsistent übersetzt.'"
        )
    vergleichstext = (
        f"Ausgangstext:\n{original}\n\n"
        f"Übersetzung:\n{uebersetzung}"
    )
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_automatische_zusammenfassung(original, uebersetzung):
    prompt = (
        "Fasse den folgenden Ausgangstext und die Übersetzung jeweils in 2-3 Sätzen zusammen. "
        "Vergleiche, ob die Kernaussage erhalten bleibt. "
        "Gib am Ende eine kurze Einschätzung, ob die Übersetzung die Hauptaussage korrekt wiedergibt."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_glossar_check(original, uebersetzung, glossar):
    prompt = (
        f"Prüfe, ob die folgenden Glossarbegriffe im Ausgangstext in der Übersetzung korrekt und konsistent verwendet wurden:\n{', '.join(glossar)}. "
        "Melde alle Abweichungen oder Inkonsistenzen."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_tonfall_pruefung(original, uebersetzung):
    prompt = (
        "Analysiere den Tonfall (z.B. höflich, sachlich, locker) im Ausgangstext und in der Übersetzung. "
        "Bewerte, ob der Tonfall in der Übersetzung zum Original passt."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_kulturelle_anpassungen(original, uebersetzung):
    prompt = (
        "Analysiere die Übersetzung im Vergleich zum Ausgangstext auf kulturelle Stolpersteine, "
        "Missverständnisse oder unpassende Formulierungen für das Zielpublikum. "
        "Weise auf mögliche kulturelle Unterschiede, Tabus oder problematische Begriffe hin. "
        "Gib konkrete Beispiele, falls vorhanden."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_stilistische_hinweise(original, uebersetzung):
    prompt = (
        "Analysiere die Übersetzung auf stilistische Schwächen. "
        "Gib Hinweise zu zu langen Sätzen, passiven Formulierungen, unnötigen Füllwörtern oder anderen stilistischen Verbesserungen. "
        "Gib konkrete Beispiele aus der Übersetzung."
    )
    vergleichstext = f"Übersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_korrekturvorschlaege(original, uebersetzung):
    prompt = (
        "Lies die Übersetzung und mache konkrete Korrekturvorschläge für alle gefundenen Fehler. "
        "Gib die fehlerhaften Stellen und jeweils einen Verbesserungsvorschlag an. "
        "Nutze eine übersichtliche Liste."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_vergleich_referenz(original, uebersetzung, referenz):
    prompt = (
        "Vergleiche die Übersetzung mit einer vorhandenen Referenzübersetzung. "
        "Liste alle Unterschiede auf, insbesondere bei Fachbegriffen, Stil und Inhalt. "
        "Gib konkrete Beispiele für Abweichungen."
    )
    vergleichstext = (
        f"Ausgangstext:\n{original}\n\n"
        f"Übersetzung:\n{uebersetzung}\n\n"
        f"Referenzübersetzung:\n{referenz}"
    )
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

def ki_abschnitts_check(original, uebersetzung):
    prompt = (
        "Vergleiche den Ausgangstext mit der Übersetzung. "
        "Erkenne und liste alle Abschnitte, Sätze oder Sinnabschnitte auf, die in der Übersetzung fehlen oder doppelt vorkommen. "
        "Gib konkrete Beispiele und Zeilennummern, falls möglich."
    )
    vergleichstext = f"Ausgangstext:\n{original}\n\nÜbersetzung:\n{uebersetzung}"
    response = ollama.chat(
        model='llama3',
        messages=[
            {'role': 'system', 'content': prompt},
            {'role': 'user', 'content': vergleichstext}
        ]
    )
    return response['message']['content']

# ----- Export-Funktionen -----
def exportiere_reduziertes_pdf():
    messagebox.showinfo("Export", "PDF (Übersetzerbericht) wurde erstellt.")
    update_status("PDF erfolgreich exportiert!", color="#2e8b57")

def exportiere_score_pdf():
    messagebox.showinfo("Export", "PDF mit Score wurde erstellt.")

def exportiere_ki_pdf(bericht, dateiname="ki_bericht.pdf"):
    try:
        c = canvas.Canvas(dateiname, pagesize=A4)
        c.setFont("Helvetica", 12)
        y = 800
        for line in bericht.splitlines():
            c.drawString(40, y, line)
            y -= 15
            if y < 40:
                c.showPage()
                y = 800
        c.save()
        os.startfile(dateiname)
    except Exception as e:
        messagebox.showerror("Exportfehler", f"PDF-Export fehlgeschlagen:\n{e}")

def pdf_export_sortiert(matches, dateiname="checker_score_bericht.pdf"):
    try:
        c = canvas.Canvas(dateiname, pagesize=A4)
        width, height = A4
        y = height - 80

        datum = datetime.now().strftime("%Y-%m-%d")

        # Deckblatt
        try:
            logo = ImageReader("checker_icon.png")
            c.drawImage(logo, 60, height - 150, width=80, height=80, mask='auto')
        except:
            pass

        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(colors.HexColor("#333333"))
        c.drawString(160, height - 100, "Checker – Übersetzungsbericht")

        c.setFont("Helvetica", 12)
        c.setFillColor(colors.black)
        c.drawString(60, height - 180, f"Erstellt am: {datum}")

        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.darkgray)
        c.drawString(60, height - 200, "Fehlerübersicht nach Regeltyp, automatisch erstellt mit dem Checker-Tool.")
        c.showPage()

        # Gruppieren & sortieren
        gruppen = defaultdict(list)
        for m in matches:
            gruppen[m.ruleId].append(m)

        for regel, eintraege in sorted(gruppen.items()):
            beschreibung = REGEL_BESCHREIBUNG.get(regel, eintraege[0].message)

            c.setFont("Helvetica-Bold", 11)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(40, y, f"🔸 {beschreibung}")
            y -= 20

            for m in eintraege:
                if y < 60:
                    c.showPage()
                    y = height - 50

                c.setFont("Courier", 9)
                c.setFillColor(colors.darkgray)
                c.drawString(40, y, f"📍 Kontext: {m.context[:80]}")
                y -= 12

                c.setFillColor(colors.green)
                c.drawString(40, y, f"💡 Vorschlag: {', '.join(m.replacements) if m.replacements else '–'}")
                y -= 20

        c.save()

        # Automatisch öffnen
        if platform.system() == "Windows":
            os.startfile(dateiname)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", dateiname])
        else:
            subprocess.call(["xdg-open", dateiname])

    except Exception as e:
        messagebox.showerror("Exportfehler", f"PDF-Export fehlgeschlagen:\n{e}")

def exportiere_bericht_pdf(matches, ki_text, dateiname="Uebersetzerbericht.pdf"):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    c = canvas.Canvas(dateiname, pagesize=A4)
    width, height = A4
    y = height - 50

    # Logo (optional)
    try:
        logo = ImageReader("checker_icon.png")  # Passe den Pfad ggf. an
        c.drawImage(logo, 50, y - 60, width=60, height=60, mask='auto')
    except Exception:
        pass

    # Überschrift
    c.setFont("Helvetica-Bold", 18)
    c.drawString(120, y, "Übersetzungs-Fehlerbericht")
    y -= 40

    # Kommentar
    c.setFont("Helvetica-Oblique", 11)
    c.setFillColor(colors.darkgray)
    kommentar = kommentar_übersetzer.get() or "-"
    c.drawString(50, y, f"Kommentar: {kommentar}")
    y -= 30

    # Fehlerübersicht nach Regeltyp gruppiert, Duplikate vermeiden
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#333333"))
    c.drawString(50, y, "Gefundene Fehler (gruppiert):")
    y -= 20

    gruppen = defaultdict(list)
    for m in matches:
        gruppen[m.ruleId].append(m)

    if not matches:
        c.setFont("Helvetica", 11)
        c.setFillColor(colors.red)
        c.drawString(60, y, "Keine Fehler gefunden.")
        y -= 15
    else:
        for regel, eintraege in sorted(gruppen.items()):
            beschreibung = REGEL_BESCHREIBUNG.get(regel, eintraege[0].message)
            c.setFont("Helvetica-Bold", 12)
            c.setFillColor(colors.HexColor("#333333"))
            c.drawString(60, y, f"🔸 {beschreibung}")
            y -= 16
            c.setFont("Helvetica", 10)
            c.setFillColor(colors.red)
            seen = set()
            for m in eintraege:
                key = (m.context[:80], tuple(m.replacements))
                if key in seen:
                    continue
                seen.add(key)
                fehlertext = f"- Kontext: {m.context[:80]}"
                vorschlag = f"  Vorschlag: {', '.join(m.replacements) if m.replacements else '–'}"
                c.drawString(70, y, fehlertext)
                y -= 12
                c.setFillColor(colors.green)
                c.drawString(90, y, vorschlag)
                y -= 14
                c.setFillColor(colors.red)
                if y < 60:
                    c.showPage()
                    y = height - 50
            y -= 6

    y -= 10
    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "KI-Kommentar:")
    y -= 20

    c.setFont("Helvetica", 11)
    for line in ki_text.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    c.save()
    os.startfile(dateiname)

def exportiere_umfassende_pruefung_pdf(konsistenz_ki, ki_ergebnis, zusammenfassung, glossar_check, tonfall, dateiname="Umfassende_Pruefung.pdf"):
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    from reportlab.lib.utils import ImageReader

    c = canvas.Canvas(dateiname, pagesize=A4)
    width, height = A4
    y = height - 50

    # Logo (optional)
    try:
        logo = ImageReader("checker_icon.png")
        c.drawImage(logo, 50, y - 60, width=60, height=60, mask='auto')
    except Exception:
        pass

    c.setFont("Helvetica-Bold", 18)
    c.drawString(120, y, "Umfassende KI-Prüfung")
    y -= 40

    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Konsistenz Kernbegriffe (KI):")
    y -= 20
    for line in konsistenz_ki.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "KI-Analyse:")
    y -= 20
    for line in ki_ergebnis.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Automatische Zusammenfassung:")
    y -= 20
    for line in zusammenfassung.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Glossar-Check:")
    y -= 20
    for line in glossar_check.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Tonfall-/Register-Prüfung:")
    y -= 20
    for line in tonfall.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Kulturelle Anpassungen:")
    y -= 20
    for line in kulturell.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    y -= 10
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y, "Stilistische Hinweise:")
    y -= 20
    for line in stilistische_hinweise.splitlines():
        c.drawString(60, y, line)
        y -= 15
        if y < 60:
            c.showPage()
            y = height - 50

    c.save()
    os.startfile(dateiname)

# ----- UI-Hilfsfunktionen -----
def zeige_emailtext():
    kommentar = kommentar_übersetzer.get().strip()
    text = f"""Betreff: Korrekturbericht zur Übersetzung

Hallo,

anbei finden Sie den automatisierten Korrekturbericht zur letzten Übersetzung.
Bitte prüfen Sie die markierten Abschnitte und überarbeiten Sie diese entsprechend.

Kommentar: {kommentar or '- keine Nachricht -'}

Beste Grüße
{kundenname.get().strip() or 'Ihr Profi Team'}"""
    win = tk.Toplevel(root)
    win.title("E-Mail-Vorschau")
    textfeld = tk.Text(win, width=80, height=20)
    textfeld.insert("1.0", text)
    textfeld.pack(padx=10, pady=10)

def zeige_ergebnisfenster(titel, text):
    win = tk.Toplevel(root)
    win.title(titel)
    textfeld = tk.Text(win, width=80, height=25)
    textfeld.insert("1.0", text)
    textfeld.pack(padx=10, pady=10)

def zeige_ergebnis_im_textfeld(text):
    ergebnis_textfeld.config(state="normal")
    ergebnis_textfeld.delete("1.0", tk.END)
    ergebnis_textfeld.insert("1.0", text)
    ergebnis_textfeld.config(state="disabled")

def zeige_sortierte_fehler(matches):
    ergebnis_textfeld.config(state="normal")
    ergebnis_textfeld.delete("1.0", tk.END)

    ergebnis_textfeld.tag_config("regel", foreground="#FFA500", font=("Arial", 10, "bold"))
    ergebnis_textfeld.tag_config("kontext", foreground="#CCCCCC")
    ergebnis_textfeld.tag_config("vorschlag", foreground="#80ff80")
    ergebnis_textfeld.tag_config("heading", foreground="#00BFFF", font=("Arial", 11, "bold"))
    ergebnis_textfeld.tag_config("diff", background="#ffcccc")

    gruppen = defaultdict(list)
    for match in matches:
        gruppen[match.ruleId].append(match)

    def zeige_detailfenster(regel, eintraege):
        if regel in offene_fenster:
            try:
                offene_fenster[regel].lift()
                return
            except:
                del offene_fenster[regel]

        win = tk.Toplevel(root)
        win.title(f"{REGEL_BESCHREIBUNG.get(regel, regel)} – Details")
        win.geometry("600x400")
        offene_fenster[regel] = win

        textfeld = tk.Text(win, wrap="word", font=("Arial", 10), bg="#1e1e1e", fg="#eaeaea", insertbackground="white")
        textfeld.pack(expand=True, fill="both", padx=10, pady=10)

        textfeld.tag_config("kontext", foreground="#CCCCCC")
        textfeld.tag_config("vorschlag", foreground="#80ff80")

        for i, m in enumerate(eintraege, 1):
            textfeld.insert("end", f"{i}. 📍 Kontext: „", "standard")
            textfeld.insert("end", m.context, "kontext")
            textfeld.insert("end", "“\n   💡 Vorschlag: ", "standard")
            textfeld.insert("end", ", ".join(m.replacements) if m.replacements else "–", "vorschlag")
            textfeld.insert("end", "\n\n")

        textfeld.config(state="disabled")

    for regel, regel_matches in sorted(gruppen.items()):
        beschreibung = REGEL_BESCHREIBUNG.get(regel, regel_matches[0].message)
        btn = tk.Button(
            ergebnis_textfeld,
            text=f"🔽 {beschreibung}",
            bg="#444", fg="white",
            font=("Arial", 10, "bold"),
            command=lambda r=regel, m=regel_matches: zeige_detailfenster(r, m)
        )
        ergebnis_textfeld.window_create("end", window=btn)
        ergebnis_textfeld.insert("end", "\n\n")

    ergebnis_textfeld.config(state="disabled")

def speichere_profil():
    profile = {
        "kunde": kundenname.get(),
        "ordner": kundenordner_pfad.get(),
        "kommentar": kommentar_übersetzer.get()
    }
    with open("profil.json", "w", encoding="utf-8") as f:
        import json
        json.dump(profile, f, indent=2)
    messagebox.showinfo("Gespeichert", "Profil wurde gespeichert.")

def speichere_letzte_werte():
    daten = {
        "ausgangsdatei": ausgangsdatei.get(),
        "uebersetzungsdatei": uebersetzungsdatei.get()
    }
    with open("letzte_werte.json", "w", encoding="utf-8") as f:
        json.dump(daten, f)

def lade_letzte_werte():
    try:
        with open("letzte_werte.json", "r", encoding="utf-8") as f:
            daten = json.load(f)
            ausgangsdatei.set(daten.get("ausgangsdatei", ""))
            uebersetzungsdatei.set(daten.get("uebersetzungsdatei", ""))
    except:
        pass

offene_fenster = {}

def öffne_ordner():
    pfad = kundenordner_pfad.get()
    if not pfad or not os.path.isdir(pfad):
        messagebox.showwarning("Fehler", "Kein gültiger Ordnerpfad angegeben!")
        return
    try:
        if platform.system() == "Windows":
            os.startfile(pfad)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", pfad])
        else:
            subprocess.Popen(["xdg-open", pfad])
    except Exception as e:
        messagebox.showerror("Fehler", f"Ordner konnte nicht geöffnet werden:\n{e}")

def vergleich_starten():
    pruefe_uebersetzungsvergleich()

# ----- Icons und Toolleiste -----
icons = lade_icons(MODE, master=root)

file_frame = ctk.CTkFrame(root, corner_radius=15)
file_frame.pack(pady=20, padx=30, fill="x")

headline = ctk.CTkLabel(
    file_frame,
    text="📂 Dateien auswählen",
    font=("Segoe UI", 20, "bold"),
    text_color=PRIMARY,
    bg_color=BG,
    anchor="center",
    justify="center"
).pack(pady=(10, 18))

ctk.CTkFrame(file_frame, height=2, fg_color=PRIMARY).pack(fill="x", padx=40, pady=(0, 18))

# Container für die drei Buttons nebeneinander
btn_row = ctk.CTkFrame(file_frame, fg_color="transparent")
btn_row.pack(pady=6)

# Ausgangsdatei
ausgang_frame = ctk.CTkFrame(btn_row, fg_color="transparent")
ausgang_frame.pack(side="left", padx=18)
btn_ausgang = ctk.CTkButton(
    ausgang_frame,
    text="Ausgangsdatei wählen",
    command=lade_ausgangsdatei,
    fg_color=PRIMARY,
    hover_color=PRIMARY_HOVER,
    text_color="white"
)
btn_ausgang.pack()
Tooltip(btn_ausgang, "Wähle die Ausgangsdatei (Originaltext) aus.")
label_ausgang = ctk.CTkLabel(ausgang_frame, text="", font=("Segoe UI", 11), text_color="#b0bec5")
label_ausgang.pack(pady=(4,0))
# Übersetzungsdatei
uebersetzung_frame = ctk.CTkFrame(btn_row, fg_color="transparent")
uebersetzung_frame.pack(side="left", padx=18)
btn_uebersetzung = ctk.CTkButton(
    uebersetzung_frame,
    text="Übersetzungsdatei wählen",
    command=lade_uebersetzungsdatei,
    fg_color=PRIMARY,
    hover_color=PRIMARY_HOVER,
    text_color="white"  # <-- geändert!
)
btn_uebersetzung.pack()
Tooltip(btn_uebersetzung, "Wähle die Übersetzungsdatei (Zieltext) aus.")
label_uebersetzung = ctk.CTkLabel(uebersetzung_frame, text="", font=("Segoe UI", 11), text_color="#b0bec5")
label_uebersetzung.pack(pady=(4,0))

# Referenzübersetzung
referenz_frame = ctk.CTkFrame(btn_row, fg_color="transparent")
referenz_frame.pack(side="left", padx=18)

btn_referenz = ctk.CTkButton(
    referenz_frame,
    text="Referenzübersetzung wählen",
    command=lade_referenzdatei,
    fg_color=PRIMARY,
    hover_color=PRIMARY_HOVER,
    text_color="white"  # <-- geändert!
)
btn_referenz.pack()
Tooltip(btn_referenz, "Optional: Wähle eine Referenzübersetzung zum Vergleich aus.")
label_referenz = ctk.CTkLabel(referenz_frame, text="", font=("Segoe UI", 11), text_color="#b0bec5")
label_referenz.pack(pady=(4,0))

# Überschrift für Prüfungen
pruef_headline = ctk.CTkLabel(
    root,
    text="📝 Prüfung",
    font=("Segoe UI", 20, "bold"),
    text_color=PRIMARY,
    bg_color=BG,
    anchor="center",
    justify="center"
)
pruef_headline.pack(pady=(10, 8))

# Prüfungs-Buttons
pruef_frame = ctk.CTkFrame(root, corner_radius=15)
pruef_frame.pack(pady=10, padx=30, fill="x")

pruefung_btn = ctk.CTkButton(
    pruef_frame,
    text="Übersetzung prüfen",
    command=pruefe_uebersetzung_threaded,
    fg_color=PRIMARY,
    hover_color=PRIMARY_HOVER,
    text_color="white",
    corner_radius=8,
    width=180,
    height=40
)
pruefung_btn.pack(pady=10)
Tooltip(pruefung_btn, "Startet die automatische Prüfung der Übersetzung.")

umfassend_btn = ctk.CTkButton(
    pruef_frame,
    text="Umfassende Prüfung",
    command=umfassende_pruefung,
    fg_color=PRIMARY,           # <-- jetzt blau!
    hover_color=PRIMARY_HOVER,  # <-- jetzt blau!
    text_color="white",
    corner_radius=8,
    width=180,
    height=40
)
umfassend_btn.pack(pady=8)
Tooltip(umfassend_btn, "Startet die umfassende KI-Prüfung mit zusätzlichen Checks.")

toolbar_buttons = [
    {"text": "PDF Export", "command": exportiere_reduziertes_pdf},
    {"text": "Score Export", "command": exportiere_score_pdf},
    {"text": "Mail", "command": zeige_emailtext},
]

toolbar_frame = ctk.CTkFrame(root, corner_radius=10)
toolbar_frame.pack(pady=(10, 0), padx=30, fill="x")
for btn in toolbar_buttons:
    b = ctk.CTkButton(
        toolbar_frame,
        text=btn["text"],
        command=btn["command"],
        fg_color=PRIMARY,
        text_color="white",  # <-- geändert!
        hover_color=PRIMARY_HOVER,
        corner_radius=8,
        width=130,
        height=36
    )
    b.pack(side="left", padx=4, pady=4)
    Tooltip(b, f"{btn['text']} ausführen")

def toggle_theme():
    pass  # Hier kannst du später die Theme-Umschaltung implementieren

# Theme-Umschalter direkt unter der Toolbar
theme_switch_frame = ctk.CTkFrame(root, fg_color="transparent")
theme_switch_frame.pack(fill="x", padx=10, pady=(10, 0))

theme_label = ctk.CTkLabel(theme_switch_frame, text="Theme:", font=("Segoe UI", 12, "bold"), text_color=FG)
theme_label.pack(side="left", padx=(4, 2))

theme_btn = ctk.CTkSwitch(
    theme_switch_frame,
    text="Dark-Mode",
    command=toggle_theme,
    onvalue="dark",
    offvalue="light"
)
theme_btn.pack(side="left", padx=4)
theme_btn.deselect()  # Startet im Light-Mode= ctk.CTkLabel(
    root,
def show_progress(text="Bitte warten..."):    text="📝 Prüfung",

root.mainloop()    return win    # Gib das Fenster zurück, damit .destroy() später funktioniert    win.update()    label.pack()    label = tk.Label(win, text=text, padx=30, pady=20)    win.title("Bitte warten")    win = tk.Toplevel(root)    # Dummy-Dialog, der einfach ein Fenster anzeigt    font=("Segoe UI", 20, "bold"),
    text_color=PRIMARY,
    bg_color=BG,
    anchor="center",
    justify="center"
)
pruef_headline.pack(pady=(10, 8))

root.mainloop()

