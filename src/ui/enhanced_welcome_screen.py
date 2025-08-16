"""Fixed broken docstring"""
"""Fixed broken docstring"""
"""Enhanced welcome screen with improved typography and layout."""Fixed broken docstring"""
        """Initialize the enhanced welcome screen."""Fixed broken docstring"""
        kwargs.setdefault('fg_color', "#F8FAFC")
        kwargs.setdefault('corner_radius', 0)
        
        super().__init__(master, **kwargs)
        
        self.app = app
        self.ui = ui_helper
        
        # Initialize UI
        self._setup_ui()
    
    def _setup_ui(self):
        """Set up the enhanced UI."""Fixed broken docstring"""
        """Create the enhanced header section."""Fixed broken docstring"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=self.ui.spacing.CONTAINER_PADDING, pady=self.ui.spacing.CONTAINER_PADDING)
        
        # Configure grid
        header.grid_columnconfigure(1, weight=1)
        
        # Logo
        logo_frame = ctk.CTkFrame(header, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="w", padx=(0, self.ui.spacing.L))
        
        logo_icon = ctk.CTkLabel()
            logo_frame
            text="📋"
            font=ctk.CTkFont(size=self.ui.typography.ICON_XL)
            width=self.ui.typography.ICON_XL
            height=self.ui.typography.ICON_XL
        )
        logo_icon.pack()
        
        # Title section
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="ew")
        
        # Main title
        title = create_heading(title_frame, "Checker Pro Suite", level="XL")
        title.pack(anchor="w")
        
        # Subtitle
        subtitle = create_body_text()
            title_frame
            "Professionelle Übersetzungstools für höchste Qualität"
            size="L"
            text_color="#6B7280"
        )
        subtitle.pack(anchor="w", pady=(self.ui.spacing.XS, 0))
        
        # Status section
        status_frame = ctk.CTkFrame(header, fg_color="transparent")
        status_frame.grid(row=0, column=2, sticky="e")
        
        # Current time
        time_label = create_body_text()
            status_frame
            "09.07.2025 - 10:43"
            size="M"
            text_color="#6B7280"
        )
        time_label.pack(anchor="e")
        
        # Version
        version_label = create_body_text()
            status_frame
            "Version 2.1.0"
            size="S"
            text_color="#9CA3AF"
        )
        version_label.pack(anchor="e", pady=(self.ui.spacing.XS, 0))
    
    def _create_main_content(self):
        """Create the main content area with three sections."""Fixed broken docstring"""
        main_container = ctk.CTkFrame(self, fg_color="transparent")
        main_container.grid(row=1, column=0, sticky="nsew", padx=self.ui.spacing.CONTAINER_PADDING, pady=(0, self.ui.spacing.CONTAINER_PADDING))
        
        # Configure three-column grid
        main_container.grid_columnconfigure(0, weight=1, uniform="col")
        main_container.grid_columnconfigure(1, weight=1, uniform="col")  
        main_container.grid_columnconfigure(2, weight=1, uniform="col")
        main_container.grid_rowconfigure(0, weight=1)
        
        # Left column - Project data
        self._create_project_section(main_container)
        
        # Middle column - Upload files
        self._create_upload_section(main_container)
        
        # Right column - Workflows
        self._create_workflow_section(main_container)
    
    def _create_project_section(self, parent):
        """Create the project section."""Fixed broken docstring"""
        section.grid(row=0, column=0, sticky="nsew", padx=(0, self.ui.spacing.M))
        
        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=self.ui.spacing.SECTION_PADDING, pady=self.ui.spacing.SECTION_PADDING)
        
        # Icon and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # Icon
        icon_label = ctk.CTkLabel()
            title_frame
            text="👤"
            font=ctk.CTkFont(size=self.ui.typography.ICON_L)
        )
        icon_label.pack(side="left", padx=(0, self.ui.spacing.M))
        
        # Title
        title_label = create_heading(title_frame, "Projektdaten", level="L")
        title_label.pack(side="left", fill="x", expand=True)
        
        # Description
        desc_label = create_body_text()
            header
            "Kundendaten eingeben • Projekt auswählen oder erstellen"
            size="M"
            text_color="#6B7280"
        )
        desc_label.pack(fill="x", pady=(self.ui.spacing.S, 0))
        
        # Content
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.ui.spacing.SECTION_PADDING, pady=(0, self.ui.spacing.SECTION_PADDING))
        
        # Enhanced customer input section with better organization
        customer_section = ctk.CTkFrame(content, fg_color="#F8FAFC", corner_radius=8)
        customer_section.pack(fill="x", pady=(0, self.ui.spacing.M))
        
        customer_section_content = ctk.CTkFrame(customer_section, fg_color="transparent")
        customer_section_content.pack(fill="x", padx=self.ui.spacing.M, pady=self.ui.spacing.M)
        
        # Customer search and selection
        search_frame = ctk.CTkFrame(customer_section_content, fg_color="transparent")
        search_frame.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        # Search label
        search_label = create_body_text(search_frame, "Kunde suchen oder auswählen:", size="M")
        search_label.pack(anchor="w", pady=(0, self.ui.spacing.XS))
        
        # Search field with icon
        search_container = ctk.CTkFrame(search_frame, fg_color="transparent")
        search_container.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        # Search icon
        search_icon = ctk.CTkLabel()
            search_container
            text="🔍"
            font=ctk.CTkFont(size=self.ui.typography.ICON_S)
            width=20
        )
        search_icon.pack(side="left", padx=(0, self.ui.spacing.S))
        
        # Search input
        customer_search = ctk.CTkEntry()
            search_container
            placeholder_text="Firmenname oder Ansprechpartner eingeben..."
            font=ctk.CTkFont(family=self.ui.typography.PRIMARY_FONT, size=self.ui.typography.BODY_M)
            height=self.ui.layout.INPUT_HEIGHT
            corner_radius=8
        )
        customer_search.pack(side="left", fill="x", expand=True)
        
        # Quick access buttons
        quick_access = ctk.CTkFrame(customer_section_content, fg_color="transparent")
        quick_access.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        # Configure grid for quick access
        quick_access.grid_columnconfigure((0, 1, 2), weight=1)
        
        new_customer_btn = create_secondary_button(quick_access, "Neuer Kunde", width=100)
        new_customer_btn.grid(row=0, column=0, sticky="w")
        
        recent_customers_btn = create_secondary_button(quick_access, "Letzte Kunden", width=100)
        recent_customers_btn.grid(row=0, column=1, sticky="ew", padx=self.ui.spacing.S)
        
        favorites_btn = create_secondary_button(quick_access, "Favoriten", width=100)
        favorites_btn.grid(row=0, column=2, sticky="e")
        
        # Action buttons with improved organization
        actions_frame = ctk.CTkFrame(content, fg_color="transparent")
        actions_frame.pack(fill="x", pady=(0, self.ui.spacing.M))
        
        # Primary action
        new_project_btn = create_primary_button(actions_frame, "Neues Projekt erstellen", width=200)
        new_project_btn.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        # Secondary actions row
        secondary_actions = ctk.CTkFrame(actions_frame, fg_color="transparent")
        secondary_actions.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        # Configure grid for equal spacing
        secondary_actions.grid_columnconfigure((0, 1), weight=1)
        
        load_project_btn = create_secondary_button(secondary_actions, "Projekt laden", width=90)
        load_project_btn.grid(row=0, column=0, sticky="ew", padx=(0, self.ui.spacing.S))
        
        save_project_btn = create_secondary_button(secondary_actions, "Speichern", width=90)
        save_project_btn.grid(row=0, column=1, sticky="ew", padx=(self.ui.spacing.S, 0))
        
        # Quick stats
        stats_frame = ctk.CTkFrame(content, fg_color="#F1F5F9", corner_radius=8)
        stats_frame.pack(fill="x", pady=(self.ui.spacing.M, 0))
        
        stats_content = ctk.CTkFrame(stats_frame, fg_color="transparent")
        stats_content.pack(fill="x", padx=self.ui.spacing.M, pady=self.ui.spacing.S)
        
        # Configure grid for stats
        stats_content.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Projects stat
        projects_stat = ctk.CTkFrame(stats_content, fg_color="transparent")
        projects_stat.grid(row=0, column=0, sticky="ew")
        
        projects_num = create_heading(projects_stat, "24", level="S")
        projects_num.pack()
        
        projects_label = create_body_text(projects_stat, "Projekte", size="S", text_color="#6B7280")
        projects_label.pack()
        
        # Customers stat
        customers_stat = ctk.CTkFrame(stats_content, fg_color="transparent")
        customers_stat.grid(row=0, column=1, sticky="ew")
        
        customers_num = create_heading(customers_stat, "8", level="S")
        customers_num.pack()
        
        customers_label = create_body_text(customers_stat, "Kunden", size="S", text_color="#6B7280")
        customers_label.pack()
        
        # Files stat
        files_stat = ctk.CTkFrame(stats_content, fg_color="transparent")
        files_stat.grid(row=0, column=2, sticky="ew")
        
        files_num = create_heading(files_stat, "156", level="S")
        files_num.pack()
        
        files_label = create_body_text(files_stat, "Dateien", size="S", text_color="#6B7280")
        files_label.pack()
        
        select_customer_btn = create_secondary_button(actions_frame, "Kunde wählen", width=180)
        select_customer_btn.pack(fill="x")
        
        # Recent projects
        recent_frame = ctk.CTkFrame(content, fg_color="transparent")
        recent_frame.pack(fill="both", expand=True, pady=(self.ui.spacing.M, 0))
        
        recent_label = create_heading(recent_frame, "Kürzlich verwendete Projekte", level="S")
        recent_label.pack(anchor="w", pady=(0, self.ui.spacing.S))
        
        # Recent projects container
        recent_container = ctk.CTkScrollableFrame(recent_frame, height=200, fg_color="#F8FAFC")
        recent_container.pack(fill="both", expand=True)
        
        # Empty state
        empty_label = create_body_text()
            recent_container
            "Keine aktuellen Projekte"
            size="M"
            text_color="#9CA3AF"
        )
        empty_label.pack(pady=self.ui.spacing.XL)
    
    def _create_upload_section(self, parent):
        """Create the upload section."""Fixed broken docstring"""
        section.grid(row=0, column=1, sticky="nsew", padx=(self.ui.spacing.M, self.ui.spacing.M))
        
        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=self.ui.spacing.SECTION_PADDING, pady=self.ui.spacing.SECTION_PADDING)
        
        # Icon and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # Icon
        icon_label = ctk.CTkLabel()
            title_frame
            text=""
            font=ctk.CTkFont(size=self.ui.typography.ICON_L)
        )
        icon_label.pack(side="left", padx=(0, self.ui.spacing.M))
        
        # Title
        title_label = create_heading(title_frame, "Dateien hochladen", level="L")
        title_label.pack(side="left", fill="x", expand=True)
        
        # Description
        desc_label = create_body_text()
            header
            "Dateien per Drag & Drop oder Button hinzufügen"
            size="M"
            text_color="#6B7280"
        )
        desc_label.pack(fill="x", pady=(self.ui.spacing.S, 0))
        
        # Content with improved file management
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.ui.spacing.SECTION_PADDING, pady=(0, self.ui.spacing.SECTION_PADDING))
        
        # Drop zone with enhanced design
        drop_zone = ctk.CTkFrame()
            content
            height=160
            fg_color="#F8FAFC"
            border_width=2
            border_color="#E2E8F0"
            corner_radius=12
        )
        drop_zone.pack(fill="x", pady=(0, self.ui.spacing.M))
        
        # Drop zone content
        drop_content = ctk.CTkFrame(drop_zone, fg_color="transparent")
        drop_content.pack(expand=True)
        
        # Upload icon
        upload_icon = ctk.CTkLabel()
            drop_content
            text="⬆"
            font=ctk.CTkFont(size=self.ui.typography.ICON_XL)
        )
        upload_icon.pack(pady=(self.ui.spacing.L, self.ui.spacing.S))
        
        # Upload text
        upload_text = create_heading(drop_content, "Dateien hierher ziehen", level="S")
        upload_text.pack()
        
        # Upload subtitle
        upload_subtitle = create_body_text()
            drop_content
            "oder klicken zum Durchsuchen"
            size="M"
            text_color="#6B7280"
        )
        upload_subtitle.pack(pady=(self.ui.spacing.XS, self.ui.spacing.S))
        
        # Upload button
        upload_btn = create_secondary_button(drop_content, "Dateien auswählen", width=160)
        upload_btn.pack()
        
        # File controls and info
        controls_frame = ctk.CTkFrame(content, fg_color="transparent")
        controls_frame.pack(fill="x", pady=(0, self.ui.spacing.M))
        
        # File format and limits info
        info_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        info_frame.pack(fill="x", pady=(0, self.ui.spacing.S))
        
        formats_label = create_body_text()
            info_frame
            "📄 Unterstützte Formate: PDF, DOCX, TXT, XLSX • Max. 50MB pro Datei"
            size="S"
            text_color="#9CA3AF"
        )
        formats_label.pack(anchor="w")
        
        # File action buttons
        actions_row = ctk.CTkFrame(controls_frame, fg_color="transparent")
        actions_row.pack(fill="x")
        
        # Configure grid for equal spacing
        actions_row.grid_columnconfigure((0, 1, 2), weight=1)
        
        # Clear all button
        clear_btn = create_secondary_button(actions_row, "Alle löschen", width=85)
        clear_btn.grid(row=0, column=0, sticky="w")
        
        # Processing options
        options_frame = ctk.CTkFrame(actions_row, fg_color="transparent")
        options_frame.grid(row=0, column=1, sticky="ew")
        
        # Auto-process checkbox
        auto_process = ctk.CTkCheckBox()
            options_frame
            text="Automatisch verarbeiten"
            font=ctk.CTkFont(family=self.ui.typography.PRIMARY_FONT, size=self.ui.typography.BODY_S)
            text_color="#6B7280"
        )
        auto_process.pack()
        
        # Batch upload button
        batch_btn = create_secondary_button(actions_row, "Batch-Upload", width=100)
        batch_btn.grid(row=0, column=2, sticky="e")
        formats_label.pack(pady=(self.ui.spacing.S, self.ui.spacing.M))
        
        # Uploaded files
        files_frame = ctk.CTkFrame(content, fg_color="transparent")
        files_frame.pack(fill="both", expand=True)
        
        files_label = create_heading(files_frame, "Hochgeladene Dateien", level="S")
        files_label.pack(anchor="w", pady=(0, self.ui.spacing.S))
        
        # Files container
        files_container = ctk.CTkScrollableFrame(files_frame, height=150, fg_color="#F8FAFC")
        files_container.pack(fill="both", expand=True)
        
        # Empty state
        empty_files_label = create_body_text()
            files_container
            "Noch keine Dateien hochgeladen"
            size="M"
            text_color="#9CA3AF"
        )
        empty_files_label.pack(pady=self.ui.spacing.XL)
    
    def _create_workflow_section(self, parent):
        """Create the workflow section."""Fixed broken docstring"""
        section.grid(row=0, column=2, sticky="nsew", padx=(self.ui.spacing.M, 0))
        
        # Header
        header = ctk.CTkFrame(section, fg_color="transparent")
        header.pack(fill="x", padx=self.ui.spacing.SECTION_PADDING, pady=self.ui.spacing.SECTION_PADDING)
        
        # Icon and title
        title_frame = ctk.CTkFrame(header, fg_color="transparent")
        title_frame.pack(fill="x")
        
        # Icon
        icon_label = ctk.CTkLabel()
            title_frame
            text="⚡"
            font=ctk.CTkFont(size=self.ui.typography.ICON_L)
        )
        icon_label.pack(side="left", padx=(0, self.ui.spacing.M))
        
        # Title
        title_label = create_heading(title_frame, "Workflows starten", level="L")
        title_label.pack(side="left", fill="x", expand=True)
        
        # Description
        desc_label = create_body_text()
            header
            "Wählen Sie einen Workflow zur Bearbeitung aus"
            size="M"
            text_color="#6B7280"
        )
        desc_label.pack(fill="x", pady=(self.ui.spacing.S, 0))
        
        # Content
        content = ctk.CTkFrame(section, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=self.ui.spacing.SECTION_PADDING, pady=(0, self.ui.spacing.SECTION_PADDING))
        
        # Workflow buttons
        workflows = [
            {"title": "Angebotsanalyse", "description": "Erstelle professionelle Angebote", "icon": "💰", "color": "#0078D4"}
            {"title": "Dateiprüfung", "description": "Prüfe Übersetzungen auf Qualität", "icon": "✅", "color": "#16A34A"}
            {"title": "Finalisierung", "description": "Finalisiere Projekte", "icon": "🏁", "color": "#DC2626"}
            {"title": "Projektübersicht", "description": "Verwalte deine Projekte", "icon": "📊", "color": "#7C3AED"}
        ]
        
        for i, workflow in enumerate(workflows):
            # Workflow card
            card = create_card(content, height=90)
            card.pack(fill="x", pady=(0, self.ui.spacing.M))
            
            # Card content
            card_content = ctk.CTkFrame(card, fg_color="transparent")
            card_content.pack(fill="both", expand=True, padx=self.ui.spacing.CARD_PADDING, pady=self.ui.spacing.CARD_PADDING)
            
            # Left side - info
            info_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True)
            
            # Icon and title
            header_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
            header_frame.pack(fill="x")
            
            # Icon
            icon_label = ctk.CTkLabel()
                header_frame
                text=workflow["icon"]
                font=ctk.CTkFont(size=self.ui.typography.ICON_M)
            )
            icon_label.pack(side="left", padx=(0, self.ui.spacing.S))
            
            # Title
            title_label = create_heading(header_frame, workflow["title"], level="S")
            title_label.pack(side="left", fill="x", expand=True)
            
            # Description
            desc_label = create_body_text()
                info_frame
                workflow["description"]
                size="S"
                text_color="#6B7280"
            )
            desc_label.pack(fill="x", pady=(self.ui.spacing.XS, 0))
            
            # Right side - button
            button_frame = ctk.CTkFrame(card_content, fg_color="transparent")
            button_frame.pack(side="right", fill="y")
            
            # Start button
            start_btn = create_primary_button()
                button_frame
                "Start"
                width=70
                height=36
                fg_color=workflow["color"]
            )
            start_btn.pack(expand=True)
            
            # Apply hover effect
            self.ui.apply_card_hover_effect(card)
    
    def _create_footer(self):
        """Create the footer section."""Fixed broken docstring"""
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=2, column=0, sticky="ew", padx=self.ui.spacing.CONTAINER_PADDING, pady=(0, self.ui.spacing.CONTAINER_PADDING))
        
        # Status info
        status_text = create_body_text()
            footer
            "✅ Bereit für die Bearbeitung"
            size="M"
            text_color="#16A34A"
        )
        status_text.pack(anchor="w")