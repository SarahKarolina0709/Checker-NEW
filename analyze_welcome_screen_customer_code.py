#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 WELCOME SCREEN CUSTOMER CODE ANALYSIS
=========================================

Analysiert Customer-bezogenen Code in welcome_screen.py für die Refaktorierung.
"""

def analyze_customer_code_in_welcome_screen():
    """Analysiere Customer-Code in welcome_screen.py"""
    
    print("🔍 WELCOME SCREEN CUSTOMER CODE ANALYSIS")
    print("=" * 60)
    
    # Finde alle Customer-bezogenen Methoden
    import re
    
    try:
        with open('welcome_screen.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Finde Customer-Funktionen
        customer_functions = re.findall(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^)]*\):', content)
        customer_related = [f for f in customer_functions if 'customer' in f.lower()]
        
        print(f"📊 GEFUNDENE CUSTOMER FUNKTIONEN ({len(customer_related)}):")
        print("-" * 50)
        
        categories = {
            'ui_creation': [],
            'business_logic': [],
            'event_handlers': [],
            'helpers': []
        }
        
        for func in customer_related:
            if any(word in func.lower() for word in ['create', 'setup', 'style', 'update']):
                if any(word in func.lower() for word in ['card', 'ui', 'display', 'button']):
                    categories['ui_creation'].append(func)
                else:
                    categories['helpers'].append(func)
            elif any(word in func.lower() for word in ['add', 'remove', 'save', 'load', 'exists']):
                categories['business_logic'].append(func)
            elif any(word in func.lower() for word in ['on_', '_handle_', 'select']):
                categories['event_handlers'].append(func)
            else:
                categories['helpers'].append(func)
        
        for category, functions in categories.items():
            if functions:
                print(f"\n{category.upper().replace('_', ' ')} ({len(functions)}):")
                for i, func in enumerate(functions, 1):
                    print(f"   {i:2d}. {func}")
        
        # Analysiere Business Logic die zu CustomerManager kann
        print(f"\n🎯 REFACTORING EMPFEHLUNGEN:")
        print("=" * 60)
        
        business_logic_candidates = categories['business_logic']
        if business_logic_candidates:
            print(f"\n🔄 ZU CUSTOMER MANAGER VERSCHIEBEN:")
            print("-" * 40)
            for func in business_logic_candidates:
                print(f"   • {func} → customer_manager.{func.replace('_customer', '').replace('customer_', '')}")
        
        ui_optimization_candidates = categories['ui_creation']
        if ui_optimization_candidates:
            print(f"\n🎨 UI-CODE OPTIMIERUNG MÖGLICH:")
            print("-" * 40)
            for func in ui_optimization_candidates:
                print(f"   • {func} → Kann vereinfacht werden")
        
        event_handler_candidates = categories['event_handlers'] 
        if event_handler_candidates:
            print(f"\n⚡ EVENT HANDLERS (BEHALTEN, ABER OPTIMIEREN):")
            print("-" * 40)
            for func in event_handler_candidates:
                print(f"   • {func} → Verwende customer_manager calls")
        
        # Geschätzte Code-Reduktion
        total_functions = len(customer_related)
        business_logic_count = len(business_logic_candidates)
        
        print(f"\n📈 GESCHÄTZTE CODE-REDUKTION:")
        print("-" * 40)
        print(f"Customer Funktionen total: {total_functions}")
        print(f"Business Logic verschiebbar: {business_logic_count}")
        print(f"Geschätzte Zeilen-Reduktion: ~{business_logic_count * 15}-{business_logic_count * 25} Zeilen")
        print(f"Plus 942 Zeilen durch welcome_screen_customer.py Elimination")
        print(f"TOTAL REDUKTION: ~{942 + business_logic_count * 20} Zeilen")
        
        print(f"\n🚀 NÄCHSTE SCHRITTE:")
        print("-" * 40)
        print("1. ✅ ERLEDIGT: welcome_screen_customer.py archiviert")
        print("2. ✅ ERLEDIGT: CustomerManager um UI-Helper erweitert")
        print("3. 🔄 TODO: Business Logic Funktionen refactorn")
        print("4. 🔄 TODO: Event Handlers auf Manager umstellen")
        print("5. 🔄 TODO: UI-Code optimieren und vereinfachen")
        
        return {
            'total_functions': total_functions,
            'business_logic': business_logic_candidates,
            'ui_creation': ui_optimization_candidates,
            'event_handlers': event_handler_candidates,
            'estimated_reduction': 942 + business_logic_count * 20
        }
        
    except Exception as e:
        print(f"❌ Analyse fehlgeschlagen: {e}")
        return None

if __name__ == "__main__":
    result = analyze_customer_code_in_welcome_screen()
    if result:
        print(f"\n✅ Analyse abgeschlossen!")
        print(f"Potentielle Code-Reduktion: ~{result['estimated_reduction']} Zeilen")
    else:
        print(f"\n❌ Analyse fehlgeschlagen!")
