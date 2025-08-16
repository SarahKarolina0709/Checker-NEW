#!/usr/bin/env python3
"""
Patch für alle Widget-Parameter um String-Concatenation-Probleme zu vermeiden
"""

import customtkinter as ctk

def safe_CTkFrame(*args, **kwargs):
    """Sichere CTkFrame-Erstellung mit Type-Safe-Parametern"""
    # Sichere Integer-Parameter
    int_params = ['height', 'width', 'corner_radius', 'border_width']
    for param in int_params:
        if param in kwargs:
            try:
                kwargs[param] = int(kwargs[param])
            except (ValueError, TypeError):
                if param == 'height':
                    kwargs[param] = 100
                elif param == 'width':
                    kwargs[param] = 200
                elif param == 'corner_radius':
                    kwargs[param] = 8
                elif param == 'border_width':
                    kwargs[param] = 0

    return ctk.CTkFrame(*args, **kwargs)

def safe_CTkLabel(*args, **kwargs):
    """Sichere CTkLabel-Erstellung mit Type-Safe-Parametern"""
    # Sichere String-Parameter
    if 'text' in kwargs:
        kwargs['text'] = str(kwargs['text'])

    # Sichere Integer-Parameter
    int_params = ['height', 'width', 'corner_radius', 'padx', 'pady']
    for param in int_params:
        if param in kwargs:
            try:
                kwargs[param] = int(kwargs[param])
            except (ValueError, TypeError):
                if param in ['height', 'width']:
                    kwargs[param] = 30
                elif param == 'corner_radius':
                    kwargs[param] = 6
                elif param in ['padx', 'pady']:
                    kwargs[param] = 8

    return ctk.CTkLabel(*args, **kwargs)

def safe_CTkButton(*args, **kwargs):
    """Sichere CTkButton-Erstellung mit Type-Safe-Parametern"""
    # Sichere String-Parameter
    if 'text' in kwargs:
        kwargs['text'] = str(kwargs['text'])

    # Sichere Integer-Parameter
    int_params = ['height', 'width', 'corner_radius']
    for param in int_params:
        if param in kwargs:
            try:
                kwargs[param] = int(kwargs[param])
            except (ValueError, TypeError):
                if param == 'height':
                    kwargs[param] = 44
                elif param == 'width':
                    kwargs[param] = 120
                elif param == 'corner_radius':
                    kwargs[param] = 8

    return ctk.CTkButton(*args, **kwargs)

# Sichere pack/grid-Methoden
def safe_pack(widget, **kwargs):
    """Sichere pack-Konfiguration mit Type-Safe-Parametern"""
    int_params = ['padx', 'pady', 'ipadx', 'ipady']
    for param in int_params:
        if param in kwargs:
            try:
                # Kann tuple sein für (x, y) Padding
                if isinstance(kwargs[param], tuple):
                    kwargs[param] = tuple(int(x) for x in kwargs[param])
                else:
                    kwargs[param] = int(kwargs[param])
            except (ValueError, TypeError):
                kwargs[param] = 8

    return widget.pack(**kwargs)

def safe_grid(widget, **kwargs):
    """Sichere grid-Konfiguration mit Type-Safe-Parametern"""
    int_params = ['padx', 'pady', 'ipadx', 'ipady', 'row', 'column', 'rowspan', 'columnspan']
    for param in int_params:
        if param in kwargs:
            try:
                # Kann tuple sein für (x, y) Padding
                if isinstance(kwargs[param], tuple):
                    kwargs[param] = tuple(int(x) for x in kwargs[param])
                else:
                    kwargs[param] = int(kwargs[param])
            except (ValueError, TypeError):
                if param in ['padx', 'pady', 'ipadx', 'ipady']:
                    kwargs[param] = 8
                elif param in ['row', 'column']:
                    kwargs[param] = 0
                elif param in ['rowspan', 'columnspan']:
                    kwargs[param] = 1

    return widget.grid(**kwargs)

print("🛡️ Widget Safety Patches loaded successfully!")