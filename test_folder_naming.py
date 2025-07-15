from customer_management_utils import CustomerManager
import json

# Test der neuen Funktionalität
cm = CustomerManager()

# Lade aktuelle Kunden
print('=== Aktuelle Kunden ===')
for customer_id, data in cm.customers_data.items():
    folder_name = cm.get_customer_folder_name(customer_id)
    print(f'ID: {customer_id}')
    print(f'  Name: {data.get("name", "N/A")}')
    print(f'  Company: {data.get("company", "N/A")}')
    print(f'  Code: {data.get("code", "N/A")}')
    print(f'  -> Ordnername: {folder_name}')
    print()

# Test: Sonderzeichen Bereinigung
print('=== Test: Sonderzeichen Bereinigung ===')
test_names = [
    'Müller & Co. KG',
    'Test-Firma AG',
    'Bäckerei Süß/Sauer',
    'IT Solutions: Next Level',
    'A-Z Handel GmbH & Co.'
]

for name in test_names:
    clean_name = cm._sanitize_folder_name(name)
    print(f'Original: "{name}"')
    print(f'Bereinigt: "{clean_name}"')
    print()
