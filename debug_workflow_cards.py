#!/usr/bin/env python3
"""
Debug script to check workflow card creation and visibility
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_workflow_cards():
    """Debug workflow card creation"""
    
    # Set up logging
    logging.basicConfig(level=logging.DEBUG, format='%(levelname)s [%(name)s] %(message)s')
    logger = logging.getLogger('workflow_debug')
    
    try:
        from checker_app import CheckerApp
        
        # Create and initialize the app
        logger.info("Creating CheckerApp...")
        app = CheckerApp()
        
        # Give it time to initialize
        app.root.update()
        
        # Check if welcome screen was created
        if hasattr(app, 'welcome_screen') and app.welcome_screen:
            logger.info("Welcome screen found!")
            
            # Check if workflow section exists
            if hasattr(app.welcome_screen, 'workflow_section'):
                workflow_section = app.welcome_screen.workflow_section
                logger.info(f"Workflow section found: {workflow_section}")
                
                # Check children of workflow section
                children = workflow_section.winfo_children()
                logger.info(f"Workflow section has {len(children)} children")
                
                for i, child in enumerate(children):
                    logger.info(f"Child {i}: {child} - {child.winfo_class()}")
                    
                    # If it's a frame, check its children
                    if hasattr(child, 'winfo_children'):
                        subchildren = child.winfo_children()
                        logger.info(f"  Has {len(subchildren)} subchildren")
                        for j, subchild in enumerate(subchildren):
                            logger.info(f"    Subchild {j}: {subchild} - {subchild.winfo_class()}")
                            
                            # If it's a scrollable frame, check its children
                            if hasattr(subchild, 'winfo_children') and 'scrollable' in str(subchild).lower():
                                scrollable_children = subchild.winfo_children()
                                logger.info(f"      Scrollable frame has {len(scrollable_children)} children")
                                for k, scroll_child in enumerate(scrollable_children):
                                    logger.info(f"        Scroll child {k}: {scroll_child} - {scroll_child.winfo_class()}")
                                    
                                    # Check if it's visible
                                    try:
                                        is_visible = scroll_child.winfo_viewable()
                                        width = scroll_child.winfo_width()
                                        height = scroll_child.winfo_height()
                                        logger.info(f"        Visibility: {is_visible}, Size: {width}x{height}")
                                    except Exception as e:
                                        logger.warning(f"        Could not check visibility: {e}")
                
                # Check workflow routes
                if hasattr(app, 'workflow_routes'):
                    workflow_routes = app.workflow_routes
                    logger.info(f"Found {len(workflow_routes)} workflow routes: {list(workflow_routes.keys())}")
                else:
                    logger.warning("No workflow_routes found in app")
                    
            else:
                logger.error("No workflow_section found in welcome screen")
        else:
            logger.error("No welcome screen found")
        
        # Keep the window open for inspection
        logger.info("App created successfully. Check the window...")
        
        # Run a simple test to see if all workflow cards are created
        def check_workflow_cards():
            try:
                if hasattr(app, 'welcome_screen') and app.welcome_screen:
                    if hasattr(app.welcome_screen, 'workflow_section'):
                        # Try to find all workflow cards
                        workflow_section = app.welcome_screen.workflow_section
                        
                        def find_workflow_cards(widget, cards_found=None):
                            if cards_found is None:
                                cards_found = []
                            
                            # Check if this widget looks like a workflow card
                            if hasattr(widget, 'winfo_class') and 'frame' in widget.winfo_class().lower():
                                # Check if it has workflow-like children
                                children = widget.winfo_children()
                                if len(children) >= 2:  # Should have icon, text, and button
                                    cards_found.append(widget)
                            
                            # Recurse into children
                            if hasattr(widget, 'winfo_children'):
                                for child in widget.winfo_children():
                                    find_workflow_cards(child, cards_found)
                            
                            return cards_found
                        
                        cards = find_workflow_cards(workflow_section)
                        logger.info(f"Found {len(cards)} potential workflow cards")
                        
                        for i, card in enumerate(cards):
                            try:
                                is_visible = card.winfo_viewable()
                                width = card.winfo_width()
                                height = card.winfo_height()
                                x = card.winfo_x()
                                y = card.winfo_y()
                                logger.info(f"Card {i}: visible={is_visible}, size={width}x{height}, pos=({x},{y})")
                            except Exception as e:
                                logger.warning(f"Card {i}: Could not get info: {e}")
                                
            except Exception as e:
                logger.error(f"Error checking workflow cards: {e}")
        
        # Schedule the check
        app.root.after(2000, check_workflow_cards)
        
        # Run the app
        app.run()
        
    except Exception as e:
        logger.error(f"Error during debug: {e}", exc_info=True)
        return False
    
    return True

if __name__ == "__main__":
    success = debug_workflow_cards()
    if success:
        print("Debug completed successfully")
    else:
        print("Debug failed")
        sys.exit(1)
