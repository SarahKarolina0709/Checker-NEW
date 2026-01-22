"""Plugin rule base class for quality analysis (additive).
Rules can subscribe to events and publish results via EventBus.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class RuleResult:
    rule: str
    passed: bool
    details: Dict[str, Any]

class BaseRule:
    name = "base"
    version = "0.1"

    def analyze(self, context: dict, cancel_event=None) -> RuleResult:  # pragma: no cover - interface
        """Analyse ausführen.

        Parameter:
            context: Dict mit Eingabedaten
            cancel_event: Optional threading.Event für kooperative Cancellation.
                           Regeln sollten langfristig regelmäßig cancel_event.is_set() prüfen
                           und frühzeitig zurückkehren.
        """
        raise NotImplementedError
