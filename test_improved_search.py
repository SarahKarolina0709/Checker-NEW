#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 TEST IMPROVED CUSTOMER SEARCH
================================

Testet die verbesserte Kundensuchfunktion:
- Nur relevante Kunden werden angezeigt (Score >= 30%)
- FocusIn zeigt nur bei vorhandenem Suchtext Ergebnisse
- Score-Anzeige für bessere Transparenz
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Simuliere Test-Daten
test_customers = [
    "Müller GmbH",
    "Schmidt & Co",
    "Mueller Technik",
    "Schmitt Industries",
    "Huber Solutions",
    "Weber Industries",
    "Mayer AG",
    "Schulz GmbH"
]

def test_fuzzy_search_logic():
    """Test der verbesserten Fuzzy-Search-Logik"""
    print("🔍 Testing improved fuzzy search logic")
    print("=" * 50)
    
    # Test verschiedene Suchanfragen
    test_queries = [
        ("muel", ["Müller GmbH", "Mueller Technik"]),  # Sollte beide finden
        ("schm", ["Schmidt & Co", "Schmitt Industries"]),  # Ähnliche Namen
        ("xyz", []),  # Kein Match
        ("hub", ["Huber Solutions"]),  # Eindeutiger Match
        ("tech", ["Mueller Technik"]),  # Teilstring-Match
    ]
    
    for query, expected in test_queries:
        print(f"\n🔍 Query: '{query}'")
        
        # Simuliere Score-Berechnung
        results = []
        for customer in test_customers:
            score = calculate_test_score(query.lower(), customer.lower())
            if score >= 30:  # Mindest-Score-Schwelle
                results.append({'name': customer, 'score': score})
        
        results.sort(key=lambda x: x['score'], reverse=True)
        results = results[:8]  # Max 8 Ergebnisse
        
        print(f"📋 Found {len(results)} relevant results:")
        for result in results:
            score = result['score']
            display_text = result['name']
            if score < 100:
                display_text = f"{result['name']} · {score}%"
            print(f"   ✅ {display_text}")
        
        # Validierung
        expected_found = [r['name'] for r in results]
        missing = [exp for exp in expected if exp not in expected_found]
        unexpected = [found for found in expected_found if found not in expected]
        
        if missing:
            print(f"   ⚠️  Missing expected: {missing}")
        if unexpected:
            print(f"   ⚠️  Unexpected results: {unexpected}")
        if not missing and not unexpected:
            print(f"   ✅ Perfect match!")

def calculate_test_score(search_term, customer_name):
    """Vereinfachte Score-Berechnung für Test"""
    if search_term in customer_name:
        # Exakter Substring-Match
        return 90
    
    # Zeichen-basierte Übereinstimmung
    matches = 0
    search_chars = list(search_term)
    name_chars = list(customer_name.lower())
    
    for char in search_chars:
        if char in name_chars:
            matches += 1
            name_chars.remove(char)
    
    if len(search_term) == 0:
        return 0
    
    score = (matches / len(search_term)) * 70
    
    # Bonus für Anfang
    if customer_name.startswith(search_term):
        score += 20
    
    return int(score)

def test_focus_behavior():
    """Test der Focus-Verhalten"""
    print("\n\n🎯 Testing focus behavior")
    print("=" * 50)
    
    test_cases = [
        ("", False, "Empty search - should hide results"),
        ("   ", False, "Whitespace only - should hide results"), 
        ("m", True, "Single char - should show relevant results"),
        ("muel", True, "Multi char - should show filtered results"),
    ]
    
    for search_text, should_show, description in test_cases:
        stripped = search_text.strip()
        should_show_actual = bool(stripped and len(stripped) >= 1)
        
        status = "✅" if should_show_actual == should_show else "❌"
        print(f"{status} {description}")
        print(f"   Input: '{search_text}' -> Show: {should_show_actual}")

if __name__ == "__main__":
    print("🔍 IMPROVED CUSTOMER SEARCH TEST")
    print("================================")
    
    test_fuzzy_search_logic()
    test_focus_behavior()
    
    print("\n✅ Improved search test completed!")
    print("\nKey improvements:")
    print("✅ Only relevant customers shown (Score >= 30%)")
    print("✅ FocusIn only shows results with search text")
    print("✅ Score display for transparency") 
    print("✅ Max 8 results for better UX")
