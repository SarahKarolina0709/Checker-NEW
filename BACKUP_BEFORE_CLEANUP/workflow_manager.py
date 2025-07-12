"""
Centralized Workflow Management for Checker-App
Handles workflow routing, state management, and transitions.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from app_logger import get_logger


class BaseWorkflow(ABC):
    """Base class for all workflows"""
    
    def __init__(self, name: str, app_reference=None):
        self.name = name
        self.app = app_reference
        self.logger = get_logger(f'workflow.{name}')
        self.is_active = False
        self.project_data = None
    
    @abstractmethod
    def start(self, project_data: Optional[Dict[str, Any]] = None):
        """Start the workflow"""
        pass
    
    @abstractmethod
    def create_ui(self, parent_widget):
        """Create the workflow UI"""
        pass
    
    def stop(self):
        """Stop the workflow"""
        self.is_active = False
        self.logger.info(f"Workflow {self.name} stopped")
    
    def cleanup(self):
        """Cleanup workflow resources"""
        self.stop()
        self.logger.debug(f"Workflow {self.name} cleaned up")
    
    def set_project_data(self, project_data: Dict[str, Any]):
        """Set project data for the workflow"""
        self.project_data = project_data
        self.logger.debug(f"Project data set for workflow {self.name}")


class WorkflowManager:
    """Manages all application workflows"""
    
    def __init__(self, app_reference=None):
        self.logger = get_logger('workflow_manager')
        self.app = app_reference
        self.workflows: Dict[str, BaseWorkflow] = {}
        self.current_workflow: Optional[BaseWorkflow] = None
        self.workflow_history = []
        self.transition_callbacks: Dict[str, Callable] = {}
        
        self.logger.info("Workflow manager initialized")
    
    def register_workflow(self, workflow_id: str, workflow_class: type, **kwargs):
        """
        Register a workflow class.
        
        Args:
            workflow_id: Unique identifier for the workflow
            workflow_class: Workflow class (subclass of BaseWorkflow)
            **kwargs: Additional arguments for workflow initialization
        """
        try:
            workflow_instance = workflow_class(
                name=workflow_id,
                app_reference=self.app,
                **kwargs
            )
            self.workflows[workflow_id] = workflow_instance
            self.logger.info(f"Workflow '{workflow_id}' registered")
            
        except Exception as e:
            self.logger.error(f"Failed to register workflow '{workflow_id}': {e}")
            raise
    
    def register_transition_callback(self, event: str, callback: Callable):
        """Register a callback for workflow transitions"""
        self.transition_callbacks[event] = callback
        self.logger.debug(f"Transition callback registered for '{event}'")
    
    def start_workflow(self, workflow_id: str, project_data: Optional[Dict[str, Any]] = None):
        """
        Start a workflow.
        
        Args:
            workflow_id: ID of the workflow to start
            project_data: Optional project data to pass to the workflow
        """
        if workflow_id not in self.workflows:
            self.logger.error(f"Workflow '{workflow_id}' not found")
            raise ValueError(f"Workflow '{workflow_id}' is not registered")
        
        # Stop current workflow if any
        if self.current_workflow:
            self._stop_current_workflow()
        
        # Start new workflow
        workflow = self.workflows[workflow_id]
        
        try:
            # Call pre-transition callback
            if 'before_start' in self.transition_callbacks:
                self.transition_callbacks['before_start'](workflow_id, project_data)
            
            # Start the workflow
            workflow.start(project_data)
            self.current_workflow = workflow
            self.workflow_history.append(workflow_id)
            
            # Call post-transition callback
            if 'after_start' in self.transition_callbacks:
                self.transition_callbacks['after_start'](workflow_id, project_data)
            
            self.logger.info(f"Workflow '{workflow_id}' started successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to start workflow '{workflow_id}': {e}")
            raise
    
    def stop_current_workflow(self):
        """Stop the currently active workflow"""
        if self.current_workflow:
            self._stop_current_workflow()
    
    def _stop_current_workflow(self):
        """Internal method to stop current workflow"""
        if self.current_workflow:
            workflow_id = self.current_workflow.name
            
            # Call pre-stop callback
            if 'before_stop' in self.transition_callbacks:
                self.transition_callbacks['before_stop'](workflow_id)
            
            # Stop workflow
            self.current_workflow.stop()
            
            # Call post-stop callback
            if 'after_stop' in self.transition_callbacks:
                self.transition_callbacks['after_stop'](workflow_id)
            
            self.logger.info(f"Workflow '{workflow_id}' stopped")
            self.current_workflow = None
    
    def get_workflow(self, workflow_id: str) -> Optional[BaseWorkflow]:
        """Get a workflow instance by ID"""
        return self.workflows.get(workflow_id)
    
    def get_current_workflow(self) -> Optional[BaseWorkflow]:
        """Get the currently active workflow"""
        return self.current_workflow
    
    def get_workflow_history(self) -> list:
        """Get the history of started workflows"""
        return self.workflow_history.copy()
    
    def is_workflow_active(self, workflow_id: str) -> bool:
        """Check if a specific workflow is currently active"""
        return (self.current_workflow is not None and 
                self.current_workflow.name == workflow_id)
    
    def cleanup_all_workflows(self):
        """Cleanup all workflows"""
        self.logger.info("Cleaning up all workflows")
        
        if self.current_workflow:
            self._stop_current_workflow()
        
        for workflow in self.workflows.values():
            try:
                workflow.cleanup()
            except Exception as e:
                self.logger.warning(f"Error cleaning up workflow {workflow.name}: {e}")
        
        self.workflows.clear()
        self.workflow_history.clear()
        self.logger.info("All workflows cleaned up")


# Example workflow implementations
class AngebotsWorkflow(BaseWorkflow):
    """Offers analysis workflow"""
    
    
    def start(self, project_data: Optional[Dict[str, Any]] = None):
        self.is_active = True
        self.project_data = project_data
        self.logger.info("Angebots workflow started")
        
        # Create UI in parent
        if self.app and hasattr(self.app, 'content_frame'):
            self.create_ui(self.app.content_frame)
    
    def create_ui(self, parent_widget):
        """Create the offers workflow UI"""
        import customtkinter as ctk
        from ui_theme import UITheme
        
        # Simple placeholder UI
        self.main_frame = ctk.CTkFrame(parent_widget)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="📊 Angebotsanalyse (AC36)",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            self.main_frame,
            text="Hier können Sie Angebote analysieren und bearbeiten.",
            font=ctk.CTkFont(size=16),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.pack(pady=10)
        
        self.logger.debug("Angebots workflow UI created")


class PruefungWorkflow(BaseWorkflow):
    """Review workflow"""
    
    
    def start(self, project_data: Optional[Dict[str, Any]] = None):
        self.is_active = True
        self.project_data = project_data
        self.logger.info("Pruefung workflow started")
        
        if self.app and hasattr(self.app, 'content_frame'):
            self.create_ui(self.app.content_frame)
    
    def create_ui(self, parent_widget):
        """Create the review workflow UI"""
        import customtkinter as ctk
        from ui_theme import UITheme
        
        self.main_frame = ctk.CTkFrame(parent_widget)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="🔍 Prüfung (v1-v5)",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            self.main_frame,
            text="Hier können Sie Übersetzungen prüfen und korrigieren.",
            font=ctk.CTkFont(size=16),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.pack(pady=10)
        
        self.logger.debug("Pruefung workflow UI created")


class FinalisierungWorkflow(BaseWorkflow):
    """Finalization workflow"""
    
    
    def start(self, project_data: Optional[Dict[str, Any]] = None):
        self.is_active = True
        self.project_data = project_data
        self.logger.info("Finalisierung workflow started")
        
        if self.app and hasattr(self.app, 'content_frame'):
            self.create_ui(self.app.content_frame)
    
    def create_ui(self, parent_widget):
        """Create the finalization workflow UI"""
        import customtkinter as ctk
        from ui_theme import UITheme
        
        self.main_frame = ctk.CTkFrame(parent_widget)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="✅ Finalisierung",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            self.main_frame,
            text="Hier können Sie Projekte finalisieren und abschließen.",
            font=ctk.CTkFont(size=16),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.pack(pady=10)
        
        self.logger.debug("Finalisierung workflow UI created")


class ProjektWorkflow(BaseWorkflow):
    """Project overview workflow"""
    
    
    def start(self, project_data: Optional[Dict[str, Any]] = None):
        self.is_active = True
        self.project_data = project_data
        self.logger.info("Projekt workflow started")
        
        if self.app and hasattr(self.app, 'content_frame'):
            self.create_ui(self.app.content_frame)
    
    def create_ui(self, parent_widget):
        """Create the project workflow UI"""
        import customtkinter as ctk
        from ui_theme import UITheme
        
        self.main_frame = ctk.CTkFrame(parent_widget)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            self.main_frame,
            text="📋 Projektübersicht",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=UITheme.COLOR_TEXT_PRIMARY
        )
        title_label.pack(pady=20)
        
        info_label = ctk.CTkLabel(
            self.main_frame,
            text="Hier können Sie Ihre Projekte verwalten und überwachen.",
            font=ctk.CTkFont(size=16),
            text_color=UITheme.COLOR_TEXT_SECONDARY
        )
        info_label.pack(pady=10)
        
        self.logger.debug("Projekt workflow UI created")
