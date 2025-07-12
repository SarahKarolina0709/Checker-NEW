"""
Enhanced Drag & Drop System
==========================
Advanced drag and drop functionality with visual feedback,
multi-format support, and sophisticated animations.
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from typing import List, Callable, Optional, Dict, Any, Tuple
import os
import threading
import time
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
import mimetypes

class DropZoneState(Enum):
    """Drop zone states."""
    NORMAL = "normal"
    HOVER = "hover"
    ACTIVE = "active"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"

@dataclass
class FileInfo:
    """File information container."""
    path: str
    name: str
    size: int
    type: str
    mime_type: str
    icon: str

class EnhancedDropZone:
    """Enhanced drag and drop zone with visual feedback."""
    
    def __init__(self, parent, width: int = 400, height: int = 200,
                 accepted_types: Optional[List[str]] = None,
                 on_files_dropped: Optional[Callable] = None,
                 on_files_changed: Optional[Callable] = None):
        self.parent = parent
        self.width = width
        self.height = height
        self.accepted_types = accepted_types or ["*"]
        self.on_files_dropped = on_files_dropped
        self.on_files_changed = on_files_changed
        
        self.current_state = DropZoneState.NORMAL
        self.dropped_files: List[FileInfo] = []
        self.is_animating = False
        
        # UI elements
        self.drop_frame = None
        self.content_frame = None
        self.icon_label = None
        self.title_label = None
        self.subtitle_label = None
        self.file_list_frame = None
        self.progress_bar = None
        self.browse_button = None
        
        # Animation properties
        self.animation_thread = None
        self.pulse_colors = ["#E3F2FD", "#BBDEFB", "#90CAF9", "#BBDEFB"]
        self.current_pulse_index = 0
        
        self._create_ui()
        self._setup_drag_drop()
    
    def _create_ui(self):
        """Create the drag and drop UI."""
        # Main drop frame
        self.drop_frame = ctk.CTkFrame(
            self.parent,
            width=self.width,
            height=self.height,
            corner_radius=15,
            border_width=2,
            border_color="#E0E0E0"
        )
        self.drop_frame.pack_propagate(False)
        
        # Content frame
        self.content_frame = ctk.CTkFrame(
            self.drop_frame,
            fg_color="transparent"
        )
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Icon
        self.icon_label = ctk.CTkLabel(
            self.content_frame,
            text="📁",
            font=ctk.CTkFont(size=48),
            text_color="#666666"
        )
        self.icon_label.pack(pady=(0, 10))
        
        # Title
        self.title_label = ctk.CTkLabel(
            self.content_frame,
            text="Drop files here",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        )
        self.title_label.pack()
        
        # Subtitle
        supported_types = ", ".join(self.accepted_types) if self.accepted_types != ["*"] else "All file types"
        self.subtitle_label = ctk.CTkLabel(
            self.content_frame,
            text=f"Supported: {supported_types}",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        self.subtitle_label.pack(pady=(5, 15))
        
        # Browse button
        self.browse_button = ctk.CTkButton(
            self.content_frame,
            text="📂 Browse Files",
            command=self._browse_files,
            width=120,
            height=32,
            font=ctk.CTkFont(size=12)
        )
        self.browse_button.pack()
        
        # File list frame (initially hidden)
        self.file_list_frame = ctk.CTkScrollableFrame(
            self.drop_frame,
            width=self.width - 40,
            height=100,
            corner_radius=10
        )
        
        # Progress bar (initially hidden)
        self.progress_bar = ctk.CTkProgressBar(
            self.drop_frame,
            width=self.width - 40,
            height=4,
            progress_color="#4CAF50"
        )
        
        self._update_visual_state()
    
    def _setup_drag_drop(self):
        """Setup drag and drop functionality."""
        # Bind drag and drop events
        self.drop_frame.drop_target_register(tk.DND_FILES)
        self.drop_frame.dnd_bind('<<Drop>>', self._handle_drop)
        self.drop_frame.dnd_bind('<<DragEnter>>', self._handle_drag_enter)
        self.drop_frame.dnd_bind('<<DragLeave>>', self._handle_drag_leave)
        self.drop_frame.dnd_bind('<<DragOver>>', self._handle_drag_over)
        
        # Alternative: Use tkinterdnd2 if available
        try:
            import tkinterdnd2 as tkdnd
            
            def setup_tkinterdnd():
                # Convert to tkdnd format
                self.drop_frame.dnd_bind('<<Drop>>', self._handle_drop_tkdnd)
                self.drop_frame.dnd_bind('<<DragEnter>>', self._handle_drag_enter_tkdnd)
                self.drop_frame.dnd_bind('<<DragLeave>>', self._handle_drag_leave_tkdnd)
                
            setup_tkinterdnd()
            
        except ImportError:
            # Fallback: manual drag and drop simulation
            self._setup_manual_drag_drop()
    
    def _setup_manual_drag_drop(self):
        """Setup manual drag and drop for systems without tkinterdnd2."""
        # Bind mouse events for visual feedback
        self.drop_frame.bind("<Button-1>", self._on_click)
        self.drop_frame.bind("<Double-Button-1>", self._browse_files)
        
        # Bind enter/leave events for hover effect
        self.drop_frame.bind("<Enter>", self._on_enter)
        self.drop_frame.bind("<Leave>", self._on_leave)
    
    def _handle_drop(self, event):
        """Handle file drop event."""
        try:
            # Get dropped files
            files = self._parse_drop_data(event.data)
            self._process_dropped_files(files)
        except Exception as e:
            print(f"Error handling drop: {e}")
            self._set_state(DropZoneState.ERROR)
    
    def _handle_drop_tkdnd(self, event):
        """Handle file drop event with tkinterdnd2."""
        try:
            files = event.data.split()
            self._process_dropped_files(files)
        except Exception as e:
            print(f"Error handling drop: {e}")
            self._set_state(DropZoneState.ERROR)
    
    def _handle_drag_enter(self, event):
        """Handle drag enter event."""
        self._set_state(DropZoneState.HOVER)
        self._start_pulse_animation()
    
    def _handle_drag_enter_tkdnd(self, event):
        """Handle drag enter event with tkinterdnd2."""
        self._set_state(DropZoneState.HOVER)
        self._start_pulse_animation()
    
    def _handle_drag_leave(self, event):
        """Handle drag leave event."""
        self._set_state(DropZoneState.NORMAL)
        self._stop_pulse_animation()
    
    def _handle_drag_leave_tkdnd(self, event):
        """Handle drag leave event with tkinterdnd2."""
        self._set_state(DropZoneState.NORMAL)
        self._stop_pulse_animation()
    
    def _handle_drag_over(self, event):
        """Handle drag over event."""
        # Visual feedback during drag over
        self._set_state(DropZoneState.ACTIVE)
    
    def _on_click(self, event):
        """Handle click event."""
        if self.current_state == DropZoneState.NORMAL:
            self._set_state(DropZoneState.ACTIVE)
            self.drop_frame.after(200, lambda: self._set_state(DropZoneState.NORMAL))
    
    def _on_enter(self, event):
        """Handle mouse enter event."""
        if self.current_state == DropZoneState.NORMAL:
            self._set_state(DropZoneState.HOVER)
    
    def _on_leave(self, event):
        """Handle mouse leave event."""
        if self.current_state == DropZoneState.HOVER:
            self._set_state(DropZoneState.NORMAL)
    
    def _parse_drop_data(self, data: str) -> List[str]:
        """Parse drop data to extract file paths."""
        # Handle different data formats
        if isinstance(data, str):
            # Split by whitespace and filter valid paths
            paths = [path.strip('{}') for path in data.split()]
            return [path for path in paths if os.path.exists(path)]
        elif isinstance(data, list):
            return [str(item) for item in data if os.path.exists(str(item))]
        return []
    
    def _process_dropped_files(self, file_paths: List[str]):
        """Process dropped files."""
        if not file_paths:
            return
        
        self._set_state(DropZoneState.PROCESSING)
        
        # Process files in background thread
        def process():
            try:
                valid_files = []
                
                for file_path in file_paths:
                    if self._is_file_accepted(file_path):
                        file_info = self._create_file_info(file_path)
                        valid_files.append(file_info)
                
                # Update UI in main thread
                self.parent.after(0, lambda: self._on_files_processed(valid_files))
                
            except Exception as e:
                print(f"Error processing files: {e}")
                self.parent.after(0, lambda: self._set_state(DropZoneState.ERROR))
        
        thread = threading.Thread(target=process, daemon=True)
        thread.start()
    
    def _is_file_accepted(self, file_path: str) -> bool:
        """Check if file type is accepted."""
        if "*" in self.accepted_types:
            return True
        
        file_extension = Path(file_path).suffix.lower()
        return file_extension in self.accepted_types
    
    def _create_file_info(self, file_path: str) -> FileInfo:
        """Create file information object."""
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        return FileInfo(
            path=file_path,
            name=path.name,
            size=path.stat().st_size,
            type=path.suffix.lower(),
            mime_type=mime_type or "application/octet-stream",
            icon=self._get_file_icon(path.suffix.lower())
        )
    
    def _get_file_icon(self, file_extension: str) -> str:
        """Get icon for file type."""
        icon_map = {
            ".txt": "📄",
            ".pdf": "📕",
            ".doc": "📘",
            ".docx": "📘",
            ".xls": "📊",
            ".xlsx": "📊",
            ".ppt": "📊",
            ".pptx": "📊",
            ".jpg": "🖼️",
            ".jpeg": "🖼️",
            ".png": "🖼️",
            ".gif": "🖼️",
            ".mp4": "🎬",
            ".avi": "🎬",
            ".mp3": "🎵",
            ".wav": "🎵",
            ".zip": "📦",
            ".rar": "📦",
            ".py": "🐍",
            ".js": "📜",
            ".html": "🌐",
            ".css": "🎨"
        }
        return icon_map.get(file_extension, "📄")
    
    def _on_files_processed(self, files: List[FileInfo]):
        """Handle processed files."""
        if files:
            self.dropped_files.extend(files)
            self._set_state(DropZoneState.SUCCESS)
            self._show_file_list()
            
            # Call callback
            if self.on_files_dropped:
                self.on_files_dropped(files)
            
            if self.on_files_changed:
                self.on_files_changed(self.dropped_files)
        else:
            self._set_state(DropZoneState.ERROR)
    
    def _show_file_list(self):
        """Show list of dropped files."""
        # Hide main content
        self.content_frame.pack_forget()
        
        # Show file list
        self.file_list_frame.pack(fill="both", expand=True, padx=20, pady=(20, 10))
        
        # Clear existing file items
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        # Add files to list
        for file_info in self.dropped_files:
            self._create_file_item(file_info)
        
        # Add control buttons
        self._create_control_buttons()
    
    def _create_file_item(self, file_info: FileInfo):
        """Create file item widget."""
        item_frame = ctk.CTkFrame(self.file_list_frame)
        item_frame.pack(fill="x", pady=2)
        
        # File icon
        icon_label = ctk.CTkLabel(
            item_frame,
            text=file_info.icon,
            font=ctk.CTkFont(size=16),
            width=30
        )
        icon_label.pack(side="left", padx=(10, 5))
        
        # File info
        info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="x", expand=True, padx=5)
        
        # File name
        name_label = ctk.CTkLabel(
            info_frame,
            text=file_info.name,
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="w"
        )
        name_label.pack(fill="x")
        
        # File details
        size_str = self._format_file_size(file_info.size)
        details_label = ctk.CTkLabel(
            info_frame,
            text=f"{size_str} • {file_info.type.upper()}",
            font=ctk.CTkFont(size=10),
            text_color="#666666",
            anchor="w"
        )
        details_label.pack(fill="x")
        
        # Remove button
        remove_btn = ctk.CTkButton(
            item_frame,
            text="✕",
            width=25,
            height=25,
            command=lambda: self._remove_file(file_info),
            fg_color="transparent",
            hover_color="#FFCDD2",
            text_color="#666666"
        )
        remove_btn.pack(side="right", padx=10)
    
    def _create_control_buttons(self):
        """Create control buttons."""
        button_frame = ctk.CTkFrame(self.drop_frame)
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # Add more button
        add_btn = ctk.CTkButton(
            button_frame,
            text="➕ Add More",
            command=self._browse_files,
            width=100,
            height=30
        )
        add_btn.pack(side="left", padx=5)
        
        # Clear all button
        clear_btn = ctk.CTkButton(
            button_frame,
            text="🗑️ Clear All",
            command=self._clear_all_files,
            width=100,
            height=30,
            fg_color="#F44336",
            hover_color="#D32F2F"
        )
        clear_btn.pack(side="right", padx=5)
    
    def _format_file_size(self, size: int) -> str:
        """Format file size in human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    def _remove_file(self, file_info: FileInfo):
        """Remove file from list."""
        if file_info in self.dropped_files:
            self.dropped_files.remove(file_info)
            
            if self.on_files_changed:
                self.on_files_changed(self.dropped_files)
            
            # Refresh file list
            if self.dropped_files:
                self._show_file_list()
            else:
                self._show_empty_state()
    
    def _clear_all_files(self):
        """Clear all files."""
        self.dropped_files.clear()
        
        if self.on_files_changed:
            self.on_files_changed(self.dropped_files)
        
        self._show_empty_state()
    
    def _show_empty_state(self):
        """Show empty state."""
        self.file_list_frame.pack_forget()
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        self._set_state(DropZoneState.NORMAL)
    
    def _browse_files(self):
        """Open file browser."""
        file_types = [("All files", "*.*")]
        if self.accepted_types != ["*"]:
            file_types.insert(0, ("Supported files", " ".join(f"*{ext}" for ext in self.accepted_types)))
        
        files = filedialog.askopenfilenames(
            title="Select files",
            filetypes=file_types
        )
        
        if files:
            self._process_dropped_files(list(files))
    
    def _set_state(self, state: DropZoneState):
        """Set drop zone state and update visuals."""
        self.current_state = state
        self._update_visual_state()
    
    def _update_visual_state(self):
        """Update visual appearance based on state."""
        state_config = {
            DropZoneState.NORMAL: {
                "border_color": "#E0E0E0",
                "fg_color": "#FAFAFA",
                "icon": "📁",
                "title": "Drop files here",
                "title_color": "#333333",
                "icon_color": "#666666"
            },
            DropZoneState.HOVER: {
                "border_color": "#2196F3",
                "fg_color": "#E3F2FD",
                "icon": "📁",
                "title": "Drop files here",
                "title_color": "#1976D2",
                "icon_color": "#2196F3"
            },
            DropZoneState.ACTIVE: {
                "border_color": "#4CAF50",
                "fg_color": "#E8F5E8",
                "icon": "📁",
                "title": "Release to drop",
                "title_color": "#388E3C",
                "icon_color": "#4CAF50"
            },
            DropZoneState.PROCESSING: {
                "border_color": "#FF9800",
                "fg_color": "#FFF3E0",
                "icon": "⏳",
                "title": "Processing files...",
                "title_color": "#F57C00",
                "icon_color": "#FF9800"
            },
            DropZoneState.SUCCESS: {
                "border_color": "#4CAF50",
                "fg_color": "#E8F5E8",
                "icon": "✅",
                "title": "Files added successfully",
                "title_color": "#388E3C",
                "icon_color": "#4CAF50"
            },
            DropZoneState.ERROR: {
                "border_color": "#F44336",
                "fg_color": "#FFEBEE",
                "icon": "❌",
                "title": "Error processing files",
                "title_color": "#D32F2F",
                "icon_color": "#F44336"
            }
        }
        
        config = state_config.get(self.current_state, state_config[DropZoneState.NORMAL])
        
        # Update frame appearance
        self.drop_frame.configure(
            border_color=config["border_color"],
            fg_color=config["fg_color"]
        )
        
        # Update icon and text
        if self.icon_label:
            self.icon_label.configure(
                text=config["icon"],
                text_color=config["icon_color"]
            )
        
        if self.title_label:
            self.title_label.configure(
                text=config["title"],
                text_color=config["title_color"]
            )
    
    def _start_pulse_animation(self):
        """Start pulse animation."""
        if self.is_animating:
            return
        
        self.is_animating = True
        
        def animate():
            while self.is_animating and self.current_state in [DropZoneState.HOVER, DropZoneState.ACTIVE]:
                try:
                    color = self.pulse_colors[self.current_pulse_index]
                    self.drop_frame.configure(fg_color=color)
                    
                    self.current_pulse_index = (self.current_pulse_index + 1) % len(self.pulse_colors)
                    time.sleep(0.3)
                    
                except Exception as e:
                    print(f"Error in pulse animation: {e}")
                    break
            
            self.is_animating = False
        
        self.animation_thread = threading.Thread(target=animate, daemon=True)
        self.animation_thread.start()
    
    def _stop_pulse_animation(self):
        """Stop pulse animation."""
        self.is_animating = False
    
    def get_widget(self) -> ctk.CTkFrame:
        """Get the main widget."""
        return self.drop_frame
    
    def get_files(self) -> List[FileInfo]:
        """Get dropped files."""
        return self.dropped_files.copy()
    
    def clear_files(self):
        """Clear all files."""
        self._clear_all_files()
    
    def set_accepted_types(self, accepted_types: List[str]):
        """Set accepted file types."""
        self.accepted_types = accepted_types
        
        # Update subtitle
        supported_types = ", ".join(accepted_types) if accepted_types != ["*"] else "All file types"
        self.subtitle_label.configure(text=f"Supported: {supported_types}")

# Example usage
def create_drag_drop_demo(parent):
    """Create a demo of the enhanced drag & drop system."""
    def on_files_dropped(files):
        print(f"Files dropped: {[f.name for f in files]}")
    
    def on_files_changed(files):
        print(f"Files changed: {len(files)} files")
    
    # Create drop zone
    drop_zone = EnhancedDropZone(
        parent,
        width=500,
        height=300,
        accepted_types=[".txt", ".pdf", ".doc", ".docx", ".jpg", ".png"],
        on_files_dropped=on_files_dropped,
        on_files_changed=on_files_changed
    )
    
    return drop_zone.get_widget()
