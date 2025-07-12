import ki_module
import time

# Test 1: Kurzer Text
print("--- Starte Test 1: Kurzer Text ---")
short_text = "Dies ist ein kurzer Testtext. Er enthält keine Fehler."
print(f"Input: {short_text}")
start_time = time.time()
result_short = ki_module.ki_qualitaetspruefung(short_text)
end_time = time.time()
print(f"Output: {result_short}")
print(f"Dauer: {end_time - start_time:.2f} Sekunden")
print("--- Ende Test 1 ---\n")

# Test 2: Längerer Text (ca. 150 Wörter)
print("--- Starte Test 2: Längerer Text ---")
long_text = """
Dies ist ein längerer deutscher Beispieltext, der für die Überprüfung durch ein KI-Modell wie Mistral über Ollama verwendet werden kann. 
Der Text hat eine angemessene Länge, um potenzielle Probleme bei der Verarbeitung von größeren Texteinheiten zu identifizieren, ohne dabei übermäßig lang zu sein. 
Er enthält einige bewusst eingebaute, subtile grammatikalische Ungenauigkeiten und stilistische Schwächen, um die Fähigkeit des Modells zur Fehlererkennung zu testen. 
Zum Beispiel könnte ein Satz eine etwas umständliche Struktur aufweisen, oder die Wortwahl könnte nicht ganz optimal sein. 
Die KI sollte in der Lage sein, Vorschläge zur Verbesserung der Lesbarkeit, zur Korrektur der Grammatik und zur Optimierung des Stils zu machen. 
Es ist wichtig zu sehen, wie das System mit einem Text umgeht, der nicht nur aus einfachen, kurzen Sätzen besteht, sondern eine gewisse Komplexität aufweist. 
Wir prüfen auch die Konsistenz der Terminologie und den allgemeinen Tonfall des Textes. 
Das Ziel ist es, ein umfassendes Feedback zu erhalten, das über eine reine Rechtschreibprüfung hinausgeht und qualitative Aspekte des Schreibens bewertet.
"""
print(f"Input-Länge: {len(long_text)} Zeichen")
start_time = time.time()
result_long = ki_module.ki_qualitaetspruefung(long_text)
end_time = time.time()
print(f"Output: {result_long}")
print(f"Dauer: {end_time - start_time:.2f} Sekunden")
print("--- Ende Test 2 ---")
