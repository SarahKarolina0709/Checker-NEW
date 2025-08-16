# -*- coding: utf-8 -*-
import os
import sys
import shutil
from datetime import datetime

# Ensure we import from workspace root
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import customtkinter as ctk

# Import the welcome screen module
from welcome_screen import WelcomeScreen


def assert_true(cond, msg):
    if not cond:
        raise AssertionError(msg)


def main():
    # Prepare temp project base within workspace to avoid touching user's real folder
    temp_projects_base = os.path.join(BASE_DIR, 'TMP_Checker_Projekte_Test')
    if os.path.isdir(temp_projects_base):
        shutil.rmtree(temp_projects_base, ignore_errors=True)
    os.makedirs(temp_projects_base, exist_ok=True)

    # Prepare a temp upload source file
    temp_src_dir = os.path.join(BASE_DIR, 'TMP_source_files')
    os.makedirs(temp_src_dir, exist_ok=True)
    src_file = os.path.join(temp_src_dir, 'test_upload.txt')
    with open(src_file, 'w', encoding='utf-8') as f:
        f.write('hello checker')

    # Create minimal CTk root and WelcomeScreen
    root = ctk.CTk()
    root.withdraw()  # hide window during test

    class _DummyApp:
        pass

    app = _DummyApp()
    screen = WelcomeScreen(root, app)

    # Point to temp projects base and ensure path resolution is stable
    screen.projects_base_path = temp_projects_base
    if hasattr(screen, '_save_configuration'):
        try:
            screen._save_configuration()
        except Exception:
            pass

    # 1) Create a new customer
    customer_name = 'NeuCorp'
    screen._create_new_customer(customer_name)
    assert_true(screen.current_customer == customer_name, 'Customer selection after create failed')
    assert_true(any((c.get('name') if isinstance(c, dict) else c) == customer_name for c in (screen.customers_data or [])),
                'Customer not added to customers_data')

    # 2) Fuzzy search should find the new customer
    matches = screen._fuzzy_search_customers('neu')
    names = [m.get('name') if isinstance(m, dict) else str(m) for m in (matches or [])]
    assert_true(any(n.lower() == customer_name.lower() for n in names), 'Fuzzy search did not return the new customer')

    # 3) Copy uploaded file into the customer's dated input folder
    screen.uploaded_files = [src_file]
    screen._copy_files_to_customer_folder(screen.uploaded_files)

    today = datetime.now().strftime('%Y-%m-%d')
    dest_path = os.path.join(temp_projects_base, customer_name, today, '01_Ausgangstext', os.path.basename(src_file))
    assert_true(os.path.exists(dest_path), f'Uploaded file not found at expected destination: {dest_path}')

    print('✅ Customer flow smoke test passed: create + fuzzy + file placement OK')

    # Cleanup temp windows & root
    try:
        root.destroy()
    except Exception:
        pass

    # Clean temp dirs (leave for inspection if needed)
    # shutil.rmtree(temp_src_dir, ignore_errors=True)
    # shutil.rmtree(temp_projects_base, ignore_errors=True)


if __name__ == '__main__':
    main()
