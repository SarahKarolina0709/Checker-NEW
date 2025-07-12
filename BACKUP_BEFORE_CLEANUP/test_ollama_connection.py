#!/usr/bin/env python3
"""
Simple test script to check Ollama connection and diagnose issues.
"""

import ollama
import sys

def test_ollama_connection():
    """Test if Ollama server is running and accessible."""
    print("Testing Ollama connection...")
    
    try:
        # Try to connect to Ollama
        client = ollama.Client()
          # Try to list available models
        print("Attempting to list models...")
        models = client.list()
        print(f"Models response: {models}")
        if 'models' in models:
            print(f"Available models: {[model.get('name', 'unknown') for model in models['models']]}")
        else:
            print("No 'models' key in response")
        
        # Try a simple chat with mistral
        print("Testing chat with mistral model...")
        response = client.chat(
            model='mistral',
            messages=[
                {
                    'role': 'user',
                    'content': 'Hello! Just testing the connection. Please respond with "Connection successful!"'
                }
            ]
        )
        
        print(f"Response from mistral: {response['message']['content']}")
        print("✅ Ollama connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {type(e).__name__}: {str(e)}")
        print("\nTroubleshooting steps:")
        print("1. Make sure Ollama is installed")
        print("2. Start Ollama server with: ollama run mistral")
        print("3. Keep the terminal with 'ollama run mistral' open")
        print("4. Check if localhost:11434 is accessible")
        return False

if __name__ == "__main__":
    success = test_ollama_connection()
    sys.exit(0 if success else 1)
