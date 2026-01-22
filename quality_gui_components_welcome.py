"""Ausgelagerte Basic Welcome Output UI-Komponente (Design-System konform, mit CTA).

Optimierungen (Refactor 2025-08-21):
 - Verwendet jetzt zentrale create_card() / create_button() aus dem Design-System
 - Einheitliche Button-Stile (primary / secondary)
 - Keyboard-Shortcuts: Ctrl+U (Quell-Dateien), Ctrl+T (Übersetzungen), Ctrl+Shift+A (Analyse)
 - Keine direkten Farb-Hex Fallbacks für Standard-UI-Elemente (nur noch Token)
 - Struktur & bestehende Logik (Transitions / Listener) unverändert
"""
from __future__ import annotations
import customtkinter as ctk
try:  # Design-System Convenience (fail-safe bei Minimal-Start)
    from design_system import create_card, create_button, get_color, get_spacing as ds_get_spacing
except Exception:  # Fallback Minimal-Implementierung
    def create_card(**kwargs): return {'fg_color': '#FFFFFF', 'corner_radius': 12, **kwargs}
    def create_button(**kwargs): return kwargs
    def get_color(name): return '#FFFFFF'
    def ds_get_spacing(name): return 16

# Adapter (falls Design-System künftig Objekte anstatt dict liefert)
def _ensure_kwargs(obj_or_dict, defaults: dict) -> dict:
    try:
        if isinstance(obj_or_dict, dict):
            return {**defaults, **obj_or_dict}
        out = dict(defaults)
        for k in ('fg_color','corner_radius','border_width','text','command','width','height','hover_color','text_color','font'):
            if hasattr(obj_or_dict, k):
                out[k] = getattr(obj_or_dict, k)
        return out
    except Exception:
        return dict(defaults)

def show_basic_welcome_output(app):
    """Zeigt den einfachen Willkommens-Output (Fallback) – i18n, theming & CTAs.

    Features:
    - i18n: alle Strings via app._t
    - Theme-safe: ausschließlich get_color / Tokens
    - CTAs: Upload / Analyse wenn Methoden existieren
    - Keyboard: Enter/Space auf Card führt Primäraktion aus
    - Thread-safe Render via root.after
    """
    try:
        # Einmaliger Listener: Wenn Dateien erscheinen, Welcome durch Dashboard ersetzen
        try:
            if not getattr(app, '_welcome_files_listener_bound', False) and hasattr(app, 'event_bus') and getattr(app.event_bus, 'subscribe', None):
                def _on_files_changed(_evt=None):
                    try:
                        total = len(app.uploaded_files.get('source', [])) + len(app.uploaded_files.get('translation', []))
                        # Vorwärts: Dateien vorhanden -> Dashboard (wenn nicht schon aktiv)
                        if total > 0 and hasattr(app, '_create_analysis_dashboard'):
                            if getattr(app, '_current_view', None) != 'dashboard':
                                _soft_transition_to_dashboard(app)
                                return
                        # Rückwärts: Keine Dateien mehr -> Welcome anzeigen (wenn Dashboard aktiv)
                        if total == 0 and getattr(app, '_current_view', None) == 'dashboard':
                            _soft_transition_to_welcome(app)
                    except Exception:
                        pass
                app.event_bus.subscribe('files.changed', _on_files_changed)
                app._welcome_files_listener_bound = True
        except Exception:
            pass

        # Direkt umschalten falls schon Dateien vorhanden
        try:
            if (len(app.uploaded_files.get('source', [])) + len(app.uploaded_files.get('translation', []))) > 0 and hasattr(app, '_create_analysis_dashboard'):
                _soft_transition_to_dashboard(app)
                return
        except Exception:
            pass

        # View-State markieren (wird endgültig nach Render gesetzt)
        app._current_view = 'welcome'

        if getattr(app, 'root', None) and hasattr(app.root, 'after'):
            return app.root.after(0, lambda: _render_welcome(app))
        _render_welcome(app)
    except Exception as e:
        try:
            (getattr(app, 'logger', None) or __import__('logging').getLogger(__name__)).exception(f"Welcome UI error: {e}")
        except Exception:
            pass


def _render_welcome(app):  # getrennt für thread-safe after()
    try:
        # Clear
        for w in list(app.output_frame.winfo_children()):
            try: w.destroy()
            except Exception: pass

        # Spacing (Design-System bevorzugt)
        get_spacing = getattr(app, 'get_spacing', None)
        if not callable(get_spacing):  # Fallback auf Design-System Convenience
            get_spacing = ds_get_spacing
        pad_outer = get_spacing('xl')
        pad_lg = get_spacing('lg')
        pad_md = get_spacing('md')
        # Colors (Tokens) – nur Token-Fallbacks über weitere Token
        primary = _safe_color(app, 'primary', _safe_color(app, 'button_primary', ''))
        text_inverse = _safe_color(app, 'white', _safe_color(app, 'gray_50', ''))
        text_primary = _safe_color(app, 'text_primary', _safe_color(app, 'gray_700', ''))
        text_secondary = _safe_color(app, 'text_secondary', _safe_color(app, 'gray_500', ''))

        # Card via Design-System
        card_cfg = _ensure_kwargs(create_card(), {'border_width': 1})
        card = ctk.CTkFrame(app.output_frame, **card_cfg)
        card.pack(fill='x', pady=pad_outer, padx=pad_outer)

        # Header-Band
        header = ctk.CTkFrame(card, fg_color=primary)
        header.pack(fill='x')
        ctk.CTkLabel(
            header,
            text=_safe_t(app, 'Translation Quality Framework'),
            font=ctk.CTkFont(*_safe_typo(app, 'title')),
            text_color=text_inverse
        ).pack(pady=pad_md)

        # Body
        body = ctk.CTkFrame(card, fg_color='transparent')
        body.pack(fill='x', padx=pad_lg, pady=pad_lg)
        ctk.CTkLabel(
            body,
            text=_safe_t(app, 'Professional Translation Quality Analysis'),
            font=ctk.CTkFont(*_safe_typo(app, 'subheading')),
            text_color=text_primary,
            justify='center'
        ).pack(pady=(0, 6))
        ctk.CTkLabel(
            body,
            text=_safe_t(app, 'Upload files to begin analysis'),
            font=ctk.CTkFont(*_safe_typo(app, 'body')),
            text_color=text_secondary,
            justify='center'
        ).pack(pady=(0, 10))

        # Actions (ausgelagert für Klarheit)
        src_handler, trans_handler, start_handler, sample_handler = _build_welcome_actions(app, body)

        # Keyboard Fokus + Shortcuts
        def _primary_action():
            if callable(start_handler):
                return _safe_call(app, start_handler)()
            if callable(src_handler):
                return _safe_call(app, src_handler)()
        try:
            card.configure(takefocus=1)
            card.bind('<Return>', lambda e: _primary_action())
            card.bind('<space>',  lambda e: _primary_action())
            # Focus-Ring (Accessibility)
            def _on_focus_in(_e):
                try: card.configure(border_width=2, border_color=primary)
                except Exception: pass
            def _on_focus_out(_e):
                try: card.configure(border_width=1)
                except Exception: pass
            card.bind('<FocusIn>', _on_focus_in)
            card.bind('<FocusOut>', _on_focus_out)
        except Exception:
            pass
        _bind_welcome_shortcuts(app, src_handler, trans_handler, start_handler)

        # Footer + Status
        ctk.CTkLabel(
            body,
            text=_safe_t(app, 'Supported formats: PDF, DOCX, TXT, DOC, RTF, ODT • Drag & drop supported'),
            font=ctk.CTkFont(*_safe_typo(app, 'caption')),
            text_color=text_secondary,
            justify='center'
        ).pack(pady=(8, 0))
        try:
            total_files = len(app.uploaded_files.get('source', [])) + len(app.uploaded_files.get('translation', []))
            ctk.CTkLabel(
                body,
                text=_safe_t(app, 'Files ready: {n}').format(n=total_files),
                font=ctk.CTkFont(*_safe_typo(app, 'caption')),
                text_color=text_secondary,
            ).pack(pady=(6,0))
        except Exception:
            pass

    except Exception as e:
        try:
            (getattr(app, 'logger', None) or __import__('logging').getLogger(__name__)).exception(f"Welcome UI render error: {e}")
        except Exception:
            pass


# Globale Shortcut Bindings (Welcome Scope)
def _bind_welcome_shortcuts(app, src_handler, trans_handler, start_handler):
    try:
        root = getattr(app, 'root', None)
        if not root: return
        # Erst alte lösen
        _unbind_welcome_shortcuts(app)
        ids = []
        def _b(seq, fn):
            try:
                bid = root.bind_all(seq, lambda e: fn(), add='+')
                ids.append((seq, bid))
            except Exception:
                pass
        if callable(src_handler):
            _b('<Control-u>', _safe_call(app, src_handler))
        if callable(trans_handler):
            _b('<Control-t>', _safe_call(app, trans_handler))
        if callable(start_handler):
            _b('<Control-Shift-a>', _safe_call(app, start_handler))
        import sys as _sys
        if _sys.platform == 'darwin':
            if callable(src_handler): _b('<Command-u>', _safe_call(app, src_handler))
            if callable(trans_handler): _b('<Command-t>', _safe_call(app, trans_handler))
            if callable(start_handler): _b('<Command-Shift-a>', _safe_call(app, start_handler))
        app._welcome_bind_ids = ids
    except Exception:
        pass

def _unbind_welcome_shortcuts(app):
    try:
        root = getattr(app, 'root', None)
        if not root: return
        for seq, _bid in getattr(app, '_welcome_bind_ids', []) or []:
            try:
                root.unbind_all(seq)
            except Exception:
                pass
        app._welcome_bind_ids = []
    except Exception:
        pass


# ----------------- Helper (lokal, keine externe Abhängigkeit) -----------------
def _safe_t(app, key: str) -> str:
    try:
        return getattr(app, '_t', lambda k: k)(key)
    except Exception:
        return key

def _safe_typo(app, name: str):
    try:
        return app.get_typography(name)
    except Exception:
        return ("Segoe UI", 14, "normal")

def _safe_color(app, key: str, fallback: str):
    try:
        return app.get_color(key) or fallback
    except Exception:
        return fallback

def _safe_call(app, fn):
    """Erzeugt einen ausführungssicheren Wrapper für CTA / Shortcut Aktionen."""
    def _wrapped():
        try:
            if callable(fn):
                fn()
        except Exception as e:
            try:
                (getattr(app, 'logger', None) or __import__('logging').getLogger(__name__)).exception(f"CTA failed: {e}")
                if hasattr(app, '_show_toast'):
                    app._show_toast(_safe_t(app, 'Action failed'), 'warning')
            except Exception:
                pass
    return _wrapped


# -------- Transition Helper -------------------------------------------------
def _soft_transition_to_dashboard(app):
    """Weicher Übergang: leichte Opacity-Reduktion, dann Dashboard-Build.

    Hinweis: CustomTkinter unterstützt kein echtes Alpha pro Frame; wir simulieren
    einen Fade durch kurzfristiges Dimmen (Textfarbe), dann kompletten Austausch.
    """
    try:
        container = getattr(app, 'output_frame', None)
        if not container:
            if hasattr(app, '_create_analysis_dashboard'):
                app._create_analysis_dashboard()
            return

        # State setzen
        app._current_view = 'transition'

        # Sammle Widgets für temporäres Dimmen
        widgets = list(container.winfo_children())
        # Vor Wechsel Shortcuts lösen
        _unbind_welcome_shortcuts(app)
        dim_color = _safe_color(app, 'gray_400', _safe_color(app, 'text_secondary', ''))

        def _dim(step=0):
            try:
                # 3 Schritte Dimmen
                if step < 3:
                    for w in widgets:
                        try:
                            if isinstance(w, ctk.CTkLabel):
                                w.configure(text_color=dim_color)
                        except Exception:
                            pass
                    if getattr(app, 'root', None) and hasattr(app.root, 'after'):
                        app.root.after(40, lambda: _dim(step+1))
                    else:
                        _dim(step+1)
                else:
                    # Dashboard zeichnen
                    try:
                        for w in widgets:
                            try:
                                w.destroy()
                            except Exception:
                                pass
                        app._create_analysis_dashboard()
                        app._current_view = 'dashboard'
                    except Exception:
                        pass
            except Exception:
                # Fallback sofort wechseln
                try:
                    app._create_analysis_dashboard()
                    app._current_view = 'dashboard'
                except Exception:
                    pass

        if getattr(app, 'root', None) and hasattr(app.root, 'after'):
            app.root.after(0, _dim)
        else:
            try:
                app._create_analysis_dashboard()
                app._current_view = 'dashboard'
            except Exception:
                pass
    except Exception:
        try:
            app._create_analysis_dashboard()
            app._current_view = 'dashboard'
        except Exception: pass


def _build_welcome_actions(app, parent):
    """Erstellt die Aktions-Buttons der Willkommenskarte konsistent über Design-System.

    Rückgabe:
        tuple(src_handler, trans_handler, start_handler, sample_handler)
    """
    try:
        import customtkinter as ctk
    except Exception:
        return (lambda: None,)*4

    # Helper zum sicheren Handler-Aufruf
    def _maybe(fn):
        return fn if callable(fn) else (lambda *a, **k: None)

    # Vorhandene, vom App-Objekt bereitgestellte Aktionen ermitteln
    src_handler = getattr(app, 'open_source_files_dialog', None) or getattr(app, 'upload_source_files', None)
    trans_handler = getattr(app, 'open_translation_files_dialog', None) or getattr(app, 'upload_translation_files', None)
    start_handler = getattr(app, 'start_quality_workflow', None) or getattr(app, 'start_quality_analysis', None)
    sample_handler = getattr(app, 'load_sample_project', None)

    src_handler = _maybe(src_handler)
    trans_handler = _maybe(trans_handler)
    start_handler = _maybe(start_handler)
    sample_handler = _maybe(sample_handler)

    # Spacing / Styles aus Design-System beziehen
    get_color = getattr(app, 'get_color', lambda n, d=None: d or '#FFFFFF')
    get_spacing = getattr(app, 'get_spacing', lambda n: 8)
    get_font = getattr(app, 'get_font', lambda n: ("Segoe UI", 12, 'normal'))
    create_button = getattr(app, 'create_button', None)
    # Fallback falls create_button nicht existiert
    def _btn_cfg(style, text):
        if callable(create_button):
            cfg = create_button(style=style, text=text)
            # Einheitliche Breite erzwingen (leicht größer für deutsche Texte)
            cfg.setdefault('width', 180)
            return cfg
        # Minimaler Fallback
        return dict(text=text, fg_color=get_color('primary'), hover_color=get_color('primary_hover'),
                    text_color=get_color('white'), font=ctk.CTkFont(*get_font('button_md')), width=180)

    btn_frame = ctk.CTkFrame(parent, fg_color='transparent')
    btn_frame.pack(fill='x', pady=(get_spacing('md'), 0))

    # Button-Reihe
    try:
        buttons = [
            ('primary', 'Analyse starten', start_handler),
            ('secondary', 'Quelltexte', src_handler),
            ('secondary', 'Übersetzungen', trans_handler),
        ]
        if sample_handler != (lambda *a, **k: None):
            buttons.append(('secondary', 'Beispiel laden', sample_handler))

        for idx, (style, label, handler) in enumerate(buttons):
            cfg = _btn_cfg(style, label)
            try:
                btn = ctk.CTkButton(btn_frame, **cfg, command=_safe_call(app, handler))
            except TypeError:
                # Falls width in create_button Stil nicht akzeptiert → entfernen und erneut
                width = cfg.pop('width', None)
                btn = ctk.CTkButton(btn_frame, **cfg, command=_safe_call(app, handler))
                if width:
                    try: btn.configure(width=width)
                    except Exception: pass
            btn.grid(row=0, column=idx, padx=(0 if idx == 0 else get_spacing('sm')), pady=0, sticky='w')

        # Grid-Stretch deaktivieren (Buttons behalten kompakte Größe)
        btn_frame.grid_columnconfigure(tuple(range(len(buttons))), weight=0)
    except Exception:
        pass

    return src_handler, trans_handler, start_handler, sample_handler


# -------- Reverse Transition Helper ----------------------------------------
def _soft_transition_to_welcome(app):
    """Weicher Übergang zurück zum Welcome Screen.

    Wird genutzt wenn alle Dateien entfernt wurden.
    """
    try:
        container = getattr(app, 'output_frame', None)
        if not container:
            show_basic_welcome_output(app)
            return

        app._current_view = 'transition'
        widgets = list(container.winfo_children())
        # Shortcuts sicher lösen vor Neuaufbau
        _unbind_welcome_shortcuts(app)
        dim_color = _safe_color(app, 'gray_400', _safe_color(app, 'text_secondary', ''))

        def _dim(step=0):
            try:
                if step < 3:
                    for w in widgets:
                        try:
                            if isinstance(w, ctk.CTkLabel):
                                w.configure(text_color=dim_color)
                        except Exception:
                            pass
                    if getattr(app, 'root', None) and hasattr(app.root, 'after'):
                        app.root.after(40, lambda: _dim(step+1))
                    else:
                        _dim(step+1)
                else:
                    for w in widgets:
                        try:
                            w.destroy()
                        except Exception:
                            pass
                    show_basic_welcome_output(app)
            except Exception:
                # Fallback direkt
                show_basic_welcome_output(app)

        if getattr(app, 'root', None) and hasattr(app.root, 'after'):
            app.root.after(0, _dim)
        else:
            show_basic_welcome_output(app)
    except Exception:
        try:
            show_basic_welcome_output(app)
        except Exception:
            pass
