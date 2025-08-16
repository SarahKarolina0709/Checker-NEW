#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

try:
    with open('customers.json', 'r', encoding='utf-8') as f:
        customers = json.load(f)
    print('📋 Aktuelle Kunden:')
    for i, customer in enumerate(customers, 1):
        print(f'   {i}. {customer["name"]}')
    print(f'\nAnzahl: {len(customers)} Kunden')
except Exception as e:
    print(f'❌ Fehler: {e}')
