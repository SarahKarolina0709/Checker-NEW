"""
Language detection module for the Checker app.
This helps ensure that appropriate language rules are applied based on text content.
"""
import re
from collections import Counter
import string

# Common language identifiers and their characteristic word sets
LANGUAGE_PATTERNS = {
    'en-US': {
        'common_words': ['the', 'and', 'to', 'of', 'in', 'is', 'that', 'for', 'with', 'on', 'at', 'this', 'it', 'by', 'as', 'are', 'was', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'but', 'or', 'if', 'when', 'what', 'where', 'who', 'how', 'why', 'which', 'than', 'then', 'now', 'here', 'there', 'all', 'some', 'any', 'no', 'not', 'only', 'just', 'very', 'so', 'too', 'also', 'more', 'most', 'much', 'many', 'new', 'old', 'good', 'bad', 'big', 'small', 'long', 'short', 'high', 'low'],
        'articles': ['the', 'a', 'an'],
        'language_code': 'en-US'
    },
    'de-DE': {
        'common_words': ['der', 'die', 'das', 'und', 'in', 'zu', 'den', 'ist', 'von', 'mit', 'des', 'sich', 'auf', 'für', 'nicht', 'eine', 'einen', 'einer', 'ein', 'als', 'auch', 'nach', 'wird', 'an', 'sind', 'oder', 'es', 'hat', 'sie', 'er', 'ich', 'wir', 'ihr', 'du', 'man', 'kann', 'soll', 'nur', 'noch', 'schon', 'aber', 'wenn', 'was', 'wie', 'wo', 'wer', 'warum', 'welche', 'dass', 'dann', 'doch', 'so', 'sehr', 'mehr', 'wieder', 'neue', 'große', 'erste', 'gute', 'andere'],
        'articles': ['der', 'die', 'das', 'ein', 'eine', 'einen'],
        'language_code': 'de-DE'
    },
    'fr': {
        'common_words': ['le', 'la', 'les', 'de', 'des', 'et', 'à', 'un', 'une', 'en', 'que', 'qui', 'pour', 'dans', 'ce', 'du', 'est', 'il', 'elle', 'nous', 'vous', 'ils', 'elles', 'on', 'avec', 'par', 'sur', 'sans', 'sous', 'mais', 'ou', 'si', 'ne', 'pas', 'plus', 'tout', 'tous', 'cette', 'ces', 'son', 'sa', 'ses', 'mon', 'ma', 'mes', 'ton', 'ta', 'tes', 'notre', 'nos', 'votre', 'vos', 'leur', 'leurs'],
        'articles': ['le', 'la', 'les', 'un', 'une', 'des'],
        'language_code': 'fr'
    },
    'es': {
        'common_words': ['el', 'la', 'los', 'las', 'de', 'en', 'y', 'a', 'que', 'por', 'con', 'no', 'un', 'una', 'es', 'del', 'al', 'se', 'le', 'lo', 'me', 'te', 'nos', 'os', 'les', 'su', 'sus', 'mi', 'mis', 'tu', 'tus', 'nuestro', 'nuestra', 'nuestros', 'nuestras', 'vuestro', 'vuestra', 'vuestros', 'vuestras', 'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas', 'pero', 'si', 'cuando', 'donde', 'como', 'mas', 'muy', 'todo', 'toda', 'todos', 'todas'],
        'articles': ['el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas'],
        'language_code': 'es'
    },
    'it': {
        'common_words': ['il', 'la', 'i', 'le', 'di', 'e', 'che', 'a', 'per', 'in', 'un', 'con', 'è', 'non', 'sono', 'del', 'della', 'dei', 'delle', 'al', 'alla', 'ai', 'alle', 'nel', 'nella', 'nei', 'nelle', 'sul', 'sulla', 'sui', 'sulle', 'da', 'dal', 'dalla', 'dai', 'dalle', 'si', 'mi', 'ti', 'ci', 'vi', 'lo', 'gli', 'sua', 'sue', 'suo', 'suoi', 'mia', 'mie', 'mio', 'miei', 'tua', 'tue', 'tuo', 'tuoi', 'ma', 'se', 'quando', 'dove', 'come', 'più', 'molto', 'tutto', 'tutta', 'tutti', 'tutte'],
        'articles': ['il', 'lo', 'la', 'i', 'gli', 'le', 'un', 'uno', 'una'],
        'language_code': 'it'
    }
}

def normalize_text(text):
    """Normalize text by removing punctuation and converting to lowercase."""
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    # Convert to lowercase
    text = text.lower()
    return text

def detect_language(text, minimum_confidence=0.3, default_lang_code='de-DE'):
    """
    Detect the language of the provided text.
    
    Args:
        text (str): The text to analyze.
        minimum_confidence (float): Minimum confidence score required (0.0-1.0).
        default_lang_code (str): Default language code to return if detection fails.
    
    Returns:
        str: The detected language code (e.g., 'en-US', 'de-DE').
    """
    if not text or len(text.strip()) < 10:  # Reduced minimum length
        print(f"[INFO] Text too short for language detection. Using default: {default_lang_code}")
        return default_lang_code
    
    # Normalize text
    normalized_text = normalize_text(text)
    words = normalized_text.split()
    
    if len(words) < 3:  # Very low minimum word count
        print(f"[INFO] Too few words for language detection. Using default: {default_lang_code}")
        return default_lang_code
    
    # Count word frequencies
    word_counter = Counter(words)
    total_words = len(words)
    
    # Calculate scores for each language
    language_scores = {}
    
    for lang_code, patterns in LANGUAGE_PATTERNS.items():
        common_words = patterns['common_words']
        articles = patterns['articles']
        
        # Score based on common words (weighted by frequency and importance)
        common_word_score = 0
        for i, word in enumerate(common_words):
            if word in word_counter:
                # Give more weight to more common words (earlier in the list)
                importance_weight = (len(common_words) - i) / len(common_words)
                frequency_weight = word_counter[word] / total_words
                common_word_score += importance_weight * frequency_weight * 10
        
        # Score based on articles (very language-specific)
        article_score = 0
        for article in articles:
            if article in word_counter:
                article_score += word_counter[article] / total_words * 5
        
        # Character and pattern-based scoring
        text_lower = text.lower()
        pattern_score = 0
        
        if lang_code == 'de-DE':
            # German-specific patterns
            pattern_score += text_lower.count('ä') * 0.5
            pattern_score += text_lower.count('ö') * 0.5
            pattern_score += text_lower.count('ü') * 0.5
            pattern_score += text_lower.count('ß') * 1.0
            pattern_score += text_lower.count('sch') * 0.3
            pattern_score += text_lower.count('ung') * 0.2
            
        elif lang_code == 'en-US':
            # English-specific patterns
            pattern_score += text_lower.count(' the ') * 0.5
            pattern_score += text_lower.count('ing ') * 0.3
            pattern_score += text_lower.count('tion') * 0.3
            pattern_score += text_lower.count('ed ') * 0.2
            # Boost for English-specific punctuation patterns
            if ':' in text and any(word in text_lower for word in ['but', 'what', 'after', 'market']):
                pattern_score += 1.0
                
        elif lang_code == 'fr':
            # French-specific patterns
            pattern_score += text_lower.count('à') * 0.3
            pattern_score += text_lower.count('é') * 0.3
            pattern_score += text_lower.count('è') * 0.3
            pattern_score += text_lower.count('ç') * 0.5
            pattern_score += text_lower.count('tion') * 0.2
            
        elif lang_code == 'es':
            # Spanish-specific patterns
            pattern_score += text_lower.count('ñ') * 0.5
            pattern_score += text_lower.count('ción') * 0.3
            pattern_score += text_lower.count('que ') * 0.2
            
        elif lang_code == 'it':
            # Italian-specific patterns
            pattern_score += text_lower.count('zione') * 0.3
            pattern_score += text_lower.count('gli ') * 0.3
            pattern_score += text_lower.count('che ') * 0.2
        
        # Combined score
        combined_score = common_word_score + article_score + pattern_score
        language_scores[lang_code] = combined_score
    
    # Find the language with the highest score
    if not language_scores or all(score == 0 for score in language_scores.values()):
        print(f"[INFO] No language patterns detected. Using default: {default_lang_code}")
        return default_lang_code
    
    best_lang = max(language_scores.items(), key=lambda x: x[1])
    lang_code, confidence = best_lang
    
    # Calculate relative confidence (difference from second best)
    sorted_scores = sorted(language_scores.values(), reverse=True)
    if len(sorted_scores) > 1 and sorted_scores[1] > 0:
        relative_confidence = (sorted_scores[0] - sorted_scores[1]) / sorted_scores[0]
    else:
        relative_confidence = confidence
    
    # Debug output
    print(f"[DEBUG] Language scores: {language_scores}")
    print(f"[DEBUG] Relative confidence: {relative_confidence:.2f}")
    
    # Use relative confidence for decision
    if relative_confidence >= minimum_confidence:
        print(f"[INFO] Detected language: {lang_code} with confidence {relative_confidence:.2f}")
        return lang_code
    else:
        print(f"[INFO] Language detection confidence too low ({relative_confidence:.2f}). Using default: {default_lang_code}")
        return default_lang_code

def main():
    """Test the language detection with sample texts."""
    test_texts = {
        "en-US": "The quick brown fox jumps over the lazy dog. This is a sample text in English.",
        "de-DE": "Der schnelle braune Fuchs springt über den faulen Hund. Dies ist ein Beispieltext auf Deutsch.",
        "fr": "Le renard brun rapide saute par-dessus le chien paresseux. Ceci est un exemple de texte en français.",
        "es": "El rápido zorro marrón salta sobre el perro perezoso. Este es un texto de ejemplo en español.",
        "it": "La veloce volpe marrone salta sopra il cane pigro. Questo è un testo di esempio in italiano."
    }
    
    for expected_lang, text in test_texts.items():
        detected = detect_language(text)
        print(f"Expected: {expected_lang}, Detected: {detected}, {'✓' if expected_lang == detected else '✗'}")

if __name__ == "__main__":
    main()
