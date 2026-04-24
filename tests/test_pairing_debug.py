#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Debug-Script für Dateipaarung"""

import tempfile
import os
from pathlib import Path

print("=" * 70)
print("Testing File Pairing System")
print("=" * 70)

# Teste PairingManager Import
try:
    from quality_gui_pairing_manager import QualityGuiPairingManager
    print("✅ QualityGuiPairingManager erfolgreich importiert")
except Exception as e:
    print(f"❌ Fehler beim Import: {e}")
    exit(1)

# Teste PairingService Import
try:
    from pairing_service import get_pairing_service
    print("✅ PairingService erfolgreich importiert")
except Exception as e:
    print(f"⚠️  PairingService nicht verfügbar: {e}")
    get_pairing_service = None

# Erstelle temporäre Testdateien
with tempfile.TemporaryDirectory() as tmpdir:
    print(f"\n📁 Erstelle Testdateien in: {tmpdir}\n")
    
    # Source-Dateien
    source_files = []
    for i in range(1, 4):
        src = Path(tmpdir) / f"document_{i}_EN.txt"
        src.write_text(f"This is test document {i} in English.", encoding='utf-8')
        source_files.append(str(src))
        print(f"   ✅ Created: {src.name}")
    
    # Translation-Dateien (mit ähnlichen Namen)
    translation_files = []
    for i in range(1, 4):
        tgt = Path(tmpdir) / f"document_{i}_DE.txt"
        tgt.write_text(f"Dies ist Testdokument {i} auf Deutsch.", encoding='utf-8')
        translation_files.append(str(tgt))
        print(f"   ✅ Created: {tgt.name}")
    
    # Zusätzliche ungepaarte Dateien
    extra_src = Path(tmpdir) / "extra_source.txt"
    extra_src.write_text("Extra source file without pair", encoding='utf-8')
    source_files.append(str(extra_src))
    print(f"   ✅ Created: {extra_src.name} (unpaired)")
    
    extra_tgt = Path(tmpdir) / "extra_translation.txt"
    extra_tgt.write_text("Extra Übersetzungsdatei ohne Paar", encoding='utf-8')
    translation_files.append(str(extra_tgt))
    print(f"   ✅ Created: {extra_tgt.name} (unpaired)")
    
    print(f"\n📊 Testdaten:")
    print(f"   Source-Dateien: {len(source_files)}")
    print(f"   Translation-Dateien: {len(translation_files)}")
    
    # Teste PairingManager
    print("\n" + "=" * 70)
    print("Testing PairingManager.run_smart_pairing()")
    print("=" * 70)
    
    try:
        manager = QualityGuiPairingManager()
        print("✅ PairingManager initialisiert")
        
        # Führe Smart Pairing aus
        if get_pairing_service:
            pairing_service_supplier = lambda: get_pairing_service(event_bus=None)
        else:
            pairing_service_supplier = None
        
        pairs, unmatched = manager.run_smart_pairing(
            source_files,
            translation_files,
            pairing_service_supplier=pairing_service_supplier
        )
        
        print(f"\n✅ Smart Pairing abgeschlossen!")
        print(f"\n📋 Ergebnisse:")
        print(f"   Gefundene Paare: {len(pairs)}")
        print(f"   Ungepaarte Source: {len(unmatched.get('source', []))}")
        print(f"   Ungepaarte Translation: {len(unmatched.get('translation', []))}")
        
        if pairs:
            print(f"\n📝 Gefundene Paare:")
            for i, pair in enumerate(pairs, 1):
                src_name = os.path.basename(pair.get('source', 'N/A'))
                tgt_name = os.path.basename(pair.get('translation', 'N/A'))
                similarity = pair.get('similarity', 0.0)
                print(f"   {i}. {src_name} ↔ {tgt_name} (Ähnlichkeit: {similarity:.2f})")
        
        if unmatched.get('source'):
            print(f"\n⚠️  Ungepaarte Source-Dateien:")
            for f in unmatched['source']:
                print(f"   - {os.path.basename(f)}")
        
        if unmatched.get('translation'):
            print(f"\n⚠️  Ungepaarte Translation-Dateien:")
            for f in unmatched['translation']:
                print(f"   - {os.path.basename(f)}")
        
        # Teste manuelle Paarung
        print("\n" + "=" * 70)
        print("Testing Manual Pairing")
        print("=" * 70)
        
        if unmatched.get('source') and unmatched.get('translation'):
            src_to_pair = unmatched['source'][0]
            tgt_to_pair = unmatched['translation'][0]
            
            print(f"\n🔧 Paare manuell:")
            print(f"   {os.path.basename(src_to_pair)} → {os.path.basename(tgt_to_pair)}")
            
            # Füge manuelles Paar hinzu
            manual_pair = {
                'source': src_to_pair,
                'translation': tgt_to_pair,
                'similarity': 1.0,
                'method': 'manual'
            }
            
            # Update Manager State
            manager.state.pairs.append(
                type('PairRecord', (), {'source': src_to_pair, 'translation': tgt_to_pair})()
            )
            manager.state.unmatched_sources = [f for f in unmatched['source'] if f != src_to_pair]
            manager.state.unmatched_translations = [f for f in unmatched['translation'] if f != tgt_to_pair]
            manager._snapshot()
            
            # Hole aktualisierte Legacy Pairs
            updated_pairs = manager.get_legacy_pairs()
            updated_unmatched = manager.get_legacy_unmatched()
            
            print(f"\n✅ Nach manueller Paarung:")
            print(f"   Paare: {len(updated_pairs)}")
            print(f"   Ungepaarte Source: {len(updated_unmatched.get('source', []))}")
            print(f"   Ungepaarte Translation: {len(updated_unmatched.get('translation', []))}")
        
        # Teste Undo/Redo
        print("\n" + "=" * 70)
        print("Testing Undo/Redo")
        print("=" * 70)
        
        prev_state = manager.undo()
        if prev_state:
            print(f"✅ Undo erfolgreich:")
            print(f"   Paare nach Undo: {len(prev_state.pairs)}")
            
            next_state = manager.redo()
            if next_state:
                print(f"✅ Redo erfolgreich:")
                print(f"   Paare nach Redo: {len(next_state.pairs)}")
            else:
                print(f"⚠️  Redo nicht möglich (kein State verfügbar)")
        else:
            print(f"⚠️  Undo nicht möglich (keine History)")
        
    except Exception as e:
        print(f"\n❌ Fehler beim Testen: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 70)
print("✅ Test abgeschlossen")
print("=" * 70)

print("\n💡 Hinweise für die GUI:")
print("   1. Dateien müssen hochgeladen werden (Upload Source/Translation)")
print("   2. Nach dem Upload wird automatisch Smart Pairing ausgeführt")
print("   3. Bei ungepaarten Dateien erscheint der 'Manuell paaren' Button")
print("   4. Im Pairing-Dialog können Dateien manuell zugeordnet werden")
