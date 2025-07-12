"""
Erweiterte Icon-Ergänzung
Fügt moderne, professionelle Icons für erweiterte UI-Funktionen hinzu
"""

import os
from PIL import Image, ImageDraw, ImageFont
import math

class ModernIconCreator:
    """Erstellt moderne, professionelle Icons"""
    
    def __init__(self, icons_dir="icons"):
        self.icons_dir = icons_dir
        self.size = 48
        self.modern_colors = {
            'primary': '#2563EB',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'info': '#3B82F6',
            'neutral': '#6B7280',
            'dark': '#1F2937'
        }
        
    def create_advanced_icons(self):
        """Erstellt erweiterte Icons für professionelle UI"""
        
        advanced_icons = [
            # Navigation & Bewegung
            ('arrow_up', self.draw_arrow_up, 'primary'),
            ('arrow_down', self.draw_arrow_down, 'primary'),
            ('arrow_right', self.draw_arrow_right, 'primary'),
            ('chevron_left', self.draw_chevron_left, 'neutral'),
            ('chevron_right', self.draw_chevron_right, 'neutral'),
            ('chevron_up', self.draw_chevron_up, 'neutral'),
            ('chevron_down', self.draw_chevron_down, 'neutral'),
            
            # Status & Feedback
            ('check_circle', self.draw_check_circle, 'success'),
            ('error_circle', self.draw_error_circle, 'error'),
            ('warning_triangle', self.draw_warning_triangle, 'warning'),
            ('info_circle', self.draw_info_circle, 'info'),
            ('loading', self.draw_loading, 'primary'),
            ('progress', self.draw_progress, 'primary'),
            
            # Dateien & Ordner (erweitert)
            ('file_text', self.draw_file_text, 'neutral'),
            ('file_image', self.draw_file_image, 'info'),
            ('file_code', self.draw_file_code, 'primary'),
            ('folder_plus', self.draw_folder_plus, 'success'),
            ('folder_minus', self.draw_folder_minus, 'error'),
            
            # Benutzer & Profile
            ('user_circle', self.draw_user_circle, 'primary'),
            ('users', self.draw_users, 'primary'),
            ('user_plus', self.draw_user_plus, 'success'),
            ('user_check', self.draw_user_check, 'success'),
            
            # Interface & Kontrollen
            ('eye', self.draw_eye, 'neutral'),
            ('eye_off', self.draw_eye_off, 'neutral'),
            ('toggle_on', self.draw_toggle_on, 'success'),
            ('toggle_off', self.draw_toggle_off, 'neutral'),
            ('slider', self.draw_slider, 'primary'),
            
            # Kommunikation & Teilen
            ('chat', self.draw_chat, 'info'),
            ('message_circle', self.draw_message_circle, 'info'),
            ('send', self.draw_send, 'primary'),
            ('reply', self.draw_reply, 'neutral'),
            
            # Tools & Aktionen
            ('copy', self.draw_copy, 'neutral'),
            ('paste', self.draw_paste, 'neutral'),
            ('cut', self.draw_cut, 'warning'),
            ('rotate', self.draw_rotate, 'primary'),
            ('refresh_circle', self.draw_refresh_circle, 'primary'),
            
            # Medien
            ('camera', self.draw_camera, 'neutral'),
            ('video', self.draw_video, 'primary'),
            ('music', self.draw_music, 'info'),
            ('headphones', self.draw_headphones, 'neutral'),
            
            # System & Verwaltung
            ('database', self.draw_database, 'primary'),
            ('server', self.draw_server, 'neutral'),
            ('cloud', self.draw_cloud, 'info'),
            ('shield', self.draw_shield, 'success'),
            ('key_modern', self.draw_key_modern, 'warning'),
            
            # Layout & Design
            ('grid', self.draw_grid, 'neutral'),
            ('layout', self.draw_layout, 'primary'),
            ('align_left', self.draw_align_left, 'neutral'),
            ('align_center', self.draw_align_center, 'neutral'),
            ('align_right', self.draw_align_right, 'neutral'),
            
            # Erweiterte Funktionen
            ('filter_list', self.draw_filter_list, 'primary'),
            ('sort_asc', self.draw_sort_asc, 'neutral'),
            ('sort_desc', self.draw_sort_desc, 'neutral'),
            ('expand', self.draw_expand, 'primary'),
            ('collapse', self.draw_collapse, 'primary'),
        ]
        
        created_count = 0
        
        if not os.path.exists(self.icons_dir):
            os.makedirs(self.icons_dir)
        
        for icon_name, draw_func, color_key in advanced_icons:
            icon_path = os.path.join(self.icons_dir, f"{icon_name}.png")
            
            # Überspringe wenn Icon bereits existiert
            if os.path.exists(icon_path):
                print(f"⏭️  Überspringe {icon_name} (bereits vorhanden)")
                continue
                
            try:
                # Erstelle Icon
                img = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                color = self.modern_colors[color_key]
                draw_func(draw, color)
                
                # Speichere Icon
                img.save(icon_path, 'PNG')
                print(f"✅ Erstellt: {icon_name}.png")
                created_count += 1
                
            except Exception as e:
                print(f"❌ Fehler bei {icon_name}: {e}")
        
        return created_count
    
    # Navigation Icons
    def draw_arrow_up(self, draw, color):
        points = [(self.size//2, self.size//4), (self.size//4, self.size*3//4), (self.size*3//4, self.size*3//4)]
        draw.polygon(points, fill=color)
        
    def draw_arrow_down(self, draw, color):
        points = [(self.size//2, self.size*3//4), (self.size//4, self.size//4), (self.size*3//4, self.size//4)]
        draw.polygon(points, fill=color)
        
    def draw_arrow_right(self, draw, color):
        points = [(self.size*3//4, self.size//2), (self.size//4, self.size//4), (self.size//4, self.size*3//4)]
        draw.polygon(points, fill=color)
        
    def draw_chevron_left(self, draw, color):
        width = self.size // 16
        points = [(self.size*3//5, self.size//4), (self.size*2//5, self.size//2), (self.size*3//5, self.size*3//4)]
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=width)
            
    def draw_chevron_right(self, draw, color):
        width = self.size // 16
        points = [(self.size*2//5, self.size//4), (self.size*3//5, self.size//2), (self.size*2//5, self.size*3//4)]
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=width)
            
    def draw_chevron_up(self, draw, color):
        width = self.size // 16
        points = [(self.size//4, self.size*3//5), (self.size//2, self.size*2//5), (self.size*3//4, self.size*3//5)]
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=width)
            
    def draw_chevron_down(self, draw, color):
        width = self.size // 16
        points = [(self.size//4, self.size*2//5), (self.size//2, self.size*3//5), (self.size*3//4, self.size*2//5)]
        for i in range(len(points)-1):
            draw.line([points[i], points[i+1]], fill=color, width=width)
    
    # Status Icons
    def draw_check_circle(self, draw, color):
        margin = self.size // 8
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=self.size//16)
        # Checkmark
        check_points = [(self.size*2//5, self.size//2), (self.size*2//5 + self.size//8, self.size*3//5), (self.size*3//4, self.size//3)]
        for i in range(len(check_points)-1):
            draw.line([check_points[i], check_points[i+1]], fill=color, width=self.size//16)
            
    def draw_error_circle(self, draw, color):
        margin = self.size // 8
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=self.size//16)
        # X
        draw.line([self.size//3, self.size//3, self.size*2//3, self.size*2//3], fill=color, width=self.size//16)
        draw.line([self.size*2//3, self.size//3, self.size//3, self.size*2//3], fill=color, width=self.size//16)
        
    def draw_warning_triangle(self, draw, color):
        points = [(self.size//2, self.size//6), (self.size//6, self.size*5//6), (self.size*5//6, self.size*5//6)]
        draw.polygon(points, outline=color, width=self.size//16)
        # Exclamation
        draw.rectangle([self.size//2-self.size//32, self.size//3, self.size//2+self.size//32, self.size*2//3], fill=color)
        draw.ellipse([self.size//2-self.size//24, self.size*3//4, self.size//2+self.size//24, self.size*3//4+self.size//12], fill=color)
        
    def draw_info_circle(self, draw, color):
        margin = self.size // 8
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=self.size//16)
        # i
        draw.ellipse([self.size//2-self.size//24, self.size//3, self.size//2+self.size//24, self.size//3+self.size//12], fill=color)
        draw.rectangle([self.size//2-self.size//32, self.size//2, self.size//2+self.size//32, self.size*2//3], fill=color)
        
    def draw_loading(self, draw, color):
        center = self.size // 2
        radius = self.size // 3
        for i in range(8):
            angle = i * math.pi / 4
            x1 = center + radius * 0.7 * math.cos(angle)
            y1 = center + radius * 0.7 * math.sin(angle)
            x2 = center + radius * math.cos(angle)
            y2 = center + radius * math.sin(angle)
            alpha = 255 - (i * 30)
            color_with_alpha = color + f"{alpha:02x}"
            draw.line([x1, y1, x2, y2], fill=color, width=self.size//24)
            
    def draw_progress(self, draw, color):
        margin = self.size // 6
        # Background
        draw.rectangle([margin, self.size//2-self.size//16, self.size-margin, self.size//2+self.size//16], 
                      outline=color, width=2)
        # Progress (50%)
        draw.rectangle([margin+2, self.size//2-self.size//16+2, self.size//2, self.size//2+self.size//16-2], 
                      fill=color)
    
    # File Icons
    def draw_file_text(self, draw, color):
        margin = self.size // 6
        # File outline
        draw.rectangle([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Text lines
        for i in range(3):
            y = margin + self.size//4 + i * self.size//8
            draw.line([margin + self.size//8, y, self.size - margin - self.size//8, y], fill=color, width=2)
            
    def draw_file_image(self, draw, color):
        margin = self.size // 6
        # File outline
        draw.rectangle([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Image (mountain and sun)
        draw.polygon([(margin+self.size//8, self.size-margin-self.size//8), 
                     (self.size//2, margin+self.size//4), 
                     (self.size-margin-self.size//8, self.size-margin-self.size//8)], fill=color)
        draw.ellipse([self.size-margin-self.size//4, margin+self.size//8, 
                     self.size-margin-self.size//8, margin+self.size//4], fill=color)
                     
    def draw_file_code(self, draw, color):
        margin = self.size // 6
        # File outline
        draw.rectangle([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Code brackets
        draw.line([margin+self.size//8, margin+self.size//4, margin+self.size//12, margin+self.size//4], fill=color, width=2)
        draw.line([margin+self.size//12, margin+self.size//4, margin+self.size//12, self.size-margin-self.size//4], fill=color, width=2)
        draw.line([margin+self.size//12, self.size-margin-self.size//4, margin+self.size//8, self.size-margin-self.size//4], fill=color, width=2)
        
    def draw_folder_plus(self, draw, color):
        # Folder
        margin = self.size // 8
        draw.rectangle([margin, margin+self.size//6, self.size-margin, self.size-margin], outline=color, width=2)
        draw.rectangle([margin, margin+self.size//6, self.size//2, margin+self.size//3], outline=color, width=2)
        # Plus
        plus_size = self.size // 6
        center = self.size // 2
        draw.line([center, center-plus_size//2, center, center+plus_size//2], fill=self.modern_colors['success'], width=3)
        draw.line([center-plus_size//2, center, center+plus_size//2, center], fill=self.modern_colors['success'], width=3)
        
    def draw_folder_minus(self, draw, color):
        # Folder
        margin = self.size // 8
        draw.rectangle([margin, margin+self.size//6, self.size-margin, self.size-margin], outline=color, width=2)
        draw.rectangle([margin, margin+self.size//6, self.size//2, margin+self.size//3], outline=color, width=2)
        # Minus
        plus_size = self.size // 6
        center = self.size // 2
        draw.line([center-plus_size//2, center, center+plus_size//2, center], fill=self.modern_colors['error'], width=3)
    
    # User Icons
    def draw_user_circle(self, draw, color):
        margin = self.size // 8
        # Circle
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Head
        head_size = self.size // 6
        draw.ellipse([self.size//2-head_size//2, margin+self.size//6, 
                     self.size//2+head_size//2, margin+self.size//6+head_size], fill=color)
        # Body
        body_width = self.size // 3
        draw.ellipse([self.size//2-body_width//2, self.size//2, 
                     self.size//2+body_width//2, self.size-margin], fill=color)
                     
    def draw_users(self, draw, color):
        # Two overlapping user circles
        for offset in [0, self.size//4]:
            x_offset = offset
            # Head
            head_size = self.size // 8
            draw.ellipse([self.size//4+x_offset-head_size//2, self.size//4, 
                         self.size//4+x_offset+head_size//2, self.size//4+head_size], fill=color)
            # Body
            body_width = self.size // 5
            draw.ellipse([self.size//4+x_offset-body_width//2, self.size//2, 
                         self.size//4+x_offset+body_width//2, self.size*3//4], fill=color)
                         
    def draw_user_plus(self, draw, color):
        # User
        margin = self.size // 6
        # Head
        head_size = self.size // 8
        draw.ellipse([margin+self.size//8-head_size//2, margin, 
                     margin+self.size//8+head_size//2, margin+head_size], fill=color)
        # Body
        body_width = self.size // 6
        draw.ellipse([margin+self.size//8-body_width//2, margin+self.size//4, 
                     margin+self.size//8+body_width//2, margin+self.size//2], fill=color)
        # Plus
        plus_size = self.size // 8
        center_x = self.size*3//4
        center_y = self.size//2
        draw.line([center_x, center_y-plus_size//2, center_x, center_y+plus_size//2], fill=self.modern_colors['success'], width=3)
        draw.line([center_x-plus_size//2, center_y, center_x+plus_size//2, center_y], fill=self.modern_colors['success'], width=3)
        
    def draw_user_check(self, draw, color):
        # User
        margin = self.size // 6
        # Head
        head_size = self.size // 8
        draw.ellipse([margin+self.size//8-head_size//2, margin, 
                     margin+self.size//8+head_size//2, margin+head_size], fill=color)
        # Body
        body_width = self.size // 6
        draw.ellipse([margin+self.size//8-body_width//2, margin+self.size//4, 
                     margin+self.size//8+body_width//2, margin+self.size//2], fill=color)
        # Check
        check_points = [(self.size*2//3, self.size//2), (self.size*3//4, self.size*3//5), (self.size*5//6, self.size*2//5)]
        for i in range(len(check_points)-1):
            draw.line([check_points[i], check_points[i+1]], fill=self.modern_colors['success'], width=3)
    
    # Interface Icons
    def draw_eye(self, draw, color):
        # Eye shape
        center_x, center_y = self.size // 2, self.size // 2
        width, height = self.size // 2, self.size // 4
        # Outer eye
        draw.ellipse([center_x-width//2, center_y-height//2, center_x+width//2, center_y+height//2], outline=color, width=2)
        # Pupil
        pupil_size = self.size // 8
        draw.ellipse([center_x-pupil_size//2, center_y-pupil_size//2, center_x+pupil_size//2, center_y+pupil_size//2], fill=color)
        
    def draw_eye_off(self, draw, color):
        self.draw_eye(draw, color)
        # Slash
        draw.line([self.size//4, self.size//4, self.size*3//4, self.size*3//4], fill=self.modern_colors['error'], width=3)
        
    def draw_toggle_on(self, draw, color):
        # Background
        width = self.size // 2
        height = self.size // 4
        x = self.size // 4
        y = self.size // 2 - height // 2
        draw.rounded_rectangle([x, y, x+width, y+height], radius=height//2, fill=color)
        # Circle
        circle_size = height - 4
        draw.ellipse([x+width-circle_size-2, y+2, x+width-2, y+height-2], fill='white')
        
    def draw_toggle_off(self, draw, color):
        # Background
        width = self.size // 2
        height = self.size // 4
        x = self.size // 4
        y = self.size // 2 - height // 2
        draw.rounded_rectangle([x, y, x+width, y+height], radius=height//2, outline=color, width=2)
        # Circle
        circle_size = height - 4
        draw.ellipse([x+2, y+2, x+circle_size+2, y+height-2], fill=color)
        
    def draw_slider(self, draw, color):
        # Track
        margin = self.size // 6
        draw.line([margin, self.size//2, self.size-margin, self.size//2], fill=color, width=4)
        # Handle
        handle_x = self.size * 2 // 3
        handle_size = self.size // 8
        draw.ellipse([handle_x-handle_size//2, self.size//2-handle_size//2, 
                     handle_x+handle_size//2, self.size//2+handle_size//2], fill=color)
    
    # Communication Icons
    def draw_chat(self, draw, color):
        # Chat bubble
        margin = self.size // 8
        bubble_height = self.size // 2
        draw.rounded_rectangle([margin, margin, self.size-margin, margin+bubble_height], 
                             radius=self.size//8, outline=color, width=2)
        # Tail
        draw.polygon([(margin+self.size//8, margin+bubble_height), 
                     (margin+self.size//6, margin+bubble_height+self.size//8), 
                     (margin+self.size//4, margin+bubble_height)], fill=color)
                     
    def draw_message_circle(self, draw, color):
        # Circle
        margin = self.size // 8
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Message lines
        for i in range(3):
            y = margin + self.size//3 + i * self.size//12
            line_width = self.size//2 - i * self.size//12
            draw.line([self.size//2-line_width//2, y, self.size//2+line_width//2, y], fill=color, width=2)
            
    def draw_send(self, draw, color):
        # Arrow pointing right-up
        points = [(self.size//6, self.size*5//6), (self.size*5//6, self.size//6), (self.size//2, self.size//3), (self.size//3, self.size//2)]
        draw.polygon(points, fill=color)
        
    def draw_reply(self, draw, color):
        # Curved arrow
        center = self.size // 2
        # Arrow head
        points = [(self.size//4, center), (self.size//3, center-self.size//8), (self.size//3, center+self.size//8)]
        draw.polygon(points, fill=color)
        # Curved line
        draw.arc([self.size//4, center-self.size//6, self.size*3//4, center+self.size//6], 
                start=180, end=0, fill=color, width=3)
    
    # Tool Icons
    def draw_copy(self, draw, color):
        # Two overlapping rectangles
        offset = self.size // 8
        margin = self.size // 6
        # Back rectangle
        draw.rectangle([margin+offset, margin+offset, self.size-margin+offset, self.size-margin+offset], 
                      outline=color, width=2)
        # Front rectangle
        draw.rectangle([margin, margin, self.size-margin, self.size-margin], outline=color, width=2, fill='white')
        
    def draw_paste(self, draw, color):
        # Clipboard
        margin = self.size // 6
        draw.rectangle([margin, margin+self.size//8, self.size-margin, self.size-margin], outline=color, width=2)
        # Clip
        clip_width = self.size // 4
        draw.rectangle([self.size//2-clip_width//2, margin, self.size//2+clip_width//2, margin+self.size//4], 
                      outline=color, width=2, fill='white')
                      
    def draw_cut(self, draw, color):
        # Scissors
        # Handles
        handle_length = self.size // 3
        draw.line([self.size//6, self.size//6, self.size//6+handle_length//2, self.size//6+handle_length//2], 
                 fill=color, width=3)
        draw.line([self.size//6, self.size*5//6, self.size//6+handle_length//2, self.size*5//6-handle_length//2], 
                 fill=color, width=3)
        # Blades
        draw.line([self.size//6+handle_length//2, self.size//6+handle_length//2, self.size*5//6, self.size//2], 
                 fill=color, width=2)
        draw.line([self.size//6+handle_length//2, self.size*5//6-handle_length//2, self.size*5//6, self.size//2], 
                 fill=color, width=2)
                 
    def draw_rotate(self, draw, color):
        # Circular arrow
        center = self.size // 2
        radius = self.size // 3
        # Arc
        draw.arc([center-radius, center-radius, center+radius, center+radius], 
                start=45, end=315, fill=color, width=3)
        # Arrow head
        angle = math.radians(315)
        x = center + radius * math.cos(angle)
        y = center + radius * math.sin(angle)
        arrow_size = self.size // 12
        draw.polygon([(x, y), (x-arrow_size, y-arrow_size//2), (x-arrow_size, y+arrow_size//2)], fill=color)
        
    def draw_refresh_circle(self, draw, color):
        # Circle with arrow
        margin = self.size // 8
        draw.ellipse([margin, margin, self.size-margin, self.size-margin], outline=color, width=2)
        # Arrow
        center = self.size // 2
        arrow_size = self.size // 8
        draw.polygon([(center+arrow_size, margin+self.size//12), 
                     (center+arrow_size+self.size//12, margin), 
                     (center+arrow_size+self.size//12, margin+self.size//6)], fill=color)
    
    # Media Icons (weitere Implementierungen für die restlichen Icons...)
    def draw_camera(self, draw, color):
        # Camera body
        margin = self.size // 6
        draw.rounded_rectangle([margin, margin+self.size//8, self.size-margin, self.size-margin], 
                             radius=self.size//12, outline=color, width=2)
        # Lens
        lens_size = self.size // 4
        center = self.size // 2
        draw.ellipse([center-lens_size//2, center-lens_size//4, center+lens_size//2, center+lens_size//4+lens_size//2], 
                    outline=color, width=2)
        # Flash
        draw.rectangle([margin+self.size//8, margin, margin+self.size//4, margin+self.size//8], fill=color)
        
    def draw_video(self, draw, color):
        # Camera body
        margin = self.size // 6
        draw.rectangle([margin, margin+self.size//6, self.size*2//3, self.size-margin], outline=color, width=2)
        # Lens
        lens_size = self.size // 6
        draw.ellipse([margin+self.size//12, margin+self.size//3, margin+self.size//12+lens_size, margin+self.size//3+lens_size], 
                    outline=color, width=2)
        # Tripod leg
        draw.line([self.size*2//3+self.size//12, margin+self.size//3, self.size-margin, self.size//2], fill=color, width=3)
        
    def draw_music(self, draw, color):
        # Musical note
        # Note head
        note_size = self.size // 8
        draw.ellipse([self.size//3, self.size*2//3, self.size//3+note_size, self.size*2//3+note_size], fill=color)
        # Stem
        draw.line([self.size//3+note_size, self.size*2//3, self.size//3+note_size, self.size//4], fill=color, width=3)
        # Flag
        draw.polygon([(self.size//3+note_size, self.size//4), 
                     (self.size//2, self.size//3), 
                     (self.size//3+note_size, self.size//2)], fill=color)
                     
    def draw_headphones(self, draw, color):
        # Headband
        center = self.size // 2
        radius = self.size // 3
        draw.arc([center-radius, center-radius//2, center+radius, center+radius*3//2], 
                start=180, end=0, fill=color, width=3)
        # Ear cups
        cup_size = self.size // 6
        draw.ellipse([center-radius-cup_size//2, center+radius//2-cup_size//2, 
                     center-radius+cup_size//2, center+radius//2+cup_size//2], fill=color)
        draw.ellipse([center+radius-cup_size//2, center+radius//2-cup_size//2, 
                     center+radius+cup_size//2, center+radius//2+cup_size//2], fill=color)
    
    # System Icons (weitere vereinfachte Implementierungen...)
    def draw_database(self, draw, color):
        # Database cylinder
        margin = self.size // 6
        height = self.size // 8
        # Top ellipse
        draw.ellipse([margin, margin, self.size-margin, margin+height], outline=color, width=2)
        # Middle body
        draw.rectangle([margin, margin+height//2, self.size-margin, self.size-margin-height//2], outline=color, width=2)
        # Bottom ellipse
        draw.ellipse([margin, self.size-margin-height, self.size-margin, self.size-margin], outline=color, width=2)
        
    def draw_server(self, draw, color):
        # Server stack
        margin = self.size // 6
        for i in range(3):
            y = margin + i * self.size//5
            draw.rectangle([margin, y, self.size-margin, y+self.size//6], outline=color, width=2)
            # Indicator lights
            draw.ellipse([self.size-margin-self.size//12, y+self.size//24, 
                         self.size-margin-self.size//24, y+self.size//12], fill=self.modern_colors['success'])
                         
    def draw_cloud(self, draw, color):
        # Cloud shape (simplified)
        center = self.size // 2
        # Main cloud body
        draw.ellipse([self.size//4, center-self.size//8, self.size*3//4, center+self.size//8], fill=color)
        # Cloud bumps
        draw.ellipse([self.size//6, center-self.size//6, self.size//2, center+self.size//12], fill=color)
        draw.ellipse([self.size//2, center-self.size//6, self.size*5//6, center+self.size//12], fill=color)
        
    def draw_shield(self, draw, color):
        # Shield shape
        center_x = self.size // 2
        margin = self.size // 6
        points = [
            (center_x, margin),
            (self.size-margin, margin+self.size//4),
            (self.size-margin, self.size//2),
            (center_x, self.size-margin),
            (margin, self.size//2),
            (margin, margin+self.size//4)
        ]
        draw.polygon(points, outline=color, width=2)
        # Check mark inside
        check_points = [(center_x-self.size//8, center_x), (center_x-self.size//16, center_x+self.size//16), (center_x+self.size//8, center_x-self.size//16)]
        for i in range(len(check_points)-1):
            draw.line([check_points[i], check_points[i+1]], fill=color, width=3)
            
    def draw_key_modern(self, draw, color):
        # Key head (circle)
        head_size = self.size // 4
        draw.ellipse([self.size//6, self.size//4, self.size//6+head_size, self.size//4+head_size], outline=color, width=2)
        # Key shaft
        draw.line([self.size//6+head_size, self.size//4+head_size//2, self.size*5//6, self.size//4+head_size//2], 
                 fill=color, width=4)
        # Key teeth
        for i in range(2):
            y = self.size//4+head_size//2 + (i+1)*self.size//16
            draw.line([self.size*3//4, self.size//4+head_size//2, self.size*3//4, y], fill=color, width=3)
    
    # Layout Icons (vereinfachte Implementierungen...)
    def draw_grid(self, draw, color):
        # Grid lines
        spacing = self.size // 4
        margin = self.size // 8
        for i in range(4):
            x = margin + i * spacing
            y = margin + i * spacing
            if x < self.size - margin:
                draw.line([x, margin, x, self.size-margin], fill=color, width=2)
            if y < self.size - margin:
                draw.line([margin, y, self.size-margin, y], fill=color, width=2)
                
    def draw_layout(self, draw, color):
        # Layout boxes
        margin = self.size // 6
        # Header
        draw.rectangle([margin, margin, self.size-margin, margin+self.size//6], outline=color, width=2)
        # Sidebar
        draw.rectangle([margin, margin+self.size//5, margin+self.size//3, self.size-margin], outline=color, width=2)
        # Main content
        draw.rectangle([margin+self.size//3+self.size//12, margin+self.size//5, self.size-margin, self.size-margin], 
                      outline=color, width=2)
                      
    def draw_align_left(self, draw, color):
        # Left-aligned lines
        margin = self.size // 6
        line_heights = [self.size//2, self.size//3, self.size*2//3]
        for i, width in enumerate(line_heights):
            y = margin + self.size//6 + i * self.size//6
            draw.line([margin, y, margin+width, y], fill=color, width=3)
            
    def draw_align_center(self, draw, color):
        # Center-aligned lines
        margin = self.size // 6
        line_widths = [self.size//2, self.size//3, self.size*2//3]
        for i, width in enumerate(line_widths):
            y = margin + self.size//6 + i * self.size//6
            start_x = (self.size - width) // 2
            draw.line([start_x, y, start_x+width, y], fill=color, width=3)
            
    def draw_align_right(self, draw, color):
        # Right-aligned lines
        margin = self.size // 6
        line_widths = [self.size//2, self.size//3, self.size*2//3]
        for i, width in enumerate(line_widths):
            y = margin + self.size//6 + i * self.size//6
            start_x = self.size - margin - width
            draw.line([start_x, y, start_x+width, y], fill=color, width=3)
    
    # Advanced function icons (vereinfachte Implementierungen...)
    def draw_filter_list(self, draw, color):
        # List with filter funnel
        margin = self.size // 6
        # Lines
        for i in range(3):
            y = margin + self.size//4 + i * self.size//6
            width = self.size//2 - i * self.size//12
            draw.line([margin, y, margin+width, y], fill=color, width=3)
        # Filter funnel
        draw.polygon([(self.size*2//3, margin), (self.size-margin, margin), 
                     (self.size*5//6, self.size//2)], outline=color, width=2)
                     
    def draw_sort_asc(self, draw, color):
        # Up arrow with lines
        margin = self.size // 6
        # Arrow
        points = [(self.size//2, margin), (self.size//3, self.size//2), (self.size*2//3, self.size//2)]
        draw.polygon(points, fill=color)
        # Lines getting shorter upward
        for i in range(3):
            y = self.size//2 + self.size//8 + i * self.size//12
            width = self.size//3 + i * self.size//12
            draw.line([self.size//2-width//2, y, self.size//2+width//2, y], fill=color, width=2)
            
    def draw_sort_desc(self, draw, color):
        # Down arrow with lines
        margin = self.size // 6
        # Arrow
        points = [(self.size//2, self.size-margin), (self.size//3, self.size//2), (self.size*2//3, self.size//2)]
        draw.polygon(points, fill=color)
        # Lines getting longer downward
        for i in range(3):
            y = margin + i * self.size//12
            width = self.size//2 - i * self.size//12
            draw.line([self.size//2-width//2, y, self.size//2+width//2, y], fill=color, width=2)
            
    def draw_expand(self, draw, color):
        # Expand arrows (four corners)
        margin = self.size // 6
        arrow_size = self.size // 8
        # Top-left
        draw.polygon([(margin, margin+arrow_size), (margin, margin), (margin+arrow_size, margin)], fill=color)
        # Top-right
        draw.polygon([(self.size-margin-arrow_size, margin), (self.size-margin, margin), (self.size-margin, margin+arrow_size)], fill=color)
        # Bottom-left
        draw.polygon([(margin, self.size-margin-arrow_size), (margin, self.size-margin), (margin+arrow_size, self.size-margin)], fill=color)
        # Bottom-right
        draw.polygon([(self.size-margin-arrow_size, self.size-margin), (self.size-margin, self.size-margin), (self.size-margin, self.size-margin-arrow_size)], fill=color)
        
    def draw_collapse(self, draw, color):
        # Collapse arrows (pointing inward)
        center = self.size // 2
        arrow_size = self.size // 8
        # From corners to center
        margin = self.size // 4
        # Top-left to center
        draw.polygon([(margin-arrow_size//2, margin), (margin, margin-arrow_size//2), (margin, margin)], fill=color)
        # Top-right to center
        draw.polygon([(self.size-margin+arrow_size//2, margin), (self.size-margin, margin-arrow_size//2), (self.size-margin, margin)], fill=color)
        # Bottom-left to center
        draw.polygon([(margin-arrow_size//2, self.size-margin), (margin, self.size-margin+arrow_size//2), (margin, self.size-margin)], fill=color)
        # Bottom-right to center
        draw.polygon([(self.size-margin+arrow_size//2, self.size-margin), (self.size-margin, self.size-margin+arrow_size//2), (self.size-margin, self.size-margin)], fill=color)

def main():
    """Hauptfunktion"""
    print("🎨 Erstelle erweiterte moderne Icons...")
    
    creator = ModernIconCreator()
    created = creator.create_advanced_icons()
    
    print(f"\n✅ {created} neue moderne Icons erstellt!")
    print("🔥 Icon-Bibliothek ist jetzt vollständig modernisiert!")

if __name__ == "__main__":
    main()
