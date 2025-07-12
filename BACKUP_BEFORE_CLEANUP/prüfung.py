import threading
import time
import language_tool_python
from collections import defaultdict
from rapidfuzz import fuzz
import spacy

# This file's own LanguageTool instance.
# Consider refactoring to use tool_config.py for consistency if this module
# is tightly integrated with checker_app.py.
# For now, keeping its independent tool management.
lt_tool_pruefung = None 

def finde_kernbegriffe(text, language_model=None): 
    if language_model is None:
        print("⚠️ [prüfung.py] finde_kernbegriffe: Kein spaCy language_model übergeben. Funktion gibt leeres Set zurück.")
        return set()
    doc = language_model(text)
    begriffe = set()
    for ent in doc.ents:
        if ent.label_ in ("PER", "ORG", "LOC", "MISC"):
            begriffe.add(ent.text)
    return begriffe

def pruefe_kernbegriffe_konsistenz(original, uebersetzung, schwelle=85, language_model_original=None, language_model_translation=None):
    # Allow passing models for original and translation language
    # For simplicity, if not passed, uses the module-level nlp_de (German specific) for original
    kernbegriffe = finde_kernbegriffe(original, language_model=language_model_original)
    fehler = []
    uebersetzer_worte = set(uebersetzung.split())
    for begriff in kernbegriffe:
        gefunden = False
        for wort in uebersetzer_worte:
            if fuzz.ratio(begriff.lower(), wort.lower()) >= schwelle:
                gefunden = True
                break
        if not gefunden:
            fehler.append(f"Kernbegriff '{begriff}' fehlt oder wurde stark verändert.")
    return fehler

def get_language_tool(language_code='de-DE'): # This is prüfung.py's own getter
    global lt_tool_pruefung 
    try:
        if lt_tool_pruefung is None or lt_tool_pruefung.language != language_code:
            print(f"ℹ️ [prüfung.py] Initialisiere LanguageTool für {language_code}...")
            lt_tool_pruefung = language_tool_python.LanguageTool(language_code)
            print(f"✅ [prüfung.py] LanguageTool für {language_code} initialisiert.")
    except Exception as e:
        print(f"⚠️ [prüfung.py] Fehler bei der Initialisierung von LanguageTool für {language_code}: {e}")
        print("   LanguageTool-basierte Prüfungen sind möglicherweise nicht verfügbar.")
        print("   Stellen Sie sicher, dass LanguageTool korrekt installiert ist und Java verfügbar ist.")
        return None
    return lt_tool_pruefung

def pruefe_uebersetzung():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def pruefe_uebersetzung_threaded():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def pruefe_uebersetzungsvergleich():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def pruefe_ki_qualitaet():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def pruefe_alle():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def umfassende_pruefung():
    # Dummy-Implementierung, da GUI-Elemente nicht bekannt
    pass

def pruefe_texte(path_original, path_uebersetzung, options, update_progress=None):
    """
    Führt alle gewählten Prüfungen auf der Übersetzung durch und gibt die Fehler strukturiert zurück.
    options: dict mit bools für grammatik, rechtschreibung, lesbarkeit, terminologie, stil, qualitaet, konsistenz_pruefen
    """
    import os
    import re
    from ki_module import (
        ki_qualitaetspruefung_mit_vergleich, ki_konsistenzpruefung, ki_stilistische_hinweise_pruefung,
        ki_qualitaetspruefung, ki_zusammenfassung, ki_glossa_check
    )
    
    def read_text(path):
        with open(path, encoding="utf-8") as f:
            return f.read()
    
    text_a = read_text(path_original)
    text_b = read_text(path_uebersetzung)
    results = {"fehler": []}
    total = sum([options.get(k, False) for k in ["grammatik","rechtschreibung","lesbarkeit","terminologie","stil","qualitaet","konsistenz_pruefen"]])
    done = 0
      # Grammatikprüfung (nur Übersetzung)
    if options.get("grammatik"):
        # Get the target language code from options, or detect it from the text
        if options.get("target_lang_code"):
            target_lang_code = options.get("target_lang_code")
        else:
            # If no language code is provided, try to detect it
            try:
                from language_detection import detect_language
                target_lang_code = detect_language(text_b)
                print(f"✓ [prüfung.py] Detected language: {target_lang_code}")
            except ImportError:
                # Fall back to default if language detection module is not available
                target_lang_code = "de-DE" 
                print(f"⚠️ [prüfung.py] Language detection module not available, using default: {target_lang_code}")
        
        tool = get_language_tool(language_code=target_lang_code)
        if tool:
            matches = tool.check(text_b)
            for match in matches: # Consider removing [:10] to get all errors or make it configurable
                results["fehler"].append({
                    "beschreibung": match.message,
                    "schweregrad": "kritisch" if 'GRAMMAR' in str(match.category) else ("mittel" if 'STYLE' in str(match.category) else "gering"),
                    "kategorie": "Grammatik",
                    "zeile": match.fromy + 1 if hasattr(match, 'fromy') else 'N/A',
                    "kontext": match.context,
                    "kontext_offset": match.contextoffset if hasattr(match, 'contextoffset') else match.offset, # offset is an alias for contextoffset
                    "fehlerlaenge": match.errorlength,
                    "regel_id": match.ruleId,
                    "problem_typ": match.ruleIssueType if hasattr(match, 'ruleIssueType') else 'Unbekannt',
                    "empfehlung": match.replacements
                })
        done += 1
        if update_progress: update_progress(done/total*100)    # Rechtschreibung (nur Übersetzung)
    if options.get("rechtschreibung"):
        # Get the target language code from options, or detect it from the text
        if options.get("target_lang_code"):
            target_lang_code = options.get("target_lang_code")
        else:
            # If no language code is provided, try to detect it
            try:
                from language_detection import detect_language
                target_lang_code = detect_language(text_b)
                print(f"✓ [prüfung.py] Detected language: {target_lang_code}")
            except ImportError:
                # Fall back to default if language detection module is not available
                target_lang_code = "de-DE" 
                print(f"⚠️ [prüfung.py] Language detection module not available, using default: {target_lang_code}")
        
        tool = get_language_tool(language_code=target_lang_code)
        if tool:
            matches = tool.check(text_b)
            for match in matches: # Consider removing [:10] to get all errors or make it configurable
                # Filter for actual spelling errors, LanguageTool often bundles more under 'TYPOS' ruleId
                if 'SPELLING' in match.category.upper() or 'TYPO' in match.ruleId.upper() or 'MORFOLOGIER' in match.ruleId.upper(): # Adjusted for broader typo catching
                    results["fehler"].append({
                        "beschreibung": match.message,
                        "schweregrad": "mittel",
                        "kategorie": "Rechtschreibung",
                        "zeile": match.fromy + 1 if hasattr(match, 'fromy') else 'N/A',
                        "kontext": match.context,
                        "kontext_offset": match.contextoffset if hasattr(match, 'contextoffset') else match.offset,
                        "fehlerlaenge": match.errorlength,
                        "regel_id": match.ruleId,
                        "problem_typ": match.ruleIssueType if hasattr(match, 'ruleIssueType') else 'Rechtschreibfehler',
                        "empfehlung": match.replacements
                    })
        done += 1
        if update_progress: update_progress(done/total*100)
    # Lesbarkeit (nur Übersetzung)
    if options.get("lesbarkeit"):
        satzlaenge = [len(s.split()) for s in re.split(r'[.!?]', text_b) if s.strip()]
        avg = sum(satzlaenge)/len(satzlaenge) if satzlaenge else 0
        if avg > 25:
            results["fehler"].append({
                "beschreibung": f"Durchschnittliche Satzlänge ist hoch: {avg:.1f} Wörter",
                "schweregrad": "mittel",
                "kategorie": "Lesbarkeit",
                "zeile": 1,
                "empfehlung": "Kürzere Sätze verwenden"
            })
        done += 1
        if update_progress: update_progress(done/total*100)
    # Terminologie (beide Texte, aber Fokus auf Übersetzung)
    if options.get("terminologie"):
        # Hier kann ein KI-Check oder ein Glossar-Check erfolgen
        ki_result = ki_konsistenzpruefung(text_a, text_b)
        if ki_result and "konsistent" not in ki_result.lower():
            results["fehler"].append({
                "beschreibung": ki_result,
                "schweregrad": "kritisch",
                "kategorie": "Terminologie",
                "zeile": 1,
                "empfehlung": "Konsistenz prüfen"
            })
        done += 1
        if update_progress: update_progress(done/total*100)
    # Stil (nur Übersetzung)
    if options.get("stil"):
        stil_result = ki_stilistische_hinweise_pruefung(text_b)
        if stil_result and "keine stilistischen schwächen" not in stil_result.lower():
            results["fehler"].append({
                "beschreibung": stil_result,
                "schweregrad": "mittel",
                "kategorie": "Stil",
                "zeile": 1,
                "empfehlung": "Stil verbessern"
            })
        done += 1
        if update_progress: update_progress(done/total*100)
    # Qualität (Vergleich, aber Bewertung der Übersetzung)
    if options.get("qualitaet"):
        qual_result = ki_qualitaetspruefung_mit_vergleich(text_a, text_b)
        if qual_result and "keine fehler" not in qual_result.lower():
            results["fehler"].append({
                "beschreibung": qual_result,
                "schweregrad": "kritisch",
                "kategorie": "Qualität",
                "zeile": 1,
                "empfehlung": "Qualität prüfen"
            })
        done += 1
        if update_progress: update_progress(done/total*100)
    # Konsistenzprüfung (Kernbegriffe, beide Texte)
    if options.get("konsistenz_pruefen"):
        kernfehler = pruefe_kernbegriffe_konsistenz(text_a, text_b)
        for f in kernfehler:
            results["fehler"].append({
                "beschreibung": f,
                "schweregrad": "kritisch",
                "kategorie": "Kernbegriffs-Konsistenz",
                "zeile": 1,
                "empfehlung": "Kernbegriff prüfen"
            })
        done += 1
        if update_progress: update_progress(done/total*100)
    return results
