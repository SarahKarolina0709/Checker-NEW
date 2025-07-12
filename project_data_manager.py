# -*- coding: utf-8 -*-
"""
Project Data Manager - Minimal Stub for Checker App

This is a minimal implementation that provides the DATA_FILE path
needed by file_operations.py for saving last_inputs.json.
"""

import os

# Define the data file path for project data storage
DATA_FILE = os.path.join(os.path.dirname(__file__), "project_data", "projects.json")

# Ensure the project_data directory exists
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

class ProjectDataManager:
    """Minimal project data manager"""
    
    def __init__(self):
        self.data_file = DATA_FILE
    
    def get_data_dir(self):
        """Returns the directory for storing project data"""
        return os.path.dirname(DATA_FILE)
