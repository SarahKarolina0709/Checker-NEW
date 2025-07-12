import customtkinter as ctk
from ui_theme import UITheme, AccessibilityHelper, enhanced_theme
from .section_header_mixin import SectionHeaderMixin
from animation_engine import animation_engine
from enhanced_visual_effects import AnimatedCard, PulsingIcon, apply_glow_effect, create_sparkle_effect, get_vibrant_color_scheme

class WorkflowSection(ctk.CTkFrame, SectionHeaderMixin):
    """
    The workflow section of the welcome screen with enhanced visual effects.
    Displays available workflows for the user to start.
    """
    def __init__(self, master, app, welcome_screen, **kwargs):
        super().__init__(master=master, fg_color="transparent", **kwargs)
        self.app = app
        self.welcome_screen = welcome_screen
        # Robust logger access with fallback
        try:
            self.logger = getattr(app, 'logger', None)
            if not self.logger:
                import logging
                self.logger = logging.getLogger(__name__)
        except Exception:
            import logging
            self.logger = logging.getLogger(__name__)

        # Configure grid to use all available space
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.create_widgets()

    def create_widgets(self):
        """Creates the widgets for the workflow section with professional design."""
        # Professional Workflow Container
        workflow_container = ctk.CTkFrame(
            self,
            **UITheme.CONTAINER_STYLE_WORKFLOW,
            height=UITheme.SECTION_CONTAINER_HEIGHT
        )
        workflow_container.grid(row=0, column=0, sticky="nsew", padx=(UITheme.SPACING_M, UITheme.SPACING_S), pady=(0, UITheme.SPACING_M))
        workflow_container.grid_columnconfigure(0, weight=1)
        workflow_container.grid_rowconfigure(1, weight=1)
        workflow_container.grid_propagate(False)

        # Professional Header
        header_frame, icon_bg = self.create_section_header(
            container=workflow_container,
            title="Workflows starten",
            subtitle="Wählen Sie einen Workflow zur Bearbeitung aus",
            icon_name="play",
            icon_bg_color=enhanced_theme.get_color('primary'),
            icon_emoji_fallback="🚀"
        )
        
        # Add simple visual enhancement to header
        def add_header_glow():
            try:
                # Simple color animation for header icon
                header_frame.configure(fg_color=enhanced_theme.get_color('primary_surface'))
            except:
                pass
        
        # Schedule header enhancement
        header_frame.after(500, add_header_glow)

        # Professional Workflow List
        workflow_list_frame = ctk.CTkScrollableFrame(
            workflow_container,
            fg_color="transparent",
            label_text="",
            scrollbar_button_color=enhanced_theme.get_color('primary'),
            scrollbar_button_hover_color=enhanced_theme.get_color('primary_hover'),
            corner_radius=UITheme.CORNER_RADIUS
        )
        workflow_list_frame.grid(row=1, column=0, sticky="nsew", padx=UITheme.SPACING_L, pady=(0, UITheme.SPACING_L))
        workflow_list_frame.grid_columnconfigure(0, weight=1)
        workflow_list_frame.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        # Scrollregion immer aktualisieren
        workflow_list_frame.bind("<Configure>", lambda e: workflow_list_frame.update_idletasks())

        # Dynamically create workflow cards with enhanced visual effects
        if hasattr(self.app, 'workflow_routes'):
            # Handle both property (main app) and method (debug app) cases
            if callable(self.app.workflow_routes):
                workflow_routes = self.app.workflow_routes()  # Call the method
            else:
                workflow_routes = self.app.workflow_routes  # Access the property
            
            self.logger.info(f"[WORKFLOW] Creating {len(workflow_routes)} workflow cards")
            for i, (workflow_id, data) in enumerate(workflow_routes.items()):
                try:
                    # Use enhanced card creation
                    card = self.create_enhanced_workflow_card(workflow_list_frame, workflow_id, data, i)
                    self.logger.info(f"[WORKFLOW] Successfully created enhanced card for {workflow_id} at row {i}")
                    
                    # Force update the scrollable frame after each card
                    workflow_list_frame.update_idletasks()
                    
                except Exception as e:
                    self.logger.error(f"[WORKFLOW] Error creating card for {workflow_id}: {e}")
                    # Continue with next workflow
                    continue
                    
            # Final update to ensure all cards are visible
            self.after(100, lambda: workflow_list_frame.update_idletasks())
        else:
            self.logger.warning("[WORKFLOW] No workflow_routes found in app")

    def create_enhanced_workflow_card(self, parent, workflow_id, data, row):
        """Creates a beautiful, enhanced workflow card with vibrant colors and animations."""
        try:
            self.logger.info(f"[WORKFLOW] Creating enhanced workflow card for {workflow_id} at row {row}")
            
            # Get vibrant color scheme based on workflow type
            color_scheme = get_vibrant_color_scheme(workflow_id.split('_')[0])
            colors = {
                'primary': color_scheme['primary'],
                'hover': enhanced_theme.get_color('primary_hover'),
                'light': enhanced_theme.get_color('card'),
                'icon_bg': color_scheme['primary'],
                'glow': color_scheme['secondary'],
                'shadow': enhanced_theme.get_color('border')
            }
            
            # Modern card with enhanced design (simplified for stability)
            card = ctk.CTkFrame(
                parent,
                corner_radius=UITheme.CORNER_RADIUS_LARGE,
                border_width=2,
                border_color=colors['primary'],
                height=UITheme.CARD_HEIGHT_COMPACT,
                fg_color=colors['light']
            )
            card.grid(row=row, column=0, sticky="ew", pady=(0, UITheme.SPACING_M))
            card.grid_columnconfigure(0, weight=0)  # Icon: fixed width
            card.grid_columnconfigure(1, weight=1)  # Text: expands
            card.grid_columnconfigure(2, weight=0)  # Button: fixed width
            card.grid_rowconfigure(0, weight=1)
            card.grid_propagate(False)

            # Modern Icon Container with enhanced design
            icon_bg = ctk.CTkFrame(
                card,
                fg_color=colors['icon_bg'],
                corner_radius=UITheme.CORNER_RADIUS,
                width=UITheme.BUTTON_HEIGHT_MEDIUM,
                height=UITheme.BUTTON_HEIGHT_MEDIUM
            )
            icon_bg.grid(row=0, column=0, sticky="ns", padx=UITheme.SPACING_M, pady=UITheme.SPACING_M)
            icon_bg.grid_propagate(False)

            # Enhanced Icon with better sizing and accessibility
            try:
                icon = self.app.get_icon(data.get('icon', 'play'), (24, 24))
                if icon:
                    icon_label = ctk.CTkLabel(icon_bg, image=icon, text="")
                    icon_label.place(relx=0.5, rely=0.5, anchor="center")
                    
                    # Add accessibility support
                    if hasattr(UITheme, 'apply_accessibility_features'):
                        UITheme.apply_accessibility_features(
                            icon_label, 
                            widget_type="icon",
                            aria_label=f"Symbol für {data.get('name', 'Workflow')}"
                        )
                else:
                    # Enhanced emoji fallback with color animation
                    emoji_map = {
                        'angebots': '💰',
                        'pruefung': '🔍', 
                        'finalisierung': '✅',
                        'projekt': '📁'
                    }
                    emoji = emoji_map.get(workflow_id.split('_')[0], '🚀')
                    emoji_label = ctk.CTkLabel(
                        icon_bg, 
                        text=emoji, 
                        font=ctk.CTkFont(size=16),
                        text_color="white"
                    )
                    emoji_label.place(relx=0.5, rely=0.5, anchor="center")
                    
                    # Add color animation manually
                    def animate_emoji_color():
                        try:
                            # Simple color animation using after method
                            current_color = colors['primary']
                            glow_color = colors['glow']
                            
                            def cycle_color(step=0):
                                try:
                                    # Cycle between primary and glow colors
                                    if step % 2 == 0:
                                        emoji_label.configure(text_color=current_color)
                                    else:
                                        emoji_label.configure(text_color=glow_color)
                                    
                                    # Schedule next color change
                                    emoji_label.after(1000, lambda: cycle_color(step + 1))
                                except:
                                    pass
                            
                            cycle_color()
                        except:
                            pass
                    
                    # Start animation after a delay
                    emoji_label.after(int(row * 200 + 1000), animate_emoji_color)
                    
                    # Add accessibility support
                    if hasattr(UITheme, 'apply_accessibility_features'):
                        UITheme.apply_accessibility_features(
                            emoji_label,
                            widget_type="icon", 
                            aria_label=f"Symbol für {data.get('name', 'Workflow')}"
                        )
            except Exception as e:
                self.logger.warning(f"[WORKFLOW] Icon loading error: {e}")
                # Final fallback with accessibility
                emoji_label = ctk.CTkLabel(
                    icon_bg, 
                    text="🚀", 
                    font=ctk.CTkFont(size=16),
                    text_color="white"
                )
                emoji_label.place(relx=0.5, rely=0.5, anchor="center")

            # Enhanced Text Container with modern spacing
            text_container = ctk.CTkFrame(card, fg_color="transparent")
            text_container.grid(row=0, column=1, sticky="nsew", padx=(UITheme.SPACING_M, UITheme.SPACING_S), pady=UITheme.SPACING_S)
            text_container.grid_columnconfigure(0, weight=1)
            text_container.grid_rowconfigure(0, weight=0)
            text_container.grid_rowconfigure(1, weight=1)

            # Enhanced Title with better typography
            title = ctk.CTkLabel(
                text_container,
                text=data.get('name', 'Unbenannter Workflow'),
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=14, weight="bold"),
                text_color=colors['primary'],
                anchor="w"
            )
            title.grid(row=0, column=0, sticky="ew", pady=(0, 2))

            # Enhanced Description with better readability
            description = ctk.CTkLabel(
                text_container,
                text=data.get('description', 'Keine Beschreibung verfügbar.'),
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=11),
                text_color=enhanced_theme.get_color('text_secondary'),
                anchor="nw",
                justify="left",
                wraplength=200
            )
            description.grid(row=1, column=0, sticky="new")

            # Modern Start Button with enhanced styling and effects
            start_button = ctk.CTkButton(
                card,
                text="Start",
                command=lambda w=workflow_id: self.welcome_screen.start_workflow_callback(w),
                fg_color=colors['primary'],
                hover_color=colors['hover'],
                text_color="white",
                font=ctk.CTkFont(family=UITheme.FONT_FAMILY_UI, size=UITheme.FONT_SIZE_BODY, weight="bold"),
                corner_radius=UITheme.CORNER_RADIUS,
                width=80,
                height=UITheme.BUTTON_HEIGHT_SMALL
            )
            start_button.grid(row=0, column=2, sticky="ns", padx=(UITheme.SPACING_S, UITheme.SPACING_M), pady=UITheme.SPACING_M)
            
            # Add simple glow effect to button
            def add_button_glow():
                try:
                    # Simple border glow effect
                    start_button.configure(border_width=1, border_color=colors['glow'])
                except:
                    pass
            
            # Schedule button enhancement
            start_button.after(int(row * 200 + 800), add_button_glow)
            
            # Add enhanced animations and effects
            self._add_enhanced_card_hover_effect(card, colors)
            self._add_enhanced_button_effects(start_button, colors)
            self._add_enhanced_entrance_animation(card, row, colors)
            
            self.logger.info(f"[WORKFLOW] Successfully created enhanced workflow card for {workflow_id}")
            return card
            
        except Exception as e:
            self.logger.error(f"[WORKFLOW] Error creating enhanced workflow card for {workflow_id}: {e}")
            raise

    def _add_enhanced_card_hover_effect(self, card, colors):
        """Adds premium hover effects with smooth transitions and vibrant colors."""
        original_fg_color = colors['light']
        hover_fg_color = enhanced_theme.get_color('surface')
        original_border_color = colors['primary']
        hover_border_color = colors['glow']
        
        # Store animation state
        card._is_hovered = False
        card._hover_animation_id = None
        
        # Enhanced color dictionaries
        base_colors = {
            "fg_color": original_fg_color,
            "border_color": original_border_color
        }
        hover_colors = {
            "fg_color": hover_fg_color,
            "border_color": hover_border_color
        }
        
        def on_enter(event):
            if card._is_hovered:
                return
            card._is_hovered = True
            
            # Change cursor to hand pointer
            try:
                card.configure(cursor="hand2")
            except Exception as e:
                self.logger.debug(f"Could not set cursor on card: {e}")
            
            # Premium hover transition with vibrant colors
            try:
                card._hover_animation_id = animation_engine.animate_premium_hover_transition(
                    card, base_colors, hover_colors, scale_factor=1.02, duration=200
                )
            except:
                # Fallback to simple color change
                card.configure(fg_color=hover_fg_color, border_color=hover_border_color)
            
            # Add subtle glow effect with simple animation
            try:
                def add_glow():
                    try:
                        # Simple glow effect using border
                        card.configure(border_width=1, border_color=colors['glow'])
                    except:
                        pass
                
                card.after(50, add_glow)
            except:
                pass
            
        def on_leave(event):
            if not card._is_hovered:
                return
            card._is_hovered = False
            
            # Reset cursor
            try:
                card.configure(cursor="")
            except:
                pass
            
            # Premium hover out transition
            try:
                animation_engine.animate_premium_hover_transition(
                    card, hover_colors, base_colors, scale_factor=1.0, duration=200
                )
            except:
                # Fallback to simple color change
                card.configure(fg_color=original_fg_color, border_color=original_border_color)
        
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)
        
        # Bind to all child widgets for better UX
        for child in card.winfo_children():
            child.bind("<Enter>", on_enter)
            child.bind("<Leave>", on_leave)

    def _add_enhanced_button_effects(self, button, colors):
        """Adds enhanced button effects with vibrant colors."""
        original_fg_color = colors['primary']
        hover_fg_color = colors['hover']
        
        def on_enter(event):
            button.configure(fg_color=hover_fg_color)
            
        def on_leave(event):
            button.configure(fg_color=original_fg_color)
            
        def on_click(event):
            # Add simple click effect
            try:
                # Simple click animation
                def flash_effect():
                    try:
                        original_color = button.cget('fg_color')
                        button.configure(fg_color=colors['glow'])
                        button.after(100, lambda: button.configure(fg_color=original_color))
                    except:
                        pass
                
                flash_effect()
            except:
                pass
        
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
        button.bind("<Button-1>", on_click)

    def _add_enhanced_entrance_animation(self, card, row, colors):
        """Adds enhanced entrance animation with vibrant colors."""
        # Simple entrance animation using opacity-like effect
        def animate_entrance():
            try:
                # Start with a subtle background color
                card.configure(fg_color=enhanced_theme.get_color('background'))
                
                # Animate to final color
                def fade_in(step=0):
                    try:
                        if step >= 10:
                            card.configure(fg_color=colors['light'])
                            return
                        
                        # Gradually change to final color
                        progress = step / 10
                        # Simple color transition simulation
                        if step % 2 == 0:
                            card.configure(fg_color=enhanced_theme.get_color('surface'))
                        else:
                            card.configure(fg_color=colors['light'])
                        
                        card.after(50, lambda: fade_in(step + 1))
                    except:
                        pass
                
                fade_in()
            except:
                pass
        
        # Delay entrance animation based on row
        card.after(int(row * 200 + 100), animate_entrance)
