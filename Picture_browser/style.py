"""
Styles for the Picture Browser application.
This module provides styling options for making the UI more modern and user-friendly.
"""

import tkinter as tk
import platform

class AppStyle:
    """Styling class for the Picture Browser application"""
    
    def __init__(self, root):
        """Initialize styling for the application"""
        self.root = root
        self.os_type = platform.system()
        self.apply_base_styles()
        
    def apply_base_styles(self):
        """Apply base styling to the application"""
        # Set application background
        bg_color = "#F0F0F0"  # Light gray background
        fg_color = "#333333"  # Dark text color
        accent_color = "#4285F4"  # Google blue for accents
        
        # Adjust for OS
        if self.os_type == "Darwin":  # macOS
            # macOS style uses slightly different colors
            bg_color = "#F2F2F2"
            accent_color = "#0066CC"  # macOS blue
            font_family = "Helvetica Neue"
        elif self.os_type == "Windows":
            # Windows style
            bg_color = "#F0F0F0"
            accent_color = "#0078D7"  # Windows blue
            font_family = "Segoe UI"
        else:  # Linux or other
            font_family = "Noto Sans"
        
        # Configure default font
        default_font = (font_family, 10)
        title_font = (font_family, 12, "bold")
        
        # Configure styles for different widgets
        self.root.configure(bg=bg_color)
        
        # Button style
        self.button_style = {
            "bg": accent_color,
            "fg": "#FFFFFF",
            "activebackground": self._adjust_color(accent_color, -20),
            "activeforeground": "#FFFFFF",
            "bd": 0,
            "padx": 10,
            "pady": 5,
            "font": default_font,
            "highlightthickness": 0,
            "borderwidth": 0,
            "cursor": "hand2"
        }
        
        # Frame style
        self.frame_style = {
            "bg": bg_color,
            "highlightthickness": 0
        }
        
        # Label style
        self.label_style = {
            "bg": bg_color,
            "fg": fg_color,
            "font": default_font
        }
        
        # Title label style
        self.title_label_style = {
            "bg": bg_color,
            "fg": fg_color,
            "font": title_font
        }
        
        # Canvas style
        self.canvas_style = {
            "bg": "#FFFFFF",
            "highlightthickness": 1,
            "highlightbackground": "#CCCCCC"
        }
        
        # Selected frame style
        self.selected_frame_style = {
            "relief": tk.RIDGE,
            "bd": 2,
            "highlightthickness": 2,
            "highlightbackground": accent_color
        }
        
        # Normal frame style
        self.normal_frame_style = {
            "relief": tk.SOLID,
            "bd": 1,
            "highlightthickness": 0
        }
        
        # Folder container style
        self.folder_container_style = {
            "bg": bg_color,
            "padx": 10,
            "pady": 10
        }
        
        # Navigation frame style
        self.nav_frame_style = {
            "bg": "#FFFFFF",
            "padx": 10,
            "pady": 5
        }
        
    def apply_styles_to_widget(self, widget, style_dict):
        """Apply a style dictionary to a widget"""
        for key, value in style_dict.items():
            try:
                widget[key] = value
            except tk.TclError:
                # Some options might not be applicable to all widgets
                pass
    
    def style_button(self, button):
        """Apply button styling"""
        button.configure(**self.button_style)
        
    def style_label(self, label, is_title=False):
        """Apply label styling"""
        if is_title:
            label.configure(**self.title_label_style)
        else:
            label.configure(**self.label_style)
    
    def style_frame(self, frame, is_selected=False):
        """Apply frame styling based on selection state"""
        if is_selected:
            frame.configure(**self.selected_frame_style)
        else:
            frame.configure(**self.normal_frame_style)
    
    def style_canvas(self, canvas):
        """Apply canvas styling"""
        canvas.configure(**self.canvas_style)
        
    def create_rounded_rect(self, canvas, x, y, width, height, radius, **kwargs):
        """Draw a rounded rectangle on a canvas"""
        # Draw the rounded rectangle
        points = [
            x + radius, y,
            x + width - radius, y,
            x + width, y,
            x + width, y + radius,
            x + width, y + height - radius,
            x + width, y + height,
            x + width - radius, y + height,
            x + radius, y + height,
            x, y + height,
            x, y + height - radius,
            x, y + radius,
            x, y
        ]
        return canvas.create_polygon(points, **kwargs, smooth=True)
    
    def _adjust_color(self, hex_color, adjustment):
        """Adjust a hex color by the given amount (positive=lighter, negative=darker)"""
        # Remove the hash from the color string
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Adjust the color
        r = max(0, min(255, r + adjustment))
        g = max(0, min(255, g + adjustment))
        b = max(0, min(255, b + adjustment))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}" 