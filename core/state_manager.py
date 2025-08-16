"""
State Management System for Checker Application
==============================================

This module provides centralized state management with validation,
consistency checks, and proper state transitions. It addresses the
inconsistent state mutations found in the logic review.

Priority 2 Implementation from Logic Review Report
"""

from pathlib import Path
from typing import Dict, Any, Optional, Set, Callable, List
import json
import logging
import threading
import time

from dataclasses import dataclass, field
from enum import Enum
import copy

class StateChangeType(Enum):
    """Types of state changes."""
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    VALIDATE = "validate"
    RESET = "reset"


class WorkflowState(Enum):
    """Workflow lifecycle states."""
    INACTIVE = "inactive"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETING = "completing"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class StateChange:
    """Record of a state change."""
    timestamp: float
    change_type: StateChangeType
    key: str
    old_value: Any
    new_value: Any
    source: str
    validation_passed: bool = True
    error_message: Optional[str] = None


@dataclass
class WorkflowContext:
    """Context information for a workflow."""
    name: str
    state: WorkflowState = WorkflowState.INACTIVE
    data: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    last_updated: float = field(default_factory=time.time)
    instance: Optional[Any] = None


class StateValidator:
    """Validates state changes according to business rules."""

    def __init__(self):
        self._validation_rules: Dict[str, List[Callable]] = {}
        self._setup_default_rules()

    def _setup_default_rules(self):
        """Setup default validation rules."""
        # Project data validation
        self.add_rule("project_data.name", self._validate_project_name)
        self.add_rule("project_data.path", self._validate_project_path)

        # Workflow state validation
        self.add_rule("current_workflow", self._validate_workflow_name)
        self.add_rule("workflow_state", self._validate_workflow_state)

    def add_rule(self, key_pattern: str, validator: Callable[[Any], tuple[bool, str]]):
        """Add a validation rule for a key pattern."""
        if key_pattern not in self._validation_rules:
            self._validation_rules[key_pattern] = []
        self._validation_rules[key_pattern].append(validator)

    def validate(self, key: str, value: Any) -> tuple[bool, str]:
        """Validate a value against all applicable rules."""
        for pattern, validators in self._validation_rules.items():
            if self._key_matches_pattern(key, pattern):
                for validator in validators:
                    try:
                        is_valid, message = validator(value)
                        if not is_valid:
                            return False, message
                    except Exception as e:
                        return False, f"Validation error: {e}"

        return True, ""

    def _key_matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if a key matches a pattern."""
        # Simple pattern matching (can be extended for regex)
        if pattern == key:
            return True
        if pattern.endswith("*") and key.startswith(pattern[:-1]):
            return True
        if "." in pattern and "." in key:
            pattern_parts = pattern.split(".")
            key_parts = key.split(".")
            if len(pattern_parts) == len(key_parts):
                return all(pp == kp or pp == "*" for pp, kp in zip(pattern_parts, key_parts))
        return False

    # Default validation rules
    def _validate_project_name(self, value: Any) -> tuple[bool, str]:
        """Validate project name."""
        if not isinstance(value, str):
            return False, "Project name must be a string"
        if len(value.strip()) == 0:
            return False, "Project name cannot be empty"
        if len(value) > 100:
            return False, "Project name too long (max 100 characters)"
        return True, ""

    def _validate_project_path(self, value: Any) -> tuple[bool, str]:
        """Validate project path."""
        if not isinstance(value, (str, Path)):
            return False, "Project path must be a string or Path"
        try:
            path = Path(value)
            if not path.exists():
                return False, f"Project path does not exist: {path}"
        except Exception as e:
            return False, f"Invalid path: {e}"
        return True, ""

    def _validate_workflow_name(self, value: Any) -> tuple[bool, str]:
        """Validate workflow name."""
        valid_workflows = {
            "pruefung", "angebots", "projekt", "finalisierung",
            "export", "ki_pruefung", "quality"
        }
        if value not in valid_workflows:
            return False, f"Invalid workflow name: {value}"
        return True, ""

    def _validate_workflow_state(self, value: Any) -> tuple[bool, str]:
        """Validate workflow state."""
        if not isinstance(value, WorkflowState):
            return False, "Workflow state must be a WorkflowState enum"
        return True, ""


class StateManager:
    """
    Centralized state management system.

    Features:
    - Thread-safe state operations
    - State validation
    - Change tracking
    - State persistence
    - Rollback capabilities
    - Event notifications
    """

    _instance: Optional['StateManager'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'StateManager':
        """Singleton pattern implementation."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the state manager."""
        if hasattr(self, '_initialized'):
            return

        self._initialized = True
        self._state: Dict[str, Any] = {}
        self._workflows: Dict[str, WorkflowContext] = {}
        self._state_lock = threading.RLock()
        self._change_history: List[StateChange] = []
        self._max_history = 1000

        # State validation
        self._validator = StateValidator()

        # Event callbacks
        self._change_callbacks: List[Callable[[StateChange], None]] = []

        # Setup logging
        self._logger = logging.getLogger(__name__)

        # Initialize default state
        self._initialize_default_state()

    @classmethod
    def get_instance(cls) -> 'StateManager':
        """Get the singleton instance."""
        return cls()

    def _initialize_default_state(self):
        """Initialize default application state."""
        default_state = {
            "current_workflow": None,
            "project_data": {},
            "ui_state": {
                "window_geometry": None,
                "theme": "default"
            },
            "app_settings": {
                "auto_save": True,
                "backup_enabled": True,
                "max_recent_projects": 10
            },
            "recent_projects": []
        }

        with self._state_lock:
            self._state.update(default_state)

    def set_value(self, key: str, value: Any, source: str = "unknown", validate: bool = True) -> bool:
        """
        Set a state value with validation.

        Args:
            key: State key
            value: New value
            source: Source of the change
            validate: Whether to validate the change

        Returns:
            True if successful, False if validation failed
        """
        with self._state_lock:
            old_value = self._state.get(key)

            # Validate if requested
            validation_passed = True
            error_message = None

            if validate:
                validation_passed, error_message = self._validator.validate(key, value)
                if not validation_passed:
                    self._logger.warning(f"Validation failed for {key}: {error_message}")
                    self._record_change(
                        StateChangeType.VALIDATE, key, old_value, value,
                        source, False, error_message
                    )
                    return False

            # Set the value
            self._state[key] = copy.deepcopy(value)

            # Record the change
            change_type = StateChangeType.CREATE if old_value is None else StateChangeType.UPDATE
            self._record_change(change_type, key, old_value, value, source, True)

            self._logger.debug(f"State updated: {key} = {value} (source: {source})")
            return True

    def get_value(self, key: str, default: Any = None) -> Any:
        """Get a state value."""
        with self._state_lock:
            return copy.deepcopy(self._state.get(key, default))

    def update_nested(self, key: str, nested_key: str, value: Any, source: str = "unknown") -> bool:
        """Update a nested value in a dictionary."""
        with self._state_lock:
            current = self._state.get(key, {})
            if not isinstance(current, dict):
                self._logger.error(f"Cannot update nested key in non-dict value: {key}")
                return False

            old_nested_value = current.get(nested_key)
            current[nested_key] = value

            return self.set_value(key, current, source)

    def delete_value(self, key: str, source: str = "unknown") -> bool:
        """Delete a state value."""
        with self._state_lock:
            if key not in self._state:
                return False

            old_value = self._state[key]
            del self._state[key]

            self._record_change(StateChangeType.DELETE, key, old_value, None, source)
            self._logger.debug(f"State deleted: {key} (source: {source})")
            return True

    def reset_state(self, source: str = "system"):
        """Reset state to defaults."""
        with self._state_lock:
            old_state = copy.deepcopy(self._state)
            self._state.clear()
            self._workflows.clear()
            self._initialize_default_state()

            self._record_change(StateChangeType.RESET, "all", old_state, self._state, source)
            self._logger.info("State reset to defaults")

    # Workflow-specific methods
    def set_current_workflow(self, workflow_name: Optional[str], source: str = "workflow") -> bool:
        """Set the current active workflow."""
        return self.set_value("current_workflow", workflow_name, source)

    def get_current_workflow(self) -> Optional[str]:
        """Get the current active workflow."""
        return self.get_value("current_workflow")

    def register_workflow(self, name: str, instance: Any = None) -> bool:
        """Register a workflow instance."""
        with self._state_lock:
            context = WorkflowContext(
                name=name,
                state=WorkflowState.INITIALIZING,
                instance=instance
            )
            self._workflows[name] = context

            self._logger.info(f"Registered workflow: {name}")
            return True

    def update_workflow_state(self, name: str, state: WorkflowState) -> bool:
        """Update workflow state."""
        with self._state_lock:
            if name not in self._workflows:
                self._logger.error(f"Workflow not registered: {name}")
                return False

            old_state = self._workflows[name].state
            self._workflows[name].state = state
            self._workflows[name].last_updated = time.time()

            self._logger.debug(f"Workflow {name} state: {old_state.value} -> {state.value}")
            return True

    def get_workflow_context(self, name: str) -> Optional[WorkflowContext]:
        """Get workflow context."""
        with self._state_lock:
            return copy.deepcopy(self._workflows.get(name))

    def unregister_workflow(self, name: str) -> bool:
        """Unregister a workflow."""
        with self._state_lock:
            if name in self._workflows:
                del self._workflows[name]
                self._logger.info(f"Unregistered workflow: {name}")
                return True
            return False

    # Project data methods
    def set_project_data(self, data: Dict[str, Any], source: str = "project") -> bool:
        """Set project data with validation."""
        return self.set_value("project_data", data, source)

    def get_project_data(self) -> Dict[str, Any]:
        """Get current project data."""
        return self.get_value("project_data", {})

    def update_project_field(self, field: str, value: Any, source: str = "project") -> bool:
        """Update a specific project field."""
        return self.update_nested("project_data", field, value, source)

    # Change tracking
    def _record_change(self, change_type: StateChangeType, key: str,
                      old_value: Any, new_value: Any, source: str,
                      validation_passed: bool = True, error_message: str = None):
        """Record a state change."""
        change = StateChange(
            timestamp=time.time(),
            change_type=change_type,
            key=key,
            old_value=old_value,
            new_value=new_value,
            source=source,
            validation_passed=validation_passed,
            error_message=error_message
        )

        self._change_history.append(change)

        # Limit history size
        if len(self._change_history) > self._max_history:
            self._change_history = self._change_history[-self._max_history:]

        # Notify callbacks
        for callback in self._change_callbacks:
            try:
                callback(change)
            except Exception as e:
                self._logger.error(f"Error in change callback: {e}")

    def get_change_history(self, limit: int = 100) -> List[StateChange]:
        """Get recent state changes."""
        with self._state_lock:
            return copy.deepcopy(self._change_history[-limit:])

    def add_change_callback(self, callback: Callable[[StateChange], None]):
        """Add a callback for state changes."""
        self._change_callbacks.append(callback)

    def remove_change_callback(self, callback: Callable[[StateChange], None]):
        """Remove a change callback."""
        if callback in self._change_callbacks:
            self._change_callbacks.remove(callback)

    # State persistence
    def save_state(self, filepath: Path) -> bool:
        """Save current state to file."""
        try:
            with self._state_lock:
                state_data = {
                    "state": self._state,
                    "workflows": {
                        name: {
                            "name": ctx.name,
                            "state": ctx.state.value,
                            "data": ctx.data,
                            "created_at": ctx.created_at,
                            "last_updated": ctx.last_updated
                        }
                        for name, ctx in self._workflows.items()
                    },
                    "timestamp": time.time()
                }

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(state_data, f, indent=2, default=str)

                self._logger.info(f"State saved to {filepath}")
                return True

        except Exception as e:
            self._logger.error(f"Failed to save state: {e}")
            return False

    def load_state(self, filepath: Path) -> bool:
        """Load state from file."""
        try:
            if not filepath.exists():
                self._logger.warning(f"State file not found: {filepath}")
                return False

            with open(filepath, 'r', encoding='utf-8') as f:
                state_data = json.load(f)

            with self._state_lock:
                # Load main state
                self._state.update(state_data.get("state", {}))

                # Load workflow contexts
                for name, ctx_data in state_data.get("workflows", {}).items():
                    context = WorkflowContext(
                        name=ctx_data["name"],
                        state=WorkflowState(ctx_data["state"]),
                        data=ctx_data.get("data", {}),
                        created_at=ctx_data.get("created_at", time.time()),
                        last_updated=ctx_data.get("last_updated", time.time())
                    )
                    self._workflows[name] = context

                self._logger.info(f"State loaded from {filepath}")
                return True

        except Exception as e:
            self._logger.error(f"Failed to load state: {e}")
            return False

    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current state."""
        with self._state_lock:
            return {
                "state_keys": list(self._state.keys()),
                "current_workflow": self._state.get("current_workflow"),
                "registered_workflows": list(self._workflows.keys()),
                "workflow_states": {
                    name: ctx.state.value
                    for name, ctx in self._workflows.items()
                },
                "change_history_size": len(self._change_history),
                "last_change": self._change_history[-1].timestamp if self._change_history else None
            }

    def set_workflow_context(self, workflow_id: str, context: dict):
        """Setzt oder aktualisiert den Kontext für einen Workflow."""
        with self._state_lock:
            if workflow_id not in self._workflows:
                self._workflows[workflow_id] = WorkflowContext(name=workflow_id, data=context)
            else:
                self._workflows[workflow_id].data.update(context)
            self._workflows[workflow_id].last_updated = time.time()


# Convenience functions for easy integration
def get_state(key: str, default: Any = None) -> Any:
    """Get a state value."""
    manager = StateManager.get_instance()
    return manager.get_value(key, default)


def set_state(key: str, value: Any, source: str = "app") -> bool:
    """Set a state value."""
    manager = StateManager.get_instance()
    return manager.set_value(key, value, source)


def get_current_workflow() -> Optional[str]:
    """Get the current workflow."""
    manager = StateManager.get_instance()
    return manager.get_current_workflow()


def set_current_workflow(workflow_name: Optional[str]) -> bool:
    """Set the current workflow."""
    manager = StateManager.get_instance()
    return manager.set_current_workflow(workflow_name)


def get_project_data() -> Dict[str, Any]:
    """Get current project data."""
    manager = StateManager.get_instance()
    return manager.get_project_data()


def set_project_data(data: Dict[str, Any]) -> bool:
    """Set project data."""
    manager = StateManager.get_instance()
    return manager.set_project_data(data)