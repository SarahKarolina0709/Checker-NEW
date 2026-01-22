"""quality_gui_settings_ui

Extrahierte Settings-spezifische UI Orchestrierung (Platzhalter).
"""
from __future__ import annotations
from typing import Any, Callable, Tuple
import tkinter as tk
try:
    import customtkinter as ctk
except Exception:  # Fallback wenn CustomTkinter nicht verfügbar beim Lint
    ctk = None  # type: ignore

class QualityGuiSettingsUI:
    """Kompakte, DRY-orientierte Settings-UI mit Fallbacks.

    - Nutzt CustomTkinter und DesignSystem, wenn verfügbar; andernfalls Tk-Fallback.
    - Zentralisierte Helfer für Buttons, Spinbox und Settings-Anwendung.
    - Deutsche Labels, keine Icons (No-Icons-Policy).
    """

    # Minimale sinnvolle Werte (Konstanten)
    MIN_SNAPSHOT_KB = 64
    MIN_ROTATE_KB = 128

    def __init__(self):
        self._bound_app = None
        self._vars: dict[str, tk.Variable] = {}   # verhindert GC von Tk-Variablen

    def bind_app(self, app):
        """Bindet Haupt-App Kontext (nur Referenz, keine Ownership)."""
        self._bound_app = app
        return self

    def build_plugins_section(self, parent):  # später: konkrete UI Widgets
        # Basissektion + Snapshot Memory Grenzwert + Logging Rotation
        try:
            frame = parent
            app = self._bound_app
            if not app:
                return parent

            # Container Card (Design System sofern verfügbar)
            card = self._make_card(frame)

            # Snapshot Memory Threshold Label
            try:
                lbl = tk.Label(card, text='Snapshot Speicher Warn-Grenzwert (KB):')
                lbl.pack(anchor='w', padx=8, pady=(8,4))
            except Exception:
                pass

            # Current value Var
            try:
                current_val = int(getattr(app, 'snapshot_memory_warn_kb', 512))
            except Exception:
                current_val = 512
            snapshot_warn_var = tk.IntVar(value=current_val)
            try:
                self._vars['snapshot_warn_kb'] = snapshot_warn_var
            except Exception:
                pass

            def _apply_threshold():
                # Generischer Apply: Attribut + Settings-Persistierung
                self._apply_setting(
                    attr='snapshot_memory_warn_kb',
                    settings_key='performance.snapshot_memory_warn_kb',
                    value=snapshot_warn_var.get(),
                    min_value=self.MIN_SNAPSHOT_KB,
                    toast_success='Grenzwert aktualisiert',
                    log_info=lambda v: f"Snapshot Memory Warn-Grenzwert aktualisiert: {v} KB",
                    coerce=int,
                )

            # Spinbox / Entry + Button
            try:
                spin = self._make_spinbox(card, snapshot_warn_var, from_=self.MIN_SNAPSHOT_KB, to=65536, step=64, width=8)
                spin.pack(anchor='w', padx=8, pady=4)
                self._attach_optional_tooltip(spin, "Warnung bei hohem Speicherverbrauch (in KB). Mindestwert 64 KB")
            except Exception:
                entry = tk.Entry(card, textvariable=snapshot_warn_var, width=10)
                entry.pack(anchor='w', padx=8, pady=4)
                self._attach_optional_tooltip(entry, "Warnung bei hohem Speicherverbrauch (in KB). Mindestwert 64 KB")

            try:
                btn = self._make_button(card, text='Übernehmen', command=_apply_threshold, style='primary')
                btn.pack(anchor='w', padx=8, pady=(4,12))
                self._attach_optional_tooltip(btn, "Einstellung speichern")
            except Exception:
                pass
            # Zusatz: Event Log Rotation Einstellungen + Delta Snapshot Flag
            try:
                sep = tk.Label(card, text='—')
                sep.pack(fill='x', padx=4, pady=(4,4))
            except Exception:
                pass

            # Rotation Size (KB)
            try:
                rot_size_lbl = tk.Label(card, text='Event Log Rotationsgröße (KB):')
                rot_size_lbl.pack(anchor='w', padx=8, pady=(4,2))
            except Exception:
                pass
            try:
                current_rot_kb = int(getattr(app, 'event_log_rotate_kb', 2048))
            except Exception:
                current_rot_kb = 2048
            log_rotate_var = tk.IntVar(value=current_rot_kb)
            try:
                self._vars['log_rotate_kb'] = log_rotate_var
            except Exception:
                pass

            try:
                rot_spin = self._make_spinbox(card, log_rotate_var, from_=self.MIN_ROTATE_KB, to=10240, step=128, width=8)
                rot_spin.pack(anchor='w', padx=8, pady=(0,4))
                self._attach_optional_tooltip(rot_spin, "Maximale Größe einer einzelnen Log-Datei (in KB). Mindestwert 128 KB")
            except Exception:
                e = tk.Entry(card, textvariable=log_rotate_var, width=10)
                e.pack(anchor='w', padx=8, pady=(0,4))
                self._attach_optional_tooltip(e, "Maximale Größe einer einzelnen Log-Datei (in KB). Mindestwert 128 KB")

            # Generation Count
            try:
                gen_lbl = tk.Label(card, text='Event Log Generationen:')
                gen_lbl.pack(anchor='w', padx=8, pady=(4,2))
            except Exception:
                pass
            try:
                current_gen = int(getattr(app, 'event_log_generations', 5))
            except Exception:
                current_gen = 5
            generations_var = tk.IntVar(value=current_gen)
            try:
                self._vars['log_generations'] = generations_var
            except Exception:
                pass
            try:
                gen_spin = tk.Spinbox(card, from_=1, to=15, increment=1, textvariable=generations_var, width=5)
                gen_spin.pack(anchor='w', padx=8, pady=(0,4))
                self._attach_optional_tooltip(gen_spin, "Anzahl der Log-Dateien, die beibehalten werden (1–15)")
            except Exception:
                e2 = tk.Entry(card, textvariable=generations_var, width=6)
                e2.pack(anchor='w', padx=8, pady=(0,4))
                self._attach_optional_tooltip(e2, "Anzahl der Log-Dateien, die beibehalten werden (1–15)")

            # Delta Snapshot Experimental Toggle
            try:
                telemetry_delta_var = tk.BooleanVar(value=bool(getattr(app, 'delta_snapshot_rnd_enabled', False)))
                delta_chk = tk.Checkbutton(card, text='Delta-Snapshot Diff Telemetrie (experimentell)', variable=telemetry_delta_var)
                delta_chk.pack(anchor='w', padx=8, pady=(6,4))
                self._attach_optional_tooltip(delta_chk, "Experimentell: Reduziert Telemetrie, indem nur Deltas gespeichert werden")
                try:
                    self._vars['delta_snapshot'] = telemetry_delta_var
                except Exception:
                    pass
            except Exception:
                telemetry_delta_var = None

            def _apply_rotation_settings():
                try:
                    size_kb = int(log_rotate_var.get())
                    gens = int(generations_var.get())
                    size_kb = max(size_kb, self.MIN_ROTATE_KB)
                    gens = max(gens, 1)

                    # Bulk-Apply (ohne mehrfach Toasts)
                    updates = [
                        dict(attr='event_log_rotate_kb', settings_key='logging.event_log_rotate_kb', value=size_kb),
                        dict(attr='event_log_generations', settings_key='logging.event_log_generations', value=gens),
                    ]
                    self._apply_settings_bulk(updates)

                    # Delta-Flag separat (optional)
                    if telemetry_delta_var is not None:
                        val = bool(telemetry_delta_var.get())
                        setattr(app, 'delta_snapshot_rnd_enabled', val)
                        self._persist_setting('performance.delta_snapshots_experimental', val)

                    if hasattr(app, 'logger'):
                        app.logger.info(
                            f"EventLog Rotation aktualisiert: {size_kb} KB / {gens} Generationen; "
                            f"DeltaSnapshots={getattr(app,'delta_snapshot_rnd_enabled', False)}"
                        )
                    if hasattr(app, 'show_toast'):
                        app.show_toast('Logging Einstellungen aktualisiert', 'success')
                except Exception as e:
                    try:
                        if hasattr(app, 'logger'):
                            app.logger.warning(f"Rotation Settings Update fehlgeschlagen: {e}")
                    except Exception:
                        pass

            try:
                rot_btn = self._make_button(card, text='Logging übernehmen', command=_apply_rotation_settings, style='secondary')
                rot_btn.pack(anchor='w', padx=8, pady=(4,12))
                self._attach_optional_tooltip(rot_btn, "Rotation & Generations-Einstellungen speichern")
            except Exception:
                pass

            return card
        except Exception:
            return parent

    # ----------------------- Helper (DRY) -----------------------
    def _t(self, text: str) -> str:
        """Übersetzungs-Hook: nutzt app._t(text) wenn vorhanden, sonst Original."""
        app = self._bound_app
        try:
            if app and hasattr(app, '_t') and callable(app._t):
                return app._t(text)
        except Exception:
            pass
        return text

    def _normalize_allowed_extensions(self, raw: str, known: list[str] | set[str] | tuple[str, ...]) -> tuple[list[str], list[str]]:
        """Normalisiert eine Komma-Liste von Dateiendungen.

        - Trimmt Leerzeichen, konvertiert zu lowercase
        - Fügt fehlenden führenden Punkt hinzu (.pdf statt pdf)
        - Entfernt Duplikate (Stabil: Reihenfolge der ersten Vorkommen bleibt erhalten)
        - Filtert auf bekannte Endungen ("known"); unbekannte werden zurückgegeben

        Returns: (normalized_list, ignored_unknowns)
        """
        try:
            known_set = set()
            for k in (known or []):
                s = str(k).lower()
                known_set.add(s if s.startswith('.') else f'.{s}')
        except Exception:
            known_set = {'.pdf', '.txt', '.docx', '.xlsx', '.doc'}
        items = [it.strip() for it in (raw or '').split(',') if it and it.strip()]
        normalized: list[str] = []
        ignored: list[str] = []
        for it in items:
            s = it.lower()
            if not s.startswith('.'):
                s = f'.{s}'
            # duplikate vermeiden; nur bekannte zulassen wenn known_set gesetzt ist
            if s in normalized:
                continue
            if known_set and s not in known_set:
                ignored.append(s)
                continue
            normalized.append(s)
        return normalized, ignored

    def build_upload_section(self, parent):
        """Upload-Einstellungen: max. Dateigröße (MB) und erlaubte Erweiterungen."""
        app = self._bound_app
        try:
            card = self._make_card(parent)
            try:
                tk.Label(card, text=self._t('Upload-Einstellungen')).pack(anchor='w', padx=12, pady=(10, 6))
            except Exception:
                pass

            # Max File Size (MB)
            row1 = tk.Frame(card)
            row1.pack(fill='x', padx=12, pady=6)
            try:
                tk.Label(row1, text=self._t('Maximale Dateigröße (MB):')).pack(side='left')
            except Exception:
                pass
            default_mb = 50
            try:
                if hasattr(app, 'settings_service') and app.settings_service:
                    default_mb = int(app.settings_service.get('upload_settings.max_file_size_mb', default_mb))
            except Exception:
                default_mb = 50
            max_mb_var = tk.IntVar(value=default_mb)
            try:
                self._vars['upload_max_mb'] = max_mb_var
            except Exception:
                pass
            try:
                sp = self._make_spinbox(row1, max_mb_var, from_=1, to=2048, step=1, width=6)
                sp.pack(side='right')
            except Exception:
                tk.Entry(row1, textvariable=max_mb_var, width=6).pack(side='right')

            # Allowed Extensions
            row2 = tk.Frame(card)
            row2.pack(fill='x', padx=12, pady=6)
            try:
                tk.Label(row2, text=self._t('Erlaubte Erweiterungen (Komma-getrennt):')).pack(anchor='w')
            except Exception:
                pass
            default_exts = ['.pdf', '.txt', '.docx', '.xlsx']
            try:
                if hasattr(app, 'settings_service') and app.settings_service:
                    val = app.settings_service.get('upload_settings.allowed_extensions', default_exts)
                    if isinstance(val, str):
                        default_exts = [e.strip() for e in val.split(',') if e.strip()]
                    elif isinstance(val, list):
                        default_exts = val
            except Exception:
                pass
            exts_var = tk.StringVar(value=', '.join(default_exts))
            try:
                self._vars['upload_exts'] = exts_var
            except Exception:
                pass
            tk.Entry(row2, textvariable=exts_var).pack(fill='x', pady=(2,0))

            def _save_upload_settings():
                try:
                    mb = int(max_mb_var.get())
                    mb = max(1, mb)
                    raw = exts_var.get()
                    # Bekannte Extensions definieren: Defaults + ggf. bisherige Werte
                    default_known = ['.pdf', '.txt', '.docx', '.xlsx', '.doc']
                    try:
                        existing = []
                        if hasattr(app, 'settings_service') and app.settings_service:
                            val = app.settings_service.get('upload_settings.allowed_extensions', [])
                            if isinstance(val, str):
                                existing = [v.strip() for v in val.split(',') if v.strip()]
                            elif isinstance(val, (list, tuple, set)):
                                existing = list(val)
                    except Exception:
                        existing = []
                    known_all = list({*(default_known), *[e if str(e).startswith('.') else f'.{str(e)}' for e in existing]})
                    norm, ignored = self._normalize_allowed_extensions(raw, known_all)
                    # Fallback: wenn alles herausgefiltert wurde, nimm Defaults
                    if not norm:
                        norm = default_known
                    # Werte persistieren
                    self._persist_setting('upload_settings.max_file_size_mb', mb)
                    self._persist_setting('upload_settings.allowed_extensions', norm)
                    # UI aktualisieren (normalisierte Liste anzeigen)
                    try:
                        exts_var.set(', '.join(norm))
                    except Exception:
                        pass
                    # Feedback
                    if hasattr(app, 'show_toast'):
                        msg = self._t('Upload-Einstellungen gespeichert')
                        if ignored:
                            msg += f" – {self._t('Unbekannte Erweiterungen ignoriert')}: {', '.join(ignored)}"
                        app.show_toast(msg, 'success')
                    if hasattr(app, 'logger'):
                        base_info = f"Upload Settings: max_mb={mb}, extensions={norm}"
                        if ignored:
                            base_info += f", ignored={ignored}"
                        app.logger.info(base_info)
                except Exception as e:
                    try:
                        if hasattr(app, 'show_toast'):
                            app.show_toast(self._t('Fehler beim Speichern der Upload-Einstellungen'), 'error')
                        if hasattr(app, 'logger'):
                            app.logger.warning(f"Upload Settings Save failed: {e}")
                    except Exception:
                        pass

            try:
                self._make_button(card, text=self._t('Speichern'), command=_save_upload_settings, style='primary').pack(anchor='w', padx=12, pady=(4, 10))
            except Exception:
                pass

            return card
        except Exception:
            return parent

    def build_paths_section(self, parent):
        """Pfad-Einstellungen: Projekte-Basisordner wählen und speichern."""
        app = self._bound_app
        try:
            card = self._make_card(parent)
            try:
                tk.Label(card, text=self._t('Pfade')).pack(anchor='w', padx=12, pady=(10, 6))
            except Exception:
                pass
            row = tk.Frame(card)
            row.pack(fill='x', padx=12, pady=6)
            try:
                tk.Label(row, text=self._t('Projekte-Basisordner:')).pack(anchor='w')
            except Exception:
                pass
            current_path = ''
            try:
                current_path = getattr(app, 'projects_base_path', '') or ''
                if not current_path and hasattr(app, 'settings_service') and app.settings_service:
                    current_path = str(app.settings_service.get('paths.projects_base_path', '') or '')
            except Exception:
                current_path = ''
            path_var = tk.StringVar(value=current_path)
            try:
                self._vars['paths_base'] = path_var
            except Exception:
                pass
            entry_row = tk.Frame(card)
            entry_row.pack(fill='x', padx=12)
            tk.Entry(entry_row, textvariable=path_var).pack(side='left', fill='x', expand=True)
            def _browse():
                try:
                    from tkinter import filedialog as tk_filedialog
                    sel = tk_filedialog.askdirectory()
                    if sel:
                        path_var.set(sel)
                except Exception:
                    pass
            try:
                self._make_button(entry_row, text=self._t('Wählen'), command=_browse, style='secondary').pack(side='left', padx=(8,0))
            except Exception:
                pass
            def _save_path():
                try:
                    p = path_var.get().strip()
                    if p:
                        setattr(app, 'projects_base_path', p)
                        self._persist_setting('paths.projects_base_path', p)
                        if hasattr(app, 'show_toast'):
                            app.show_toast(self._t('Pfad gespeichert'), 'success')
                        if hasattr(app, 'logger'):
                            app.logger.info(f"Paths: projects_base_path={p}")
                    else:
                        if hasattr(app, 'show_toast'):
                            app.show_toast(self._t('Bitte einen gültigen Ordner wählen'), 'warning')
                except Exception as e:
                    try:
                        if hasattr(app, 'show_toast'):
                            app.show_toast(self._t('Fehler beim Speichern des Pfads'), 'error')
                        if hasattr(app, 'logger'):
                            app.logger.warning(f"Save path failed: {e}")
                    except Exception:
                        pass
            try:
                self._make_button(card, text=self._t('Speichern'), command=_save_path, style='primary').pack(anchor='w', padx=12, pady=(6, 10))
            except Exception:
                pass
            return card
        except Exception:
            return parent

    def _make_combobox(self, parent, values: list[str], width: int = 220, initial: str | None = None) -> Tuple[object, Callable[[], str], Callable[[str], None]]:
        """Erstellt eine ComboBox (CTk oder Tk-OptionMenu) und gibt Widget, getter, setter zurück."""
        app = self._bound_app
        try:
            if ctk and hasattr(app, 'get_color'):
                cb = ctk.CTkComboBox(parent, values=values, width=width)
                if initial:
                    try:
                        cb.set(initial)
                    except Exception:
                        pass
                return cb, cb.get, cb.set
        except Exception:
            pass
        var = tk.StringVar(value=initial or (values[0] if values else ''))
        om = tk.OptionMenu(parent, var, *(values or ['']))
        try:
            setattr(om, '_tk_var', var)  # für spätere Speicherung gegen GC
        except Exception:
            pass
        return om, var.get, (lambda v: var.set(v))

    def build_calendar_section(self, parent):
        """Kalender-Einstellungen: Bundesland-Auswahl."""
        app = self._bound_app
        try:
            card = self._make_card(parent)
            try:
                tk.Label(card, text=self._t('Kalender')).pack(anchor='w', padx=12, pady=(10, 6))
            except Exception:
                pass
            row = tk.Frame(card)
            row.pack(fill='x', padx=12, pady=6)
            try:
                tk.Label(row, text=self._t('Bundesland:')).pack(side='left')
            except Exception:
                pass
            laender = [
                self._t('Auto'), self._t('Baden-Württemberg'), self._t('Bayern'), self._t('Berlin'), self._t('Brandenburg'),
                self._t('Bremen'), self._t('Hamburg'), self._t('Hessen'), self._t('Mecklenburg-Vorpommern'), self._t('Niedersachsen'),
                self._t('Nordrhein-Westfalen'), self._t('Rheinland-Pfalz'), self._t('Saarland'), self._t('Sachsen'), self._t('Sachsen-Anhalt'),
                self._t('Schleswig-Holstein'), self._t('Thüringen')
            ]
            current = None
            try:
                current = getattr(app, 'calendar_bundesland', None)
                if not current and hasattr(app, 'settings_service') and app.settings_service:
                    current = app.settings_service.get('calendar_settings.bundesland', None)
            except Exception:
                current = None
            # Fallback auf 'Auto', wenn current nicht in Liste
            if not current or current not in laender:
                current = laender[0]
            cb_widget, cb_get, cb_set = self._make_combobox(row, laender, width=220, initial=current)
            try:
                getattr(cb_widget, 'pack')(side='right')
            except Exception:
                pass
            # Tk-Fallback-Var gegen GC sichern
            try:
                tk_var = getattr(cb_widget, '_tk_var', None)
                if tk_var is not None:
                    self._vars['calendar_bundesland'] = tk_var  
            except Exception:
                pass

            def _save_calendar():
                try:
                    val = cb_get()
                    setattr(app, 'calendar_bundesland', val)
                    self._persist_setting('calendar_settings.bundesland', val)
                    if hasattr(app, 'show_toast'):
                        app.show_toast(self._t('Kalender-Einstellungen gespeichert'), 'success')
                    if hasattr(app, 'logger'):
                        app.logger.info(f"Calendar: bundesland={val}")
                except Exception as e:
                    try:
                        if hasattr(app, 'show_toast'):
                            app.show_toast(self._t('Fehler beim Speichern der Kalender-Einstellungen'), 'error')
                        if hasattr(app, 'logger'):
                            app.logger.warning(f"Calendar Save failed: {e}")
                    except Exception:
                        pass
            try:
                self._make_button(card, text=self._t('Speichern'), command=_save_calendar, style='primary').pack(anchor='w', padx=12, pady=(6, 10))
            except Exception:
                pass
            return card
        except Exception:
            return parent
    def build_notifications_section(self, parent):
        """Benachrichtigungs-/Toast-Einstellungen als Card erstellen.

        - Max. sichtbare Toasts (1..10)
        - Test-/Leeren-Buttons
        - Persistiert 'notifications.max_visible' über settings_service
        """
        app = self._bound_app
        try:
            card = self._make_card(parent)
            # Titel
            try:
                title = tk.Label(card, text='Benachrichtigungen')
                title.pack(anchor='w', padx=12, pady=(10, 6))
            except Exception:
                pass

            # Aktuellen Max-Wert ermitteln
            current_max = 4
            try:
                if hasattr(app, 'toast_system') and app.toast_system:
                    current_max = int(app.toast_system.get_max_visible())
            except Exception:
                current_max = 4

            # Zeile: Max. sichtbare Toasts
            row = tk.Frame(card)
            row.pack(fill='x', padx=12, pady=6)
            try:
                lbl = tk.Label(row, text='Max. sichtbare Toasts:')
                lbl.pack(side='left')
            except Exception:
                pass
            max_var = tk.IntVar(value=current_max)
            try:
                self._vars['notif_max_visible'] = max_var
            except Exception:
                pass
            try:
                sp = self._make_spinbox(row, max_var, from_=1, to=10, step=1, width=5)
                sp.pack(side='right')
                self._attach_optional_tooltip(sp, 'Anzahl gleichzeitig sichtbarer Toasts (1–10)')
            except Exception:
                ent = tk.Entry(row, textvariable=max_var, width=6)
                ent.pack(side='right')

            # Speichern-Button
            def _save_max_toasts():
                try:
                    val = int(max_var.get())
                    if val < 1 or val > 10:
                        if hasattr(app, 'show_toast'):
                            app.show_toast('Wert muss zwischen 1 und 10 liegen', 'warning')
                        return
                    if hasattr(app, 'toast_system') and app.toast_system:
                        app.toast_system.set_max_visible(val)
                    self._persist_setting('notifications.max_visible', val)
                    if hasattr(app, 'show_toast'):
                        app.show_toast('Toast-Anzahl aktualisiert', 'success')
                    if hasattr(app, 'logger'):
                        app.logger.info(f"Benachrichtigungen: max_visible = {val}")
                except Exception as e:
                    try:
                        if hasattr(app, 'show_toast'):
                            app.show_toast('Fehler beim Aktualisieren', 'error')
                        if hasattr(app, 'logger'):
                            app.logger.warning(f"Max Toasts Update fehlgeschlagen: {e}")
                    except Exception:
                        pass

            try:
                save_btn = self._make_button(card, text='Speichern', command=_save_max_toasts, style='primary')
                save_btn.pack(anchor='w', padx=12, pady=(2, 6))
            except Exception:
                pass

            # Test- und Leeren-Buttons
            btn_row = tk.Frame(card)
            btn_row.pack(fill='x', padx=12, pady=(2, 10))
            def _test_toasts():
                try:
                    if not hasattr(app, 'toast_system') or not app.toast_system:
                        return
                    app.toast_system.show_success('Test Erfolg')
                    app.toast_system.show_info('Test Info')
                    app.toast_system.show_warning('Test Warnung')
                    app.toast_system.show_error('Test Fehler')
                except Exception:
                    pass
            def _clear_toasts():
                try:
                    if hasattr(app, 'toast_system') and app.toast_system:
                        app.toast_system.close_all()
                        if hasattr(app, 'show_toast'):
                            app.show_toast('Alle Toasts geschlossen', 'info')
                except Exception:
                    pass
            try:
                tbtn = self._make_button(btn_row, text='Test', command=_test_toasts, style='secondary')
                tbtn.pack(side='left', padx=(0, 8))
                cbtn = self._make_button(btn_row, text='Leeren', command=_clear_toasts, style='secondary')
                cbtn.pack(side='left')
            except Exception:
                pass

            # Restore aus Settings (falls vorhanden)
            try:
                if hasattr(app, 'settings_service') and app.settings_service:
                    stored_max = int(app.settings_service.get('notifications.max_visible', current_max))
                    if stored_max != current_max and hasattr(app, 'toast_system') and app.toast_system:
                        app.toast_system.set_max_visible(stored_max)
                        try:
                            max_var.set(stored_max)
                        except Exception:
                            pass
            except Exception:
                pass

            return card
        except Exception:
            return parent

    def _make_card(self, parent):
        app = self._bound_app
        try:
            if ctk and hasattr(app, 'get_color'):
                card = ctk.CTkFrame(
                    parent,
                    fg_color=app.get_color('surface'),
                    border_width=1,
                    border_color=app.get_color('surface_border')
                )
                card.pack(fill='x', padx=12, pady=12)
                return card
        except Exception:
            pass
        # Fallback
        card = tk.Frame(parent)
        card.pack(fill='x', padx=12, pady=12)
        return card

    def _make_button(self, parent, text: str, command, style: str = 'primary'):
        app = self._bound_app
        try:
            if ctk and hasattr(app, 'get_color'):
                fg = app.get_color('primary') if style == 'primary' else (
                    app.get_color('secondary') if style == 'secondary' else app.get_color('surface')
                )
                hover = app.get_color('primary_hover') if style == 'primary' else (
                    app.get_color('secondary_hover') if style == 'secondary' else app.get_color('surface_hover')
                )
                text_color = app.get_color('text_inverse') if style in ('primary', 'secondary') else app.get_color('gray_700')
                return ctk.CTkButton(parent, text=text, command=command, fg_color=fg, hover_color=hover, text_color=text_color)
        except Exception:
            pass
        return tk.Button(parent, text=text, command=command)

    def _make_spinbox(self, parent, var, from_: int, to: int, step: int, width: int = 8):
        def _vcmd(P: str) -> bool:
            if P == "":
                return True
            if not P.isdigit():
                return False
            try:
                v = int(P)
                return from_ <= v <= to
            except Exception:
                return False
        try:
            vcmd = (parent.register(_vcmd), "%P")
            return tk.Spinbox(parent, from_=from_, to=to, increment=step,
                              textvariable=var, width=width,
                              validate='key', validatecommand=vcmd)
        except Exception:
            # Fallback: Entry ohne Inkrement
            return tk.Entry(parent, textvariable=var, width=width)

    def _apply_setting(self, *, attr: str, settings_key: str | None, value: Any, min_value: Any, toast_success: str, log_info, coerce=int):
        app = self._bound_app
        try:
            v = coerce(value)
            try:
                # Nur untere Schranke – obere optional durch Spinbox begrenzt
                if min_value is not None:
                    v = v if v >= min_value else min_value
            except Exception:
                pass
            setattr(app, attr, v)
            if settings_key:
                self._persist_setting(settings_key, v)
            if hasattr(app, 'logger'):
                msg = log_info(v) if callable(log_info) else str(log_info)
                app.logger.info(msg)
            if hasattr(app, 'show_toast'):
                app.show_toast(toast_success, 'success')
        except Exception as e:
            try:
                if hasattr(app, 'logger'):
                    app.logger.warning(f"Einstellungs-Update fehlgeschlagen ({attr}): {e}")
            except Exception:
                pass

    def _apply_settings_bulk(self, updates: list[dict]):
        """Wendet mehrere (attr, settings_key, value) Updates an – ohne mehrfachen Toast."""
        app = self._bound_app
        for up in updates:
            try:
                attr = up.get('attr')
                value = up.get('value')
                settings_key = up.get('settings_key')
                if attr is not None:
                    setattr(app, attr, value)
                if settings_key:
                    self._persist_setting(settings_key, value)
            except Exception:
                # Einzelne Fehler nicht die gesamte Anwendung blockieren lassen
                pass

    def _persist_setting(self, settings_key: str, value: Any):
        app = self._bound_app
        try:
            if hasattr(app, 'settings_service') and app.settings_service:
                app.settings_service.set(settings_key, value)
        except Exception:
            pass

    def _attach_optional_tooltip(self, widget, text: str, delay: int = 500):
        app = self._bound_app
        try:
            if hasattr(app, '_attach_tooltip') and callable(app._attach_tooltip):
                app._attach_tooltip(widget, text, delay)
        except Exception:
            pass

__all__ = [
    'QualityGuiSettingsUI'
]
