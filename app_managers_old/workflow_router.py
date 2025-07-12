"""
Workflow Router - Manages workflow initialization, routing and state
Extracted from CheckerApp to improve separation of concerns
"""

import logging
from typing import Dict, Optional, Any
import customtkinter as ctk


class WorkflowRouter:
    """Manages workflow routing and state management"""
    
    def __init__(self, app_instance):
        self.app = app_instance
        self.logger = logging.getLogger("WorkflowRouter")
        self.workflows: Dict[str, Any] = {}
        self.workflow_stack = ctk.CTkFrame(app_instance.root)
        self.workflow_stack.pack(fill="both", expand=True)
        self.current_workflow: Optional[str] = None
        
        # Initialize workflow status
        self.workflow_status = {
            'current_workflow': None,
            'workflow_history': [],
            'last_project_data': None
        }
    
    def initialize_workflows(self):
        """Initialisiert alle verfügbaren Workflows"""
        try:
            self.logger.info("[WORKFLOW_ROUTER] Initializing workflows...")
            
            # Initialize workflow instances with enhanced error handling
            self._init_angebots_workflow()
            self._init_pruefung_workflow()
            self._init_finalisierung_workflow()
            self._init_projekt_workflow()
            
            workflows_count = len(self.workflows)
            self.logger.info(f"[WORKFLOW_ROUTER] {workflows_count} workflows initialized successfully")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_ROUTER] Error initializing workflows: {e}")
            # Ensure workflows dict exists even on error
            if not self.workflows:
                self.workflows = {}
    
    def _init_angebots_workflow(self):
        """Initialisiert den Angebots-Workflow"""
        try:
            from angebots_workflow import AngebotsanalyseWorkflow
            
            workflow_frame = ctk.CTkFrame(self.workflow_stack)
            workflow = AngebotsanalyseWorkflow(
                root=workflow_frame,
                app=self.app,
                back_to_welcome_callback=self.app.return_to_welcome
            )
            
            if workflow is not None:
                self.workflows['angebots_workflow'] = {
                    'instance': workflow,
                    'frame': workflow_frame,
                    'name': 'Angebotsanalyse'
                }
                # Initially hide
                workflow_frame.pack_forget()
                self.logger.info("[WORKFLOW_ROUTER] Angebots workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_ROUTER] Angebots workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_ROUTER] Could not initialize angebots_workflow: {e}")
            self._create_stub_workflow('angebots_workflow', 'Angebotsanalyse')
    
    def _init_pruefung_workflow(self):
        """Initialisiert den Prüfungs-Workflow"""
        try:
            from pruefung_workflow import PruefungWorkflow
            
            workflow_frame = ctk.CTkFrame(self.workflow_stack)
            workflow = PruefungWorkflow(
                parent=workflow_frame,
                app=self.app,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['pruefung_workflow'] = {
                    'instance': workflow,
                    'frame': workflow_frame,
                    'name': 'Dateiprüfung'
                }
                workflow_frame.pack_forget()
                self.logger.info("[WORKFLOW_ROUTER] Pruefung workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_ROUTER] Pruefung workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_ROUTER] Could not initialize pruefung_workflow: {e}")
            self._create_stub_workflow('pruefung_workflow', 'Dateiprüfung')
    
    def _init_finalisierung_workflow(self):
        """Initialisiert den Finalisierungs-Workflow"""
        try:
            from finalisierung_workflow2 import FinalisierungsWorkflow
            
            workflow_frame = ctk.CTkFrame(self.workflow_stack)
            workflow = FinalisierungsWorkflow(
                parent=workflow_frame,
                app=self.app,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['finalisierung_workflow'] = {
                    'instance': workflow,
                    'frame': workflow_frame,
                    'name': 'Finalisierung'
                }
                workflow_frame.pack_forget()
                self.logger.info("[WORKFLOW_ROUTER] Finalisierung workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_ROUTER] Finalisierung workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_ROUTER] Could not initialize finalisierung_workflow: {e}")
            self._create_stub_workflow('finalisierung_workflow', 'Finalisierung')
    
    def _init_projekt_workflow(self):
        """Initialisiert den Projekt-Workflow"""
        try:
            from projekt_workflow import ProjektWorkflow
            
            workflow_frame = ctk.CTkFrame(self.workflow_stack)
            workflow = ProjektWorkflow(
                parent=workflow_frame,
                app=self.app,
                project_data={}
            )
            
            if workflow is not None:
                self.workflows['projekt_workflow'] = {
                    'instance': workflow,
                    'frame': workflow_frame,
                    'name': 'Projektübersicht'
                }
                workflow_frame.pack_forget()
                self.logger.info("[WORKFLOW_ROUTER] Projekt workflow initialized")
            else:
                self.logger.warning("[WORKFLOW_ROUTER] Projekt workflow returned None")
                
        except Exception as e:
            self.logger.warning(f"[WORKFLOW_ROUTER] Could not initialize projekt_workflow: {e}")
            self._create_stub_workflow('projekt_workflow', 'Projektübersicht')
    
    def _create_stub_workflow(self, workflow_name: str, display_name: str):
        """Erstellt einen Stub-Workflow als Fallback"""
        try:
            workflow_frame = ctk.CTkFrame(self.workflow_stack)
            
            # Add a simple message
            message_label = ctk.CTkLabel(
                workflow_frame,
                text=f"{display_name} wird geladen...",
                font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold")
            )
            message_label.pack(expand=True, fill="both", padx=50, pady=50)
            
            # Add a back button
            back_button = ctk.CTkButton(
                workflow_frame,
                text="Zurück zur Übersicht",
                command=self.app.return_to_welcome,
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold")
            )
            back_button.pack(pady=20)
            
            # Store the stub
            self.workflows[workflow_name] = {
                'instance': None,
                'frame': workflow_frame,
                'name': display_name
            }
            workflow_frame.pack_forget()
            
            self.logger.info(f"[WORKFLOW_ROUTER] Created stub for {workflow_name}")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_ROUTER] Error creating stub for {workflow_name}: {e}")
    
    def start_workflow(self, workflow_name: str, confirm: bool = False) -> bool:
        """Starts a workflow with improved state management"""
        try:
            # Bei Keyboard-Shortcuts: Bestätigung anfordern
            if confirm:
                workflow_names = {
                    'angebots_workflow': 'Angebotsanalyse',
                    'pruefung_workflow': 'Dateiprüfung', 
                    'finalisierung_workflow': 'Finalisierung',
                    'projekt_workflow': 'Projektübersicht'
                }
                
                from tkinter import messagebox
                workflow_display_name = workflow_names.get(workflow_name, workflow_name)
                result = messagebox.askyesno(
                    "Workflow starten", 
                    f"Möchten Sie den Workflow '{workflow_display_name}' starten?"
                )
                
                if not result:
                    self.logger.info(f"[WORKFLOW_ROUTER] User cancelled workflow start: {workflow_name}")
                    return False
            
            # Check if workflow exists
            if workflow_name not in self.workflows:
                if hasattr(self.app, 'notification_center'):
                    self.app.notification_center.show_notification(
                        f"Workflow '{workflow_name}' nicht verfügbar", "warning"
                    )
                self.logger.warning(f"[WORKFLOW_ROUTER] Workflow not found: {workflow_name}")
                return False
            
            # Hide welcome screen
            if hasattr(self.app, 'welcome_screen') and self.app.welcome_screen:
                self.app.welcome_screen.pack_forget()
            
            # Hide current workflow if any
            if self.current_workflow and self.current_workflow in self.workflows:
                self.workflows[self.current_workflow]['frame'].pack_forget()
            
            # Show the requested workflow using the stack system
            workflow_info = self.workflows[workflow_name]
            workflow_frame = workflow_info['frame']
            workflow_instance = workflow_info['instance']
            
            # Show the workflow frame
            workflow_frame.pack(fill="both", expand=True)
            
            # Initialize workflow if it has a show method
            if hasattr(workflow_instance, 'show_workflow'):
                workflow_instance.show_workflow()
            
            # Update current workflow
            self.current_workflow = workflow_name
            self.workflow_status['current_workflow'] = workflow_name
            self.workflow_status['workflow_history'].append(workflow_name)
            
            # Update status
            if hasattr(self.app, '_update_status'):
                self.app._update_status(f"Workflow '{workflow_name}' gestartet", "info")
            
            self.logger.info(f"[WORKFLOW_ROUTER] Started workflow: {workflow_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_ROUTER] Error starting workflow {workflow_name}: {e}")
            if hasattr(self.app, 'notification_center'):
                self.app.notification_center.show_notification(
                    f"Fehler beim Starten des Workflows: {e}", "error"
                )
            return False
    
    def show_welcome_screen(self):
        """Shows the welcome screen and hides all workflows"""
        try:
            # Hide current workflow
            if self.current_workflow and self.current_workflow in self.workflows:
                self.workflows[self.current_workflow]['frame'].pack_forget()
            
            # Show welcome screen
            if hasattr(self.app, 'welcome_screen') and self.app.welcome_screen:
                self.app.welcome_screen.pack(fill="both", expand=True)
            
            # Update state
            self.current_workflow = None
            self.workflow_status['current_workflow'] = None
            
            self.logger.info("[WORKFLOW_ROUTER] Welcome screen shown")
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW_ROUTER] Error showing welcome screen: {e}")
    
    @property
    def workflow_routes(self):
        """Returns workflow routes for the welcome screen"""
        return {
            'angebots_workflow': {
                'name': 'Angebotsanalyse',
                'icon': 'euro-money-2',
                'description': 'Erstelle professionelle Angebote',
                'callback': lambda: self.start_workflow('angebots_workflow')
            },
            'pruefung_workflow': {
                'name': 'Dateiprüfung',
                'icon': 'check',
                'description': 'Prüfe Übersetzungen auf Qualität',
                'callback': lambda: self.start_workflow('pruefung_workflow')
            },
            'finalisierung_workflow': {
                'name': 'Finalisierung',
                'icon': 'success',
                'description': 'Finalisiere Projekte',
                'callback': lambda: self.start_workflow('finalisierung_workflow')
            },
            'projekt_workflow': {
                'name': 'Projektübersicht',
                'icon': 'project',
                'description': 'Verwalte deine Projekte',
                'callback': lambda: self.start_workflow('projekt_workflow')
            }
        }
