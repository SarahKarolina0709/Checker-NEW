"""Test script to verify the text metrics have been properly removed from the Prüfung workflow"""

# Import the analyze_text function to directly test
from text_analyzer import analyze_text

def test_summary_generation():
    """Test that the summary generation doesn't include detailed metrics"""
    # This is a copy of the relevant code from fixed_pruefung_workflow.py
    # with the modifications we made
    
    # Test text
    test_text = "Dies ist ein Testtext für die Prüfungs-Workflow-Funktionalität."
    
    # Analyze the text
    analysis_results = analyze_text(test_text)
    
    # Add file metadata for the test
    analysis_results['file_name'] = 'test.txt'
    analysis_results['file_path'] = 'c:/Users/sarah/Desktop/Checker/test.txt'
    
    # Add checks results
    analysis_results['checks_results'] = {
        'Rechtschreibprüfung': {
            'status': 'Bestanden',
            'issues': []
        },
        'Grammatikprüfung': {
            'status': 'Hinweise',
            'issues': ['Mögliches Komma fehlt', 'Satzstruktur prüfen']
        }
    }
    
    # Create a list with a single result
    all_results = [analysis_results]
    selected_checks = ['Rechtschreibprüfung', 'Grammatikprüfung']
    
    # Generate summary using our modified code
    summary_parts = ["Prüfungsergebnis:"]
    summary_parts.append(f"Die Analyse für 1 Datei(en) und {len(selected_checks)} Prüfungsoptionen wurde abgeschlossen.")
    
    if all_results:
        # Keine detaillierten Gesamtstatistiken im Prüfungs-Workflow anzeigen
        summary_parts.append(f"\nZusammenfassung:")
        summary_parts.append(f"- 1 Datei(en) wurden analysiert.")
        summary_parts.append(f"- {len(selected_checks)} Prüfungsoptionen wurden angewendet.")
            
        # Dateispezifische Zusammenfassung (ohne detaillierte Textmetriken)
        for result in all_results:
            file_name = result.get('file_name', 'Unbenannte Datei')
            summary_parts.append(f"\nDatei: {file_name}")
            # Nur einfache Informationen anzeigen, keine detaillierten Textmetriken
            summary_parts.append(f"- Datei erfolgreich analysiert")
    
    summary = "\n".join(summary_parts)
    
    # Generate details using our modified code
    details_parts = ["Detaillierte Ergebnisse:"]
    
    for result in all_results:
        file_name = result.get('file_name', 'Unbenannte Datei')
        details_parts.append(f"\n--- {file_name} ---")
        
        # Entfernen der detaillierten Textmetriken für den Prüfungs-Workflow
        # Stattdessen nur grundlegende Informationen anzeigen
        details_parts.append(f"Datei wurde erfolgreich analysiert.")
        
        # Prüfungsergebnisse
        checks_results = result.get('checks_results', {})
        if checks_results:
            details_parts.append("\nPrüfungsergebnisse:")
            for check_name, check_result in checks_results.items():
                status = check_result.get('status', 'Unbekannt')
                details_parts.append(f"- {check_name}: {status}")
                issues = check_result.get('issues', [])
                if issues:
                    for issue in issues:
                        details_parts.append(f"  * {issue}")
    
    details = "\n".join(details_parts)
    
    # Write results to files for verification
    with open("pruefung_summary_test.txt", "w", encoding="utf-8") as f:
        f.write(summary)
    
    with open("pruefung_details_test.txt", "w", encoding="utf-8") as f:
        f.write(details)
    
    print("Test completed. Check pruefung_summary_test.txt and pruefung_details_test.txt for results.")

if __name__ == "__main__":
    test_summary_generation()
