"""Modulare Komponenten für Metrik-Karten der Quality GUI.

Erweiterte, rückwärtskompatible Version der ursprünglichen build_metric_card Funktion:
- i18n via app._t
- Fallback-Farben (kein Crash falls <color>_light fehlt)
- Optionaler on_click + Keyboard-Fokus
- Dynamischer wraplength für Beschreibung
- Live-Update API: card.update_metric(value_new=..., desc_new=..., progress_value=...)
- ProgressBar bei numerischen Werten (abschaltbar / konfigurierbar)
- Thread-safe Updates (root.after)

No-Icons-Policy: icon_text Param existiert nur für neutrale ASCII (kein Emoji verwenden).
"""
from __future__ import annotations
import customtkinter as ctk

def build_metric_card(
    app,
    parent,
    title: str,
    value: str,
    color: str,
    description: str,
    column: int,
    *,
    on_click=None,
    icon_text: str = "",      # Hinweis: gemäss No-Icons-Policy keine Emojis benutzen
    unit: str = "",
    show_progress: bool = True,
    value_max: float | None = 100.0,
    focus_ring: bool = True,
    enable_tooltip: bool = True,
    lock_height: bool = False
):
    """Erzeuge eine Metrik-Karte (erweitert & rückwärtskompatibel).

    Alte Parameter bleiben unverändert; neue sind optional.
    """
    try:  # GUI-Schutz
        # Farb-Fallbacks (nutzt Design-System Tokens)
        try:
            bg = app.get_color(f"{color}_light") or app.get_color("surface")
        except Exception:
            bg = getattr(app, "get_color", lambda *_: "#FFFFFF")("surface")
        try:
            fg = app.get_color(color) or app.get_color("primary")
        except Exception:
            fg = getattr(app, "get_color", lambda *_: "#1F4E79")("primary")

        # Corner-Radius aus Design-System falls verfügbar
        try:
            radius = app.design_system['components']['borders'].get('radius_lg', 18)  # type: ignore[attr-defined]
        except Exception:
            radius = 18

        card = ctk.CTkFrame(
            parent,
            fg_color=bg,
            corner_radius=radius,
            border_width=0,
            border_color=fg  # wird bei Focus-Ring dynamisch genutzt
        )
        card.grid(row=0, column=column, sticky="nsew", padx=8, pady=0)

        if lock_height:  # Optionale Stabilisierung der Höhe bei variablen Beschreibungen
            try:
                card.grid_propagate(False)
            except Exception:
                pass

        # Fokus ermöglichen (Keyboard Accessibility)
        for _target in ("_outer_frame",):
            try:
                obj = getattr(card, _target, None)
                if obj:
                    obj.configure(takefocus=1)  # type: ignore[arg-type]
            except Exception:
                pass
        try:
            card.configure(takefocus=1)
        except Exception:
            pass

        # Titel (i18n)
        lbl_title = ctk.CTkLabel(
            card,
            text=_safe_t(app, title),
            font=ctk.CTkFont(*_safe_typo(app, 'subheading')),
            text_color=_safe_color(app, 'text_primary')
        )
        lbl_title.pack(pady=(14, 4), padx=12)

        # Reihe für Icon + Wert
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(pady=(0, 2), padx=12, fill="x")

        if icon_text and not _contains_emoji(icon_text):  # Policy: kein Emoji/Icon
            try:
                ctk.CTkLabel(
                    row,
                    text=icon_text,
                    font=ctk.CTkFont(*_safe_typo(app, 'heading')),
                    text_color=fg
                ).pack(side="left", padx=(0, 6))
            except Exception:
                pass

        # Wert + Einheit (kein Doppel-Suffix)
        val_str = f"{value}{unit}" if unit and not str(value).endswith(unit) else str(value)
        lbl_value = ctk.CTkLabel(
            row,
            text=val_str,
            font=ctk.CTkFont(*_safe_typo(app, 'title')),
            text_color=fg
        )
        lbl_value.pack(side="left")

        # ProgressBar wenn sinnvoll (numerisch + value_max)
        if show_progress and _is_number(value) and value_max and float(value_max) > 0:
            try:
                prog = ctk.CTkProgressBar(card)
                prog.pack(fill="x", padx=12, pady=(6, 0))
                prog.set(_safe_progress(value, value_max))
            except Exception:
                prog = None
        else:
            prog = None

        # Beschreibung (i18n) mit dynamischem wraplength
        lbl_desc = ctk.CTkLabel(
            card,
            text=_safe_t(app, description),
            font=ctk.CTkFont(*_safe_typo(app, 'caption')),
            text_color=_safe_color(app, 'text_secondary'),
            wraplength=150,
            justify="center"
        )
        lbl_desc.pack(pady=(6, 16), padx=10)

        def _sync_wrap(_=None):  # Responsive wrap mit Min/Max-Korridor
            try:
                w = card.winfo_width()
                if w > 0:
                    # 120 - 280 Korridor, 80% Breite
                    lbl_desc.configure(wraplength=min(280, max(120, int(w * 0.8))))
            except Exception:
                pass
        card.bind("<Configure>", _sync_wrap)

        # Tooltip für lange Beschreibungen (optional)
        if enable_tooltip and len(str(description)) > 40:
            try:
                lbl_desc.bind(
                    "<Enter>",
                    lambda e, t=_safe_t(app, description): getattr(app, '_show_tooltip', lambda *a, **k: None)(lbl_desc, t)
                )
                lbl_desc.bind(
                    "<Leave>",
                    lambda e: getattr(app, '_hide_tooltip', lambda *a, **k: None)()
                )
            except Exception:
                pass

        # Interaktion (Click + Keyboard)
        if on_click:
            def _safe_call():
                try:
                    on_click()
                except Exception as e:  # pragma: no cover
                    _log_exc(app, f"metric_card on_click failed: {e}")

            for w in (card, row, lbl_value, lbl_title, lbl_desc):
                try:
                    w.bind("<Button-1>", lambda e, _c=_safe_call: _c())
                except Exception:
                    pass
            try:
                card.bind("<Return>", lambda e: _safe_call())
                card.bind("<space>", lambda e: _safe_call())
                card.bind("<Enter>", lambda e: card.configure(cursor="hand2"))
                card.bind("<Leave>", lambda e: card.configure(cursor=""))
            except Exception:
                pass

        # Focus-Ring (optional)
        if focus_ring:
            def _on_focus_in(_e):
                try:
                    card.configure(border_width=2, border_color=fg)
                except Exception:
                    pass
            def _on_focus_out(_e):
                try:
                    card.configure(border_width=0)
                except Exception:
                    pass
            try:
                card.bind("<FocusIn>", _on_focus_in)
                card.bind("<FocusOut>", _on_focus_out)
            except Exception:
                pass

        # Live-Update API
        def update(value_new=None, unit_new=None, desc_new=None, progress_value=None):
            def _apply():  # Innerer Thread-safe-Executor
                try:
                    if value_new is not None:
                        use_unit = unit_new if unit_new is not None else unit
                        txt = f"{value_new}{use_unit}" if use_unit and not str(value_new).endswith(use_unit) else str(value_new)
                        lbl_value.configure(text=txt)
                    if desc_new is not None:
                        lbl_desc.configure(text=_safe_t(app, desc_new))
                    if prog is not None and progress_value is not None and value_max:
                        try:
                            prog.set(_safe_progress(progress_value, value_max))
                        except Exception:
                            pass
                except Exception as e:  # pragma: no cover
                    _log_exc(app, f"metric_card update failed: {e}")

            root = getattr(app, "root", None)
            if root and hasattr(root, "after"):
                try:
                    root.after(0, _apply)
                except Exception:
                    _apply()
            else:
                _apply()

        card.update_metric = update  # type: ignore[attr-defined]
        return card

    except Exception as e:  # pragma: no cover
        _log_exc(app, f"Error building metric card: {e}")
        return None


# ----------------------------- Helper ---------------------------------
def _is_number(x) -> bool:
    try:
        s = str(x).replace(",", ".").strip().rstrip("%")
        float(s)
        return True
    except Exception:
        return False

def _safe_progress(value, value_max):
    try:
        s = str(value).replace(",", ".").strip().rstrip("%")
        return max(0.0, min(float(s)/float(value_max), 1.0))
    except Exception:
        return 0.0

def _log_exc(app, msg: str):
    try:
        (getattr(app, "logger", None) or __import__("logging").getLogger(__name__)).exception(msg)
    except Exception:
        pass

def _safe_t(app, key: str) -> str:
    try:
        return getattr(app, "_t", lambda k: k)(key)
    except Exception:
        return key

def _safe_color(app, key: str):
    try:
        return app.get_color(key)
    except Exception:
        return "#333333"

def _safe_typo(app, name: str):
    try:
        return app.get_typography(name)
    except Exception:
        return ("Segoe UI", 14, "normal")

def _contains_emoji(text: str) -> bool:
    # Grobe Erkennung (Policy: keine Emojis / Icons)
    return any(ord(c) > 0x2600 for c in text)  # einfache Heuristik
