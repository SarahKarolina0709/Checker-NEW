import customtkinter as ctk
from ultra_modern_welcome_screen_v2 import UltraModernWelcomeScreen
from PIL import Image, ImageDraw
import os

class MockApp:
    """Eine Mock-App-Klasse, die das Verhalten der Hauptanwendung simuliert,
    insbesondere das Laden von Icons."""
    def __init__(self, root):
        self.root = root
        self.icon_cache = {}
        # Pfad zu den Icons (angenommen, sie sind im selben Verzeichnis)
        self.icon_path = os.path.dirname(os.path.abspath(__file__))

    def get_icon(self, name, size=(20, 20)):
        """Lädt ein Icon oder erstellt ein Platzhalter-Icon, wenn es nicht gefunden wird."""
        # Versuche, ein echtes Icon zu laden, um das UI besser zu testen
        try:
            icon_file = os.path.join(self.icon_path, "icons", f"{name}.png") # Standard-Icon-Verzeichnis
            if os.path.exists(icon_file):
                image = Image.open(icon_file).resize(size, Image.LANCZOS)
                ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=size)
                self.icon_cache[name] = ctk_image
                return ctk_image
        except Exception as e:
            print(f"Konnte Icon nicht laden {name}: {e}")

        # Fallback: Erstelle ein einfaches Platzhalter-Rechteck, wenn das Icon fehlt
        placeholder = Image.new('RGBA', size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(placeholder)
        draw.rectangle((0, 0, size[0] - 1, size[1] - 1), outline="gray", width=1)
        ctk_image = ctk.CTkImage(light_image=placeholder, dark_image=placeholder, size=size)
        self.icon_cache[name] = ctk_image
        return ctk_image

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Final Welcome Screen Test")
        self.geometry("1400x900") # Größeres Fenster für eine bessere Übersicht

        # Erstelle eine Mock-App-Instanz, die die Haupt-App simuliert
        self.mock_app_instance = MockApp(self)

        # Mock-Callback-Funktion, um die Interaktion zu protokollieren
        def mock_app_callback(workflow_type, customer_data):
            print(f"WORKFLOW GESTARTET: Typ='{workflow_type}', Kundendaten={customer_data}")

        # Initialisiere den Welcome Screen mit den korrekten Argumenten
        self.welcome_screen = UltraModernWelcomeScreen(
            master=self, # Korrektes master-Argument
            app=self.mock_app_instance,
            app_callback=mock_app_callback
        )
        self.welcome_screen.pack(expand=True, fill="both")

if __name__ == "__main__":
    # Erstelle das Icon-Verzeichnis, falls es nicht existiert
    if not os.path.exists("icons"):
        os.makedirs("icons")
    app = App()
    app.mainloop()
