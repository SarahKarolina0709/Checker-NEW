import ollama
from ollama._types import ResponseError, RequestError
import language_tool_python
import os
import requests
from threading import Thread
from queue import Queue

# Globale Variable für den Timeout-Zähler
ollama_timeout_counter = 0

# ----- PROMPT DICTIONARIES -----
# Structure: PROMPT_DICT_<FUNCTION_NAME> = { "lang_code": { "fachgebiet": { "pruefstufe": "prompt_text" } } }

DEFAULT_LANG = "de-DE"
FALLBACK_LANG = "en-US"
DEFAULT_FACHGEBIET = "Allgemein" # Default subject area if specific one not found

PROMPTS_QUALITAETS = {
    "de-DE": {
        "Allgemein": {
            "v1": """Gib deine Ergebnisse als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der den Fehler enthält.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine kurze, klare Erklärung des Fehlers.
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.
---
Aufgabenstellung: Bewerte die Übersetzungsqualität des ZIELTEXTS. Achte besonders auf Bedeutungsunterschiede, falsche Zahlen, Namen, Maßeinheiten, Datumsformate und sinnentstellende Grammatikfehler. Der Ausgangstext dient nur als Referenz und soll nicht geprüft werden.""",
            "v2": "Bewerte die Übersetzungsqualität und nenne GROBE FEHLER. Achte besonders auf SINNFEHLER, falsche TERMINOLOGIE, AUSLASSUNGEN wichtiger Informationen. Ignoriere kleinere Stilprobleme und leichte Grammatikfehler. Gib konkrete Beispiele für die groben Fehler.",
            "v3": "Bewerte die Übersetzungsqualität STRENG FOKUSSIERT auf KRITISCHE FEHLER. Ignoriere Stil, Grammatik (außer sinnentstellend), Wortwahl (außer klar falsch). Melde NUR: Falsche Zahlen, vertauschte Namen, falsche Maßeinheiten, komplett gegenteilige Bedeutung. Gib konkrete Beispiele NUR für diese kritischen Fehler."
        },
        "Technik": {
            "v1": """Gib deine Ergebnisse als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der den Fehler enthält.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine kurze, klare Erklärung des Fehlers.
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.
---
Aufgabenstellung: [Technik] Bewerte die technische Übersetzungsqualität. Fokus auf korrekte Fachtermini, Konsistenz technischer Bezeichnungen und klare Verständlichkeit technischer Anweisungen.""",
            "v2": "[Technik] Bewerte auf GROBE FEHLER in der technischen Übersetzung. Sind Fachbegriffe falsch? Gibt es sinnentstellende Fehler in technischen Beschreibungen? Auslassungen?",
            "v3": "[Technik] Bewerte STRENG auf KRITISCHE FEHLER in der technischen Übersetzung. Falsche Maßeinheiten, vertauschte Komponentenbezeichnungen, sicherheitsrelevante Fehlübersetzungen."
        }
        # Add other Fachgebiete for de-DE here if needed
    },
    "en-US": {
        "Allgemein": {
            "v1": """Return your results as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that contains the error.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": A short, clear explanation of the error.
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.
---
Task: Evaluate the translation quality of the TARGET TEXT. Pay close attention to differences in meaning, incorrect numbers, names, units of measurement, date formats, and grammar errors that distort meaning. The source text is for reference only and should not be checked.""",
            "v2": "Evaluate the translation quality and list MAJOR ERRORS. Focus on MEANING ERRORS, incorrect TERMINOLOGY, OMISSIONS of important information. Ignore minor style issues and slight grammatical errors. Provide specific examples of major errors.",
            "v3": "Evaluate the translation quality STRICTLY FOCUSED on CRITICAL ERRORS. Ignore style, grammar (unless it distorts meaning), word choice (unless clearly wrong). Report ONLY: Incorrect numbers, swapped names, incorrect units of measurement, completely opposite meaning. Provide specific examples ONLY for these critical errors."
        },
        "Technik": {
            "v1": """Return your results as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that contains the error.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": A short, clear explanation of the error.
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.
---
Task: [Technical] Evaluate the technical translation quality. Focus on correct technical terms, consistency of technical designations, and clear understanding of technical instructions.""",
            "v2": "[Technical] Evaluate for MAJOR ERRORS in the technical translation. Are technical terms incorrect? Are there meaning-distorting errors in technical descriptions? Omissions?",
            "v3": "[Technical] Evaluate STRICTLY for CRITICAL ERRORS in the technical translation. Incorrect units of measurement, swapped component names, safety-critical mistranslations."
        }
        # Add other Fachgebiete for en-US here if needed
    }
}

PROMPTS_QUALITAETS_VERGLEICH = {
    "de-DE": {
        "Allgemein": {
            "v1": """Vergleiche den Ausgangstext mit der Übersetzung. Gib alle gefundenen signifikanten Unterschiede als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der den Fehler enthält.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine kurze, klare Erklärung des Fehlers, die auch den entsprechenden Teil aus dem AUSGANGSTEXT enthält.
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.
---
Aufgabenstellung: Vergleiche Ausgangstext und Übersetzung. Konzentriere dich auf Unterschiede in Bedeutung, Zahlen, Namen, Maßeinheiten und Datumsformaten. Ignoriere rein stilistische Unterschiede.""",
            "v2": "Vergleiche Ausgangstext und Übersetzung und identifiziere GROBE UNTERSCHIEDE. Gib alle Unterschiede in folgender Markdown-Tabelle aus:\\n| Kategorie | Original | Übersetzung | Bemerkung |\\n|-----------|----------|-------------|-----------|\\nKategorien: Bedeutungsunterschiede, Terminologie, Auslassungen, Zahlen, Namen, Maßeinheiten, Datumsformate. Ignoriere kleinere stilistische Unterschiede und leichte Grammatikfehler. Am Ende bewerte die Übersetzungsqualität bzgl. grober Fehler in 1-2 Sätzen.",
            "v3": "Vergleiche Ausgangstext und Übersetzung STRENG FOKUSSIERT auf KRITISCHE UNTERSCHIEDE. Ignoriere Stil, Grammatik (außer sinnentstellend), Wortwahl (außer klar falsch). Gib NUR Unterschiede in folgender Markdown-Tabelle aus:\\n| Kategorie | Original | Übersetzung | Bemerkung |\\n|-----------|----------|-------------|-----------|\\nKategorien NUR: Zahlen, Namen, Maßeinheiten, Datumsformate, krasse Bedeutungsänderung. Am Ende bewerte kurz, ob KRITISCHE Fehler vorliegen."
        },
        "Technik": { 
            "v1": """[Technik] Vergleiche den technischen Ausgangstext mit der Übersetzung. Gib alle gefundenen signifikanten Unterschiede als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der den Fehler enthält.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine kurze, klare Erklärung des Fehlers, die auch den entsprechenden Teil aus dem AUSGANGSTEXT enthält.
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.
---
Aufgabenstellung: Vergleiche Ausgangstext und Übersetzung. Konzentriere dich auf Unterschiede in technischen Begriffen, Zahlen, Maßeinheiten und Konsistenz technischer Spezifikationen.""",
            "v2": "[Technik] Vergleiche Ausgangstext und Übersetzung und identifiziere GROBE technische UNTERSCHIEDE. Fokus auf falsche Fachtermini, Abweichungen in technischen Daten. Tabelle wie oben.",
            "v3": "[Technik] Vergleiche Ausgangstext und Übersetzung STRENG FOKUSSIERT auf KRITISCHE technische UNTERSCHIEDE. Falsche Werte, Einheiten, sicherheitsrelevante Abweichungen. Tabelle wie oben."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": """Compare the source text with the translation. Return all significant differences found as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that contains the error.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": A short, clear explanation of the error, which also includes the corresponding part from the SOURCE TEXT.
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.
---
Task: Compare the source text and translation. Focus on differences in meaning, numbers, names, units of measurement, and date formats. Ignore purely stylistic differences.""",
            "v2": "Compare the source text and translation and identify MAJOR DIFFERENCES. List all differences in the following Markdown table:\\n| Category | Original | Translation | Remark |\\n|-----------|----------|-------------|-----------|\\nCategories: Differences in meaning, terminology, omissions, numbers, names, units of measurement, date formats. Ignore minor stylistic differences and slight grammatical errors. Finally, assess the translation quality regarding major errors in 1-2 sentences.",
            "v3": "Compare the source text and translation STRICTLY FOCUSED on CRITICAL DIFFERENCES. Ignore style, grammar (unless it distorts meaning), word choice (unless clearly wrong). List ONLY differences in the following Markdown table:\\n| Category | Original | Translation | Remark |\\n|-----------|----------|-------------|-----------|\\nCategories ONLY: Numbers, names, units of measurement, date formats, drastic change in meaning. Finally, briefly assess if CRITICAL errors are present."
        },
        "Technik": {
            "v1": """[Technical] Compare the technical source text with the translation. Return all significant differences found as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that contains the error.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": A short, clear explanation of the error, which also includes the corresponding part from the SOURCE TEXT.
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.
---
Task: Compare the source text and translation. Focus on differences in technical terms, numbers, units of measurement, and consistency of technical specifications.""",
            "v2": "[Technical] Compare for MAJOR technical DIFFERENCES. Focus on incorrect technical terms, deviations in technical data. Table as above.",
            "v3": "[Technical] Compare STRICTLY for CRITICAL technical DIFFERENCES. Incorrect values, units, safety-relevant deviations. Table as above."
        }
    }
}

PROMPTS_TERMINOLOGIE = {
    "de-DE": {
        "Allgemein": {
            "v1": '''Überprüfe die korrekte Übersetzung und konsistente Verwendung von Fachterminologie im Zieltext im Vergleich zum Ausgangstext. Gib alle gefundenen Fehler als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der fehlerhafte oder inkonsistente Begriff aus der ÜBERSETZUNG.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine Erklärung des Fehlers, die den korrekten Begriff aus dem Ausgangstext oder die erwartete Terminologie nennt.
Konzentriere dich besonders auf die folgenden Kernbegriffe, falls angegeben: {key_terms}
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.''',
            "v2": '''Überprüfe GROBE Fehler in der Übersetzung und Verwendung von Fachterminologie im Zieltext.
Konzentriere dich besonders auf die folgenden Kernbegriffe, falls angegeben:
{key_terms}
Melde nur signifikante Abweichungen oder falsche Verwendungen.
Wenn keine spezifischen Kernbegriffe angegeben wurden, führe eine allgemeine, aber fokussierte Terminologieprüfung durch.''',
            "v3": '''Überprüfe KRITISCHE Fehler in der Übersetzung und Verwendung von Fachterminologie im Zieltext.
Konzentriere dich besonders auf die folgenden Kernbegriffe, falls angegeben:
{key_terms}
Melde nur eindeutig falsche oder sinnentstellende Verwendung von Fachtermini.
Wenn keine spezifischen Kernbegriffe angegeben wurden, prüfe auf offensichtlich falsche Terminologie.'''
        },
        "Technik": {
            "v1": '''[Technik] Überprüfe die korrekte technische Übersetzung und konsistente Verwendung von Fachterminologie. Gib alle gefundenen Fehler als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der fehlerhafte oder inkonsistente Begriff aus der ÜBERSETZUNG.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine Erklärung des Fehlers, die den korrekten Begriff aus dem Ausgangstext oder die erwartete Terminologie nennt.
Konzentriere dich besonders auf die folgenden technischen Kernbegriffe, falls angegeben: {key_terms}
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.''',
            "v2": '''[Technik] Überprüfe GROBE Fehler in der technischen Übersetzung und Verwendung von Fachterminologie.
Konzentriere dich besonders auf die folgenden technischen Kernbegriffe, falls angegeben:
{key_terms}
Melde nur signifikante Abweichungen oder falsche Verwendungen technischer Termini.
Wenn keine spezifischen Kernbegriffe angegeben wurden, führe eine allgemeine, aber fokussierte technische Terminologieprüfung durch.''',
            "v3": '''[Technik] Überprüfe KRITISCHE Fehler in der technischen Übersetzung und Verwendung von Fachterminologie.
Konzentriere dich besonders auf die folgenden technischen Kernbegriffe, falls angegeben:
{key_terms}
Melde nur eindeutig falsche oder sinnentstellende Verwendung technischer Fachtermini, die zu Fehlfunktionen oder Missverständnissen führen könnten.
Wenn keine spezifischen Kernbegriffe angegeben wurden, prüfe auf offensichtlich falsche technische Terminologie.'''
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": '''Check the correct translation and consistent use of specialized terminology in the target text compared to the source text. Return all found errors as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The incorrect or inconsistent term from the TRANSLATION.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": An explanation of the error, naming the correct term from the source text or the expected terminology.
Focus particularly on the following key terms, if provided: {key_terms}
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.''',
            "v2": '''Check for MAJOR errors in the translation and use of specialized terminology in the target text.
Focus particularly on the following key terms, if provided:
{key_terms}
Report only significant deviations or incorrect uses.
If no specific key terms were provided, perform a general but focused terminology check.''',
            "v3": '''Check for CRITICAL errors in the translation and use of specialized terminology in the target text.
Focus particularly on the following key terms, if provided:
{key_terms}
Report only clearly incorrect or meaning-distorting uses of specialized terms.
If no specific key terms were provided, check for obviously incorrect terminology.'''
        },
        "Technik": {
            "v1": '''[Technical] Check the correct technical translation and consistent use of specialized terminology. Return all found errors as a JSON array of objects. Each object should represent an error and have the following keys:
- "error_text": The incorrect or inconsistent term from the TRANSLATION.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": An explanation of the error, naming the correct term from the source text or the expected terminology.
Focus particularly on the following technical key terms, if provided: {key_terms}
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array.''',
            "v2": '''[Technical] Check for MAJOR errors in the technical translation and use of specialized terminology.
Focus particularly on the following technical key terms, if provided:
{key_terms}
Report only significant deviations or incorrect uses of technical terms.
If no specific key terms were provided, perform a general but focused technical terminology check.''',
            "v3": '''[Technical] Check for CRITICAL errors in the technical translation and use of specialized terminology.
Focus particularly on the following technical key terms, if provided:
{key_terms}
Report only clearly incorrect or meaning-distorting uses of technical terms that could lead to malfunctions or misunderstandings.
If no specific key terms were provided, check for obviously incorrect technical terminology.'''
        }
    }
}

PROMPTS_KONSISTENZ = {
    "de-DE": {
        "Allgemein": {
            "v1": """Prüfe die Übersetzung auf die konsistente Verwendung von Eigennamen, Fachbegriffen und Organisationen im Vergleich zum Ausgangstext. Gib alle Inkonsistenzen als JSON-Array von Objekten zurück. Jedes Objekt soll eine Inkonsistenz repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der inkonsistente Begriff aus der ÜBERSETZUNG.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem die Inkonsistenz auftritt.
- "explanation": Eine Erklärung der Inkonsistenz, die den Originalbegriff und die verschiedenen verwendeten Varianten in der Übersetzung aufzeigt.
Wenn keine Inkonsistenzen gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.
---
Aufgabenstellung: Finde Begriffe, die im Ausgangstext einheitlich sind, aber in der Übersetzung uneinheitlich wiedergegeben werden.""",
            "v2": "Vergleiche Eigennamen, Fachbegriffe und Organisationen im Ausgangstext mit der Übersetzung. Liste Fälle auf, in denen ein Begriff unterschiedlich oder nicht konsistent übersetzt wurde, was zu Verständnisproblemen führen könnte. Ignoriere rein grammatische Anpassungen und kleinere stilistische Variationen. Wenn alles konsistent ist, schreibe: 'Kernbegriffe wurden weitgehend konsistent übersetzt.'",
            "v3": "Vergleiche Eigennamen, Fachbegriffe, Zahlen und Schlüsselorganisationen im Ausgangstext mit der Übersetzung. Liste NUR KRITISCHE Inkonsistenzen auf (z.B. 'Meyer' vs. 'Müller', '100 EUR' vs. '100 USD', unterschiedliche Produktnamen). Ignoriere grammatische Anpassungen und kleinere stilistische Variationen. Wenn alles kritisch konsistent ist, schreibe: 'Keine kritischen Inkonsistenzen bei Kernbegriffen gefunden.'"
        },
        "Technik": {
            "v1": """[Technik] Prüfe die Konsistenz technischer Fachbegriffe und Produktnamen zwischen Original und Übersetzung. Gib alle Inkonsistenzen als JSON-Array von Objekten zurück. Jedes Objekt soll eine Inkonsistenz repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der inkonsistente Begriff aus der ÜBERSETZUNG.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem die Inkonsistenz auftritt.
- "explanation": Eine Erklärung der Inkonsistenz, die den Originalbegriff und die verschiedenen verwendeten Varianten in der Übersetzung aufzeigt.
Wenn keine Inkonsistenzen gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.""",
            "v2": "[Technik] Prüfe die Konsistenz technischer Fachbegriffe, Produktnamen und spezifischer technischer Bezeichnungen zwischen Original und Übersetzung. Liste GROBE Abweichungen. (v2)", 
            "v3": "[Technik] Prüfe die Konsistenz technischer Fachbegriffe, Produktnamen und spezifischer technischer Bezeichnungen zwischen Original und Übersetzung. Liste KRITISCHE Abweichungen. (v3)", 
            "v4": "[Technik] Prüfe die Konsistenz technischer Fachbegriffe, Produktnamen und spezifischer technischer Bezeichnungen zwischen Original und Übersetzung. Liste KRITISCHE Abweichungen. (v4)", 
            "v5": "[Technik] Prüfe die Konsistenz technischer Fachbegriffe, Produktnamen und spezifischer technischer Bezeichnungen zwischen Original und Übersetzung. Liste ABSOLUT KRITISCHE Abweichungen. (v5)" 
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": """Check the translation for consistent use of proper nouns, technical terms, and organizations compared to the source text. Return all inconsistencies as a JSON array of objects. Each object should represent an inconsistency and have the following keys:
- "error_text": The inconsistent term from the TRANSLATION.
- "context": The full paragraph from the TRANSLATION where the inconsistency occurs.
- "explanation": An explanation of the inconsistency, showing the original term and the different variants used in the translation.
If no inconsistencies are found, return an empty JSON array `[]`. Output ONLY the JSON array.
---
Task: Find terms that are uniform in the source text but are rendered inconsistently in the translation.""",
            "v2": "Compare proper nouns, technical terms, and organizations in the source text with the translation. List cases where a term was translated differently or inconsistently, which could lead to comprehension problems. Ignore purely grammatical adjustments and minor stylistic variations. If everything is consistent, write: 'Key terms have been largely translated consistently.'",
            "v3": "Compare proper nouns, technical terms, numbers, and key organizations in the source text with the translation. List ONLY CRITICAL inconsistencies (e.g., 'Meyer' vs. 'Müller', '100 EUR' vs. '100 USD', different product names). Ignore grammatical adjustments and minor stylistic variations. If all critical aspects are consistent, write: 'No critical inconsistencies found in key terms.'"
        },
        "Technik": {
            "v1": """[Technical] Check the consistency of technical terms and product names between the original and the translation. Return all inconsistencies as a JSON array of objects. Each object should represent an inconsistency and have the following keys:
- "error_text": The inconsistent term from the TRANSLATION.
- "context": The full paragraph from the TRANSLATION where the inconsistency occurs.
- "explanation": An explanation of the inconsistency, showing the original term and the different variants used in the translation.
If no inconsistencies are found, return an empty JSON array `[]`. Output ONLY the JSON array.""",
            "v2": "[Technical] Check the consistency of technical terms, product names, and specific technical designations between original and translation. List MAJOR deviations. (v2)",
            "v3": "[Technical] Check the consistency of technical terms, product names, and specific technical designations between original and translation. List CRITICAL deviations. (v3)",
            "v4": "[Technical] Check the consistency of technical terms, product names, and specific technical designations between original and translation. List CRITICAL deviations. (v4)",
            "v5": "[Technical] Check the consistency of technical terms, product names, and specific technical designations between original and translation. List ABSOLUTELY CRITICAL deviations. (v5)"
        }
    }
}

PROMPTS_ZUSAMMENFASSUNG = {
    "de-DE": {
        "Allgemein": {
            "v1": "Fasse den folgenden Ausgangstext und die Übersetzung jeweils in 2-3 Sätzen zusammen. Vergleiche, ob die Kernaussage erhalten bleibt. Gib am Ende eine kurze Einschätzung, ob die Übersetzung die Hauptaussage korrekt wiedergibt.",
            "v2": "Fasse Ausgangstext und Übersetzung KURZ (1-2 Sätze pro Text) zusammen. Bleibt die Kernaussage erhalten? Kurze Einschätzung.",
            "v3": "Automatische Zusammenfassung ist für Prüfstufe v3 nicht vorgesehen."
        }
        # Fachgebiet specific summaries might not be common, but can be added
    },
    "en-US": {
        "Allgemein": {
            "v1": "Summarize the following source text and translation, each in 2-3 sentences. Compare whether the core message is preserved. At the end, provide a brief assessment of whether the translation correctly conveys the main message.",
            "v2": "Briefly summarize the source text and translation (1-2 sentences per text). Is the core message preserved? Brief assessment.",
            "v3": "Automatic summarization is not intended for check level v3."
        }
    }
}

PROMPTS_GLOSSAR = {
    "de-DE": {
        "Allgemein": {
            "v1": "Prüfe, ob die folgenden Glossarbegriffe im Ausgangstext in der Übersetzung korrekt und konsistent verwendet wurden (detailliert):\\n{glossar_terms}. Melde alle Abweichungen oder Inkonsistenzen.",
            "v2": "Prüfe, ob die folgenden Glossarbegriffe im Ausgangstext in der Übersetzung korrekt und konsistent verwendet wurden (fokussiert auf klare Abweichungen):\\n{glossar_terms}. Melde alle Abweichungen oder Inkonsistenzen.",
            "v3": "Prüfe, ob die folgenden Glossarbegriffe im Ausgangstext in der Übersetzung korrekt und konsistent verwendet wurden (STRENG fokussiert auf KRITISCHE Abweichungen, z.B. falscher Begriff für Schlüsselterminologie):\\n{glossar_terms}. Melde alle Abweichungen oder Inkonsistenzen."
        },
        "Technik": {
             "v1": "[Technik] Glossarcheck: Prüfe STRIKT, ob diese technischen Fachbegriffe aus dem Glossar korrekt und konsistent übersetzt wurden:\\n{glossar_terms}. Achte auf branchenübliche Entsprechungen und korrekte Verwendung im technischen Kontext.",
             "v2": "[Technik] Glossarcheck (grob): Wurden die wichtigsten technischen Glossarbegriffe korrekt verwendet?\\n{glossar_terms}",
             "v3": "[Technik] Glossarcheck (kritisch): Gibt es KRASS falsche Verwendungen von technischen Glossarbegriffen?\\n{glossar_terms}"
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": "Check if the following glossary terms in the source text have been used correctly and consistently in the translation (detailed):\\n{glossar_terms}. Report all deviations or inconsistencies.",
            "v2": "Check if the following glossary terms in the source text have been used correctly and consistently in the translation (focused on clear deviations):\\n{glossar_terms}. Report all deviations or inconsistencies.",
            "v3": "Check if the following glossary terms in the source text have been used correctly and consistently in the translation (STRICTLY focused on CRITICAL deviations, e.g., wrong term for key terminology):\\n{glossar_terms}. Report all deviations or inconsistencies."
        },
        "Technik": {
             "v1": "[Technik] Glossarcheck: Prüfe STRIKT, ob diese technischen Fachbegriffe aus dem Glossar korrekt und konsistent übersetzt wurden:\\n{glossar_terms}. Achte auf branchenübliche Entsprechungen und korrekte Verwendung im technischen Kontext.",
             "v2": "[Technik] Glossarcheck (grob): Wurden die wichtigsten technischen Glossarbegriffe korrekt verwendet?\\n{glossar_terms}",
             "v3": "[Technik] Glossarcheck (kritisch): Gibt es KRASS falsche Verwendungen von technischen Glossarbegriffen?\\n{glossar_terms}"
        }
    }
}

PROMPTS_TONFALL = {
    "de-DE": {
        "Allgemein": {
            "v1": """Analysiere, ob der Tonfall der Übersetzung zum Ausgangstext passt. Melde signifikante Abweichungen als JSON-Array. Jedes Objekt soll eine Abweichung repräsentieren und die folgenden Schlüssel haben:
- "error_text": Ein repräsentativer Satz oder Teil aus der ÜBERSETZUNG, der die Tonfall-Abweichung zeigt.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem die Abweichung auftritt.
- "explanation": Eine Erklärung, wie sich der Tonfall unterscheidet (z.B. "Original ist sachlich, Übersetzung ist zu umgangssprachlich").
Wenn der Tonfall passt, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.""",
            "v2": "Analysiere den Tonfall (z.B. höflich, sachlich, locker) im Ausgangstext und in der Übersetzung (kurz und bündig, nur bei groben Abweichungen). Bewerte, ob der Tonfall in der Übersetzung zum Original passt.",
            "v3": "Tonfallprüfung ist für Prüfstufe v3 nicht vorgesehen."
        },
        "Marketing": {
            "v1": """[Marketing] Analysiere, ob der Tonfall der Übersetzung zur Marketingbotschaft des Originals passt. Melde signifikante Abweichungen als JSON-Array. Jedes Objekt soll eine Abweichung repräsentieren und die folgenden Schlüssel haben:
- "error_text": Ein repräsentativer Satz oder Teil aus der ÜBERSETZUNG, der die Tonfall-Abweichung zeigt.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem die Abweichung auftritt.
- "explanation": Eine Erklärung, wie sich der Tonfall unterscheidet (z.B. "Original ist werblich und überzeugend, Übersetzung ist zu neutral").
Wenn der Tonfall passt, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.""",
            "v2": "[Marketing] Analysiere den Tonfall. Ist er werblich, überzeugend, zielgruppengerecht? Passt der Ton der Übersetzung zur Marketingbotschaft des Originals? (v2 - Fokus auf grobe Abweichungen)",
            "v3": "Tonfallprüfung ist für Prüfstufe v3 nicht vorgesehen."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": """Analyze if the tone of the translation matches the source text. Report significant deviations as a JSON array. Each object should represent a deviation and have the following keys:
- "error_text": A representative sentence or part from the TRANSLATION that shows the tonal deviation.
- "context": The full paragraph from the TRANSLATION in which the deviation occurs.
- "explanation": An explanation of how the tone differs (e.g., "Original is formal, translation is too casual").
If the tone matches, return an empty JSON array `[]`. Output ONLY the JSON array.""",
            "v2": "Analyze the tone (e.g., polite, formal, casual) in the source text and translation (briefly, only for major deviations). Assess whether the tone in the translation matches the original.",
            "v3": "Tone analysis is not intended for check level v3."
        },
        "Marketing": {
            "v1": """[Marketing] Analyze if the tone of the translation fits the marketing message of the original. Report significant deviations as a JSON array. Each object should represent a deviation and have the following keys:
- "error_text": A representative sentence or part from the TRANSLATION that shows the tonal deviation.
- "context": The full paragraph from the TRANSLATION in which the deviation occurs.
- "explanation": An explanation of how the tone differs (e.g., "Original is promotional and persuasive, translation is too neutral").
If the tone fits, return an empty JSON array `[]`. Output ONLY the JSON array.""",
            "v2": "[Marketing] Analyze the tone. Is it promotional, persuasive, target-audience appropriate? Does the tone of the translation match the marketing message of the original? (v2 - focus on major deviations)",
            "v3": "Tone analysis is not intended for check level v3."
        }
    }
}

PROMPTS_KULTURELL = {
    "de-DE": {
        "Allgemein": {
            "v1": "Analysiere die Übersetzung im Vergleich zum Ausgangstext auf kulturelle Stolpersteine (umfassend), Missverständnisse oder unpassende Formulierungen für das Zielpublikum. Weise auf mögliche kulturelle Unterschiede, Tabus oder problematische Begriffe hin. Gib konkrete Beispiele, falls vorhanden.",
            "v2": "Analysiere die Übersetzung im Vergleich zum Ausgangstext auf kulturelle Stolpersteine (nur auf offensichtliche und gravierende kulturelle Fehltritte), Missverständnisse oder unpassende Formulierungen für das Zielpublikum. Weise auf mögliche kulturelle Unterschiede, Tabus oder problematische Begriffe hin. Gib konkrete Beispiele, falls vorhanden.",
            "v3": "Prüfung kultureller Anpassungen ist für Prüfstufe v3 nicht vorgesehen."
        },
        "Tourismus": {
            "v1": "[Tourismus] Prüfe auf kulturelle Anpassungen für Touristen aus dem Zielmarkt. Sind Ortsnamen, Attraktionen, kulturelle Referenzen passend und verständlich übersetzt/erklärt?",
            "v2": "[Tourismus] Prüfe auf kulturelle Anpassungen für Touristen aus dem Zielmarkt. Sind Ortsnamen, Attraktionen, kulturelle Referenzen passend und verständlich übersetzt/erklärt? (v2 - Fokus auf grobe Fehler)",
            "v3": "Prüfung kultureller Anpassungen ist für Prüfstufe v3 nicht vorgesehen."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": "Analyze the translation compared to the source text for cultural pitfalls (comprehensively), misunderstandings, or inappropriate formulations for the target audience. Point out possible cultural differences, taboos, or problematic terms. Provide specific examples if available.",
            "v2": "Analyze the translation compared to the source text for cultural pitfalls (only for obvious and serious cultural missteps), misunderstandings, or inappropriate formulations for the target audience. Point out possible cultural differences, taboos, or problematic terms. Provide specific examples if available.",
            "v3": "Cultural adaptation check is not intended for check level v3."
        },
        "Tourismus": {
            "v1": "[Tourism] Check for cultural adaptations for tourists from the target market. Are place names, attractions, cultural references appropriately and understandably translated/explained?",
            "v2": "[Tourism] Check for cultural adaptations for tourists from the target market. Are place names, attractions, cultural references appropriately and understandably translated/explained? (v2 - focus on major errors)",
            "v3": "Cultural adaptation check is not intended for check level v3."
        }
    }
}

PROMPTS_STILISTIK = {
    "de-DE": {
        "Allgemein": {
            "v1": """Analysiere die Übersetzung auf stilistische Schwächen. Gib deine Ergebnisse als JSON-Array von Objekten zurück. Jedes Objekt soll eine stilistische Schwäche repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der die stilistische Schwäche aufweist.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem die Schwäche auftritt.
- "explanation": Eine kurze Erklärung der stilistischen Schwäche (z.B. "Passivkonstruktion", "Langer Satz", "Füllwort").
Wenn keine stilistischen Schwächen gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus.""",
            "v2": "Stilistische Hinweise sind nur für Prüfstufe v1 vorgesehen.",
            "v3": "Stilistische Hinweise sind nur für Prüfstufe v1 vorgesehen."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": """Analyze the translation for stylistic weaknesses. Return your findings as a JSON array of objects. Each object should represent a stylistic weakness and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that exhibits the stylistic weakness.
- "context": The full paragraph from the TRANSLATION in which the weakness occurs.
- "explanation": A brief explanation of the stylistic weakness (e.g., "Passive voice", "Long sentence", "Filler word").
If no stylistic weaknesses are found, return an empty JSON array `[]`. Output ONLY the JSON array.""",
            "v2": "Stylistic hints are only intended for check level v1.",
            "v3": "Stylistic hints are only intended for check level v1."
        }
    }
}

PROMPTS_KORREKTUR = { 
    "de-DE": {
        "Allgemein": {
            "v1": """Finde Fehler in der Übersetzung und schlage Korrekturen vor. Gib deine Ergebnisse als JSON-Array von Objekten zurück. Jedes Objekt soll einen Fehler mit Korrekturvorschlag repräsentieren und die folgenden Schlüssel haben:
- "error_text": Der genaue Textausschnitt aus der ÜBERSETZUNG, der den Fehler enthält.
- "context": Der vollständige Absatz aus der ÜBERSETZUNG, in dem der Fehler auftritt.
- "explanation": Eine kurze Erklärung des Fehlers und ein konkreter Korrekturvorschlag (z.B. "Grammatikfehler. Vorschlag: '...korrigierter Text...'").
Wenn keine Fehler gefunden werden, gib ein leeres JSON-Array `[]` zurück. Gib NUR das JSON-Array aus."""
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": """Find errors in the translation and suggest corrections. Return your findings as a JSON array of objects. Each object should represent an error with a correction suggestion and have the following keys:
- "error_text": The exact text snippet from the TRANSLATION that contains the error.
- "context": The full paragraph from the TRANSLATION in which the error occurs.
- "explanation": A brief explanation of the error and a concrete correction suggestion (e.g., "Grammar error. Suggestion: '...corrected text...'").
If no errors are found, return an empty JSON array `[]`. Output ONLY the JSON array."""
        }
    }
}

PROMPTS_REFERENZ_VERGLEICH = { 
    "de-DE": {
        "Allgemein": {
            "v1": "Vergleiche die Übersetzung mit einer vorhandenen Referenzübersetzung. Liste alle Unterschiede auf, insbesondere bei Fachbegriffen, Stil und Inhalt. Gib konkrete Beispiele für Abweichungen."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": "Compare the translation with an existing reference translation. List all differences, especially in technical terms, style, and content. Provide specific examples of deviations."
        }
    }
}

PROMPTS_ABSCHNITTS_CHECK = { # Does not typically vary by Pruefstufe or Fachgebiet
    "de-DE": {
        "Allgemein": {
            "v1": "Vergleiche den Ausgangstext mit der Übersetzung. Erkenne und liste alle Abschnitte, Sätze oder Sinnabschnitte auf, die in der Übersetzung fehlen oder doppelt vorkommen. Gib konkrete Beispiele und Zeilennummern, falls möglich."
        }
    },
    "en-US": {
        "Allgemein": {
            "v1": "Compare the source text with the translation. Identify and list all sections, sentences, or meaningful segments that are missing or duplicated in the translation. Provide specific examples and line numbers if possible."
        }
    }
}

PROMPTS_FEHLER_KLASSIFIZIERUNG = {
    "de-DE": {
        "Allgemein": { # Default Fachgebiet
            "v1": """Du erhältst eine Liste von Fehlermeldungen aus einer Textprüfung. Klassifiziere jeden Fehler als "kritisch" oder "stilistisch".
Kritische Fehler sind z.B.: Grammatikfehler, die den Sinn verändern; Rechtschreibfehler bei wichtigen Begriffen; falsche Zeichensetzung, die zu Missverständnissen führt; Inkonsistenzen.
Stilistische Fehler sind z.B.: Ungelenke Formulierungen, Wortwiederholungen, Füllwörter, Vorschläge zur besseren Lesbarkeit, die den Sinn aber nicht grundlegend verändern.
Gib für jede Eingabezeile NUR das Wort "kritisch" oder "stilistisch" zurück, eine Klassifizierung pro Zeile.
Beispiel Eingabe:
1. Fehler: Möglicher Tippfehler gefunden. Kontext: Das ist ein Beispiltext.
2. Fehler: Komma fehlt vor Nebensatz. Kontext: Er sagte dass er kommt.
Beispiel Ausgabe:
stilistisch
kritisch
""",
            "v2": """Du erhältst eine Liste von Fehlermeldungen. Klassifiziere jeden Fehler als "kritisch" oder "stilistisch".
Für Prüfstufe v2 gelten als kritisch: Echte Grammatikfehler, Rechtschreibfehler in Fachbegriffen/Namen, sinnentstellende Zeichensetzungsfehler.
Stilistische Fehler (z.B. leichte Ungeschicklichkeiten, Wortwahl ohne Sinnänderung) sind für v2 meist zu ignorieren, aber wenn sie gemeldet werden, klassifiziere sie als "stilistisch".
Gib für jede Eingabezeile NUR das Wort "kritisch" oder "stilistisch" zurück.
""",
            "v3": """Du erhältst eine Liste von Fehlermeldungen. Klassifiziere jeden Fehler als "kritisch" oder "stilistisch".
Für Prüfstufe v3 gelten NUR Fehler als kritisch, die den Sinn ENTSCHEIDEND verändern oder FALSCHAUSSAGEN bewirken (z.B. falsche Zahlen, Daten, Namen, krasse Grammatikfehler).
Alles andere ist "stilistisch" oder zu ignorieren.
Gib für jede Eingabezeile NUR das Wort "kritisch" oder "stilistisch" zurück.
"""
        }
        # Fachgebiet-spezifische Klassifizierungsanweisungen können hier hinzugefügt werden.
    },
    "en-US": {
        "Allgemein": {
            "v1": """You will receive a list of error messages from a text check. Classify each error as "critical" or "stylistic".
Critical errors include: Grammatical errors that change the meaning; spelling errors in important terms; incorrect punctuation leading to misunderstandings; inconsistencies.
Stylistic errors include: Awkward phrasing, word repetitions, filler words, suggestions for better readability that do not fundamentally change the meaning.
For each input line, return ONLY the word "critical" or "stylistic", one classification per line.
Example input:
1. Error: Possible typo found. Context: This is an example text.
2. Error: Missing comma before subordinate clause. Context: He said that he is coming.
Example output:
stylistic
critical
""",
            "v2": """You will receive a list of error messages. Classify each error as "critical" or "stylistic".
For check level v2, critical errors are: Genuine grammar errors, spelling errors in technical terms/names, punctuation errors that distort meaning.
Stylistic errors (e.g., minor awkwardness, word choice without change in meaning) should mostly be ignored for v2, but if reported, classify them as "stylistic".
For each input line, return ONLY the word "critical" or "stylistic".
""",
            "v3": """You will receive a list of error messages. Classify each error as "critical" or "stylistic".
For check level v3, ONLY errors that CRUCIALLY change the meaning or cause FALSE STATEMENTS (e.g. incorrect numbers, dates, names, severe grammatical errors) are considered critical.
Everything else is "stylistic" or to be ignored.
For each input line, return ONLY the word "critical" or "stylistic".
"""
        }
        # Fachgebiet-spezifische Klassifizierungsanweisungen können hier hinzugefügt werden.
    }
}

# Default timeout in seconds for Ollama requests
DEFAULT_OLLAMA_TIMEOUT = 5  # Extrem kurzer Timeout für Tests

# Global timeout counter for fallback behavior
OLLAMA_TIMEOUT_COUNT = 0
MAX_TIMEOUTS_BEFORE_FALLBACK = 3

# ----- Helper Function to get specific prompt -----
def _get_prompt(prompt_dict_name, language_code, fachgebiet, pruefstufe, source_language_code=None):
    """
    Retrieves a prompt based on language, subject area, and check level.
    If source_language_code is provided, it first attempts to find a prompt specific
    to the source-target language pair (e.g., "en-US_de-DE").
    If a pair-specific prompt is not found, or if source_language_code is not provided,
    it falls back to prompts based on the target language_code.
    Further fallbacks to DEFAULT_LANG, FALLBACK_LANG, and DEFAULT_FACHGEBIET are applied.
    """
    prompt_dict = globals().get(f"PROMPTS_{prompt_dict_name.upper()}")
    if not prompt_dict:
        return f"Error: Prompt dictionary PROMPTS_{prompt_dict_name.upper()} not found."

    lang_prompts = None
    pair_key_attempted = None # To store the pair key if tried, for better error messages
    final_lang_key_used = language_code # Start by assuming target language key will be used

    if source_language_code and language_code:
        pair_key = f"{source_language_code}_{language_code}"
        pair_key_attempted = pair_key
        lang_prompts = prompt_dict.get(pair_key)
        if lang_prompts:
            final_lang_key_used = pair_key # Pair key was successful

    if not lang_prompts: # Fallback to target language only
        final_lang_key_used = language_code # Reset to target language key
        lang_prompts = prompt_dict.get(language_code)
        if not lang_prompts:
            final_lang_key_used = DEFAULT_LANG # Try default language
            lang_prompts = prompt_dict.get(DEFAULT_LANG)
            if not lang_prompts:
                final_lang_key_used = FALLBACK_LANG # Try fallback language
                lang_prompts = prompt_dict.get(FALLBACK_LANG)
    
    if not lang_prompts: # If still no prompts found after all fallbacks for language
        error_msg = f"Error: No prompts found for target language \'{language_code}\'"
        if pair_key_attempted:
            error_msg += f", language pair \'{pair_key_attempted}\'"
        error_msg += f", default language \'{DEFAULT_LANG}\', or fallback language \'{FALLBACK_LANG}\'.\""
        return error_msg

    # At this point, lang_prompts is set, and final_lang_key_used reflects what key was used to get it.
    fach_prompts = lang_prompts.get(fachgebiet, lang_prompts.get(DEFAULT_FACHGEBIET))
    if not fach_prompts: 
        return (f"Error: No prompts for Fachgebiet \'{fachgebiet}\' or default Fachgebiet \'{DEFAULT_FACHGEBIET}\' "
                f"within the language/pair configuration found under key \'{final_lang_key_used}\'.")
        
    prompt = fach_prompts.get(pruefstufe)
    if prompt is None:
        # Fallback for pruefstufe: try descending levels from current to v1
        current_level_str = pruefstufe.lstrip('v')
        if current_level_str.isdigit():
            current_level = int(current_level_str)
            for level in range(current_level - 1, 0, -1): # Try v(current-1) down to v1
                fallback_pruefstufe = f"v{level}"
                prompt = fach_prompts.get(fallback_pruefstufe)
                if prompt is not None:
                    break 
        
        if prompt is None: 
            if pruefstufe != "v1": # Avoid trying v1 again if it was the initial request or already tried
                prompt = fach_prompts.get("v1")
                # if prompt is not None:
                    # print(f"Hinweis: Prompt für Prüfstufe \'{pruefstufe}\' nicht gefunden, Fallback auf \'v1\' wird verwendet für {prompt_dict_name}.")


        if prompt is None: # If \'v1\' is also not found or no numeric fallback was successful
            return (f"Hinweis: Kein spezifischer Prompt für Prüfstufe \'{pruefstufe}\' (und kein Fallback-Prompt auf niedrigere Stufen oder \\\'v1\\\' vorhanden) "
                    f"im Fachgebiet \'{fachgebiet}\' für Sprachkonfiguration \'{final_lang_key_used}\'. "
                    f"Prüfung möglicherweise nicht vorgesehen.")
            
    return prompt

# ----- Helper Function to call Ollama -----
def _call_ollama(prompt, model="mistral", timeout=300):
    global ollama_timeout_counter
    if ollama_timeout_counter >= 3:
        return "KI-Analyse übersprungen, da der Dienst wiederholt nicht erreichbar war."

    try:
        host = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        print(f"[DEBUG][KI] Verbindungsversuch zu Ollama: Host={host}, Model={model}, Timeout={timeout}s")
        client = ollama.Client(host=host)

        # Verbindungstest (optional, aber gut für die Diagnose)
        try:
            client.list()
            print(f"[DEBUG][KI] Ollama-Verbindungstest erfolgreich")
        except Exception as e:
            print(f"[DEBUG][KI] Ollama-Verbindungstest fehlgeschlagen: {e}")
            return f"Fehler bei der Verbindung zu Ollama: {e}"

        print("[DEBUG][KI] Sende Anfrage an Ollama mit vollem Text...")
        response = client.chat(
            model=model,
            messages=[{'role': 'user', 'content': prompt}],
            stream=False,
            options={'temperature': 0.0}
        )
        print("[DEBUG][KI] Antwort von Ollama erhalten.")
        
        ollama_timeout_counter = 0  # Reset counter on success
        return response['message']['content']
    except requests.exceptions.ReadTimeout:
        ollama_timeout_counter += 1
        print(f"[DEBUG][KI] Anfrage an Ollama hat das Timeout überschritten. Versuch {ollama_timeout_counter}/3.")
        return f"Timeout bei der Anfrage an Ollama (Versuch {ollama_timeout_counter}/3)."
    except ResponseError as e:
        # Error from Ollama API (e.g. model not found, bad request to the model endpoint)
        error_message = f"Ollama API Fehler: {str(e)}."
        if hasattr(e, 'status_code') and e.status_code:
             error_message += f" (Status Code: {e.status_code})"
        print(f"[DEBUG][KI] ResponseError: {error_message}")
        return error_message
    except RequestError as e:        # Network or connection error (e.g., ollama server not running, network issue, client-side timeout)
        error_message = f"Ollama Verbindungsfehler: {str(e)}. Bitte sicherstellen, dass der Ollama-Server läuft und erreichbar ist und die Timeout-Einstellungen ({timeout}s) passen."
        print(f"[DEBUG][KI] RequestError: {error_message}")
        return error_message
    except Exception as e: # General fallback for unexpected errors
        error_message = f"Allgemeiner Fehler bei der Kommunikation mit Ollama ({type(e).__name__}): {str(e)}"
        
        # Track timeouts for fallback behavior
        if "timeout" in str(e).lower() or "timed out" in str(e).lower():
            ollama_timeout_counter += 1
            print(f"[DEBUG][KI] ⚠️ Timeout #{ollama_timeout_counter} erkannt")
            if ollama_timeout_counter >= 3:
                print(f"[DEBUG][KI] 🚫 Timeout-Limit erreicht, weitere KI-Anfragen werden übersprungen")
        
        print(f"[DEBUG][KI] Exception: {error_message}")
        return error_message

# ----- Main KI Functions -----

def ki_qualitaetspruefung(text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Führt eine allgemeine Qualitätsprüfung des Textes durch.
    """
    prompt_template = _get_prompt("QUALITAETS", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template # Return the error/note directly

    full_prompt = f"{prompt_template}\n\nÜbersetzung (Sprache: {language_code}):\n{text}"
    
    return _call_ollama(full_prompt)


def ki_qualitaetspruefung_vergleich(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Vergleicht Ausgangs- und Zieltext auf Unterschiede.
    """
    prompt_template = _get_prompt("QUALITAETS_VERGLEICH", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_terminologiepruefung(source_text, target_text, key_terms=None, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Prüft die konsistente und korrekte Verwendung von Terminologie.
    """
    prompt_template = _get_prompt("TERMINOLOGIE", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    key_terms_str = "\n".join(key_terms) if key_terms else "Keine spezifischen Begriffe vorgegeben."
    prompt_with_terms = prompt_template.format(key_terms=key_terms_str)
    
    full_prompt = f"{prompt_with_terms}\n\nAusgangstext:\n{source_text}\n\nZieltext:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_konsistenzpruefung(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Prüft auf konsistente Übersetzung von Eigennamen, Begriffen etc.
    """
    prompt_template = _get_prompt("KONSISTENZ", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_zusammenfassung(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Fasst Ausgangs- und Zieltext zusammen und vergleicht die Kernaussage.
    """
    prompt_template = _get_prompt("ZUSAMMENFASSUNG", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_glossa_check(source_text, target_text, glossar_terms, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Prüft die Einhaltung eines Glossars.
    """
    prompt_template = _get_prompt("GLOSSAR", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    glossar_str = "\n".join(glossar_terms)
    prompt_with_glossar = prompt_template.format(glossar_terms=glossar_str)
    
    full_prompt = f"{prompt_with_glossar}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_tonfall_pruefung(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Analysiert und vergleicht den Tonfall von Ausgangs- und Zieltext.
    """
    prompt_template = _get_prompt("TONFALL", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_kulturelle_pruefung(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1", source_language_code=None):
    """
    Prüft auf kulturelle Anpassungen und mögliche Stolpersteine.
    """
    prompt_template = _get_prompt("KULTURELL", language_code, fachgebiet, pruefstufe, source_language_code=source_language_code)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def ki_stilistik_pruefung(text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Prüft einen Text auf stilistische Schwächen.
    """
    prompt_template = _get_prompt("STILISTIK", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nText zur Prüfung:\n{text}"
    
    return _call_ollama(full_prompt)


def ki_korrekturvorschlaege(text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Erstellt konkrete Korrekturvorschläge für einen Text.
    """
    # This function might not need a complex prompt structure if it's always the same task
    prompt_template = _get_prompt("KORREKTUR", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nText zur Korrektur:\n{text}"
    
    return _call_ollama(full_prompt)


def ki_referenz_vergleich(text, reference_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Vergleicht einen Text mit einer Referenzübersetzung.
    """
    prompt_template = _get_prompt("REFERENZ_VERGLEICH", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nÜbersetzung:\n{text}\n\nReferenztext:\n{reference_text}"
    
    return _call_ollama(full_prompt)


def ki_abschnitts_check(source_text, target_text, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Prüft auf fehlende oder doppelte Abschnitte.
    """
    prompt_template = _get_prompt("ABSCHNITTS_CHECK", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    full_prompt = f"{prompt_template}\n\nAusgangstext:\n{source_text}\n\nÜbersetzung:\n{target_text}"
    
    return _call_ollama(full_prompt)


def klassifiziere_fehler(fehler_liste, language_code="de-DE", fachgebiet="Allgemein", pruefstufe="v1"):
    """
    Klassifiziert eine Liste von Fehlern in 'kritisch' oder 'stilistisch'.
    """
    prompt_template = _get_prompt("FEHLER_KLASSIFIZIERUNG", language_code, fachgebiet, pruefstufe)
    if "Error:" in prompt_template or "Hinweis:" in prompt_template:
        return prompt_template

    fehler_str = "\n".join(fehler_liste)
    full_prompt = f"{prompt_template}\n\nFehlerliste:\n{fehler_str}"
    
    return _call_ollama(full_prompt)

class KIModule:
    def __init__(self, model_name="mistral:latest", language="de-DE", ollama_host="127.0.0.1", ollama_port=11434):
        self.model_name = model_name
        self.language = language
        self.ollama_host = ollama_host
        self.ollama_port = ollama_port
        self.client = ollama.Client(host=f'http://{self.ollama_host}:{self.ollama_port}')
        self.lang_tool = None # Lazy initialization
        self.ollama_timeout_counter = 0

    def _initialize_language_tool(self):
        """Initializes LanguageTool lazily."""
        if self.lang_tool is None:
            try:
                # Versuche, die Sprache aus dem Code zu extrahieren (z.B. 'de-DE' -> 'de')
                lang_code = self.language.split('-')[0]
                self.lang_tool = language_tool_python.LanguageTool(lang_code)
            except Exception as e:
                print(f"Error initializing LanguageTool for language '{self.language}': {e}")
                # Fallback auf eine Standardsprache, falls die Initialisierung fehlschlägt
                try:
                    self.lang_tool = language_tool_python.LanguageTool('de')
                except Exception as e_fallback:
                    print(f"Error initializing LanguageTool with fallback 'de': {e_fallback}")
                    self.lang_tool = None # Set to None if even fallback fails

    def _get_prompt(self, prompt_dict, lang, fachgebiet, pruefstufe):
        """Retrieves a prompt based on language, subject, and level, with fallback logic."""
        lang_prompts = prompt_dict.get(lang, prompt_dict.get(FALLBACK_LANG, {}))
        fachgebiet_prompts = lang_prompts.get(fachgebiet, lang_prompts.get(DEFAULT_FACHGEBIET, {}))
        return fachgebiet_prompts.get(pruefstufe, "") # Return empty string if level not found

    def _run_ollama_in_thread(self, prompt, text_input, result_queue):
        """Runs the Ollama request in a separate thread to handle timeouts."""
        try:
            full_prompt = f"{prompt}\n\n---\nZIELTEXT:\n{text_input}"
            response = self.client.chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': full_prompt}],
                options={'temperature': 0.0, 'top_p': 0.1}
            )
            result_queue.put(response['message']['content'])
        except RequestError as e:
            if "timeout" in str(e).lower():
                self.ollama_timeout_counter += 1
                print(f"Ollama request timed out. Total timeouts: {self.ollama_timeout_counter}")
                result_queue.put(f'{{"error": "Ollama request timed out", "details": "{str(e)}"}}')
            else:
                print(f"Ollama request error: {e}")
                result_queue.put(f'{{"error": "Ollama request error", "details": "{str(e)}"}}')
        except ResponseError as e:
            print(f"Ollama response error: {e}")
            result_queue.put(f'{{"error": "Ollama response error", "status_code": {e.status_code}, "details": "{e.error}"}}')
        except Exception as e:
            print(f"An unexpected error occurred with Ollama: {e}")
            result_queue.put(f'{{"error": "An unexpected error occurred with Ollama", "details": "{str(e)}"}}')

    def run_quality_check(self, text, fachgebiet, pruefstufe, timeout=60):
        prompt = self._get_prompt(PROMPTS_QUALITAETS, self.language, fachgebiet, pruefstufe)
        if not prompt:
            return f'{{"error": "Prompt not found for the given parameters."}}'

        result_queue = Queue()
        thread = Thread(target=self._run_ollama_in_thread, args=(prompt, text, result_queue))
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            self.ollama_timeout_counter += 1
            print(f"Ollama thread timed out after {timeout} seconds. Total timeouts: {self.ollama_timeout_counter}")
            # It's hard to terminate the thread, but we can return an error message.
            return f'{{"error": "Request timed out after {timeout} seconds."}}'
        else:
            return result_queue.get()

    def run_comparison_check(self, text1, text2, fachgebiet, pruefstufe, timeout=120):
        prompt = self._get_prompt(PROMPTS_QUALITAETS_VERGLEICH, self.language, fachgebiet, pruefstufe)
        if not prompt:
            return f'{{"error": "Prompt not found for the given parameters."}}'

        full_input = f"AUSGANGSTEXT:\n{text1}\n\nÜBERSETZUNG:\n{text2}"
        result_queue = Queue()
        thread = Thread(target=self._run_ollama_in_thread, args=(prompt, full_input, result_queue))
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            self.ollama_timeout_counter += 1
            print(f"Ollama thread timed out after {timeout} seconds. Total timeouts: {self.ollama_timeout_counter}")
            return f'{{"error": "Request timed out after {timeout} seconds."}}'
        else:
            return result_queue.get()

    def run_language_tool_check(self, text):
        self._initialize_language_tool()
        if not self.lang_tool:
            return [] # Return empty list if LanguageTool is not available
        try:
            matches = self.lang_tool.check(text)
            return matches
        except Exception as e:
            print(f"Error during LanguageTool check: {e}")
            return [] # Return empty list on error

    def check_ollama_model_availability(self, model_name):
        """Checks if a specific model is available in Ollama."""
        try:
            models = self.client.list().get('models', [])
            return any(model['name'] == model_name for model in models)
        except Exception as e:
            print(f"Error checking Ollama model availability: {e}")
            return False

# ----- Worker Classes and Functions (Legacy, can be removed or refactored if KIModule is used everywhere) -----

class OllamaWorker(Thread):
    def __init__(self, prompt, text_input, result_queue, model_name="mistral", timeout=300):
        Thread.__init__(self)
        self.prompt = prompt
        self.text_input = text_input
        self.result_queue = result_queue
        self.model_name = model_name
        self.timeout = timeout

    def run(self):
        try:
            full_prompt = f"{self.prompt}\n\n---\nZIELTEXT:\n{self.text_input}"
            response = ollama.Client().chat(
                model=self.model_name,
                messages=[{'role': 'user', 'content': full_prompt}],
                options={'temperature': 0.0, 'top_p': 0.1}
            )
            self.result_queue.put(response['message']['content'])
        except Exception as e:
            self.result_queue.put(f'Error: {str(e)}')
