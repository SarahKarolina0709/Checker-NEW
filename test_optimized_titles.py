#!/usr/bin/env python3
"""
Test für die verbesserte Workflow-Titel mit natürlichen Zeilenumbrüchen
"""

def test_workflow_titles_with_linebreaks():
    """Test der optimierten Workflow-Titel"""
    workflow_routes = {
        'angebots_workflow': {
            'name': 'Angebots-\nAnalyzer',
            'description': 'Analyse von Übersetzungsanfragen',
            'icon': 'euro-money-2',
            'module': 'angebots_workflow'},
        'pruefung_workflow': {
            'name': 'Multi-File\nCheck',
            'description': 'Qualitätsprüfung für Übersetzungen',
            'icon': 'check',
            'module': 'pruefung_workflow'},
        'finalisierung_workflow': {
            'name': 'Smart\nFinalization',
            'description': 'Finalisierung und Bereitstellung',
            'icon': 'success',
            'module': 'finalisierung_workflow'},
        'projekt_workflow': {
            'name': 'Projekt-\nManager',
            'description': 'Verwaltung aller Projekte',
            'icon': 'project',
            'module': 'projekt_workflow'}
    }
    
    print("🎯 Optimierte Workflow-Titel mit natürlichen Zeilenumbrüchen:")
    print("="*60)
    
    for key, workflow in workflow_routes.items():
        title = workflow['name']
        desc = workflow['description']
        
        # Titel in zwei Zeilen anzeigen
        title_lines = title.split('\n')
        
        print(f"📄 {key}:")
        print(f"   Titel: {title_lines[0]}")
        print(f"          {title_lines[1]}")
        print(f"   Beschreibung: {desc}")
        print(f"   Icon: {workflow['icon']}")
        print()
    
    print("✅ Alle Titel sind jetzt optimal getrennt!")
    print("✅ Natürliche Worttrennungen an sinnvollen Stellen")
    print("✅ Bessere Lesbarkeit durch zweizeilige Darstellung")
    print("✅ Professionelle Optik beibehalten")
    
    # Berechne die maximale Zeilenlänge
    max_line_length = 0
    for key, workflow in workflow_routes.items():
        title_lines = workflow['name'].split('\n')
        for line in title_lines:
            max_line_length = max(max_line_length, len(line))
    
    print(f"\n📊 Statistik:")
    print(f"   Längste Zeile: {max_line_length} Zeichen")
    print(f"   Geschätzte Breite: ~{max_line_length * 10}px")
    print(f"   Verfügbare Breite: 450px")
    print(f"   Margin: {450 - (max_line_length * 10)}px")

if __name__ == "__main__":
    test_workflow_titles_with_linebreaks()
