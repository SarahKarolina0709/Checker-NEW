from customer_management_utils import CustomerManager
import os

# Test: Neuen Kunden hinzufügen und Ordner erstellen
cm = CustomerManager()

print('=== Test: Neuer Kunde mit Ordnererstellung ===')

# Neuen Testkunden hinzufügen
new_customer_id = cm.add_new_customer(
    name='Demo Firma',
    code='DEMO',
    company='Demo Firma AG & Co. KG',
    contact='Max Mustermann',
    email='max@demofirma.de'
)

if new_customer_id:
    print(f'Neuer Kunde erstellt:')
    print(f'  ID: {new_customer_id}')
    
    # Ordnername prüfen
    folder_name = cm.get_customer_folder_name(new_customer_id)
    print(f'  Ordnername: {folder_name}')
    
    # Upload-Ordner erstellen
    upload_folder = cm.create_upload_folder(new_customer_id)
    print(f'  Upload-Ordner: {upload_folder}')
    
    # Prüfen ob Ordner existiert
    if os.path.exists(upload_folder):
        print(f'  ✓ Ordner wurde erfolgreich erstellt!')
    else:
        print(f'  ✗ Ordner existiert nicht!')
        
    # Ordnerstruktur anzeigen
    base_path = "Checker_Projekte"
    if os.path.exists(base_path):
        print(f'\n=== Ordnerstruktur in {base_path} ===')
        for item in os.listdir(base_path):
            item_path = os.path.join(base_path, item)
            if os.path.isdir(item_path):
                print(f'  📁 {item}')
else:
    print('Fehler beim Erstellen des Kunden!')
