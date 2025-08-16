"""
Angebots-Workflow
"""
import logging

class AngebotsWorkflow:
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger(__name__)

    def run(self):
        self.logger.info("Angebots-Workflow wird ausgeführt.")
        # Hier würde die eigentliche Workflow-Logik stehen
        self.app.notification_center.show_info("Workflow", "Angebots-Workflow gestartet.")
        # Nach Abschluss zurück zum Welcome-Screen
        self.app.workflow_router.return_to_welcome()