"""Dynamic plugin loader (rekursiv) für Rule-Klassen.

Additiv & fehlertolerant:
 - Rekursive Durchsuchung des ``plugins`` Pakets (auch Unterpakete wie ``plugins.rules``)
 - Filtert ``BaseRule`` selbst sowie optionale EXCLUDE Namen
 - Bricht bei Einzel-Importfehlern NICHT ab

Warum Änderung?
 Ursprünglicher Loader ignorierte Unterpakete (``mod.ispkg`` wurde übersprungen),
 wodurch ``plugins/rules/dummy_rule.py`` nicht entdeckt wurde. Diese Version
 erweitert die Suche rekursiv, bleibt aber API‑kompatibel (``discover_rules()`` Rückgabe unverändert).
"""
from __future__ import annotations
import pkgutil
import importlib
import inspect
from types import ModuleType
from typing import List, Type, Iterable
from .base_rule import BaseRule

EXCLUDE = {"base_rule", "__pycache__"}

def _iter_modules_recursive(package: ModuleType) -> Iterable[ModuleType]:  # pragma: no cover (Best effort)
    """Rekursiv alle Module & Subpakete eines gegebenen Pakets liefern.
    Fehlerhafte Importe werden still übersprungen (bewusst additive Robustheit)."""
    prefix = package.__name__ + "."
    try:
        package_path = package.__path__  # type: ignore[attr-defined]
    except Exception:
        return []
    for modinfo in pkgutil.iter_modules(package_path):
        name = modinfo.name
        if name in EXCLUDE:
            continue
        full_name = prefix + name
        try:
            module = importlib.import_module(full_name)
        except Exception:
            continue
        yield module
        # Wenn Sub-Paket: rekursiv tiefer gehen
        if modinfo.ispkg:
            yield from _iter_modules_recursive(module)

def discover_rules() -> List[Type[BaseRule]]:
    """Finde alle konkreten Rule-Subklassen (rekursiv)."""
    rules: List[Type[BaseRule]] = []
    try:
        import plugins  # Root Package Referenz
        for module in _iter_modules_recursive(plugins):  # type: ignore
            try:
                for _, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, BaseRule) and obj is not BaseRule:
                        rules.append(obj)
            except Exception:
                continue
    except Exception:
        pass
    return rules

__all__ = ["discover_rules"]
