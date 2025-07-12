# Reparatur für show_customer_menu Methode

def show_customer_menu(self):
    """Zeige moderne Kundenverwaltungs-GUI."""
    try:
        print("[DEBUG] show_customer_menu called - using ModernCustomerGUI")
        
        # Prüfe ob die App noch läuft
        if not hasattr(self, 'root') or not self.root:
            print("[DEBUG] App ist nicht initialisiert")
            return
        
        # Verwende neue moderne GUI
        self.show_modern_customer_gui()
        
    except Exception as e:
        print(f"[DEBUG] FEHLER in show_customer_menu: {e}")
        import traceback
        traceback.print_exc()
        if hasattr(self, 'notification_center'):
            self.notification_center.show_notification(f"Customer Menu Fehler: {str(e)}", "error")
