"""Status-Bar Komponenten für die Quality GUI.

Erweitert um:
 - Thread-sichere Helper-APIs (set_status, set_progress, set_files)
 - i18n via app._t
 - Dynamische Version (app.version)
 - Indeterminate / Busy-State Unterstützung
 - Accessibility (Font-Scaling, optional on_status_announce Hook)
 - Defensive Fallbacks beim Design-System
 - Eliding langer Status-Texte & Re-Konfiguration bei Resize
 - Click-Handler (Version / Files Bereich)
Idempotent: Mehrfachaufruf überschreibt nur Widgets/Helper konsistent.
"""
from __future__ import annotations
import customtkinter as ctk
try:  # Font-Messung für präziseres Eliding
    import tkinter.font as tkfont
except Exception:  # pragma: no cover
    tkfont = None


def build_status_bar(app):  # noqa: C901 (umfangreicher, logisch segmentiert)
    """Erstellt/aktualisiert die Status-Bar und hängt komfortable Update-APIs an `app`.

    Kann gefahrlos mehrfach aufgerufen werden (idempotent)."""
    # -------------------- Fallback & Convenience Layer --------------------
    _t = getattr(app, "_t", lambda s, **_: s)
    _get_color_raw = getattr(app, "get_color", None)
    _get_typo = getattr(app, "get_typography", lambda n: ("Segoe UI", 14, "normal"))
    accessibility = getattr(app, "accessibility", {}) or {}
    font_scale = getattr(accessibility, "get", lambda *_: 1.0)("font_scale", 1.0)

    def _get_color(token: str, fallback: str = "#FFFFFF"):
        try:
            if callable(_get_color_raw):
                c = _get_color_raw(token)
                if c:
                    return c
        except Exception:
            pass
        return fallback

    def _font(name: str):
        try:
            fam, size, *rest = _get_typo(name)
            weight = rest[0] if rest else "normal"
            try:
                size = int(float(size) * float(font_scale))
            except Exception:
                pass
            return ctk.CTkFont(family=fam, size=size, weight=weight)
        except Exception:
            return ctk.CTkFont(family="Segoe UI", size=14, weight="normal")

    root = getattr(app, "root", None)
    if root is None:  # Ohne Root kein Aufbau möglich
        return

    # -------------------- Build nur falls nicht vorhanden --------------------
    try:
        existing = hasattr(app, "status_bar") and getattr(app.status_bar, "winfo_exists", lambda: False)()
        if not existing:
            app.status_bar = ctk.CTkFrame(
                root,
                height=42,
                fg_color=_get_color("surface_elevated", "#F8FAFC"),
                border_width=1,
                corner_radius=0,
            )
            app.status_bar.pack(fill="x", side="bottom", padx=0, pady=0)
            app.status_bar.pack_propagate(False)

            status_content = ctk.CTkFrame(app.status_bar, fg_color=_get_color("transparent", "transparent"))
            status_content.pack(fill="both", expand=True, padx=20, pady=8)

            # Left Section
            left_section = ctk.CTkFrame(status_content, fg_color=_get_color("transparent", "transparent"))
            left_section.pack(side="left", fill="y")

            app.status_indicator = ctk.CTkLabel(
                left_section,
                text="OK",
                font=_font("body"),
                text_color=_get_color("success", "#059669"),
                width=36,
            )
            app.status_indicator.pack(side="left", padx=(0, 8))

            app.status_label = ctk.CTkLabel(
                left_section,
                text=_t("System Ready"),
                font=_font("body"),
                text_color=_get_color("text_primary", "#1F2937"),
                anchor="w",
            )
            app.status_label.pack(side="left")

            # Middle / Progress
            app.progress_section = ctk.CTkFrame(status_content, fg_color=_get_color("transparent", "transparent"))
            app.progress_section.pack(side="left")
            # Progress-Elemente: initial verborgen solange 0%
            app.mini_progress = ctk.CTkProgressBar(
                app.progress_section,
                width=120,
                height=10,
                progress_color=_get_color("primary", "#1F4E79"),
                fg_color=_get_color("gray_200", "#E5E7EB"),
                corner_radius=6,
                border_width=1,
                border_color=_get_color("gray_200", "#E5E7EB"),
            )
            try: app.mini_progress.set(0)
            except Exception: pass
            app.progress_text = ctk.CTkLabel(
                app.progress_section,
                text="",
                font=_font("caption"),
                text_color=_get_color("primary", "#1F4E79"),
            )

            def _hide_progress_initial():
                try:
                    app.mini_progress.pack_forget()
                    app.progress_text.pack_forget()
                except Exception: pass
            _hide_progress_initial()

            # Right Section
            right_section = ctk.CTkFrame(status_content, fg_color=_get_color("transparent", "transparent"))
            right_section.pack(side="right", fill="y")

            app.file_count_label = ctk.CTkLabel(
                right_section,
                text=_t("Files: {n}").format(n=0),
                font=_font("caption"),
                text_color=_get_color("text_secondary", "#6B7280"),
            )
            app.file_count_label.pack(side="right", padx=(16, 0))

            # History Info (optional, dynamisch aktualisiert von _push_history)
            app.history_info_label = ctk.CTkLabel(
                right_section,
                text="History: 0",
                font=_font("caption"),
                text_color=_get_color("gray_500", "#6B7280"),
            )
            app.history_info_label.pack(side="right", padx=(16, 0))

            separator = ctk.CTkLabel(
                right_section,
                text="|",
                font=_font("caption"),
                text_color=_get_color("gray_400", "#9CA3AF"),
            )
            separator.pack(side="right", padx=(8, 8))

            version_value = getattr(app, "version", "v2.5")
            app.version_label = ctk.CTkLabel(
                right_section,
                text=_t("Quality Framework {v}").format(v=version_value),
                font=_font("caption"),
                text_color=_get_color("text_secondary", "#6B7280"),
            )
            app.version_label.pack(side="right")
    except Exception as build_exc:  # pragma: no cover
        try:
            print(f"Error building status bar: {build_exc}")
        except Exception:
            pass
        return

    # -------------------- Helper & State --------------------
    COLOR_BY_TYPE = {
        "info": (
            _get_color("info", _get_color("primary", "#1F4E79")),
            _get_color("text_primary", "#1F2937"),
        ),
        "success": (
            _get_color("success", "#059669"),
            _get_color("text_primary", "#1F2937"),
        ),
        "warning": (
            _get_color("warning", "#D97706"),
            _get_color("text_primary", "#1F2937"),
        ),
        "error": (
            _get_color("error", "#DC2626"),
            _get_color("text_primary", "#1F2937"),
        ),
    }
    ICON_BY_TYPE = {"info": "INFO", "success": "OK", "warning": "WARNUNG", "error": "FEHLER"}

    # Originaltext für Eliding merken
    app._status_full_text = getattr(app, "_status_full_text", app.status_label.cget("text"))

    _resize_job = {"id": None}
    _destroyed = {"val": False}

    def _truncate_status():
        """Eliding mit dynamischer Breitenberechnung und Font-Messung."""
        try:
            full = getattr(app, "_status_full_text", app.status_label.cget("text")) or ""
            total_w = max(1, app.status_bar.winfo_width())
            # dynamisch Breiten anderer Segmente abziehen
            right_w = getattr(app, "version_label", None).winfo_width() if getattr(app, "version_label", None) else 0
            files_w = getattr(app, "file_count_label", None).winfo_width() if getattr(app, "file_count_label", None) else 0
            prog_w = getattr(app, "progress_section", None).winfo_width() if getattr(app, "progress_section", None) else 0
            indicator_w = getattr(app, "status_indicator", None).winfo_width() if getattr(app, "status_indicator", None) else 0
            paddings = 60  # heuristische Innenabstände
            avail_px = max(80, total_w - (right_w + files_w + prog_w + indicator_w + paddings))
            # Font bestimmen (auch für CTkFont)
            fnt = None
            if tkfont is not None:
                try:
                    lbl_font = app.status_label.cget("font")
                    if isinstance(lbl_font, ctk.CTkFont):
                        cfg = {"family": lbl_font.cget("family"), "size": lbl_font.cget("size"), "weight": lbl_font.cget("weight")}
                        fnt = tkfont.Font(**cfg)
                    elif isinstance(lbl_font, str):
                        fnt = tkfont.nametofont(lbl_font)
                except Exception:
                    fnt = None
            if fnt is None:
                max_chars = max(8, int(avail_px / 7))
                display = full if len(full) <= max_chars else full[: max_chars - 1].rstrip() + "…"
                app.status_label.configure(text=display)
                return
            if fnt.measure(full) <= avail_px:
                app.status_label.configure(text=full)
                return
            lo, hi = 0, len(full)
            best = ""
            ell = "…"
            while lo <= hi:
                mid = (lo + hi) // 2
                candidate = full[:mid] + ell
                if fnt.measure(candidate) <= avail_px:
                    best = candidate
                    lo = mid + 1
                else:
                    hi = mid - 1
            app.status_label.configure(text=best or ell)
        except Exception:
            pass

    def _schedule_truncate():
        try:
            if _resize_job["id"]:
                root.after_cancel(_resize_job["id"])
        except Exception:
            pass
        try:
            _resize_job["id"] = root.after(60, _truncate_status)
        except Exception:
            _truncate_status()

    def _on_destroy(_e=None):
        _destroyed["val"] = True
        try:
            if _resize_job["id"]:
                root.after_cancel(_resize_job["id"])
        except Exception:
            pass
        # Tooltip ggf. schließen (falls vorhanden)
        try:
            if hasattr(app, "_status_tooltip") and app._status_tooltip and app._status_tooltip.winfo_exists():
                app._status_tooltip.destroy()
        except Exception:
            pass
    try:
        app.status_bar.bind("<Destroy>", _on_destroy)
    except Exception:
        pass

    def _safe_call(fn, *a, **k):
        try:
            root.after(0, lambda: fn(*a, **k))
        except Exception:
            pass

    def _relative_luminance(hex_color: str) -> float:
        try:
            hc = hex_color.lstrip('#')
            if len(hc) == 3:
                hc = ''.join(ch*2 for ch in hc)
            r = int(hc[0:2], 16) / 255.0
            g = int(hc[2:4], 16) / 255.0
            b = int(hc[4:6], 16) / 255.0
            def _c(c):
                return c/12.92 if c <= 0.03928 else ((c+0.055)/1.055)**2.4
            r, g, b = _c(r), _c(g), _c(b)
            return 0.2126*r + 0.7152*g + 0.0722*b
        except Exception:
            return 0.0

    def _ensure_contrast(fg: str, bg: str) -> str:
        try:
            L1 = _relative_luminance(fg)
            L2 = _relative_luminance(bg)
            contrast = (max(L1, L2) + 0.05) / (min(L1, L2) + 0.05)
            if contrast < 2.5:  # einfache Schwelle, kein volles WCAG
                return _get_color("gray_900", "#111827")
        except Exception:
            return fg
        return fg

    def set_status(text: str, type_: str = "info", announce: bool = True):
        """Setzt Status-Text & Typ (thread-sicher).

        Parameters
        ----------
        text : str
            Neuer Status-Text (wird elided falls nötig)
        type_ : str
            info|success|warning|error bestimmt Farben/Icon
        announce : bool
            Optionaler Screenreader/Hook Call"""
        icon = ICON_BY_TYPE.get(type_, ICON_BY_TYPE["info"])
        color_icon, color_text = COLOR_BY_TYPE.get(type_, COLOR_BY_TYPE["info"])
        # Kontrast-Sicherheitsnetz für Text
        surface_bg = _get_color("surface_elevated", "#F8FAFC")
        color_text = _ensure_contrast(color_text, surface_bg)

        def _do():
            try:
                app._status_full_text = text
                app.status_indicator.configure(text=icon, text_color=color_icon)
                app.status_label.configure(text=text, text_color=color_text)
                _truncate_status()
                if announce:
                    cb = getattr(app, "on_status_announce", None)
                    if callable(cb):
                        try:
                            cb(text, type_)
                        except Exception:
                            pass
            except Exception:
                pass

        _safe_call(_do)

    def set_progress(
        pct: float | None = None,
        text: str | None = None,
        *,
        indeterminate: bool | None = None,
        type_: str = "info",
    ):
        """Aktualisiert Fortschritt. pct in [0,1]; indeterminate=True für Busy.

        pct=None lässt Balken/Anzeige unverändert. text=None lässt Status-Text unverändert."""
        color_icon, _ = COLOR_BY_TYPE.get(type_, COLOR_BY_TYPE["info"])

        def _do():
            try:
                app.mini_progress.configure(progress_color=color_icon)
                if indeterminate is True:
                    try:
                        app.mini_progress.start()
                        # Sichtbar machen falls versteckt
                        if not app.mini_progress.winfo_ismapped():
                            app.mini_progress.pack(side="left", padx=(20, 6))
                            app.progress_text.pack(side="left", padx=(2, 0))
                    except Exception:
                        pass
                    app.progress_text.configure(text="…")
                else:
                    try:
                        app.mini_progress.stop()
                    except Exception:
                        pass
                    if pct is not None:
                        val = max(0.0, min(1.0, float(pct)))
                        app.mini_progress.set(val)
                        if val <= 0.0:
                            # 0%: Balken ausblenden für kompakte Statuszeile
                            try:
                                app.mini_progress.pack_forget()
                                app.progress_text.pack_forget()
                            except Exception:
                                pass
                        else:
                            if not app.mini_progress.winfo_ismapped():
                                app.mini_progress.pack(side="left", padx=(20,6))
                                app.progress_text.pack(side="left", padx=(2,0))
                            app.progress_text.configure(text=f"{int(val * 100)}%")
                if text is not None:
                    app._status_full_text = text
                    app.status_label.configure(text=text)
                    _truncate_status()
            except Exception:
                pass

        _safe_call(_do)

    def set_files(n: int):
        """Aktualisiert Dateizähler."""
        def _do():
            try:
                app.file_count_label.configure(text=_t("Files: {n}").format(n=int(max(0, n))))
            except Exception:
                pass

        _safe_call(_do)

    # -------------------- Erweiterte Komfort-APIs --------------------
    app._status_prev_stack = getattr(app, "_status_prev_stack", [])  # für Verschachtelung (begrenzt)
    app._status_busy = getattr(app, "_status_busy", False)

    def flash_status(text: str, type_: str = "info", duration_ms: int = 3000):
        """Temporärer Status; danach Rückkehr zum vorherigen.

        Thread-safe & verschachtelbar."""
        prev = (getattr(app, "_status_full_text", ""), app.status_indicator.cget("text"))
        if len(app._status_prev_stack) > 20:
            app._status_prev_stack.pop(0)
        app._status_prev_stack.append(prev)
        set_status(text, type_)

        def _restore():
            try:
                if app._status_prev_stack:
                    old_text, _old_icon = app._status_prev_stack.pop()
                    if old_text:
                        set_status(old_text, announce=False)
            except Exception:
                pass

        try:
            root.after(duration_ms, _restore)
        except Exception:
            _restore()

    def set_busy(on: bool = True, text: str | None = None, type_: str = "info"):
        """Schaltet Busy/Indeterminate Modus ein/aus (pct bleibt bei Ende unverändert)."""
        app._status_busy = on
        if on:
            set_progress(indeterminate=True, text=text or getattr(app, "_status_full_text", ""), type_=type_)
        else:
            set_progress(indeterminate=False, pct=None, text=text)

    class StatusActivity:
        """Context-Manager für automatische Busy-Anzeige.

        Beispiel:
            with app.status_activity("Lade Daten…"):
                heavy_work()
        """

        def __init__(self, message: str, type_: str = "info"):
            self.message = message
            self.type_ = type_
            self._start_text = None

        def __enter__(self):
            self._start_text = getattr(app, "_status_full_text", "")
            set_busy(True, self.message, self.type_)
            return self

        def __exit__(self, exc_type, exc, tb):
            if exc:
                set_status(_t("Fehler"), "error")
            else:
                set_busy(False, self._start_text or _t("Fertig"), "success")
            return False  # Exceptions nicht unterdrücken

    # Exponieren erweiterter APIs
    app.flash_status = flash_status
    app.set_busy = set_busy
    app.status_activity = StatusActivity

    # Idempotent: nur überschreiben, keine harten Annahmen
    app.set_status = set_status
    app.set_progress = set_progress
    app.set_files = set_files

    # Initiale Standardwerte (nur beim ersten Aufbau sinnvoll)
    try:
        if not existing:
            # Kompakte Initialanzeige
            try:
                app.file_count_label.configure(text=_t("Dateien: 0"))
            except Exception:
                pass
            set_status(_t("System Ready"), "success", announce=False)
            set_progress(0.0, indeterminate=False, type_="info")
            set_files(0)
    except Exception:
        pass

    # Click-Handler / Cursor nur wenn Callback existiert
    try:
        if hasattr(app, "show_about_dialog"):
            app.version_label.configure(cursor="hand2")
            app.version_label.bind("<Button-1>", lambda _e: app.show_about_dialog())
        else:
            app.version_label.configure(cursor="arrow")
        if hasattr(app, "focus_files_panel"):
            app.file_count_label.configure(cursor="hand2")
            app.file_count_label.bind("<Button-1>", lambda _e: app.focus_files_panel())
        else:
            app.file_count_label.configure(cursor="arrow")
    except Exception:
        pass

    # Tooltip für vollen Status-Text
    def _bind_tooltip(widget, get_text):
        tip = {"w": None}

        def _destroy_tip():
            try:
                if tip["w"] and tip["w"].winfo_exists():
                    tip["w"].destroy()
            except Exception:
                pass
            tip["w"] = None

        def enter(_e):
            if _destroyed["val"]:
                return
            try:
                txt = get_text()
                if not txt:
                    return
                _destroy_tip()
                tw = ctk.CTkToplevel(widget)
                tip["w"] = tw
                app._status_tooltip = tw
                tw.overrideredirect(True)
                c = ctk.CTkLabel(
                    tw,
                    text=txt,
                    font=_font("caption"),
                    fg_color=_get_color("surface", "#FFFFFF"),
                    text_color=_get_color("text_primary", "#1F2937"),
                    corner_radius=8,
                    padx=8,
                    pady=6,
                )
                c.pack()
                tw.update_idletasks()
                x = widget.winfo_rootx() + 10
                y = widget.winfo_rooty() - (tw.winfo_height() + 8)
                # Clamp an Bildschirmgrenzen
                scr_w = widget.winfo_screenwidth()
                scr_h = widget.winfo_screenheight()
                x = max(0, min(x, scr_w - tw.winfo_width()))
                y = max(0, min(y, scr_h - tw.winfo_height()))
                tw.geometry(f"+{x}+{y}")
                try:
                    tw.bind("<Escape>", lambda __: _destroy_tip())
                except Exception:
                    pass
            except Exception:
                _destroy_tip()

        def leave(_e):
            _destroy_tip()

        try:
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.bind("<Destroy>", lambda _e: _destroy_tip())
        except Exception:
            pass

    try:
        _bind_tooltip(app.status_label, lambda: getattr(app, "_status_full_text", ""))
    except Exception:
        pass

    # Resize -> Eliding
    try:
        # Vorherigen Handler entfernen um keine Mehrfach-Binds zu sammeln
        app.status_bar.bind("<Configure>", "")
        app.status_bar.bind("<Configure>", lambda _e: _schedule_truncate())
    except Exception:
        pass

    # Getter & Version-Setter
    def get_status() -> str:
        return getattr(app, "_status_full_text", "") or ""

    def get_progress() -> float | None:
        try:
            return float(getattr(app.mini_progress, "_progress_value", None))
        except Exception:
            return None

    def set_version(v: str):
        try:
            app.version = v
            app.version_label.configure(text=_t("Quality Framework {v}").format(v=v))
        except Exception:
            pass

    app.get_status = get_status
    app.get_progress = get_progress
    app.set_version = set_version

    return app.status_bar
