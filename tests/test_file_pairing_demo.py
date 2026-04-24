#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🎯 SMART FILE PAIRING DEMO
Demonstriert die intelligente Dateipaarung
"""

import os
import sys
from difflib import SequenceMatcher

def normalize_filename(filepath):
    """📝 NORMALIZE FILENAME - Bereinige Dateiname für Vergleich"""
    try:
        filename = os.path.splitext(os.path.basename(filepath))[0].lower()
        
        # Entferne häufige Präfixe/Suffixe
        remove_patterns = [
            '_source', '_target', '_translation', '_translated', '_trans',
            '_original', '_orig', '_src', '_übersetzung', '_übersetzt',
            '_quelle', '_ziel', 'source_', 'target_', 'trans_', 'orig_'
        ]
        
        for pattern in remove_patterns:
            filename = filename.replace(pattern, '')
        
        # Entferne Zahlen am Ende (Versionsnummern)
        import re
        filename = re.sub(r'_v?\d+$', '', filename)
        filename = re.sub(r'_\d+$', '', filename)
        
        return filename.strip('_- ')
        
    except Exception:
        return os.path.basename(filepath).lower()

def calculate_filename_similarity(name1, name2):
    """📊 CALCULATE FILENAME SIMILARITY - Berechne Ähnlichkeit zwischen Dateinamen"""
    try:
        if name1 == name2:
            return 1.0
            
        # Längste gemeinsame Teilsequenz
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        # Bonus für exakte Kern-Übereinstimmung
        if name1 in name2 or name2 in name1:
            similarity += 0.2
            
        # Bonus für Wort-Übereinstimmungen
        words1 = set(name1.split('_'))
        words2 = set(name2.split('_'))
        common_words = len(words1 & words2)
        total_words = len(words1 | words2)
        
        if total_words > 0:
            word_similarity = common_words / total_words
            similarity = (similarity + word_similarity) / 2
        
        return min(similarity, 1.0)
        
    except Exception:
        return 0.0

def demo_smart_pairing():
    """🎯 DEMO SMART FILE PAIRING"""
    print("🎯 SMART FILE PAIRING DEMO")
    print("=" * 50)
    
    # Beispiel-Dateien für Demo
    test_cases = [
        {
            'source': [
                'vertrag_original.pdf',
                'dokument_source.docx', 
                'bericht_v2_quelle.txt',
                'manual_eng.pdf'
            ],
            'translation': [
                'vertrag_übersetzung.pdf',
                'dokument_translation.docx',
                'bericht_v2_übersetzt.txt',
                'manual_ger.pdf',
                'komplett_andere_datei.pdf'
            ]
        }
    ]
    
    for case_num, case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {case_num}:")
        print("-" * 30)
        
        print("📄 Ausgangstexte:")
        for f in case['source']:
            normalized = normalize_filename(f)
            print(f"  • {f} → normalisiert: '{normalized}'")
        
        print("\n📋 Übersetzungen:")
        for f in case['translation']:
            normalized = normalize_filename(f)
            print(f"  • {f} → normalisiert: '{normalized}'")
        
        # Smart Pairing durchführen
        print(f"\n🎯 SMART PAIRING ERGEBNISSE:")
        print("-" * 30)
        
        pairs = []
        unmatched_source = []
        unmatched_translation = list(case['translation'])
        
        for source_file in case['source']:
            source_name = normalize_filename(source_file)
            best_match = None
            best_score = 0
            
            for trans_file in unmatched_translation:
                trans_name = normalize_filename(trans_file)
                similarity = calculate_filename_similarity(source_name, trans_name)
                
                if similarity > best_score and similarity > 0.6:  # 60% Minimum
                    best_match = trans_file
                    best_score = similarity
            
            if best_match:
                pairs.append({
                    'source': source_file,
                    'translation': best_match,
                    'similarity': best_score
                })
                unmatched_translation.remove(best_match)
                print(f"✅ PAIR: {source_file} ↔ {best_match}")
                print(f"   Ähnlichkeit: {best_score:.1%}")
            else:
                unmatched_source.append(source_file)
                print(f"❌ UNMATCHED: {source_file} (keine ähnliche Übersetzung gefunden)")
        
        # Ungepaarte Übersetzungen
        for unmatched in unmatched_translation:
            print(f"⚠️ UNMATCHED TRANSLATION: {unmatched}")
        
        print(f"\n📊 ZUSAMMENFASSUNG:")
        print(f"   • {len(pairs)} erfolgreich gepaarte Dateien")
        print(f"   • {len(unmatched_source)} ungepaarte Ausgangstexte")
        print(f"   • {len(unmatched_translation)} ungepaarte Übersetzungen")

if __name__ == "__main__":
    demo_smart_pairing()
