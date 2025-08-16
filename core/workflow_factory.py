"""
Workflow Factory System for Checker Application
==============================================

This module provides a unified workflow creation and management system
to replace the inconsistent workflow instantiation patterns found in
the logic review. It ensures consistent workflow lifecycle management.

Priority 3 Implementation from Logic Review Report
"""

from typing import Dict, Any, Optional, Type, Protocol, Set
import logging
import threading

from .state_manager import StateManager, WorkflowState
from .thread_manager import ThreadManager
from dataclasses import dataclass
from enum import Enum
import importlib

class WorkflowType(Enum):
    """Supported workflow types."""
    PRUEFUNG = "pruefung"
    ANGEBOTS = "angebots"
    PROJEKT = "projekt"
    FINALISIERUNG = "finalisierung"
    EXPORT = "export"
    KI_PRUEFUNG = "ki_pruefung"
    QUALITY = "quality"


class WorkflowLifecycle(Enum):
    """Workflow lifecycle management strategies."""
    ALWAYS_NEW = "always_new"  # Create new instance every time
    REUSE = "reuse"           # Reuse existing instance
    CONDITIONAL = "conditional"  # Conditional based on state


@dataclass
class WorkflowConfig:
    """Configuration for workflow creation."""
    workflow_type: WorkflowType
    module_name: str
    class_name: str
    lifecycle: WorkflowLifecycle
    requires_project_data: bool = False
    lazy_load: bool = True
    daemon_threads: bool = True
    max_instances: int = 1


class WorkflowProtocol(Protocol):
    """Protocol that all workflows should implement."""

    def show_workflow(self, project_data: Optional[Dict[str, Any]] = None) -> None:
        """Display the workflow UI."""
        ...

    def hide_workflow(self) -> None:
        """Hide the workflow UI."""
        ...

    def cleanup(self) -> None:
        """Cleanup workflow resources."""
        ...

    def get_state(self) -> Dict[str, Any]:
        """Get workflow state."""
        ...

    def set_state(self, state: Dict[str, Any]) -> None:
        """Set workflow state."""
        ...


class WorkflowInstance:
    """Wrapper for workflow instances with metadata."""

    def __init__(self, workflow_type: WorkflowType, instance: Any, config: WorkflowConfig):
        self.workflow_type = workflow_type
        self.instance = instance
        self.config = config
        self.created_at = threading.current_thread().ident
        self.usage_count = 0
        self.last_used = 0
        self.is_active = False

    def use(self):
        """Mark as used and increment counter."""
        self.usage_count += 1
        self.last_used = threading.current_thread().ident
        self.is_active = True

    def release(self):
        """Mark as released."""
        self.is_active = False


class WorkflowFactory:
    """
    Centralized workflow factory and lifecycle manager.

    Features:
    - Unified workflow creation
    - Lifecycle management (always new, reuse, conditional)
    - Lazy loading with error handling
    - Resource cleanup
    - Thread safety
    - Configuration-driven
    """

    _instance: Optional['WorkflowFactory'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'WorkflowFactory':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the workflow factory."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._instances: Dict[WorkflowType, WorkflowInstance] = {}
        self._loaded_modules: Dict[str, Any] = {}
        self._instance_lock = threading.RLock()

        # State and thread managers
        self._state_manager = StateManager.get_instance()
        self._thread_manager = ThreadManager.get_instance()

        # Setup logging
        self._logger = logging.getLogger(__name__)

        # Configure workflows
        self._configs = self._setup_workflow_configs()

    @classmethod
    def get_instance(cls) -> 'WorkflowFactory':
        """Get the singleton instance."""
        return cls()

    def _setup_workflow_configs(self) -> Dict[WorkflowType, WorkflowConfig]:
        """Setup workflow configurations."""
        return {
            WorkflowType.PRUEFUNG: WorkflowConfig(
                workflow_type=WorkflowType.PRUEFUNG,
                module_name="pruefung_workflow_ctk",
                class_name="PruefungWorkflowCTK",
                lifecycle=WorkflowLifecycle.ALWAYS_NEW,  # Always create new for fresh state
                requires_project_data=True
            ),
            WorkflowType.ANGEBOTS: WorkflowConfig(
                workflow_type=WorkflowType.ANGEBOTS,
                module_name="angebots_workflow",
                class_name="AngebotsanalyseWorkflow",
                lifecycle=WorkflowLifecycle.REUSE,  # Can reuse instance
                requires_project_data=False
            ),
            WorkflowType.PROJEKT: WorkflowConfig(
                workflow_type=WorkflowType.PROJEKT,
                module_name="projekt_workflow",
                class_name="ProjektWorkflow",
                lifecycle=WorkflowLifecycle.REUSE,
                requires_project_data=True
            ),
            WorkflowType.FINALISIERUNG: WorkflowConfig(
                workflow_type=WorkflowType.FINALISIERUNG,
                module_name="finalisierung_workflow",
                class_name="FinalisierungWorkflow",
                lifecycle=WorkflowLifecycle.CONDITIONAL,  # Conditional based on project state
                requires_project_data=True
            ),
            WorkflowType.EXPORT: WorkflowConfig(
                workflow_type=WorkflowType.EXPORT,
                module_name="export",
                class_name="ExportWorkflow",
                lifecycle=WorkflowLifecycle.ALWAYS_NEW,  # New for each export
                requires_project_data=True
            ),
            WorkflowType.KI_PRUEFUNG: WorkflowConfig(
                workflow_type=WorkflowType.KI_PRUEFUNG,
                module_name="ki_module",
                class_name="KIQualitaetspruefung",
                lifecycle=WorkflowLifecycle.REUSE,
                requires_project_data=True,
                lazy_load=True  # Prevent hanging on import
            ),
        }

    def create_workflow(self,
                       workflow_type: WorkflowType,
                       root_widget: Any,
                       back_callback: callable,
                       project_data: Optional[Dict[str, Any]] = None,
                       force_new: bool = False) -> Optional[Any]:
        """
        Create or get a workflow instance.

        Args:
            workflow_type: Type of workflow to create
            root_widget: Parent widget for the workflow UI
            back_callback: Callback for returning to previous screen
            project_data: Project data if required
            force_new: Force creation of new instance

        Returns:
            Workflow instance or None if creation failed
        """
        with self._instance_lock:
            config = self._configs.get(workflow_type)
            if not config:
                self._logger.error(f"Unknown workflow type: {workflow_type}")
                return None

            # Check if we should create new instance
            should_create_new = (
                force_new or
                config.lifecycle == WorkflowLifecycle.ALWAYS_NEW or
                workflow_type not in self._instances or
                (config.lifecycle == WorkflowLifecycle.CONDITIONAL and
                 self._should_create_new_conditional(workflow_type, project_data))
            )

            if not should_create_new and workflow_type in self._instances:
                # Reuse existing instance
                instance_wrapper = self._instances[workflow_type]
                instance_wrapper.use()

                # Update state manager
                self._state_manager.register_workflow(workflow_type.value, instance_wrapper.instance)
                self._state_manager.update_workflow_state(workflow_type.value, WorkflowState.ACTIVE)

                self._logger.debug(f"Reusing workflow instance: {workflow_type.value}")
                return instance_wrapper.instance

            # Create new instance
            try:
                instance = self._create_new_instance(
                    config, root_widget, back_callback, project_data
                )

                if instance:
                    # Wrap and store instance
                    wrapper = WorkflowInstance(workflow_type, instance, config)
                    wrapper.use()
                    self._instances[workflow_type] = wrapper

                    # Register with state manager
                    self._state_manager.register_workflow(workflow_type.value, instance)
                    self._state_manager.update_workflow_state(workflow_type.value, WorkflowState.ACTIVE)

                    self._logger.info(f"Created new workflow instance: {workflow_type.value}")
                    return instance

            except Exception as e:
                self._logger.error(f"Failed to create workflow {workflow_type.value}: {e}")
                self._state_manager.update_workflow_state(workflow_type.value, WorkflowState.ERROR)
                return None

            return None

    def _create_new_instance(self,
                           config: WorkflowConfig,
                           root_widget: Any,
                           back_callback: callable,
                           project_data: Optional[Dict[str, Any]]) -> Optional[Any]:
        """Create a new workflow instance."""

        # Load module if needed
        module = self._load_module(config.module_name, config.lazy_load)
        if not module:
            return None

        # Get workflow class
        workflow_class = getattr(module, config.class_name, None)
        if not workflow_class:
            self._logger.error(f"Class {config.class_name} not found in {config.module_name}")
            return None

        # Prepare constructor arguments
        kwargs = {
            "root": root_widget,
            "back_callback": back_callback
        }

        # Add project data if required
        if config.requires_project_data and project_data:
            kwargs["project_data"] = project_data

        # Handle specific workflow constructor patterns
        if config.workflow_type == WorkflowType.ANGEBOTS:
            kwargs["back_to_welcome_callback"] = back_callback
            if "back_callback" in kwargs:
                del kwargs["back_callback"]

        # Create instance
        try:
            instance = workflow_class(**kwargs)
            return instance

        except Exception as e:
            self._logger.error(f"Failed to instantiate {config.class_name}: {e}")
            return None

    def _load_module(self, module_name: str, lazy_load: bool = True) -> Optional[Any]:
        """Load a module with optional lazy loading."""

        if module_name in self._loaded_modules:
            return self._loaded_modules[module_name]

        try:
            if lazy_load and module_name == "ki_module":
                # Special handling for ki_module to prevent hanging
                def load_ki_module():
                    try:
                        module = importlib.import_module(module_name)
                        self._loaded_modules[module_name] = module
                        return module
                    except Exception as e:
                        self._logger.error(f"Failed to load {module_name}: {e}")
                        return None

                # Load in background thread
                thread_name = f"load-{module_name}"
                self._thread_manager.start_thread(
                    name=thread_name,
                    target=load_ki_module,
                    daemon=True
                )

                # Wait with timeout
                if self._thread_manager.wait_for_thread(thread_name, timeout=10.0):
                    return self._loaded_modules.get(module_name)
                else:
                    self._logger.warning(f"Timeout loading {module_name}")
                    return None
            else:
                # Regular synchronous loading
                module = importlib.import_module(module_name)
                self._loaded_modules[module_name] = module
                return module

        except Exception as e:
            self._logger.error(f"Failed to load module {module_name}: {e}")
            return None

    def _should_create_new_conditional(self,
                                     workflow_type: WorkflowType,
                                     project_data: Optional[Dict[str, Any]]) -> bool:
        """Determine if a new instance should be created based on conditions."""

        if workflow_type == WorkflowType.FINALISIERUNG:
            # Create new if project data changed significantly
            current_project = self._state_manager.get_project_data()
            if not current_project or not project_data:
                return True

            # Compare relevant fields
            key_fields = ["name", "path", "type", "version"]
            for field in key_fields:
                if current_project.get(field) != project_data.get(field):
                    return True

            return False

        # Default to creating new
        return True

    def release_workflow(self, workflow_type: WorkflowType) -> bool:
        """Release a workflow instance."""
        with self._instance_lock:
            if workflow_type in self._instances:
                wrapper = self._instances[workflow_type]
                wrapper.release()

                # Update state manager
                self._state_manager.update_workflow_state(workflow_type.value, WorkflowState.INACTIVE)

                # Cleanup if needed
                if hasattr(wrapper.instance, 'cleanup'):
                    try:
                        wrapper.instance.cleanup()
                    except Exception as e:
                        self._logger.error(f"Error during workflow cleanup: {e}")

                self._logger.debug(f"Released workflow: {workflow_type.value}")
                return True

            return False

    def cleanup_workflow(self, workflow_type: WorkflowType) -> bool:
        """Cleanup and remove a workflow instance."""
        with self._instance_lock:
            if workflow_type in self._instances:
                wrapper = self._instances[workflow_type]

                # Cleanup instance
                if hasattr(wrapper.instance, 'cleanup'):
                    try:
                        wrapper.instance.cleanup()
                    except Exception as e:
                        self._logger.error(f"Error during workflow cleanup: {e}")

                # Remove from instances
                del self._instances[workflow_type]

                # Update state manager
                self._state_manager.unregister_workflow(workflow_type.value)

                self._logger.info(f"Cleaned up workflow: {workflow_type.value}")
                return True

            return False

    def cleanup_all_workflows(self):
        """Cleanup all workflow instances."""
        with self._instance_lock:
            workflow_types = list(self._instances.keys())
            for workflow_type in workflow_types:
                self.cleanup_workflow(workflow_type)

            self._logger.info("Cleaned up all workflows")

    def get_active_workflows(self) -> Set[WorkflowType]:
        """Get set of active workflow types."""
        with self._instance_lock:
            return {wf_type for wf_type, wrapper in self._instances.items() if wrapper.is_active}

    def get_workflow_instance(self, workflow_type: WorkflowType) -> Optional[Any]:
        """Get workflow instance if it exists."""
        with self._instance_lock:
            wrapper = self._instances.get(workflow_type)
            return wrapper.instance if wrapper else None

    def get_workflow_stats(self) -> Dict[str, Any]:
        """Get workflow factory statistics."""
        with self._instance_lock:
            return {
                "total_instances": len(self._instances),
                "active_instances": len([w for w in self._instances.values() if w.is_active]),
                "loaded_modules": list(self._loaded_modules.keys()),
                "workflow_types": [wf.value for wf in self._instances.keys()],
                "configs": {wf.value: {
                    "lifecycle": config.lifecycle.value,
                    "lazy_load": config.lazy_load,
                    "requires_project_data": config.requires_project_data
                } for wf, config in self._configs.items()}
            }


# Convenience functions for easy integration
def create_workflow(workflow_type: str,
                   root_widget: Any,
                   back_callback: callable,
                   project_data: Optional[Dict[str, Any]] = None) -> Optional[Any]:
    """Create a workflow instance."""
    try:
        wf_type = WorkflowType(workflow_type)
        factory = WorkflowFactory.get_instance()
        return factory.create_workflow(wf_type, root_widget, back_callback, project_data)
    except ValueError:
        logging.error(f"Invalid workflow type: {workflow_type}")
        return None


def release_workflow(workflow_type: str) -> bool:
    """Release a workflow instance."""
    try:
        wf_type = WorkflowType(workflow_type)
        factory = WorkflowFactory.get_instance()
        return factory.release_workflow(wf_type)
    except ValueError:
        return False


def cleanup_workflow(workflow_type: str) -> bool:
    """Cleanup a workflow instance."""
    try:
        wf_type = WorkflowType(workflow_type)
        factory = WorkflowFactory.get_instance()
        return factory.cleanup_workflow(wf_type)
    except ValueError:
        return False


def cleanup_all_workflows():
    """Cleanup all workflows."""
    factory = WorkflowFactory.get_instance()
    factory.cleanup_all_workflows()