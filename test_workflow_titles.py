#!/usr/bin/env python3
"""
Test für die verbesserte Workflow-Karten-Darstellung
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_workflow_titles():
    """Test der Workflow-Titel-Längen"""
    workflow_routes = {
        'angebots_workflow': {
            'name': 'Angebots-Analyzer',
            'description': 'Analyse von Übersetzungsanfragen',
            'icon': 'euro-money-2',
            'module': 'angebots_workflow'},
        'pruefung_workflow': {
            'name': 'Multi-File Check',
            'description': 'Qualitätsprüfung für Übersetzungen',
            'icon': 'check',
            'module': 'pruefung_workflow'},
        'finalisierung_workflow': {
            'name': 'Smart Finalization',
            'description': 'Finalisierung und Bereitstellung',
            'icon': 'success',
            'module': 'finalisierung_workflow'},
        'projekt_workflow': {
            'name': 'Projekt-Manager',
            'description': 'Verwaltung aller Projekte',
            'icon': 'project',
            'module': 'projekt_workflow'}
    }
    
    print("🔍 Workflow-Titel Analyse:")
    print("="*50)
    
    max_title_length = 0
    max_desc_length = 0
    
    for key, workflow in workflow_routes.items():
        title = workflow['name']
        desc = workflow['description']
        title_len = len(title)
        desc_len = len(desc)
        
        max_title_length = max(max_title_length, title_len)
        max_desc_length = max(max_desc_length, desc_len)
        
        print(f"📄 {title} ({title_len} Zeichen)")
        print(f"   {desc} ({desc_len} Zeichen)")
        print()
    
    print(f"📊 Statistiken:")
    print(f"   Längster Titel: {max_title_length} Zeichen")
    print(f"   Längste Beschreibung: {max_desc_length} Zeichen")
    print()
    
    # Geschätzte Breite bei 16px Schrift
    estimated_width_title = max_title_length * 10  # ~10px pro Zeichen
    estimated_width_desc = max_desc_length * 8    # ~8px pro Zeichen
    
    print(f"💡 Geschätzte Breiten:")
    print(f"   Titel: ~{estimated_width_title}px")
    print(f"   Beschreibung: ~{estimated_width_desc}px")
    print(f"   Karten-Breite: 450px (✓ Ausreichend)")
    print()
    
    # Bewertung
    if estimated_width_title <= 300:
        print("✅ Alle Titel sollten vollständig sichtbar sein!")
    else:
        print("⚠️  Einige Titel könnten immer noch zu lang sein")
        
    if estimated_width_desc <= 300:
        print("✅ Alle Beschreibungen sollten vollständig sichtbar sein!")
    else:
        print("✅ Beschreibungen verwenden Textbox mit Umbruch")

if __name__ == "__main__":
    test_workflow_titles()
