import spacy
import language_tool_python
from tkinter import messagebox # For showing errors if models can't be loaded

# --- Global Tool Instances ---
lt_tool_instance = None
spacy_model_instance = None

# --- Configuration Maps ---
LANG_CODE_MAP_TO_LT = {
    # Existing
    "DE": "de-DE",
    "EN": "en-US", # Default English to US, can be overridden by specific EN-GB etc.
    "FR": "fr-FR",
    "ES": "es-ES",

    # German variations
    "de": "de-DE",
    "de-AT": "de-AT",
    "de-CH": "de-CH",

    # English variations
    "en-GB": "en-GB",
    "en-AU": "en-AU",
    "en-CA": "en-CA",
    "en-ZA": "en-ZA", # South Africa

    # Romance languages
    "fr": "fr-FR",
    "es": "es-ES",
    "it": "it-IT", "IT": "it-IT",
    "pt": "pt-PT", "PT": "pt-PT", # Portugal
    "pt-BR": "pt-BR", # Brazil
    "ro": "ro-RO", "RO": "ro-RO", # Romanian

    # Slavic languages
    "pl": "pl-PL", "PL": "pl-PL", # Polish
    "ru": "ru-RU", "RU": "ru-RU", # Russian
    "cs": "cs-CZ", "CS": "cs-CZ", # Czech
    "sk": "sk-SK", "SK": "sk-SK", # Slovak
    "uk": "uk-UA", "UK": "uk-UA", # Ukrainian
    "be": "be-BY", "BE": "be-BY", # Belarusian
    "sl": "sl-SI", "SL": "sl-SI", # Slovenian

    # Scandinavian languages
    "sv": "sv-SE", "SV": "sv-SE", # Swedish
    "da": "da-DK", "DA": "da-DK", # Danish
    "nb": "nb-NO", "NB": "nb-NO", # Norwegian Bokmål
    "no": "nb-NO", # General Norwegian to Bokmål

    # Other Germanic
    "nl": "nl-NL", "NL": "nl-NL", # Dutch
    "nl-BE": "nl-BE", # Dutch (Belgium)

    # Asian languages
    "ja": "ja-JP", "JA": "ja-JP", # Japanese
    "zh": "zh-CN", "ZH": "zh-CN", # Chinese (Simplified, Mainland) - LT often uses just 'zh' or 'zh-CN'
    "ko": "ko-KR", "KO": "ko-KR", # Korean (LanguageTool might not have specific Korean support, placeholder)
    "ar": "ar",    "AR": "ar",    # Arabic
    "fa": "fa",    "FA": "fa",    # Persian/Farsi
    "el": "el-GR", "EL": "el-GR", # Greek
    "he": "he-IL", "HE": "he-IL", # Hebrew (LanguageTool might not have specific Hebrew support, placeholder)
    "hi": "hi-IN", "HI": "hi-IN", # Hindi (LanguageTool might not have specific Hindi support, placeholder)
    "id": "id-ID", "ID": "id-ID", # Indonesian (LanguageTool might not have specific Indonesian support, placeholder)
    "th": "th-TH", "TH": "th-TH", # Thai (LanguageTool might not have specific Thai support, placeholder)
    "tr": "tr-TR", "TR": "tr-TR", # Turkish (LanguageTool might not have specific Turkish support, placeholder)
    "vi": "vi-VN", "VI": "vi-VN", # Vietnamese (LanguageTool might not have specific Vietnamese support, placeholder)

    # Other European
    "ca": "ca-ES", "CA": "ca-ES", # Catalan
    "eo": "eo",    "EO": "eo",    # Esperanto
    "eu": "eu-ES", "EU": "eu-ES", # Basque
    "ga": "ga-IE", "GA": "ga-IE", # Irish
    "gl": "gl-ES", "GL": "gl-ES", # Galician
    "hu": "hu-HU", "HU": "hu-HU", # Hungarian
    "is": "is-IS", "IS": "is-IS", # Icelandic (LanguageTool might not have specific Icelandic support, placeholder)
    "lt": "lt-LT", "LT": "lt-LT", # Lithuanian
    "lv": "lv-LV", "LV": "lv-LV", # Latvian (LanguageTool might not have specific Latvian support, placeholder)
    "mk": "mk-MK", "MK": "mk-MK", # Macedonian (LanguageTool might not have specific Macedonian support, placeholder)
    "mt": "mt-MT", "MT": "mt-MT", # Maltese (LanguageTool might not have specific Maltese support, placeholder)
    "et": "et-EE", "ET": "et-EE", # Estonian
    "fi": "fi-FI", "FI": "fi-FI", # Finnish (LanguageTool might not have specific Finnish support, placeholder)
    "br": "br-FR", "BR": "br-FR", # Breton
    "km": "km-KH", "KM": "km-KH", # Khmer
    "tl": "tl-PH", "TL": "tl-PH", # Tagalog

    # Indic languages (placeholders, check LT support)
    "bn": "bn-IN", "BN": "bn-IN", # Bengali
    "gu": "gu-IN", "GU": "gu-IN", # Gujarati
    "kn": "kn-IN", "KN": "kn-IN", # Kannada
    "ml": "ml-IN", "ML": "ml-IN", # Malayalam
    "mr": "mr-IN", "MR": "mr-IN", # Marathi
    "pa": "pa-IN", "PA": "pa-IN", # Punjabi
    "ta": "ta-IN", "TA": "ta-IN", # Tamil
    "te": "te-IN", "TE": "te-IN", # Telugu

    # African languages (placeholders, check LT support)
    "af": "af-ZA", "AF": "af-ZA", # Afrikaans
    "sw": "sw-KE", "SW": "sw-KE", # Swahili

    # Add more mappings as needed based on LanguageTool's supported languages
    # and common short codes used.
    # The format is "SHORT_CODE": "LanguageTool_Code"
    # It's good to include both uppercase (e.g., "DE") and lowercase (e.g., "de")
    # if users might input them differently, though the primary matching in
    # lade_ausgangsdatei_main_ui uses .upper() on extracted codes.
}

SPACY_MODEL_MAP = {
    "de-DE": "de_core_news_sm",
    "de": "de_core_news_sm",
    "en-US": "en_core_web_sm",
    "en": "en_core_web_sm",
    "es-ES": "es_core_news_sm",
    "es": "es_core_news_sm",
    "fr-FR": "fr_core_news_sm",
    "fr": "fr_core_news_sm",
}

LT_EXCLUDE_CATEGORIES_BY_LEVEL = {
    "v1": set(),
    "v2": {"STYLE", "TYPOGRAPHY", "CASING", "REDUNDANCY", "NON_STANDARD_PHRASES", "COLLOCATIONS"},
    "v3": {"STYLE", "TYPOGRAPHY", "CASING", "REDUNDANCY", "NON_STANDARD_PHRASES", "COLLOCATIONS", "PUNCTUATION", "GRAMMAR_SUGGESTIONS_STYLE"},
}

REGEL_BESCHREIBUNG = {
    "UPPERCASE_SENTENCE_START": "Großschreibung am Satzanfang",
    "COMMA_PARENTHESIS_WHITESPACE": "Komma oder Klammer Abstand",
    "EN_QUOTES": "Englische Anführungszeichen",
}

# --- Tool Getters ---
def get_language_tool(language_code='de-DE'):
    """Initialisiert LanguageTool einmal pro Sprache oder gibt die existierende Instanz zurück."""
    global lt_tool_instance
    if lt_tool_instance is None or lt_tool_instance.language != language_code:
        print(f"Initialisiere LanguageTool für {language_code}...")
        try:
            lt_tool_instance = language_tool_python.LanguageTool(language_code)
            print(f"LanguageTool für {language_code} initialisiert.")
        except Exception as e:
            print(f"Fehler bei der Initialisierung von LanguageTool für {language_code}: {e}")
            messagebox.showerror("LanguageTool Fehler", f"Konnte LanguageTool für {language_code} nicht initialisieren:\n{e}")
            lt_tool_instance = None # Ensure it's None if failed
    return lt_tool_instance

def get_spacy_model(language_code='de-DE'):
    """Lädt und gibt das spaCy-Modell für die angegebene Sprache zurück, mit Caching."""
    global spacy_model_instance
    
    simple_lang_code = language_code.split('-')[0].lower()
    target_model_name = SPACY_MODEL_MAP.get(language_code, SPACY_MODEL_MAP.get(simple_lang_code))

    if not target_model_name:
        messagebox.showwarning(
            "Fehlendes spaCy Modell",
            f"Kein spaCy-Modell für Sprache '{language_code}' oder '{simple_lang_code}' in SPACY_MODEL_MAP definiert.\n"
            "Kernbegriff-Analyse wird übersprungen."
        )
        return None

    if spacy_model_instance is not None and hasattr(spacy_model_instance, 'lang'):
        current_model_lang_short = spacy_model_instance.lang
        target_model_lang_short = target_model_name.split('_')[0] # e.g., 'de' from 'de_core_news_sm'
        if current_model_lang_short == target_model_lang_short:
            print(f"✅ spaCy Modell '{target_model_name}' ({current_model_lang_short}) bereits geladen.")
            return spacy_model_instance

    print(f"ℹ️ Lade spaCy Modell '{target_model_name}' für Sprache '{language_code}'...")
    try:
        spacy_model_instance = spacy.load(target_model_name)
        print(f"✅ spaCy Modell '{target_model_name}' erfolgreich geladen.")
    except OSError:
        print(f"⚠️ spaCy Modell '{target_model_name}' nicht gefunden.")
        messagebox.showwarning(
            "Modell fehlt",
            f"Das spaCy-Modell '{target_model_name}' für die Sprache '{language_code}' konnte nicht geladen werden. "
            "Die Funktion 'Kernbegriffe Konsistenz' ist daher deaktiviert.\n\n"
            f"Bitte installieren Sie es z.B. mit:\npython -m spacy download {target_model_name}"
        )
        spacy_model_instance = None
    return spacy_model_instance

