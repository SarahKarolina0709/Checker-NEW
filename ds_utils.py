"""Design-System und Format-Hilfsfunktionen (wiederverwendbar).

Regeln:
- Keine direkten Hex-Farben in der UI, nur über app.get_color()/DesignSystem
- Defensive Fallbacks, damit Module auch in Tests/Headless laufen
"""
from __future__ import annotations
from typing import Any, Optional, Tuple


def fmt_percent(v: Any) -> str:
    """Formatiert Zahlen als Prozent/Skalar.

    - None -> '–'
    - 0..1 -> '{:.1f}%'
    - sonst: 2 Nachkommastellen bei numerischen Werten
    """
    try:
        if v is None:
            return '–'
        if isinstance(v, (int, float)):
            if 0 <= v <= 1:
                return f"{v*100:.1f}%"
            return f"{v:.2f}"
        return str(v)
    except Exception:
        return str(v)


def clamp01(x: Any) -> float:
    try:
        xf = float(x)
    except Exception:
        return 0.0
    if xf < 0.0:
        return 0.0
    if xf > 1.0:
        return 1.0
    return xf


def clamp_percent_100(x: Any) -> float:
    try:
        xf = float(x)
    except Exception:
        return 0.0
    if xf < 0.0:
        return 0.0
    if xf > 100.0:
        return 100.0
    return xf


def ds_get_color(app: Any, token: str, fallback: Optional[str] = None) -> str:
    """Sicherer Color-Resolver über Design-System.

    Versucht app.get_color(token); nutzt Fallback; sonst 'text' oder '#000000'.
    """
    try:
        if hasattr(app, 'get_color') and callable(getattr(app, 'get_color')):
            return app.get_color(token)
    except Exception:
        pass
    if fallback:
        return fallback
    try:
        if hasattr(app, 'get_color') and callable(getattr(app, 'get_color')):
            return app.get_color('text')
    except Exception:
        pass
    return '#000000'


def get_spacing(app: Any, key: str, default: int = 16) -> int:
    """Spacing aus Design-System, mit numerischem Fallback."""
    try:
        if hasattr(app, 'get_spacing') and callable(getattr(app, 'get_spacing')):
            val = app.get_spacing(key)
            if isinstance(val, (int, float)):
                return int(val)
    except Exception:
        pass
    # leichte Defaults
    mapping = {'xs': 4, 'sm': 8, 'md': 16, 'lg': 24, 'xl': 32}
    return mapping.get(key, default)


def get_font(app: Any, name: str, default: Tuple[str, int, str] = ("Segoe UI", 14, "normal")) -> Tuple[str, int, str]:
    """Typografie aus Design-System, als Tupel für CTkFont(*tuple)."""
    try:
        if hasattr(app, 'get_typography') and callable(getattr(app, 'get_typography')):
            ft = app.get_typography(name)
            if isinstance(ft, (list, tuple)) and len(ft) >= 2:
                # (family, size, weight?)
                return tuple(ft)  # type: ignore[return-value]
    except Exception:
        pass
    return default


def safe_radius(app: Any, token: str, fallback: int = 12) -> int:
    """Liest Corner-Radius sicher aus dem Design-System und castet auf int."""
    try:
        ds = getattr(app, 'design_system', None)
        if isinstance(ds, dict):
            val = ds.get('components', {}).get('borders', {}).get(token, fallback)
            try:
                return int(val)  # kann auch tuple/float sein → int()
            except Exception:
                return fallback
    except Exception:
        pass
    return fallback


def get_total_files(app: Any) -> int:
    """Zählt Quelle+Übersetzung aus app.uploaded_files (robust)."""
    try:
        uf = getattr(app, 'uploaded_files', None) or {}
        if isinstance(uf, dict):
            s = uf.get('source') or []
            t = uf.get('translation') or []
            return (len(s) if isinstance(s, (list, tuple)) else 0) + (len(t) if isinstance(t, (list, tuple)) else 0)
    except Exception:
        pass
    return 0
