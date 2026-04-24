"""Analyse-Konfigurationssektion (Neuaufbau nach vollständiger Reorganisation).

Ziele des Neuaufbaus:
- Zusammengeführte Karte für Sprache, Optionen und Qualitätskriterien
- Kompakter Header mit Status-Badges
- Linke Spalte: Sprachpaar, Prüftiefe, Analyse-Bausteine, Semantik + lokales Modell, Glossar, Reset
- Rechte Spalte: Qualitätskriterien mit responsivem Grid (3/2/1 Spalten) + Toolbar (Alle an/aus, Export, Import, Standard)
- Vereinfachung: Kein Drag&Drop / Reorder / Critical Flags aktuell sichtbar (Backend-Persistenz für Reihenfolge bleibt)
- Collapse weit    # Toolbar Buttons - Kompakte, einheitliche Typographie
    def _toolbar_btn(text, cmd, tooltip=None):
        b = ctk.CTkButton(
            toolbar, 
            text=app._t(text), 
            width=42, 
            height=28, 
            fg_color=app.get_color('transparent'), 
            hover_color=app.get_color('surface_hover'),
            text_color=app.get_color('text_secondary'),
            font=ctk.CTkFont('Segoe UI', 10, weight='normal'),
            command=cmd
        ) (nur Grid + Summary)
"""
from __future__ import annotations
from typing import Any, Dict, List
import logging
from ds_utils import safe_radius

try:
    import customtkinter as ctk  # type: ignore
    import tkinter as tk
except Exception:  # pragma: no cover
    ctk = None  # type: ignore
    tk = None  # type: ignore


def build_analysis_section(app, parent):
    if ctk is None:
        return
    logger = logging.getLogger(__name__)

    # ---------- Helpers ----------
    if not hasattr(app, '_ctkfont_cache'):
        app._ctkfont_cache = {}

    def _font(token: str):
        try:
            cache = app._ctkfont_cache
            if token not in cache:
                cache[token] = ctk.CTkFont(*app.get_typography(token))
            return cache[token]
        except Exception:
            return ctk.CTkFont('Segoe UI', 12)

    def _sp(token: str, fallback: int) -> int:
        try:
            return int(app.get_spacing(token))
        except Exception:
            return fallback

    def _radius(token: str, fallback: int) -> int:
        return safe_radius(app, token, fallback)

    # ---------- Mappings / Defaults ----------
    if not hasattr(app, 'LANG_DISPLAY2ISO'):
        # Anzeige -> ISO (Deutsch lokalisiert)
        app.LANG_DISPLAY2ISO = {  # type: ignore
            'Englisch': 'en', 'Deutsch': 'de', 'Französisch': 'fr', 'Spanisch': 'es', 'Italienisch': 'it', 'Auto-Erkennung': 'auto'
        }
    if not hasattr(app, 'DEPTH_OPTIONS'):
        app.DEPTH_OPTIONS = [  # type: ignore
            ('quick', 'Schnelle Analyse'),
            ('medium', 'Mittlere Analyse'),
            ('extensive', 'Umfangreiche Analyse')
        ]

    default_quality = [
        ('accuracy', 'Genauigkeit'),
        ('fluency', 'Flüssigkeit'),
        ('grammar', 'Grammatik'),
        ('terminology', 'Terminologie'),
        ('style', 'Stil'),
        ('completeness', 'Vollständigkeit')
    ]
    key_to_label = {k: v for k, v in default_quality}

    # ---------- Card Grundstruktur ----------
    card = app._create_card_frame(parent, corner_radius=_radius('radius_md', 8), border_width=1)
    card.pack(fill='x', padx=4, pady=(0, 6))

    header_frame = ctk.CTkFrame(card, fg_color=app.get_color('surface'), height=46)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    header_content = ctk.CTkFrame(header_frame, fg_color=app.get_color('transparent'))
    header_content.pack(fill='x', padx=_sp('md', 16), pady=_sp('xs', 4))
    try:
        app._add_header_accent(header_content, 'warning')
    except Exception:
        pass
    header_label = ctk.CTkLabel(header_content, text=app._t('2. Analyse'), font=ctk.CTkFont(*app.get_typography('heading_sm')), text_color=app.get_color('text_primary'))
    header_label.pack(side='left', padx=(10,0))
    badge_container = ctk.CTkFrame(header_content, fg_color=app.get_color('transparent'))
    badge_container.pack(side='right', padx=(0,4))
    status_label = ctk.CTkLabel(header_content, text=app._t('Bereit'), font=_font('caption'), text_color=app.get_color('success'))
    status_label.pack(side='right')

    content = ctk.CTkFrame(card, fg_color=app.get_color('transparent'))
    content.pack(fill='x', padx=_sp('md',16), pady=_sp('md',10))

    # Sprachsektion
    lang_section = ctk.CTkFrame(content, fg_color=app.get_color('surface'), border_width=1, border_color=app.get_color('surface_border'), corner_radius=_radius('radius_md',8))
    lang_section.pack(fill='x', pady=(0,_sp('md',12)))
    lang_header = ctk.CTkLabel(lang_section, text=app._t('Sprachpaar-Konfiguration'), font=_font('heading_xs'), text_color=app.get_color('text_primary'))
    lang_header.pack(pady=(_sp('md',10), _sp('sm',6)))
    lang_frame = ctk.CTkFrame(lang_section, fg_color=app.get_color('transparent'))
    lang_frame.pack(fill='x', padx=_sp('md',15), pady=(0,_sp('md',15)))
    lang_frame.grid_columnconfigure(0, weight=1)
    lang_frame.grid_columnconfigure(1, weight=1)

    app.var_source_lang = getattr(app, 'var_source_lang', tk.StringVar(value='auto'))
    app.var_target_lang = getattr(app, 'var_target_lang', tk.StringVar(value='de'))
    _langs_src = [app._t(x) for x in ['Auto-Erkennung','Deutsch','Englisch','Französisch','Spanisch','Italienisch']]
    _langs_tgt = [app._t(x) for x in ['Deutsch','Englisch','Französisch','Spanisch','Italienisch']]
    def _on_src_lang(sel: str):
        try:
            # robust: sowohl lokalisierten Key als auch Original prüfen
            iso = app.LANG_DISPLAY2ISO.get(sel)
            if iso is None:
                rev = {app._t(k): v for k, v in app.LANG_DISPLAY2ISO.items()}
                iso = rev.get(sel, 'auto')
            app.var_source_lang.set(iso)
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.lang.source', app.var_source_lang.get())
        except Exception:
            pass
    # Quelle-Dropdown im sichtbaren, hellen Wrapper
    src_wrap = ctk.CTkFrame(
        lang_frame,
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    src_wrap.grid(row=0, column=0, sticky='ew', padx=(0,8))
    app.source_lang = ctk.CTkOptionMenu(
        src_wrap,
        values=_langs_src,
        fg_color=app.get_color('white'),
        button_color=app.get_color('primary'),
        button_hover_color=app.get_color('primary_hover'),
        dropdown_fg_color=app.get_color('white'),
        dropdown_hover_color=app.get_color('surface_hover'),
        text_color=app.get_color('gray_900'),
        dropdown_text_color=app.get_color('text_primary'),
        font=_font('body'),
        command=_on_src_lang,
        corner_radius=6,
        height=36
    )
    app.source_lang.set(app._t('Auto-Erkennung'))
    app.source_lang.pack(fill='x', padx=8, pady=8)
    def _on_tgt_lang(sel: str):
        try:
            iso = app.LANG_DISPLAY2ISO.get(sel)
            if iso is None:
                rev = {app._t(k): v for k, v in app.LANG_DISPLAY2ISO.items()}
                iso = rev.get(sel, 'de')
            app.var_target_lang.set(iso)
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.lang.target', app.var_target_lang.get())
        except Exception:
            pass
    # Ziel-Dropdown im sichtbaren, hellen Wrapper
    tgt_wrap = ctk.CTkFrame(
        lang_frame,
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    tgt_wrap.grid(row=0, column=1, sticky='ew', padx=(8,0))
    app.target_lang = ctk.CTkOptionMenu(
        tgt_wrap,
        values=_langs_tgt,
        fg_color=app.get_color('white'),
        button_color=app.get_color('primary'),
        button_hover_color=app.get_color('primary_hover'),
        dropdown_fg_color=app.get_color('white'),
        dropdown_hover_color=app.get_color('surface_hover'),
        text_color=app.get_color('gray_900'),
        dropdown_text_color=app.get_color('text_primary'),
        font=_font('body'),
        command=_on_tgt_lang,
        corner_radius=6,
        height=36
    )
    app.target_lang.set(app._t('Deutsch'))
    app.target_lang.pack(fill='x', padx=8, pady=8)

    # Persistierte Sprachwahl anwenden (ISO -> Anzeige)
    try:
        if getattr(app,'settings_service',None):
            s = app.settings_service.get('analysis.lang.source', 'auto')
            t = app.settings_service.get('analysis.lang.target', 'de')
            iso2disp = {v: k for k, v in app.LANG_DISPLAY2ISO.items()}
            if s in iso2disp:
                app.source_lang.set(app._t(iso2disp[s]))
            if t in iso2disp:
                app.target_lang.set(app._t(iso2disp[t]))
            app.var_source_lang.set(s)
            app.var_target_lang.set(t)
    except Exception:
        pass

    # Erweiterte Analyse Sektion - Modernisierte UX mit verbesserter visueller Hierarchie
    options_section = ctk.CTkFrame(content, fg_color=app.get_color('background'), border_width=0, corner_radius=0)
    options_section.pack(fill='both', expand=True, pady=(0, 0))
    
    # Header Container mit Hintergrund
    options_header_container = ctk.CTkFrame(options_section, fg_color=app.get_color('surface'))
    options_header_container.pack(fill='x', padx=0, pady=(0, 0))
    
    # Hauptheader - KONSISTENTE TYPOGRAPHIE
    options_header = ctk.CTkLabel(
        options_header_container, 
        text=app._t('Erweiterte Analyse'), 
        font=_font('heading_md'),  # ✅ Verwendet get_typography (war size 18)
        text_color=app.get_color('text_primary')
    )
    options_header.pack(anchor='w', padx=24, pady=(20, 4))
    
    # Untertitel - KONSISTENTE TYPOGRAPHIE
    options_desc = ctk.CTkLabel(
        options_header_container,
        text=app._t('Konfiguration der Analysemodule und Qualitätskriterien'),
        font=_font('body'),  # ✅ Verwendet get_typography (war size 12)
        text_color=app.get_color('text_secondary')
    )
    options_desc.pack(anchor='w', padx=24, pady=(0, 20))

    # Hauptcontainer mit optimierter 50/50-Aufteilung
    main_container = ctk.CTkFrame(options_section, fg_color=app.get_color('background'))
    main_container.pack(fill='both', expand=True, padx=24, pady=(16, 24))
    
    # Feste Spaltenbreiten für echte Gleichmäßigkeit
    main_container.grid_columnconfigure(0, weight=1, minsize=360, uniform="analysis_cols")
    main_container.grid_columnconfigure(1, weight=1, minsize=360, uniform="analysis_cols")
    main_container.grid_rowconfigure(0, weight=1)
    
    # Konfiguration Links - Moderne Card mit subtiler Elevation
    config_section = ctk.CTkFrame(
        main_container, 
        fg_color=app.get_color('surface'), 
        corner_radius=12,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    config_section.grid(row=0, column=0, sticky='nsew', padx=(0, 12))
    
    # Card Header - Modernisiertes Design
    config_header_frame = ctk.CTkFrame(
        config_section, 
        fg_color=app.get_color('white'),
        corner_radius=12
    )
    config_header_frame.pack(fill='x', padx=1, pady=1)
    
    config_header = ctk.CTkLabel(
        config_header_frame, 
        text=app._t('Konfiguration'), 
        font=ctk.CTkFont('Segoe UI', 14, weight='bold'), 
        text_color=app.get_color('text_primary')
    )
    config_header.pack(pady=16, padx=20, anchor='w')
    
    config_content = ctk.CTkFrame(config_section, fg_color=app.get_color('transparent'))
    config_content.pack(fill='both', expand=True, padx=20, pady=(4, 20))

    # Labels mit KONSISTENTER TYPOGRAPHIE - Gleiche Font überall
    section_label_cfg = dict(
        font=_font('body_bold'),  # ✅ Verwendet get_typography für Konsistenz
        text_color=app.get_color('text_secondary')
    )

    # Prüftiefe - Modernisiertes Dropdown
    depth_frame = ctk.CTkFrame(config_content, fg_color=app.get_color('transparent'))
    depth_frame.pack(fill='x', pady=(0, 20))
    depth_label = ctk.CTkLabel(depth_frame, text=app._t('Prüftiefe'), **section_label_cfg)
    depth_label.pack(anchor='w', pady=(0, 8))
    
    app.var_depth = getattr(app, 'var_depth', tk.StringVar(value='medium'))
    _depth_values_localized = [app._t(lbl) for _, lbl in app.DEPTH_OPTIONS]
    # Dropdown mit besserer Typographie
    # Mapping: lokalisierter Label -> interner Key
    _DEPTH_LABEL2KEY = {app._t(lbl): key for key, lbl in app.DEPTH_OPTIONS}
    _DEPTH_ALIASES = {
        'standard': 'medium',
        'deep': 'extensive',
        'full': 'extensive'
    }
    def _on_depth_change(selected: str):
        try:
            key = _DEPTH_LABEL2KEY.get(selected)
            if key is None:
                key = _DEPTH_ALIASES.get(selected, 'medium')
            app.var_depth.set(key)
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.depth', key)
            # Optional: Statusanzeige / Toast
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Prüftiefe gesetzt')+': '+selected, 'info', 2000)
            # Automatisches Profil anwenden falls Kriterien schon existieren
            try:
                if hasattr(app,'quality_vars') and app.quality_vars:
                    _apply_depth_profile(key)
            except Exception:
                pass
        except Exception:
            pass
    # Eingabefeld-Wrapper mit deutlich sichtbarem Rahmen für bessere Lesbarkeit
    depth_input_wrap = ctk.CTkFrame(
        depth_frame,
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')  # Stil wie Module-Container
    )
    depth_input_wrap.pack(fill='x', pady=(2, 12))

    app.analysis_depth = ctk.CTkOptionMenu(
        depth_input_wrap,
        values=_depth_values_localized,
        fg_color=app.get_color('white'),  # ✅ Weißer Hintergrund für Text-Bereich
        button_color=app.get_color('primary'),  # ✅ Blauer Button
        button_hover_color=app.get_color('primary_hover'),
        dropdown_fg_color=app.get_color('white'),
        dropdown_hover_color=app.get_color('surface_hover'),
        text_color=app.get_color('gray_900'),  # ✅ Dunkler Text "Standard"
        dropdown_text_color=app.get_color('text_primary'),
        font=_font('body_bold'),
        dropdown_font=_font('body'),
        width=300,
        height=40,
        corner_radius=6,
        command=_on_depth_change
    )
    try:
        # Pfeil/Arrow auf weiß setzen – verschiedene interne Attribute absichern
        for _attr in ('_open_button', '_dropdown_button', '_button'):
            _btn = getattr(app.analysis_depth, _attr, None)
            if _btn:
                try:
                    _btn.configure(text_color=app.get_color('white'))
                except Exception:
                    pass
        # Sicherheit: Dropdown-Menü hell halten
        if hasattr(app.analysis_depth, '_dropdown_menu') and app.analysis_depth._dropdown_menu:
            app.analysis_depth._dropdown_menu.configure(fg_color=app.get_color('white'))
        # Fallback: Zeichne einen weißen, sauberen Chevron auf Canvas (kein Icon/Text)
        try:
            _btn = getattr(app.analysis_depth, '_open_button', None) or \
                   getattr(app.analysis_depth, '_dropdown_button', None) or \
                   getattr(app.analysis_depth, '_button', None)
            if _btn:
                # Vorhandenes Canvas bereinigen
                try:
                    if getattr(app, 'analysis_depth_white_arrow_canvas', None):
                        app.analysis_depth_white_arrow_canvas.destroy()
                except Exception:
                    pass
                # Canvas klein halten und Hintergrund an Button-Farbe anpassen
                _bg = app.get_color('primary')
                c = tk.Canvas(_btn, width=16, height=12, highlightthickness=0, bd=0, bg=_bg)
                # Zwei Linien als Chevron ▾ zeichnen (rundere Kappen für Anti-Aliasing-Effekt)
                c.create_line(3, 4, 8, 9, fill=app.get_color('white'), width=2, capstyle=tk.ROUND)
                c.create_line(13, 4, 8, 9, fill=app.get_color('white'), width=2, capstyle=tk.ROUND)
                c.place(relx=0.5, rely=0.5, anchor='center')
                c.lift()
                # Hover-State anpassen, damit Canvas-Hintergrund mitwechselt
                def _on_enter(_e):
                    try:
                        c.configure(bg=app.get_color('primary_hover'))
                    except Exception:
                        pass
                def _on_leave(_e):
                    try:
                        c.configure(bg=app.get_color('primary'))
                    except Exception:
                        pass
                try:
                    _btn.bind('<Enter>', _on_enter)
                    _btn.bind('<Leave>', _on_leave)
                except Exception:
                    pass
                app.analysis_depth_white_arrow_canvas = c
        except Exception:
            pass
    except Exception:
        pass
    app.analysis_depth.set(app._t('Mittlere Analyse'))
    # Im Wrapper mit Innenabstand platzieren, damit der Rahmen sichtbar bleibt
    app.analysis_depth.pack(fill='x', padx=12, pady=10)
    # Entfernt: frühere Hinweiszeile zu Profilen (reduziert visuelle Dichte)
    # (Bei Bedarf wieder aktivierbar – Code bewusst gelöscht statt versteckt um Rendering-Kosten zu sparen.)
    # Persistierten Wert anwenden
    try:
        if getattr(app,'settings_service',None):
            saved_depth = app.settings_service.get('analysis.depth', 'medium')
            legacy_map = {
                'standard': 'medium',
                'deep': 'extensive',
                'full': 'extensive'
            }
            normalized_depth = legacy_map.get(saved_depth, saved_depth)
            if normalized_depth != saved_depth:
                try:
                    app.settings_service.set('analysis.depth', normalized_depth)
                except Exception:
                    pass
            # reverse lookup: key -> localized label
            key2label = {k: app._t(lbl) for k,lbl in app.DEPTH_OPTIONS}
            if normalized_depth in key2label:
                app.analysis_depth.set(key2label[normalized_depth])
                app.var_depth.set(normalized_depth)
    except Exception:
        pass

    # Module Label - Klarere Hierarchie
    phases_header = ctk.CTkLabel(config_content, text=app._t('Module'), **section_label_cfg)
    phases_header.pack(anchor='w', pady=(20, 8))
    
    # Module Container - Modernisiertes Card-Design
    toggle_container = ctk.CTkFrame(
        config_content, 
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    toggle_container.pack(fill='x', pady=(0, 20))
    try:
        toggle_container.lift()
    except Exception:
        pass
    
    toggle_frame = ctk.CTkFrame(toggle_container, fg_color="transparent")
    toggle_frame.pack(fill='x', padx=16, pady=16)

    # State Variablen (bestehend beibehalten / wiederverwenden)
    app.var_phase2_enabled = getattr(app, 'var_phase2_enabled', tk.BooleanVar(value=True))
    app.var_phase3_enabled = getattr(app, 'var_phase3_enabled', tk.BooleanVar(value=False))
    app.var_phase3_semantic = getattr(app, 'var_phase3_semantic', tk.BooleanVar(value=False))
    app.var_phase3_semantic_ollama = getattr(app, 'var_phase3_semantic_ollama', tk.BooleanVar(value=False))

    def _persist_bool(key: str, var):
        try:
            if getattr(app, 'settings_service', None):
                app.settings_service.set(key, bool(var.get()))
        except Exception:
            pass

    # Persistierte Werte wiederherstellen
    try:
        if getattr(app, 'settings_service', None):
            app.var_phase2_enabled.set(bool(app.settings_service.get('analysis.phase2.enabled', True)))
            app.var_phase3_enabled.set(bool(app.settings_service.get('analysis.phase3.enabled', False)))
            app.var_phase3_semantic.set(bool(app.settings_service.get('analysis.phase3.semantic', False)))
            app.var_phase3_semantic_ollama.set(bool(app.settings_service.get('analysis.phase3.semantic.use_ollama', False)))
    except Exception:
        pass

    def _update_status_label():
        pass  # ersetzt durch Badge-Renderer

    # Checkboxes - Größere, modernere Checkboxen
    phase2_cb = ctk.CTkCheckBox(
        toggle_frame, 
        text=app._t('Struktur & Glossar'), 
        variable=app.var_phase2_enabled, 
        font=ctk.CTkFont('Segoe UI', 13), 
        text_color=app.get_color('text_primary'),
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        checkbox_height=18, 
        checkbox_width=18,
        corner_radius=4,
        command=lambda: (_persist_bool('analysis.phase2.enabled', app.var_phase2_enabled), _update_status_label())
    )
    phase2_cb.pack(anchor='w', pady=(0, 10))
    
    phase3_cb = ctk.CTkCheckBox(
        toggle_frame, 
        text=app._t('Stil & Lesbarkeit'), 
        variable=app.var_phase3_enabled, 
        font=ctk.CTkFont('Segoe UI', 13), 
        text_color=app.get_color('text_primary'),
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        checkbox_height=18, 
        checkbox_width=18,
        corner_radius=4,
        command=lambda: (_persist_bool('analysis.phase3.enabled', app.var_phase3_enabled), _update_status_label())
    )
    phase3_cb.pack(anchor='w', pady=(0, 10))
    
    semantic_cb = ctk.CTkCheckBox(
        toggle_frame,
        text=app._t('Semantik'),
        variable=app.var_phase3_semantic,
        font=ctk.CTkFont('Segoe UI', 13),
        text_color=app.get_color('text_primary'),
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        checkbox_height=18,
        checkbox_width=18,
        corner_radius=4,
        command=lambda: (_persist_bool('analysis.phase3.semantic', app.var_phase3_semantic), _update_status_label())
    )
    semantic_cb.pack(anchor='w', pady=(0, 8))

    # Lokales Modell
    app.var_ollama_model = getattr(app, 'var_ollama_model', tk.StringVar(value=''))
    try:
        if getattr(app, 'settings_service', None):
            saved_model = app.settings_service.get('analysis.phase3.semantic.ollama_model', '')
            if saved_model:
                app.var_ollama_model.set(saved_model)
    except Exception:
        pass

    def _persist_model():
        try:
            if getattr(app, 'settings_service', None):
                app.settings_service.set('analysis.phase3.semantic.ollama_model', app.var_ollama_model.get())
        except Exception:
            pass

    def _ollama_health_check(timeout=1.0):
        try:
            import urllib.request
            with urllib.request.urlopen('http://127.0.0.1:11434/api/version', timeout=timeout):  # type: ignore
                return True
        except Exception:
            return False

    def _fetch_models():
        models = []
        try:
            import json, urllib.request
            req = urllib.request.Request('http://127.0.0.1:11434/api/tags', method='GET')
            with urllib.request.urlopen(req, timeout=2) as resp:  # type: ignore
                data = json.loads(resp.read().decode('utf-8'))
                for m in data.get('models', []):
                    n = m.get('name','')
                    if n:
                        models.append(n)
        except Exception:
            pass
        emb = [m for m in models if 'embed' in m.lower()]
        return emb or models or ['nomic-embed-text']

    def _apply_models(lst: List[str]):
        try:
            if getattr(app, 'ollama_model_dropdown', None):
                app.ollama_model_dropdown.configure(values=lst)
            if app.var_ollama_model.get() not in lst:
                app.var_ollama_model.set(lst[0]); _persist_model()
        except Exception:
            pass

    def _async_models():
        import threading
        def _worker():
            lst = _fetch_models()
            try:
                (getattr(app,'root', app)).after(0, lambda: _apply_models(lst))
            except Exception:
                pass
        threading.Thread(target=_worker, daemon=True).start()

    def _on_toggle_local():
        _persist_bool('analysis.phase3.semantic.use_ollama', app.var_phase3_semantic_ollama)
        enabled = bool(app.var_phase3_semantic_ollama.get())
        wrap = getattr(app, 'ollama_model_wrap', None)
        if enabled:
            if not _ollama_health_check():
                app.var_phase3_semantic_ollama.set(False)
                _persist_bool('analysis.phase3.semantic.use_ollama', app.var_phase3_semantic_ollama)
                if getattr(app,'show_toast',None):
                    app.show_toast(app._t('Ollama nicht erreichbar'), 'warning')
                if wrap and wrap.winfo_manager():
                    wrap.pack_forget()
                return
            if wrap and not wrap.winfo_manager():
                wrap.pack(anchor='w', pady=(0,2))
            _async_models()
        else:
            if wrap and wrap.winfo_manager():
                wrap.pack_forget()

    semantic_ollama_cb = ctk.CTkCheckBox(
        toggle_frame, 
        text=app._t('Lokal (Ollama)'), 
        variable=app.var_phase3_semantic_ollama, 
        font=_font('body'),  # ✅ Konsistente Font
        text_color=app.get_color('text_secondary'),
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        checkbox_height=18,  # ✅ Standardisiert auf 18 (war 16)
        checkbox_width=18,   # ✅ Standardisiert auf 18 (war 16)
        corner_radius=4,
        command=_on_toggle_local
    )
    semantic_ollama_cb.pack(anchor='w', pady=(4, 8), padx=(0, 0))  # ✅ Kein Einzug - direkt unter Semantik

    # Modell-Dropdown mit besserer Sichtbarkeit: Label + kräftiger Rahmen
    _model_wrap = ctk.CTkFrame(
        toggle_frame,
        fg_color=app.get_color('surface'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('primary')
    )
    app.ollama_model_wrap = _model_wrap
    # Label für Klarheit
    model_label = ctk.CTkLabel(
        _model_wrap,
        text=app._t('Modell'),
        font=_font('caption'),
        text_color=app.get_color('text_secondary')
    )
    model_label.pack(anchor='w', padx=8, pady=(6,2))
    app.ollama_model_dropdown = ctk.CTkOptionMenu(
        _model_wrap,
        values=['nomic-embed-text'],
        variable=app.var_ollama_model,
        command=lambda _: _persist_model(),
        fg_color=app.get_color('primary'),
        button_color=app.get_color('primary_hover'),
        button_hover_color=app.get_color('primary'),
        text_color=app.get_color('text_inverse'),
        font=_font('body'),  # ✅ Konsistente Font (war hardcoded)
        width=200,
        height=34
    )
    app.ollama_model_dropdown.pack(fill='x', padx=8, pady=(0,8))

    def _focus_in(_e):
        try:
            _model_wrap.configure(border_color=app.get_color('primary_hover'))
        except Exception:
            pass
    def _focus_out(_e):
        try:
            _model_wrap.configure(border_color=app.get_color('primary'))
        except Exception:
            pass
    app.ollama_model_dropdown.bind('<FocusIn>', _focus_in)
    app.ollama_model_dropdown.bind('<FocusOut>', _focus_out)
    if app.var_phase3_semantic_ollama.get() and _ollama_health_check():
        app.ollama_model_wrap.pack(anchor='w', pady=(0,2))
        _async_models()
    else:
        try:
            app.var_phase3_semantic_ollama.set(False)
        except Exception:
            pass

    # =====================================================================
    # KI-Prüfungen (Custom Prompts) - Benutzerdefinierte Fragen an Ollama
    # =====================================================================
    ki_header = ctk.CTkLabel(config_content, text=app._t('KI-Prüfungen'), **section_label_cfg)
    ki_header.pack(anchor='w', pady=(20, 8))
    
    ki_container = ctk.CTkFrame(
        config_content,
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    ki_container.pack(fill='x', pady=(0, 20))
    
    ki_content = ctk.CTkFrame(ki_container, fg_color=app.get_color('transparent'))
    ki_content.pack(fill='x', padx=16, pady=12)
    
    # Beschreibungstext
    ki_desc = ctk.CTkLabel(
        ki_content,
        text=app._t('Stellen Sie spezifische Fragen, die vor der Analyse geprüft werden:'),
        font=_font('caption'),
        text_color=app.get_color('text_secondary'),
        wraplength=280,
        justify='left'
    )
    ki_desc.pack(anchor='w', pady=(0, 8))
    
    # Variable für benutzerdefinierte Prüfung
    app.var_custom_ki_prompt = getattr(app, 'var_custom_ki_prompt', tk.StringVar(value=''))
    app.var_custom_ki_enabled = getattr(app, 'var_custom_ki_enabled', tk.BooleanVar(value=False))
    
    # Persistierte Werte laden
    try:
        if getattr(app, 'settings_service', None):
            saved_prompt = app.settings_service.get('analysis.ki.custom_prompt', '')
            saved_enabled = app.settings_service.get('analysis.ki.custom_enabled', False)
            if saved_prompt:
                app.var_custom_ki_prompt.set(saved_prompt)
            app.var_custom_ki_enabled.set(bool(saved_enabled))
    except Exception:
        pass
    
    # Checkbox zum Aktivieren
    def _on_toggle_custom_ki():
        try:
            if getattr(app, 'settings_service', None):
                app.settings_service.set('analysis.ki.custom_enabled', bool(app.var_custom_ki_enabled.get()))
        except Exception:
            pass
        # Textfeld-Zustand aktualisieren
        try:
            state = 'normal' if app.var_custom_ki_enabled.get() else 'disabled'
            app.custom_ki_textbox.configure(state=state)
        except Exception:
            pass
    
    ki_enable_cb = ctk.CTkCheckBox(
        ki_content,
        text=app._t('Benutzerdefinierte Prüfung aktivieren'),
        variable=app.var_custom_ki_enabled,
        font=_font('body'),
        text_color=app.get_color('text_primary'),
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        checkbox_height=18,
        checkbox_width=18,
        corner_radius=4,
        command=_on_toggle_custom_ki
    )
    ki_enable_cb.pack(anchor='w', pady=(0, 8))
    
    # Textfeld für benutzerdefinierte Frage
    app.custom_ki_textbox = ctk.CTkTextbox(
        ki_content,
        height=60,
        fg_color=app.get_color('white'),
        text_color=app.get_color('text_primary'),
        border_width=1,
        border_color=app.get_color('gray_300'),
        font=_font('body'),
        corner_radius=6,
        wrap='word'
    )
    app.custom_ki_textbox.pack(fill='x', pady=(0, 8))
    
    # Platzhalter einfügen falls leer
    if app.var_custom_ki_prompt.get():
        app.custom_ki_textbox.insert('1.0', app.var_custom_ki_prompt.get())
    else:
        app.custom_ki_textbox.insert('1.0', 'z.B. "Prüfe ob alle Produktnamen korrekt beibehalten wurden"')
        app.custom_ki_textbox.configure(text_color=app.get_color('text_tertiary'))
    
    # State je nach Checkbox
    if not app.var_custom_ki_enabled.get():
        app.custom_ki_textbox.configure(state='disabled')
    
    def _on_ki_focus_in(_e):
        try:
            txt = app.custom_ki_textbox.get('1.0', 'end-1c')
            if txt.startswith('z.B.'):
                app.custom_ki_textbox.delete('1.0', 'end')
                app.custom_ki_textbox.configure(text_color=app.get_color('text_primary'))
        except Exception:
            pass
    
    def _on_ki_focus_out(_e):
        try:
            txt = app.custom_ki_textbox.get('1.0', 'end-1c').strip()
            app.var_custom_ki_prompt.set(txt)
            # Persistieren
            if getattr(app, 'settings_service', None):
                app.settings_service.set('analysis.ki.custom_prompt', txt)
            if not txt:
                app.custom_ki_textbox.insert('1.0', 'z.B. "Prüfe ob alle Produktnamen korrekt beibehalten wurden"')
                app.custom_ki_textbox.configure(text_color=app.get_color('text_tertiary'))
        except Exception:
            pass
    
    app.custom_ki_textbox.bind('<FocusIn>', _on_ki_focus_in)
    app.custom_ki_textbox.bind('<FocusOut>', _on_ki_focus_out)
    
    # Vordefinierte Prüfungen als Schnellauswahl
    ki_presets_label = ctk.CTkLabel(
        ki_content,
        text=app._t('Schnellauswahl:'),
        font=_font('caption'),
        text_color=app.get_color('text_secondary')
    )
    ki_presets_label.pack(anchor='w', pady=(4, 4))
    
    ki_presets_frame = ctk.CTkFrame(ki_content, fg_color=app.get_color('transparent'))
    ki_presets_frame.pack(fill='x', pady=(0, 4))
    
    # Vordefinierte Prüfungen laden
    try:
        from quality_gui_custom_prompts import PREDEFINED_CHECKS
        presets = list(PREDEFINED_CHECKS.items())[:4]  # Erste 4 anzeigen
    except Exception:
        presets = [
            ('terminology', {'name': 'Terminologie', 'prompt': 'Prüfe Terminologie-Konsistenz'}),
            ('formality', {'name': 'Anrede', 'prompt': 'Prüfe formelle/informelle Anrede'}),
            ('anglicisms', {'name': 'Anglizismen', 'prompt': 'Finde unnötige Anglizismen'}),
        ]
    
    def _apply_preset(prompt_text):
        try:
            if not app.var_custom_ki_enabled.get():
                app.var_custom_ki_enabled.set(True)
                _on_toggle_custom_ki()
            app.custom_ki_textbox.configure(state='normal')
            app.custom_ki_textbox.delete('1.0', 'end')
            app.custom_ki_textbox.insert('1.0', prompt_text)
            app.custom_ki_textbox.configure(text_color=app.get_color('text_primary'))
            app.var_custom_ki_prompt.set(prompt_text)
            if getattr(app, 'settings_service', None):
                app.settings_service.set('analysis.ki.custom_prompt', prompt_text)
        except Exception:
            pass
    
    for i, (key, info) in enumerate(presets):
        name = info.get('name', key) if isinstance(info, dict) else key
        prompt = info.get('prompt', '') if isinstance(info, dict) else ''
        btn = ctk.CTkButton(
            ki_presets_frame,
            text=name,
            width=65,
            height=24,
            fg_color=app.get_color('gray_100'),
            hover_color=app.get_color('gray_200'),
            text_color=app.get_color('text_secondary'),
            font=ctk.CTkFont('Segoe UI', 10),
            corner_radius=4,
            command=lambda p=prompt: _apply_preset(p)
        )
        btn.pack(side='left', padx=(0, 4))

    # Glossar Label - Konsistent mit anderen Sections
    gloss_header = ctk.CTkLabel(config_content, text=app._t('Glossar'), **section_label_cfg)
    gloss_header.pack(anchor='w', pady=(20, 8))
    
    gloss_container = ctk.CTkFrame(
        config_content, 
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    gloss_container.pack(fill='x', pady=(0, 20))
    
    gloss_frame = ctk.CTkFrame(gloss_container, fg_color=app.get_color('transparent'))
    gloss_frame.pack(fill='x', padx=16, pady=16)
    
    app.var_glossary_path = getattr(app, 'var_glossary_path', tk.StringVar(value=''))
    try:
        if getattr(app, 'settings_service', None):
            existing = app.settings_service.get('analysis.phase2.glossary_path', '')
            if existing:
                app.var_glossary_path.set(existing)
    except Exception:
        pass
    
    gloss_entry = ctk.CTkEntry(
        gloss_frame, 
        textvariable=app.var_glossary_path, 
        placeholder_text=app._t('Glossar-Datei auswählen...'),
        fg_color=app.get_color('white'), 
        text_color=app.get_color('text_primary'),
        border_width=1,
        border_color=app.get_color('gray_300'),
        corner_radius=6,
        height=36,
        font=_font('body')  # ✅ Konsistente Font (war hardcoded)
    )
    gloss_entry.pack(fill='x', pady=(0, 12))

    def _browse_gloss():
        try:
            if tk is None or not getattr(app, 'root', None):
                return
            from tkinter import filedialog
            p = filedialog.askopenfilename(title='Glossar auswählen', filetypes=[('CSV','*.csv'),('TSV','*.tsv'),('Alle','*.*')])
            if p:
                app.var_glossary_path.set(p)
                if getattr(app,'settings_service',None):
                    app.settings_service.set('analysis.phase2.glossary_path', p)
                if getattr(app,'show_toast',None):
                    app.show_toast(app._t('Glossar gesetzt'), 'success')
        except Exception:
            pass
    
    # Button - KONSISTENTE TYPOGRAPHIE
    gloss_btn = ctk.CTkButton(
        gloss_frame, 
        text=app._t('Durchsuchen'), 
        command=_browse_gloss,
        fg_color=app.get_color('primary'),
        hover_color=app.get_color('primary_hover'),
        text_color=app.get_color('white'),
        font=_font('body'),  # ✅ Konsistente Font (war size 13)
        corner_radius=6,
        height=36
    )
    gloss_btn.pack(fill='x')

    # Reset Button als Card-Action
    def _reset_defaults():
        try:
            app.source_lang.set(app._t('Auto-Erkennung'))
            app.target_lang.set(app._t('Deutsch'))
            app.analysis_depth.set(app._t('Mittlere Analyse'))
            app.var_depth.set('medium')
            app.var_phase2_enabled.set(True)
            app.var_phase3_enabled.set(False)
            app.var_phase3_semantic.set(False)
            app.var_phase3_semantic_ollama.set(False)
            # Persistenz
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.lang.source', 'auto')
                app.settings_service.set('analysis.lang.target', 'de')
                app.settings_service.set('analysis.depth', 'medium')
                app.settings_service.set('analysis.phase2.enabled', True)
                app.settings_service.set('analysis.phase3.enabled', False)
                app.settings_service.set('analysis.phase3.semantic', False)
                app.settings_service.set('analysis.phase3.semantic.use_ollama', False)
                app.settings_service.set('analysis.phase2.glossary_path', '')
            app.var_glossary_path.set('')
            try:
                _persist_enabled(); _persist_order()
            except Exception:
                pass
            try:
                _apply_depth_profile('medium')
            except Exception:
                pass
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Standards wiederhergestellt'), 'success')
        except Exception:
            pass
    
    reset_container = ctk.CTkFrame(
        config_content, 
        fg_color=app.get_color('white'),
        corner_radius=8,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    reset_container.pack(fill='x')
    
    reset_frame = ctk.CTkFrame(reset_container, fg_color=app.get_color('transparent'))
    reset_frame.pack(fill='x', padx=16, pady=16)
    
    # Reset Button - KONSISTENTE TYPOGRAPHIE
    reset_btn = ctk.CTkButton(
        reset_frame, 
        text=app._t('Konfiguration zurücksetzen'), 
        fg_color=app.get_color('white'),
        hover_color=app.get_color('gray_100'),
        text_color=app.get_color('text_secondary'),
        border_width=1,
        border_color=app.get_color('gray_300'),
        font=_font('body'),  # ✅ Konsistente Font (war size 12)
        corner_radius=6,
        height=36,
        command=_reset_defaults
    )
    reset_btn.pack(fill='x')

    # ---------- Qualitätskriterien Rechte Spalte - Moderne Card ----------
    qc_section = ctk.CTkFrame(
        main_container, 
        fg_color=app.get_color('surface'), 
        corner_radius=12,
        border_width=1,
        border_color=app.get_color('gray_200')
    )
    qc_section.grid(row=0, column=1, sticky='nsew', padx=(12, 0))
    
    # Header Frame - Konsistent mit linker Seite
    qc_header_frame = ctk.CTkFrame(
        qc_section, 
        fg_color=app.get_color('white'),
        corner_radius=12
    )
    qc_header_frame.pack(fill='x', padx=1, pady=1)
    
    # Header Bar mit Toolbar
    qc_header_bar = ctk.CTkFrame(qc_header_frame, fg_color=app.get_color('transparent'))
    qc_header_bar.pack(fill='x', padx=20, pady=16)
    
    # Qualitätskriterien Header - KONSISTENTE TYPOGRAPHIE mit linker Seite
    qc_header = ctk.CTkLabel(
        qc_header_bar, 
        text=app._t('Qualitätskriterien'), 
        font=_font('body_bold'),  # ✅ Gleiche Font wie "Konfiguration"
        text_color=app.get_color('text_primary')
    )
    qc_header.pack(side='left')
    
    qc_container = ctk.CTkFrame(qc_section, fg_color=app.get_color('transparent'))
    qc_container.pack(fill='both', expand=True, padx=20, pady=(4, 20))
    
    # Toolbar - Modernere Toggle-Buttons
    toolbar_container = ctk.CTkFrame(
        qc_header_bar, 
        fg_color=app.get_color('gray_100'),
        corner_radius=6
    )
    toolbar_container.pack(side='right')
    
    toolbar = ctk.CTkFrame(toolbar_container, fg_color=app.get_color('transparent'))
    toolbar.pack(padx=4, pady=4)
    
    # Collapse Toggle
    qc_collapsed = getattr(app, 'qc_collapsed', False)
    qc_toggle_btn = ctk.CTkButton(
        toolbar,
        text='−' if not qc_collapsed else '+',
        width=28,
        height=28,
        fg_color=app.get_color('transparent'),
        text_color=app.get_color('text_secondary'),
        hover_color=app.get_color('surface_hover'),
        font=ctk.CTkFont(size=16, weight='bold'),
        command=None
    )
    qc_toggle_btn.pack(side='left', padx=(0, 4))
    
    # Grid Container
    qc_grid_container = ctk.CTkFrame(qc_container, fg_color=app.get_color('transparent'))
    if not qc_collapsed:
        qc_grid_container.pack(fill='both', expand=True)
    
    def _apply_qc_collapsed_ui(collapsed: bool):
        if collapsed:
            try:
                qc_grid_container.pack_forget()
                qc_toggle_btn.configure(text='+')
            except Exception:
                pass
            try:
                collapse_btn.configure(text=app._t('+'))
            except Exception:
                pass
        else:
            try:
                qc_grid_container.pack(fill='both', expand=True)
                qc_toggle_btn.configure(text='−')
            except Exception:
                pass
            try:
                collapse_btn.configure(text=app._t('−'))
            except Exception:
                pass

    def _toggle_qc():
        collapsed = not bool(getattr(app, 'qc_collapsed', False))
        app.qc_collapsed = collapsed
        try:
            if getattr(app, 'var_qc_collapsed', None) is not None:
                app.var_qc_collapsed.set(collapsed)
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.qc.collapsed', collapsed)
        except Exception:
            pass
        _apply_qc_collapsed_ui(collapsed); _render(force=True)

    qc_toggle_btn.configure(command=_toggle_qc)

    # Reihenfolge laden
    app.quality_vars = getattr(app, 'quality_vars', {})
    persistent_order = []
    try:
        if getattr(app, 'settings_service', None):
            persistent_order = app.settings_service.get('analysis.qc.order', []) or []
    except Exception:
        pass
    ordered = [k for k in persistent_order if k in key_to_label]
    ordered += [k for k,_ in default_quality if k not in ordered]
    app.quality_order = ordered

    persisted_enabled = {}
    try:
        if getattr(app,'settings_service',None):
            persisted_enabled = app.settings_service.get('analysis.qc.enabled', {}) or {}
    except Exception:
        pass
    apply_profile_on_init = not bool(persisted_enabled)

    def _persist_order():
        try:
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.qc.order', list(app.quality_order))
        except Exception:
            pass
    def _persist_enabled():
        try:
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.qc.enabled', {k: bool(v.get()) for k,v in app.quality_vars.items()})
        except Exception:
            pass

    # Grid + Summary mit modernem Design - ✅ Einheitliches Card-Design wie Module-Container
    criteria_grid_container = ctk.CTkFrame(
        qc_grid_container, 
        fg_color=app.get_color('white'),  # ✅ Weißer Hintergrund wie Module
        corner_radius=8,
        border_width=1,  # ✅ Sichtbarer Rahmen
        border_color=app.get_color('gray_200')  # ✅ Gleiche Rahmenfarbe wie Module
    )
    criteria_grid_container.pack(fill='both', expand=True, pady=(0, 12))
    
    summary_bar = ctk.CTkFrame(qc_grid_container, fg_color=app.get_color('transparent'))
    summary_bar.pack(fill='x')
    
    # Status Label - Zurückhaltende Typographie
    app.qc_focus_label = ctk.CTkLabel(
        summary_bar, 
        text=app._t('Alle Kriterien aktiv'), 
        font=ctk.CTkFont('Segoe UI', 10), 
        text_color=app.get_color('text_secondary')
    )
    app.qc_focus_label.pack(side='left', fill='x', expand=True)

    # Toolbar Buttons - KONSISTENTE TYPOGRAPHIE UND BESSERE BREITE
    def _toolbar_btn(text, cmd, tooltip=None):
        b = ctk.CTkButton(
            toolbar, 
            text=app._t(text), 
            width=50,  # ✅ Breiter für bessere Lesbarkeit (war 42)
            height=28, 
            fg_color=app.get_color('transparent'), 
            hover_color=app.get_color('surface_hover'),
            text_color=app.get_color('text_secondary'),
            font=_font('caption'),  # ✅ Konsistente caption Font
            command=cmd
        )
        try:
            b.configure(border_width=1, border_color=app.get_color('surface_border'))
        except Exception:
            pass
        if tooltip and hasattr(app, '_tooltip'):
            try:
                app._tooltip(b, tooltip)
            except Exception:
                pass
        b.pack(side='left', padx=1)
        return b

    def _set_all(state: bool):
        try:
            for v in app.quality_vars.values():
                v.set(state)
            _on_qc_change(); _update_simple_status()
        except Exception:
            pass

    import json
    def _export():
        try:
            if tk is None or not getattr(app, 'root', None):
                return
            from tkinter import filedialog as fd
            prof = {'order': app.quality_order, 'enabled': {k: bool(v.get()) for k,v in app.quality_vars.items()}}
            p = fd.asksaveasfilename(defaultextension='.json', filetypes=[('JSON','*.json')], title='Profil exportieren')
            if not p: return
            with open(p,'w',encoding='utf-8') as f:
                json.dump(prof,f,ensure_ascii=False,indent=2)
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Profil exportiert'), 'success')
        except Exception:
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Export fehlgeschlagen'), 'error')
    def _import():
        try:
            if tk is None or not getattr(app, 'root', None):
                return
            from tkinter import filedialog as fd
            p = fd.askopenfilename(filetypes=[('JSON','*.json')], title='Profil laden')
            if not p: return
            with open(p,'r',encoding='utf-8') as f:
                prof = json.load(f)
            order = prof.get('order') or []
            enabled = prof.get('enabled') or {}
            cleaned = [k for k in order if k in key_to_label]
            cleaned += [k for k in key_to_label if k not in cleaned]
            app.quality_order = cleaned
            for k,v in enabled.items():
                if k in app.quality_vars:
                    app.quality_vars[k].set(bool(v))
            _persist_order(); _on_qc_change(); _render(force=True); _update_simple_status()
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Profil geladen'), 'success')
        except Exception:
            if getattr(app,'show_toast',None):
                app.show_toast(app._t('Import fehlgeschlagen'), 'error')

    def _reset_quality():
        try:
            app.quality_order = [k for k,_ in default_quality]
            for k in app.quality_order:
                if k in app.quality_vars:
                    app.quality_vars[k].set(True)
            _persist_order(); _on_qc_change(); _render(force=True); _update_simple_status()
        except Exception:
            pass

    btn_all_off = _toolbar_btn('Aus', lambda: _set_all(False), 'Alle deaktivieren')
    btn_all_on = _toolbar_btn('An', lambda: _set_all(True), 'Alle aktivieren')
    btn_export = _toolbar_btn('Exp', _export, 'Profil exportieren') 
    btn_import = _toolbar_btn('Imp', _import, 'Profil importieren')
    btn_default = _toolbar_btn('Std', _reset_quality, 'Standardkriterien')

    # Criteria grid mit modernem Card-Design
    criteria_grid = ctk.CTkFrame(criteria_grid_container, fg_color=app.get_color('transparent'))
    criteria_grid.pack(fill='both', expand=True, padx=16, pady=16)
    last_cols = {'val':0}
    tooltip_map = {
        'accuracy': 'Übersetzungsgenauigkeit',
        'fluency': 'Natürlicher Lesefluss', 
        'grammar': 'Grammatikalische Korrektheit',
        'terminology': 'Fachbegriffe konsistent',
        'style': 'Stil und Tonalität',
        'completeness': 'Vollständige Übertragung'
    }

    def _calc_cols(width: int) -> int:
        """3/2/1 Spalten (≈ ≥900/≥600/sonst)."""
        try:
            w = int(width or 0)
        except Exception:
            w = 0
        if w >= 900:
            return 3
        if w >= 600:
            return 2
        return 1

    def _on_qc_change():
        try:
            if getattr(app,'settings_service',None):
                app.settings_service.set('analysis.qc.enabled', {k: bool(v.get()) for k,v in app.quality_vars.items()})
        except Exception:
            pass
        _update_qc_summary()
        try:
            if hasattr(app, '_on_qc_change') and callable(app._on_qc_change):
                app._on_qc_change()  # type: ignore
        except Exception:
            pass

    def _update_qc_summary():
        try:
            total = len(app.quality_order)
            active = sum(1 for k in app.quality_order if bool(app.quality_vars.setdefault(k, tk.BooleanVar(value=persisted_enabled.get(k, True))).get()))
            if active == total:
                app.qc_focus_label.configure(text=app._t('Alle Kriterien aktiv'))
            else:
                app.qc_focus_label.configure(text=app._t('Aktiv: ') + f"{active}/{total}")
        except Exception:
            pass

    # Tiefenprofile: definieren welche Kriterien aktiv sein sollen
    DEPTH_PROFILES = {
        'quick': ['accuracy', 'terminology', 'completeness'],
        'medium': ['accuracy', 'fluency', 'grammar', 'terminology', 'completeness'],
        'extensive': ['accuracy', 'fluency', 'grammar', 'terminology', 'style', 'completeness']
    }
    DEPTH_MODULES = {
        'quick': {
            'phase2': True,
            'phase3': False,
            'semantic': False,
            'semantic_ollama': False
        },
        'medium': {
            'phase2': True,
            'phase3': True,
            'semantic': False,
            'semantic_ollama': False
        },
        'extensive': {
            'phase2': True,
            'phase3': True,
            'semantic': True,
            'semantic_ollama': False
        }
    }
    DEPTH_PROFILE_ALIASES = {
        'standard': 'medium',
        'deep': 'extensive',
        'full': 'extensive'
    }
    def _apply_depth_profile(depth_key: str):
        try:
            normalized_key = DEPTH_PROFILE_ALIASES.get(depth_key, depth_key)
            targets = set(DEPTH_PROFILES.get(normalized_key, DEPTH_PROFILES['medium']))
            changed = False
            for k in app.quality_order:
                v = app.quality_vars.setdefault(k, tk.BooleanVar(value=True))
                desired = k in targets
                if bool(v.get()) != desired:
                    v.set(desired); changed = True
            if changed:
                _persist_enabled(); _update_qc_summary(); _render(force=True)

            module_cfg = DEPTH_MODULES.get(normalized_key, {})
            module_changed = False
            module_map = {
                'phase2': ('var_phase2_enabled', 'analysis.phase2.enabled'),
                'phase3': ('var_phase3_enabled', 'analysis.phase3.enabled'),
                'semantic': ('var_phase3_semantic', 'analysis.phase3.semantic'),
                'semantic_ollama': ('var_phase3_semantic_ollama', 'analysis.phase3.semantic.use_ollama')
            }
            for key, (attr, setting_key) in module_map.items():
                if key not in module_cfg:
                    continue
                var = getattr(app, attr, None)
                if var is None or not hasattr(var, 'get') or not hasattr(var, 'set'):
                    continue
                desired = bool(module_cfg[key])
                if bool(var.get()) != desired:
                    var.set(desired)
                    module_changed = True
                _persist_bool(setting_key, var)
            if module_changed:
                try:
                    _update_simple_status()
                except Exception:
                    pass
        except Exception:
            pass

    def _render(force: bool=False):
        try:
            width = criteria_grid.winfo_width() or criteria_grid_container.winfo_width()
            cols = _calc_cols(width)
            if not force and cols == last_cols['val'] and criteria_grid.winfo_children():
                return
            last_cols['val'] = cols
            for w in list(criteria_grid.winfo_children()):
                try: w.destroy()
                except Exception: pass
            for c in range(cols):
                criteria_grid.grid_columnconfigure(c, weight=1)
            r=0; c=0
            for key in app.quality_order:
                if key not in app.quality_vars:
                    app.quality_vars[key] = tk.BooleanVar(value=persisted_enabled.get(key, True))
                # ✅ KONSISTENTE CHECKBOX-GRÖSSE und TYPOGRAPHIE
                cb = ctk.CTkCheckBox(
                    criteria_grid, 
                    text=app._t(key_to_label.get(key,key)), 
                    variable=app.quality_vars[key], 
                    font=_font('body'),  # ✅ Konsistente Font (war caption)
                    checkbox_height=18,  # ✅ Standardisiert auf 18 (war 16)
                    checkbox_width=18,   # ✅ Standardisiert auf 18 (war 16)
                    corner_radius=4,  # ✅ Abgerundete Ecken wie Module-Checkboxen
                    command=_on_qc_change, 
                    text_color=app.get_color('text_primary'),
                    fg_color=app.get_color('primary'),
                    hover_color=app.get_color('primary_hover')
                )
                cb.grid(row=r, column=c, sticky='w', padx=(0,12), pady=(0,8))  # ✅ Besseres Spacing
                try:
                    if hasattr(app,'_attach_tooltip'):
                        app._attach_tooltip(cb, app._t(tooltip_map.get(key, key)))
                except Exception:
                    pass
                c += 1
                if c >= cols:
                    c = 0; r += 1
            _update_qc_summary();
        except Exception:
            pass

    def _resize(_e):
        _render()
    criteria_grid_container.bind('<Configure>', _resize)

    # Collapse
    try:
        initial_collapse = False
        if getattr(app,'settings_service',None):
            initial_collapse = bool(app.settings_service.get('analysis.qc.collapsed', False))
        app.var_qc_collapsed = getattr(app,'var_qc_collapsed', tk.BooleanVar(value=initial_collapse))
    except Exception:
        pass

    def _toggle_qc_panel():
        _toggle_qc()

    collapse_btn = ctk.CTkButton(qc_header_bar, text=app._t('−'), width=30, height=24, fg_color=app.get_color('surface'), command=_toggle_qc_panel)
    try:
        collapse_btn.configure(border_width=1, border_color=app.get_color('surface_border'), text_color=app.get_color('text_primary'))
    except Exception:
        pass
    collapse_btn.pack(side='left', padx=(8,0))
    _apply_qc_collapsed_ui(bool(getattr(app,'var_qc_collapsed', tk.BooleanVar(value=False)).get()))

    # Initial Render + Failsafe: sicherstellen, dass Grid sichtbar bleibt
    def _ensure_qc_visible():
        try:
            # Falls das Grid leer ist (z.B. wegen kollabiertem Zustand aus Settings), entkollabieren und neu rendern
            if not criteria_grid.winfo_children():
                _apply_qc_collapsed_ui(False)
                _render(force=True)
        except Exception:
            pass

    _render(force=True)
    try:
        (getattr(app,'root', app)).after(0, lambda: (_render(force=True), _ensure_qc_visible()))
    except Exception:
        pass

    # Tooltips
    try:
        if hasattr(app,'_attach_tooltip'):
            app._attach_tooltip(phase2_cb, app._t('Struktur + Glossar + Sicherheit'))
            app._attach_tooltip(phase3_cb, app._t('Stil/Risiko/Lesbarkeit'))
            app._attach_tooltip(semantic_cb, app._t('Bedeutungsvergleich'))
            app._attach_tooltip(semantic_ollama_cb, app._t('Lokales Embedding über Ollama'))
    except Exception:
        pass

    # Vereinfachter Status ohne Badges
    def _update_simple_status():
        try:
            for w in list(badge_container.winfo_children()):
                try: w.destroy()
                except Exception: pass
            depth_key = 'medium'
            try:
                if hasattr(app, 'var_depth') and hasattr(app.var_depth, 'get'):
                    depth_key = app.var_depth.get() or 'medium'
            except Exception:
                depth_key = 'medium'
            depth_texts = {
                'quick': app._t('Schnelle Analyse – Zahlen, Namen, Vollständigkeit'),
                'medium': app._t('Mittlere Analyse – Sprachqualität & Struktur'),
                'extensive': app._t('Umfangreiche Analyse – Vollständiges Regelset')
            }
            label_text = depth_texts.get(depth_key)
            if label_text:
                status_label.configure(text=label_text)
            else:
                active = sum(1 for k in app.quality_order if bool(app.quality_vars[k].get())) if app.quality_order else 0
                total = len(app.quality_order)
                status_label.configure(
                    text=(f"{active}/{total} " + app._t('Active')) if total else app._t('Bereit')
                )
        except Exception:
            pass

    old_on_qc = getattr(app,'_on_qc_change', None)
    def _wrapped_on_qc():  # type: ignore
        try: _update_simple_status()
        except Exception: pass
        if callable(old_on_qc):
            try: old_on_qc()  # type: ignore
            except Exception: pass
    app._on_qc_change = _wrapped_on_qc  # type: ignore
    _update_simple_status()

    if apply_profile_on_init:
        try:
            _apply_depth_profile(app.var_depth.get() or 'medium')
            _update_simple_status()
        except Exception:
            pass

    logger.debug('Analyse-Sektion neu aufgebaut')
