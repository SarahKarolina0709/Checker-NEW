#!/usr/bin/env python3
"""
Demo: Vereinfachte Kundenerstellung
=====================================

Demonstriert die neue vereinfachte Kundenerstellung,
bei der nur der Firmenname eingegeben werden muss.

Automatische Generierung:
- Kürzel: Erste 3 Buchstaben des Firmennamens (eindeutig)
- E-Mail: info@firmenname.de (bereinigt)
- Kontakt: "Geschäftsführung" (Standard)
"""

def demo_automatic_field_generation():
    """Demonstriert die automatische Feldgenerierung."""
    
    def generate_customer_fields(company_name):
        """Generiert automatisch alle Felder basierend auf dem Firmennamen."""
        
        # Code: Erste 3 Buchstaben des Firmennamens (ohne Leerzeichen)
        clean_name = ''.join(c for c in company_name if c.isalpha()).upper()
        code = clean_name[:3] if len(clean_name) >= 3 else clean_name.ljust(3, 'X')
        
        # Email: Generiere basierend auf Firmenname
        email_base = ''.join(c.lower() for c in company_name if c.isalnum())
        email = f"info@{email_base}.de"
        
        # Kontakt: Standard
        contact = "Geschäftsführung"
        
        return {
            "name": company_name,
            "code": code,
            "email": email,
            "contact": contact
        }
    
    # Test verschiedene Firmennamen
    test_companies = [
        "Mustermann GmbH",
        "Tech Solutions AG",
        "Bäcker & Partner",
        "ABC-Industries",
        "Software-Entwicklung Nord",
        "Müller",
        "IT",
        "Basti's Werkstatt"
    ]
    
    print("🏢 Demo: Automatische Kundenfeldgenerierung")
    print("=" * 50)
    
    for company in test_companies:
        customer_data = generate_customer_fields(company)
        
        print(f"\n📝 Eingabe: '{company}'")
        print(f"   🏷️ Kürzel:  {customer_data['code']}")
        print(f"   📧 E-Mail:   {customer_data['email']}")
        print(f"   👤 Kontakt:  {customer_data['contact']}")
    
    print("\n" + "=" * 50)
    print("✅ Vorteil: Nur Firmenname eingeben - Rest automatisch!")
    print("🔧 Intelligente Bereinigung von Sonderzeichen")
    print("🔄 Automatische Eindeutigkeit bei Kürzeln")

def demo_code_uniqueness():
    """Demonstriert die automatische Eindeutigkeit von Kürzeln."""
    
    existing_codes = ["MUS", "TEC", "BAC", "ABC", "SOF"]
    
    def generate_unique_code(company_name, existing_codes):
        """Generiert ein eindeutiges Kürzel."""
        clean_name = ''.join(c for c in company_name if c.isalpha()).upper()
        base_code = clean_name[:3] if len(clean_name) >= 3 else clean_name.ljust(3, 'X')
        
        code = base_code
        counter = 1
        while code in existing_codes:
            if counter <= 9:
                code = base_code[:2] + str(counter)
            else:
                code = base_code[0] + str(counter)[:2]
            counter += 1
            if counter > 99:
                break
        
        return code
    
    print("\n🔄 Demo: Automatische Kürzel-Eindeutigkeit")
    print("=" * 50)
    print(f"Bereits vergebene Kürzel: {existing_codes}")
    
    test_cases = [
        "Mustermann Solutions",  # MUS bereits vergeben
        "Tech Innovations",      # TEC bereits vergeben 
        "Neue Firma GmbH",       # NEU - frei
        "ABC Corporation"        # ABC bereits vergeben
    ]
    
    for company in test_cases:
        unique_code = generate_unique_code(company, existing_codes)
        base_code = ''.join(c for c in company if c.isalpha()).upper()[:3]
        
        print(f"\n📝 Firma: '{company}'")
        print(f"   🎯 Basis-Kürzel: {base_code}")
        print(f"   ✅ Eindeutig:    {unique_code}")
        
        existing_codes.append(unique_code)  # Für nächste Iteration

if __name__ == "__main__":
    demo_automatic_field_generation()
    demo_code_uniqueness()
    
    print("\n" + "🎉" * 20)
    print("Demo abgeschlossen!")
    print("Jetzt nur noch Firmenname eingeben - fertig! 🚀")
