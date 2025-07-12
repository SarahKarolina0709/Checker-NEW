#!/usr/bin/env python3
"""
Minimal test für Ollama mit sehr kurzem Text
"""

import ollama

def test_minimal_ollama():
    try:
        client = ollama.Client(timeout=30)
        
        # Sehr kurzer Test-Text
        test_text = "Test Dokument."
        
        print(f"Teste Ollama mit Text: '{test_text}'")
        
        response = client.chat(
            model="mistral",
            messages=[
                {
                    'role': 'system',
                    'content': 'Du bist ein Textprüfer. Analysiere den Text kurz.',
                },
                {
                    'role': 'user',
                    'content': test_text,
                }
            ]
        )
        
        print("✅ Erfolg!")
        print(f"Antwort: {response['message']['content']}")
        return True
        
    except Exception as e:
        print(f"❌ Fehler: {e}")
        return False

if __name__ == "__main__":
    test_minimal_ollama()
