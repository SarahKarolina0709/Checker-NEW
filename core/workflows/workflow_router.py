"""
WorkflowRouter for the Modular CheckerApp Architecture

Manages workflow initialization, routing, and state management.
"""
import logging
from tkinter import messagebox
from typing import Dict, Any, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from core.app import CheckerApp

# Import structured logging
try:
    from structured_logging import WorkflowLogger
except ImportError:
    logging.warning("Structured logging not available - falling back to standard logging")
    WorkflowLogger = None

class WorkflowRouter:
    """
    Manages workflow initialization, routing, and state management.
    Provides a clear, centralized control for all application workflows.
    """
    
    def __init__(self, app: 'CheckerApp') -> None:
        """Initialize the workflow router."""
        self.app = app
        
        if WorkflowLogger:
            self.logger = WorkflowLogger(f"{__name__}.WorkflowRouter")
        else:
            self.logger = logging.getLogger(f"{__name__}.WorkflowRouter")
        
        self.workflows: Dict[str, Any] = {}
        self.active_workflow: Optional[str] = None
        
        self._register_workflows()
        
    def _register_workflows(self) -> None:
        """Register all available workflows."""
        try:
            # TODO: Restore the missing workflow files: angebots_workflow.py, finalisierung_workflow.py
            # The files seem to have been deleted. They need to be restored from a backup or git history.
            # from .angebots_workflow import AngebotsanalyseWorkflow
            from .pruefung_workflow import PruefungWorkflow
            # from .finalisierung_workflow import FinalisierungWorkflow
            from .projekt_workflow import ProjektWorkflow
            
            self.workflows = {
                # "angebots_workflow": AngebotsanalyseWorkflow,
                "pruefung_workflow": PruefungWorkflow,
                # "finalisierung_workflow": FinalisierungWorkflow,
                "projekt_workflow": ProjektWorkflow,
            }
            self.logger.info(f"Registered {len(self.workflows)} workflows successfully (some may be disabled)")
            
        except ImportError as e:
            self.logger.error(f"Error registering workflows: {e}")
            messagebox.showerror("Fehler bei Workflow-Registrierung", 
                                 f"Einige Workflows konnten nicht geladen werden: {e}")
        except Exception as e:
            self.logger.error(f"An unexpected error occurred during workflow registration: {e}")
            messagebox.showerror("Kritischer Fehler", 
                                 "Ein unerwarteter Fehler ist bei der Workflow-Registrierung aufgetreten.")

    def start_workflow(self, workflow_name: str, confirm: bool = False, **kwargs: Any) -> None:
        """Start a workflow by name."""
        if workflow_name not in self.workflows:
            self.logger.error(f"Workflow '{workflow_name}' not found.")
            if hasattr(self.app, 'notification_center'):
                self.app.notification_center.show_error(
                    "Workflow nicht gefunden",
                    f"Der angeforderte Workflow '{workflow_name}' ist nicht registriert."
                )
            return

        if confirm:
            result = messagebox.askyesno(
                "Workflow starten",
                f"Möchten Sie den '{workflow_name.replace('_', ' ').title()}' starten?"
            )
            if not result:
                self.logger.info(f"Workflow '{workflow_name}' start cancelled by user.")
                return
        
        try:
            self.logger.info(f"Starting workflow: {workflow_name}")
            self.active_workflow = workflow_name
            
            # Get workflow class
            workflow_class = self.workflows[workflow_name]
            
            # Initialize and run the workflow
            workflow_instance = workflow_class(self.app, **kwargs)
            workflow_instance.run()
            
            if hasattr(self.app, 'ui_initializer'):
                self.app.ui_initializer.update_status(
                    f"Workflow '{workflow_name}' gestartet", "loading"
                )
            
        except Exception as e:
            self.logger.error(f"Error starting workflow '{workflow_name}': {e}")
            if hasattr(self.app, 'error_monitor'):
                self.app.error_monitor.handle_error(
                    f"Fehler beim Starten von '{workflow_name}'", e
                )

    def return_to_welcome(self) -> None:
        """Return to the welcome screen, clearing any active workflow."""
        try:
            if self.active_workflow:
                self.logger.info(f"Returning to welcome screen from '{self.active_workflow}'")
                self.active_workflow = None
            
            # Clear main container
            if hasattr(self.app, 'ui_manager') and hasattr(self.app.ui_manager, 'main_container'):
                for widget in self.app.ui_manager.main_container.winfo_children():
                    widget.destroy()
            
            # Show welcome screen if available
            if hasattr(self.app, 'welcome_screen') and self.app.welcome_screen:
                self.app.welcome_screen.show()
            elif hasattr(self.app, 'create_welcome_screen'):
                self.app.create_welcome_screen()

            # Update status if notification center is available
            if hasattr(self.app, 'notification_center'):
                self.app.notification_center.update_status("Bereit", "success")
                
        except Exception as e:
            self.logger.error(f"Error returning to welcome screen: {e}")

    def get_active_workflow(self) -> Optional[str]:
        """Return the name of the active workflow."""
        return self.active_workflow
