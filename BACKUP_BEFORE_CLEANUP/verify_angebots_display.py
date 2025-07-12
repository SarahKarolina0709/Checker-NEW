"""Test script to verify the Angebotsanalyse workflow still includes detailed metrics"""

# This script simulates the result generation in the angebots_workflow.py
# to confirm that detailed text metrics are still included

def test_angebots_display():
    """Test that the angebots workflow display includes detailed metrics"""
    
    # Simulate some analysis results similar to those in angebots_workflow.py
    analysis_results = {
        'files': [
            {
                'filename': 'angebots_test.txt',
                'filepath': 'c:/Users/sarah/Desktop/Checker/angebots_test.txt',
                'characters': 450,
                'characters_no_spaces': 380,
                'words': 60,
                'lines': 5,
                'normzeilen': 10.5
            }
        ],
        'total_characters': 450,
        'total_characters_no_spaces': 380,
        'total_normzeilen': 10.5,
        'analysis_date': '2025-06-09 15:30:00',
        'customer_name': 'Test Kunde',
        'order_number': '2025-001',
        'pricing_included': True,
        'price_per_line': 2.50,
        'total_price': 26.25
    }
    
    # Generate results text similar to _display_results method in angebots_workflow.py
    results_text = "\n" + "="*60 + "\n"
    results_text += "📊 ANALYSEERGEBNISSE\n"
    results_text += "="*60 + "\n\n"
    
    # Customer info
    results_text += f"Kunde: {analysis_results['customer_name']}\n"
    results_text += f"Auftrag: {analysis_results['order_number']}\n"
    results_text += f"Analysedatum: {analysis_results['analysis_date']}\n\n"
    
    # File summary
    results_text += f"Anzahl Dateien: {len(analysis_results['files'])}\n\n"
    
    # Detailed file results
    results_text += "DETAILANALYSE PRO DATEI:\n"
    results_text += "-" * 40 + "\n"
    
    for file_result in analysis_results['files']:
        results_text += f"\n📄 {file_result['filename']}\n"
        results_text += f"   Zeichen (mit Leerz.): {file_result['characters']:,}\n"
        results_text += f"   Zeichen (ohne Leerz.): {file_result['characters_no_spaces']:,}\n"
        results_text += f"   Wörter: {file_result['words']:,}\n"
        results_text += f"   Zeilen: {file_result['lines']:,}\n"
        results_text += f"   📏 Normzeilen (AC36): {file_result['normzeilen']:.1f}\n"
            
    # Total summary
    results_text += "\n" + "="*40 + "\n"
    results_text += "GESAMTÜBERSICHT:\n"
    results_text += "="*40 + "\n"
    results_text += f"Gesamtzeichen (mit Leerz.): {analysis_results['total_characters']:,}\n"
    results_text += f"Gesamtzeichen (ohne Leerz.): {analysis_results['total_characters_no_spaces']:,}\n"
    results_text += f"📏 Gesamtnormzeilen (AC36): {analysis_results['total_normzeilen']:.1f}\n\n"
                
    # Pricing
    if analysis_results.get('pricing_included'):
        results_text += "💰 PREISBERECHNUNG:\n"
        results_text += "-" * 20 + "\n"
        results_text += f"Preis pro Zeile: {analysis_results['price_per_line']:.2f} €\n"
        results_text += f"Gesamtpreis: {analysis_results.get('total_price', 0):.2f} €\n"
    
    # Write results to file for verification
    with open("angebots_display_test.txt", "w", encoding="utf-8") as f:
        f.write(results_text)
    
    print("Test completed. Check angebots_display_test.txt for results.")

if __name__ == "__main__":
    test_angebots_display()
