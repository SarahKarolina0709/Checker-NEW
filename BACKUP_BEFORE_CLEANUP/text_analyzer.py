import re
from collections import Counter
import math # Added for math.ceil

def count_characters(text: str, with_spaces=True, without_spaces=True):
    """
    Counts characters in the text.
    Returns a dictionary with counts for 'with_spaces' and 'without_spaces'.
    """
    counts = {}
    if with_spaces:
        counts["with_spaces"] = len(text)
    if without_spaces:
        counts["without_spaces"] = len(text.replace(" ", "").replace("\n", "").replace("\r", ""))
    return counts

def count_words(text: str) -> int:
    """
    Counts words in the text. Words are sequences of alphanumeric characters.
    """
    if not text.strip():
        return 0
    # A simple regex to find sequences of word characters.
    # This handles basic punctuation attached to words but might need refinement for complex cases.
    words = re.findall(r'\b[\w\'-]+\b', text.lower())
    return len(words)

def count_sentences(text: str) -> int:
    """
    Counts sentences in the text.
    Uses a simple heuristic: counts '.', '!', '?' as sentence terminators.
    This is a basic approach and might not be accurate for all texts.
    """
    if not text.strip():
        return 0
    # Count occurrences of sentence-ending punctuation.
    # This is a very basic heuristic. For more accuracy, NLTK or spaCy would be better.
    sentence_terminators = re.findall(r'[.!?]+', text)
    count = len(sentence_terminators)
    
    # If the text doesn't end with a terminator but has content, count it as one sentence.
    if count == 0 and text.strip():
        return 1
    # Check if the last character is NOT a sentence terminator, but there's content.
    # This handles cases where the last sentence might not have punctuation.
    if text.strip() and not text.strip()[-1] in ['.','!','?']:
        # If we already found terminators, this implies an unterminated last sentence.
        if count > 0 :
             # Only increment if the content after the last terminator is substantial (e.g. not just whitespace)
            last_segment = text.split(sentence_terminators[-1])[-1] if sentence_terminators else text
            if last_segment.strip():
                count +=1
    return count if count > 0 else (1 if text.strip() else 0)


def count_paragraphs(text: str) -> int:
    """
    Counts paragraphs in the text.
    Paragraphs are assumed to be separated by one or more blank lines (two newlines).
    """
    if not text.strip():
        return 0
    # Split by two or more newlines, then filter out empty strings that result from multiple blank lines.
    paragraphs = re.split(r'\n\s*\n+', text.strip())
    # Filter out any "paragraphs" that are just whitespace after splitting
    actual_paragraphs = [p for p in paragraphs if p.strip()]
    return len(actual_paragraphs) if actual_paragraphs else (1 if text.strip() else 0)

def count_lines_by_length(text: str, target_length: int) -> int:
    """
    Counts lines in the text that have exactly the target_length (including spaces).
    """
    if not text:
        return 0
    lines = text.splitlines() # splitlines() handles various newline characters
    count = 0
    for line in lines:
        # len(line) includes all characters on the line, including leading/trailing whitespace on that specific line.
        if len(line) == target_length:
            count += 1
    return count

def calculate_normzeilen(char_count_with_spaces, chars_per_normzeile=36):
    """Calculates the number of standard lines based on character count."""
    if chars_per_normzeile <= 0:
        return 0
    return math.ceil(char_count_with_spaces / chars_per_normzeile)

def calculate_repetitions(text, min_line_len_chars=15, min_repetition_count=2):
    """
    Calculates line repetitions based on a minimum character length per line.
    Returns a summary string and a dictionary of repeated lines.
    """
    lines = text.splitlines()
    
    normalized_lines = []
    for line in lines:
        stripped_line = line.strip()
        if len(stripped_line) >= min_line_len_chars:
            normalized_lines.append(stripped_line)

    if not normalized_lines:
        return f"Keine Zeilen mit mind. {min_line_len_chars} Zeichen gefunden.", {}

    line_counts = Counter(normalized_lines)
    
    repeated_lines_details = {}
    total_repeated_lines_count = 0
    total_chars_in_repetitions = 0

    for line_text, count in line_counts.items():
        if count >= min_repetition_count:
            repeated_lines_details[line_text] = count
            total_repeated_lines_count += count # Count all instances of repeated lines
            total_chars_in_repetitions += len(line_text) * count

    if not repeated_lines_details:
        return f"Keine Zeilen mind. {min_repetition_count}x wiederholt (Mindestlänge {min_line_len_chars} Zeichen).", {}

    summary = (
        f"{len(repeated_lines_details)} eindeutige Zeilen (mind. {min_line_len_chars} Z.) wiederholen sich mind. {min_repetition_count}x. "
        f"Insgesamt {total_repeated_lines_count} wiederholte Zeileninstanzen, "
        f"ca. {total_chars_in_repetitions} Zeichen in Wiederholungen."
    )
    return summary, repeated_lines_details


def analyze_text(text):
    """
    Performs various text analyses and returns a dictionary of results.
    """
    char_with_spaces = count_characters(text).get("with_spaces", 0)
    normzeilen_ac36 = calculate_normzeilen(char_with_spaces, 36)
    # Use the updated calculate_repetitions for lines
    line_repetition_summary, _ = calculate_repetitions(text, min_line_len_chars=15) 

    return {
        "characters_with_spaces": char_with_spaces,
        "characters_without_spaces": count_characters(text).get("without_spaces", 0),
        "words": count_words(text),
        "sentences": count_sentences(text), # Still useful to have sentence count
        "paragraphs": count_paragraphs(text),
        "lines": len(text.splitlines()) if text else 0,
        "normzeilen_ac36": normzeilen_ac36,
        "line_repetition_summary": line_repetition_summary # Updated key
    }

if __name__ == '__main__':
    sample_text_1 = "Dies ist ein Beispielsatz. Ein zweiter Satz! Und ein dritter?"
    sample_text_2 = "Ein einzelner Satz ohne Punkt"
    sample_text_3 = "Absatz 1.\n\nAbsatz 2 ist hier.\n\n\nAbsatz 3."
    sample_text_4 = "Viele Wörter hier. Und noch mehr Wörter da drüben."
    sample_text_5 = "  " # Whitespace only
    sample_text_6 = "EinWort"
    sample_text_7 = "Hallo Welt.\nWie geht es dir?\nMir geht es gut.\n\nDas ist ein neuer Absatz.\nUnd noch einer."

    print(f"Text 1: '{sample_text_1}'")
    print(f"Analyse 1: {analyze_text(sample_text_1)}")
    # Expected: chars_ws=62, chars_wos=51, words=12, sentences=3, paragraphs=1

    print(f"\nText 2: '{sample_text_2}'")
    print(f"Analyse 2: {analyze_text(sample_text_2)}")
    # Expected: chars_ws=30, chars_wos=26, words=5, sentences=1, paragraphs=1
    
    print(f"\nText 3: '{sample_text_3}'")
    print(f"Analyse 3: {analyze_text(sample_text_3)}")
    # Expected: chars_ws=43, chars_wos=33, words=9, sentences=3, paragraphs=3

    print(f"\nText 4: '{sample_text_4}'")
    print(f"Analyse 4: {analyze_text(sample_text_4)}")
    # Expected: chars_ws=55, chars_wos=46, words=10, sentences=2, paragraphs=1
    
    print(f"\nText 5 (Whitespace): '{sample_text_5}'")
    print(f"Analyse 5: {analyze_text(sample_text_5)}")
    # Expected: all 0 (or chars_ws=2, chars_wos=0 if not stripping before analysis)
    # Current analyze_text handles empty string, but count_paragraphs strips.
    # Let's ensure analyze_text handles text that is only whitespace.
    # If text.strip() is empty, it should return all zeros.

    print(f"\nText 6 (EinWort): '{sample_text_6}'")
    print(f"Analyse 6: {analyze_text(sample_text_6)}")
    # Expected: chars_ws=7, chars_wos=7, words=1, sentences=1, paragraphs=1

    print(f"\nText 7 (Complex): '{sample_text_7}'")
    print(f"Analyse 7: {analyze_text(sample_text_7)}")
    # Expected: sentences=5, paragraphs=2

    sample_text_8 = "This line has exactly 36 characters.\n" + \
                    "This line also has 36 characters!!\n" + \
                    "This line is much longer than 36 characters and also not 55.\n" + \
                    "This line has exactly fifty-five characters in length.\n" + \
                    "Another line with 36 characters...."
    
    print(f"\nText 8 (Line Lengths): '{sample_text_8}'")
    analysis_8 = analyze_text(sample_text_8)
    print(f"Analyse 8: {analysis_8}")
    # Expected for Text 8:
    # lines_length_36: 3 (lines 1, 2, and 5)
    # lines_length_55: 1 (line 4)
    # Other counts as per their definitions.
    # Line 1: "This line has exactly 36 characters." (len=36)
    # Line 2: "This line also has 36 characters!!" (len=36)
    # Line 3: "This line is much longer than 36 characters and also not 55." (len=66)
    # Line 4: "This line has exactly fifty-five characters in length." (len=55)
    # Line 5: "Another line with 36 characters...." (len=36)

    assert analysis_8["lines_length_36"] == 3
    assert analysis_8["lines_length_55"] == 1
    
    sample_text_9_empty = ""
    print(f"\nText 9 (Empty): '{sample_text_9_empty}'")
    print(f"Analyse 9: {analyze_text(sample_text_9_empty)}")
    # Expected: all 0s

    sample_text_10_no_match_length = "Short line\nAnother short line"
    print(f"\nText 10 (No match length): '{sample_text_10_no_match_length}'")
    analysis_10 = analyze_text(sample_text_10_no_match_length)
    print(f"Analyse 10: {analysis_10}")
    assert analysis_10["lines_length_36"] == 0
    assert analysis_10["lines_length_55"] == 0

    sample_text_german = """
Dies ist ein Beispielsatz. Dies ist ein weiterer Beispielsatz!
Und noch einer? Ja, noch einer.
Dieser Satz wiederholt sich. Dieser Satz wiederholt sich. Dieser Satz wiederholt sich.
Ein kurzer Satz. Ein kurzer Satz.
Ein sehr langer Satz, der viele Wörter enthält und sich hoffentlich nicht wiederholt, es sei denn, er ist Teil eines Tests.
    """
    analysis = analyze_text(sample_text_german)
    print("Textanalyse Ergebnisse:")
    for key, value in analysis.items():
        print(f"{key.replace('_', ' ').capitalize()}: {value}")

    print("\nDetaillierte Zeilen-Wiederholungen (min 15 Zeichen):")
    # Test the line repetition directly
    summary, details = calculate_repetitions(sample_text_german, min_line_len_chars=15)
    if details:
        for line, count in details.items():
            print(f"- '{line[:60]}...' (wiederholt {count}x)")
    else:
        print(summary)

    sample_text_for_normzeilen = "Dieser Text hat genau sechsunddreißig Zeichen." # 36 chars
    analysis_norm = analyze_text(sample_text_for_normzeilen)
    print(f"\nNormzeilen für '{sample_text_for_normzeilen}': {analysis_norm['normzeilen_ac36']}")

    sample_text_72 = sample_text_for_normzeilen + " " + sample_text_for_normzeilen # 73 chars with space
    analysis_norm_72 = analyze_text(sample_text_72)
    print(f"Normzeilen für 73 Zeichen Text: {analysis_norm_72['normzeilen_ac36']}")
