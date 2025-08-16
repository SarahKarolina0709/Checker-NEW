#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔍 SUPER SIMPLE FUZZY MATCH DEBUG
Einfacher Test um herauszufinden warum der Dialog nicht erscheint
"""

import sys
import os
sys.path.append(os.getcwd())

# Light mode enforcement
import customtkinter as ctk
ctk.set_appearance_mode("light")

from customer_manager import CustomerManager
import tkinter as tk

def test_simple_fuzzy():
    """🎯 Super einfacher Test: Erstelle einen Kunden und teste fuzzy match"""
    print("🔍 SIMPLE FUZZY MATCH TEST")
    print("=" * 40)
    
    # CustomerManager testen
    cm = CustomerManager()
    
    # Erstelle Testkunden
    print("📝 Erstelle Testkunden...")
    success, msg, _ = cm.add_customer("hallo")
    print(f"   Add 'hallo': {success} - {msg}")
    
    # Teste fuzzy match
    print("\n🎯 Teste Fuzzy Match für 'halo'...")
    success, msg, similar = cm.add_customer("halo")
    print(f"   Add 'halo': {success} - {msg}")
    print(f"   Similar customers: {similar}")
    
    # Analysiere das Ergebnis
    if not success and similar:
        print("\n✅ FUZZY MATCH ERKANNT!")
        print("   Backend funktioniert korrekt")
        for customer in similar:
            print(f"   - {customer['name']}: {customer['score']}%")
        return True
    else:
        print("\n❌ Kein Fuzzy Match erkannt")
        return False

def test_simple_dialog():
    """🎯 Super einfacher Dialog-Test"""
    print("\n🔍 SIMPLE DIALOG TEST")
    print("=" * 40)
    
    root = ctk.CTk()
    root.title("Simple Dialog Test")
    root.geometry("400x300")
    
    def show_dialog():
        dialog = ctk.CTkToplevel(root)
        dialog.title("Test Dialog")
        dialog.geometry("300x200")
        dialog.transient(root)
        dialog.grab_set()
        
        label = ctk.CTkLabel(dialog, text="Test Dialog funktioniert!")
        label.pack(pady=50)
        
        close_btn = ctk.CTkButton(
            dialog, 
            text="Schließen", 
            command=dialog.destroy
        )
        close_btn.pack(pady=20)
        
        print("✅ Dialog sollte jetzt sichtbar sein")
    
    # Button um Dialog zu öffnen
    test_btn = ctk.CTkButton(
        root, 
        text="Dialog testen", 
        command=show_dialog
    )
    test_btn.pack(pady=50)
    
    print("🎯 Fenster öffnet sich - klicke auf 'Dialog testen'")
    root.mainloop()

if __name__ == "__main__":
    print("🚀 SUPER SIMPLE FUZZY DEBUG TOOL")
    print("=" * 50)
    
    # Test 1: Backend Fuzzy Match
    backend_works = test_simple_fuzzy()
    
    if backend_works:
        print("\n🎯 Backend funktioniert! Teste jetzt Dialog...")
        input("Drücke Enter um Dialog-Test zu starten...")
        test_simple_dialog()
    else:
        print("❌ Backend-Problem! Fuzzy Match funktioniert nicht.")
