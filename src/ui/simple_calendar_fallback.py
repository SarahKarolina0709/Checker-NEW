import calendar
from datetime import datetime

try:
    import customtkinter as ctk
except Exception:  # Fallback: avoid hard crash if not available in some tools
    ctk = None


def open_simple_calendar(app, focus_date=None):
    """
    Open a lightweight simple calendar window using the app's design system.
    - app: main UI instance providing get_color, get_spacing, get_typography, _cr
    - focus_date: optional datetime to open the calendar focused/highlighted
    """
    if ctk is None:
        raise RuntimeError("CustomTkinter not available")

    # Resolve helpers from app with safe fallbacks
    def _color(name, default="#FFFFFF"):
        try:
            return app.get_color(name)
        except Exception:
            return default

    def _spacing(key, default=8):
        try:
            return app.get_spacing(key)
        except Exception:
            return default

    def _font(name, fallback=("Segoe UI", 12, "normal")):
        try:
            return app.get_typography(name)
        except Exception:
            return fallback

    def _cr(key, fallback=12):
        try:
            return app._cr(key, fallback)
        except Exception:
            try:
                return int(fallback)
            except Exception:
                return 12

    # Create window
    window = ctk.CTkToplevel(app)
    window.title("Enhanced Simple Calendar - Checker Pro")
    window.geometry("1000x700")
    window.transient(app)
    window.grab_set()
    window.resizable(True, True)

    try:
        app._center_dialog(window, 1000, 700)
    except Exception:
        pass

    main_container = ctk.CTkFrame(window, fg_color="transparent")
    main_container.pack(fill="both", expand=True, padx=20, pady=20)

    # Header
    header_frame = ctk.CTkFrame(
        main_container,
        fg_color=_color('surface_secondary'),
        border_width=1,
        border_color=_color('surface_border')
    )
    header_frame.pack(fill="x", pady=(0, _spacing('md')))

    header_content = ctk.CTkFrame(header_frame, fg_color="transparent")
    header_content.pack(fill="x", padx=_spacing('lg'), pady=_spacing('sm'))

    # Title + date
    now = datetime.now()
    title = ctk.CTkLabel(
        header_content,
        text="Projektkalender (Einfach)",
        font=ctk.CTkFont(*_font("heading_sm")),
        text_color=_color('text_primary')
    )
    title.pack(side="left")

    # Content area (2 columns)
    content_frame = ctk.CTkFrame(main_container, fg_color="transparent")
    content_frame.pack(fill="both", expand=True)
    content_frame.grid_columnconfigure(0, weight=2)
    content_frame.grid_columnconfigure(1, weight=1)

    # Grid column
    cal_container = ctk.CTkFrame(
        content_frame,
        fg_color=_color('white'),
        corner_radius=_cr('borders.radius_custom_15'),
        border_width=1,
        border_color=_color('surface_border')
    )
    cal_container.grid(row=0, column=0, sticky="nsew", padx=(0, 15))

    cal_header = ctk.CTkFrame(
        cal_container,
        fg_color=_color('surface_secondary'),
        corner_radius=_cr('borders.radius_md')
    )
    cal_header.pack(fill="x", padx=_spacing('md'), pady=(_spacing('sm'), 0))

    nav_frame = ctk.CTkFrame(cal_header, fg_color="transparent")
    nav_frame.pack(fill="x", pady=_spacing('sm'))

    # Determine current date (use focus_date if provided)
    current_date = focus_date if isinstance(focus_date, datetime) else now

    # Keep state on window object
    window._current_calendar_date = current_date
    window._calendar_view_mode = 'month'
    window._highlight_date = focus_date if isinstance(focus_date, datetime) else None

    def _format_month_year(dt):
        months = [
            "Januar", "Februar", "März", "April", "Mai", "Juni",
            "Juli", "August", "September", "Oktober", "November", "Dezember"
        ]
        return f"{months[dt.month-1]} {dt.year}"

    def _refresh_calendar():
        # clear grid
        for w in grid_container.winfo_children():
            w.destroy()
        if window._calendar_view_mode == 'month':
            _create_month_grid(grid_container, window._current_calendar_date)
        else:
            _create_month_list(grid_container, window._current_calendar_date)

    def _navigate(direction):
        dt = window._current_calendar_date
        if direction > 0:
            if dt.month == 12:
                dt = dt.replace(year=dt.year + 1, month=1)
            else:
                dt = dt.replace(month=dt.month + 1)
        else:
            if dt.month == 1:
                dt = dt.replace(year=dt.year - 1, month=12)
            else:
                dt = dt.replace(month=dt.month - 1)
        window._current_calendar_date = dt
        month_lbl.configure(text=_format_month_year(dt))
        _refresh_calendar()

    prev_btn = ctk.CTkButton(
        nav_frame,
        text="Zurück",
        command=lambda: _navigate(-1),
        **app._button_style('secondary', 'sm', 'solid')
    )
    prev_btn.pack(side="left")

    month_lbl = ctk.CTkLabel(
        nav_frame,
        text=_format_month_year(current_date),
        font=ctk.CTkFont(*_font("subheading")),
        text_color=_color('primary')
    )
    month_lbl.pack(side="left", expand=True)

    next_btn = ctk.CTkButton(
        nav_frame,
        text="Weiter",
        command=lambda: _navigate(1),
        **app._button_style('secondary', 'sm', 'solid')
    )
    next_btn.pack(side="right")

    toggle_frame = ctk.CTkFrame(cal_header, fg_color="transparent")
    toggle_frame.pack(fill="x", pady=(0, _spacing('sm')))

    def _toggle(active):
        return {**app._button_style('secondary', 'sm', 'solid' if active else 'outline')}

    month_btn = ctk.CTkButton(
        toggle_frame, text="Monat",
        command=lambda: _set_view('month'),
        **_toggle(True)
    )
    month_btn.pack(side="left")

    list_btn = ctk.CTkButton(
        toggle_frame, text="Liste",
        command=lambda: _set_view('list'),
        **_toggle(False)
    )
    list_btn.pack(side="left", padx=(_spacing('xs'), 0))

    grid_container = ctk.CTkFrame(cal_container, fg_color="transparent")
    grid_container.pack(fill="both", expand=True, padx=_spacing('md'), pady=(_spacing('sm'), _spacing('md')))

    def _set_view(mode):
        if mode not in ('month', 'list'):
            return
        window._calendar_view_mode = mode
        month_btn.configure(**_toggle(mode == 'month'))
        list_btn.configure(**_toggle(mode == 'list'))
        _refresh_calendar()

    def _on_day_click(y, m, d):
        try:
            app._show_enhanced_day_details(y, m, d)
        except Exception:
            pass

    def _create_month_grid(parent, dt):
        cal = calendar.monthcalendar(dt.year, dt.month)
        # Weekday headers
        days = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        header = ctk.CTkFrame(parent, fg_color=_color('surface_secondary'), corner_radius=_cr('borders.radius_md'))
        header.pack(fill="x", pady=(0, 15))
        for i, dayname in enumerate(["KW"] + days):
            lbl = ctk.CTkLabel(header, text=dayname, font=ctk.CTkFont(*_font("small")), text_color=_color('gray_600'), width=50 if dayname != "KW" else 32)
            lbl.grid(row=0, column=i, padx=3, pady=10, sticky="ew")
            header.grid_columnconfigure(i, weight=0 if dayname == "KW" else 1)

        grid = ctk.CTkFrame(parent, fg_color="transparent")
        grid.pack(fill="both", expand=True)

        today = datetime.now()
        highlight = window._highlight_date

        for r, week in enumerate(cal):
            # KW column
            try:
                rep_day = next((d for d in week if d != 0), 1)
                from datetime import date as _date
                kw = int(_date(dt.year, dt.month, rep_day).isocalendar()[1])
            except Exception:
                kw = 0
            kw_lbl = ctk.CTkLabel(grid, text=(f"{kw}" if kw else ""), font=ctk.CTkFont(*_font("caption")), text_color=_color('gray_500'), width=32)
            kw_lbl.grid(row=r, column=0, padx=2, pady=2, sticky="nsew")
            grid.grid_columnconfigure(0, weight=0)

            for c, day in enumerate(week):
                if day == 0:
                    empty = ctk.CTkFrame(grid, fg_color="transparent", width=50, height=45)
                    empty.grid(row=r, column=c + 1, padx=2, pady=2, sticky="nsew")
                    continue

                is_today = (day == today.day and dt.month == today.month and dt.year == today.year)
                is_highlight = bool(highlight and highlight.year == dt.year and highlight.month == dt.month and highlight.day == day)
                has_projects = False
                try:
                    has_projects = bool(app._check_day_has_projects(dt.year, dt.month, day))
                except Exception:
                    pass

                # Colors
                if is_today:
                    bg = _color('primary'); hover = _color('primary_hover'); tc = _color('white'); bw = 2; bc = _color('info_light')
                elif is_highlight:
                    bg = _color('white'); hover = _color('surface_hover'); tc = _color('primary'); bw = 2; bc = _color('primary')
                elif has_projects:
                    bg = _color('success_light'); hover = _color('surface_hover'); tc = _color('gray_800'); bw = 1; bc = _color('surface_border')
                else:
                    bg = _color('white'); hover = _color('surface_hover'); tc = _color('gray_700'); bw = 1; bc = _color('surface_border')

                btn = ctk.CTkButton(
                    grid,
                    text=str(day),
                    font=ctk.CTkFont(*_font("small" if (is_today or has_projects) else "caption")),
                    fg_color=bg,
                    hover_color=hover,
                    text_color=tc,
                    border_width=bw,
                    border_color=bc,
                    width=50,
                    height=45,
                    corner_radius=_cr('borders.radius_md'),
                    command=lambda d=day: _on_day_click(dt.year, dt.month, d)
                )
                btn.grid(row=r, column=c + 1, padx=2, pady=2, sticky="nsew")
                grid.grid_columnconfigure(c + 1, weight=1)

    def _create_month_list(parent, dt):
        import calendar as _cal
        from datetime import date as _date
        list_frame = ctk.CTkScrollableFrame(parent, fg_color=_color('surface'), corner_radius=_cr('borders.radius_md'))
        list_frame.pack(fill="both", expand=True)
        last_day = _cal.monthrange(dt.year, dt.month)[1]
        any_entries = False
        for d in range(1, last_day + 1):
            try:
                if app._check_day_has_projects(dt.year, dt.month, d):
                    any_entries = True
                    row = ctk.CTkFrame(list_frame, fg_color=_color('white'), corner_radius=_cr('borders.radius_md'), border_width=1, border_color=_color('surface_border'))
                    row.pack(fill="x", padx=16, pady=8)

                    inner = ctk.CTkFrame(row, fg_color="transparent")
                    inner.pack(fill="x", padx=16, pady=12)

                    # Date label
                    try:
                        label_text = app._format_date_de(_date(dt.year, dt.month, d))
                    except Exception:
                        label_text = f"{dt.year}-{dt.month:02d}-{d:02d}"
                    lbl = ctk.CTkLabel(inner, text=label_text, font=ctk.CTkFont(*_font('label')), text_color=_color('text_primary'))
                    lbl.pack(side="left")

                    # Action
                    btn = ctk.CTkButton(inner, text="Details", command=lambda yd=(dt.year, dt.month, d): app._show_enhanced_day_details(*yd), **app._button_style('secondary', 'sm', 'outline'))
                    btn.pack(side="right")
            except Exception:
                pass
        if not any_entries:
            empty = ctk.CTkLabel(parent, text="Keine Projekte in diesem Monat", font=ctk.CTkFont(*_font('body')), text_color=_color('text_secondary'))
            empty.pack(pady=_spacing('lg'))

    # Right info column (simple placeholder, reusing app's function if available)
    info_container = ctk.CTkFrame(
        content_frame,
        fg_color=_color('white'),
        corner_radius=_cr('borders.radius_custom_15'),
        border_width=1,
        border_color=_color('border')
    )
    info_container.grid(row=0, column=1, sticky="nsew", padx=(15, 0))

    try:
        app._create_enhanced_project_info(info_container, window._current_calendar_date)
    except Exception:
        placeholder = ctk.CTkLabel(info_container, text="Projektinfo", font=ctk.CTkFont(*_font('body')), text_color=_color('text_secondary'))
        placeholder.pack(padx=16, pady=16)

    # Initial render
    _refresh_calendar()
    return window
