import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True
from screeninfo import get_monitors
import json
import time
from style import AppStyle

class PhotoBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Picture Browser")
        self.folder_frames = []
        self.current_image_index = 0
        self.all_images = []
        self.selected_folder = None
        self.single_mode = True  # Default to single folder mode
        self.current_page = 0
        self.folders_per_page = 16
        self.rows = 4
        self.cols = 4
        self.last_render_time = 0
        self.zoom_factor = 1.0  # 默认缩放比例
        
        # Apply styling
        self.style = AppStyle(root)

        # Get screen dimensions and adjust for OS
        self.detect_screen_size()

        # Set main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.style.apply_styles_to_widget(self.main_frame, self.style.frame_style)

        # Create top menu bar
        self.create_top_menu_bar()

        # Add title and navigation at the top
        self.top_frame = tk.Frame(self.main_frame)
        self.top_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)
        self.style.apply_styles_to_widget(self.top_frame, self.style.nav_frame_style)

        # Add title
        self.title_label = tk.Label(self.top_frame, text="Picture Browser")
        self.title_label.pack(side=tk.LEFT, pady=10, padx=10)
        self.style.style_label(self.title_label, is_title=True)

        # Create container for folder frames
        self.folder_container = tk.Frame(self.main_frame)
        self.folder_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.style.apply_styles_to_widget(self.folder_container, self.style.folder_container_style)

        # Add and create navigation buttons at the top
        self.create_navigation()

        # Status bar at bottom
        self.status_bar = tk.Label(self.main_frame, text="Ready", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.style.style_label(self.status_bar)

        # Bind events
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Tab>", self.toggle_mode)
        self.root.bind("<Control-a>", self.add_folder)
        self.root.bind("<Delete>", self.delete_selected_folder)
        self.root.bind("<Control-s>", self.save_image)
        self.root.bind("<Button-3>", self.show_context_menu)
        self.root.bind("<Configure>", self.on_window_resize)
        self.root.bind("<Control-plus>", self.zoom_in)
        self.root.bind("<Control-minus>", self.zoom_out)
        self.root.bind("<Control-0>", self.reset_zoom)

        # Initialize context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="保存", command=self.save_image)
        self.context_menu.add_command(label="切换到全局模式", command=self.toggle_mode_from_context_menu)

        # Load application data if exists
        self.load_app_data()
        
        # Log startup to update log
        self.log_update("Application started")

        # Create folder status area
        self.create_folder_status_area()

    def create_top_menu_bar(self):
        """创建包含所有功能的菜单栏"""
        # 创建主菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="添加文件夹", command=self.add_folder, accelerator="Ctrl+A")
        self.file_menu.add_command(label="保存当前图片", command=self.save_image, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="设置目标文件夹", command=self.set_target_folder)
        self.file_menu.add_command(label="移除选中文件夹", command=self.delete_selected_folder, accelerator="Delete")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.root.quit)

    def set_target_folder(self):
        """Set the target folder for moving images"""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder = folder
            self.status_bar.config(text=f"目标文件夹已设置为: {folder}")
            # Log the action
            self.log_update(f"Target folder set: {folder}")
            
            # Save application data
            self.save_app_data()

    def show_shortcuts(self):
        """Display keyboard shortcuts help dialog"""
        shortcuts = """
        Keyboard Shortcuts:
        
        Ctrl+A: Add a new folder
        Delete: Remove selected folder
        Ctrl+S: Save current image
        Tab: Toggle between Single and Global mode
        ←: Previous image
        →: Next image
        Right-click: Show context menu
        """
        
        help_window = tk.Toplevel(self.root)
        help_window.title("Keyboard Shortcuts")
        help_window.geometry("400x300")
        
        text = tk.Text(help_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, shortcuts)
        text.config(state=tk.DISABLED)
        
        # Center window
        help_window.update_idletasks()
        width = help_window.winfo_width()
        height = help_window.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        help_window.geometry(f"+{x}+{y}")

    def show_about(self):
        """Display about dialog"""
        about_text = """
        Picture Browser
        
        A simple application for browsing images in multiple folders.
        
        Features:
        - Browse multiple image folders
        - Switch between single folder and global browsing modes
        - Save images to custom locations
        - Responsive layout adapts to window size
        
        Copyright © 2023
        """
        
        about_window = tk.Toplevel(self.root)
        about_window.title("About Picture Browser")
        about_window.geometry("400x300")
        
        text = tk.Text(about_window, wrap=tk.WORD)
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        text.insert(tk.END, about_text)
        text.config(state=tk.DISABLED)
        
        # Center window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (self.root.winfo_width() // 2) - (width // 2) + self.root.winfo_x()
        y = (self.root.winfo_height() // 2) - (height // 2) + self.root.winfo_y()
        about_window.geometry(f"+{x}+{y}")

    def on_window_resize(self, event=None):
        """Handle window resize events to update layout"""
        # Only process if this is a root window resize event
        if event and event.widget == self.root:
            # Update screen dimensions
            self.detect_screen_size()
            # Recalculate dimensions and refresh display
            self.recalculate_dimensions()
            self.display_folders()
            
    def detect_screen_size(self):
        """Detect screen dimensions and adjust for OS specifics"""
        # Get current window size instead of screen size
        self.screen_width = self.root.winfo_width()
        self.screen_height = self.root.winfo_height()
        
        # Make sure we have valid dimensions (on startup they might be 1)
        if self.screen_width <= 1:
            self.screen_width = 1024  # Default width
        if self.screen_height <= 1:
            self.screen_height = 768  # Default height
            
        # Calculate dimensions based on adaptive layout
        self.recalculate_dimensions()
        
    def recalculate_dimensions(self):
        """Calculate folder dimensions based on current page layout"""
        # Calculate padding and margins
        horizontal_padding = 40  # Total horizontal padding
        vertical_padding = 100   # Increased for top navigation
        
        # Calculate available space
        available_width = self.screen_width - horizontal_padding
        available_height = self.screen_height - vertical_padding
        
        # Ensure we're working with valid dimensions
        available_width = max(300, available_width)
        available_height = max(200, available_height)
        
        # Determine number of folders currently displayed
        folders_on_page = min(self.folders_per_page, 
                             len(self.folder_frames[self.current_page*self.folders_per_page:
                                                  (self.current_page+1)*self.folders_per_page]))
        
        # Determine layout
        if folders_on_page <= 4:
            self.cols = max(1, folders_on_page)  # Ensure cols is at least 1
            self.rows = 1 if folders_on_page > 0 else 0
        else:
            self.cols = 4
            self.rows = (folders_on_page + 3) // 4  # Ceiling division
            
        # Calculate folder dimensions with spacing
        self.folder_width = (available_width // max(1, self.cols)) - 20  # Ensure no division by zero, increased spacing
        self.folder_height = (available_height // max(1, self.rows)) - 20 if self.rows > 0 else available_height - 20

    def create_navigation(self):
        """Create navigation buttons at the top"""
        # Navigation buttons frame (right side)
        self.nav_frame = tk.Frame(self.top_frame)
        self.nav_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.style.apply_styles_to_widget(self.nav_frame, self.style.nav_frame_style)
        
        # Add folder button
        self.add_btn = tk.Button(self.nav_frame, text="Add Folder", command=self.add_folder)
        self.add_btn.pack(side=tk.LEFT, padx=5)
        self.style.style_button(self.add_btn)
        
        # Page navigation
        self.prev_page_btn = tk.Button(self.nav_frame, text="← Prev", command=self.prev_page)
        self.prev_page_btn.pack(side=tk.LEFT, padx=5)
        self.style.style_button(self.prev_page_btn)
        
        self.page_label = tk.Label(self.nav_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT, padx=5)
        self.style.style_label(self.page_label)
        
        self.next_page_btn = tk.Button(self.nav_frame, text="Next →", command=self.next_page)
        self.next_page_btn.pack(side=tk.LEFT, padx=5)
        self.style.style_button(self.next_page_btn)
        
        # Mode toggle button
        self.mode_btn = tk.Button(self.nav_frame, text="Toggle Mode", command=self.toggle_mode)
        self.mode_btn.pack(side=tk.LEFT, padx=5)
        self.style.style_button(self.mode_btn)
        
        # Update navigation state
        self.update_navigation()
        
    def update_navigation(self):
        """Update navigation buttons and page display"""
        total_pages = max(1, (len(self.folder_frames) + self.folders_per_page - 1) // self.folders_per_page)
        self.page_label.config(text=f"Page {self.current_page + 1}/{total_pages}")
        
        # Enable/disable navigation buttons
        self.prev_page_btn.config(state=tk.NORMAL if self.current_page > 0 else tk.DISABLED)
        self.next_page_btn.config(state=tk.NORMAL if self.current_page < total_pages - 1 else tk.DISABLED)

    def next_page(self):
        """Go to next page of folders"""
        total_pages = (len(self.folder_frames) + self.folders_per_page - 1) // self.folders_per_page
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.display_folders()
            self.update_navigation()
            self.log_update(f"Navigated to page {self.current_page + 1}")

    def prev_page(self):
        """Go to previous page of folders"""
        if self.current_page > 0:
            self.current_page -= 1
            self.display_folders()
            self.update_navigation()
            self.log_update(f"Navigated to page {self.current_page + 1}")

    def add_folder(self, event=None):
        """Add a new folder to the browser"""
        folder = filedialog.askdirectory()
        if folder:
            # Create frame object (not displayed yet)
            frame = tk.Frame(self.folder_container, relief=tk.SOLID, bd=2)
            self.style.style_frame(frame)
            
            # Canvas for image display
            canvas = tk.Canvas(frame)
            canvas.pack(fill=tk.BOTH, expand=True)
            self.style.style_canvas(canvas)

            # Filename and buttons frame
            bottom_frame = tk.Frame(frame)
            bottom_frame.pack(fill=tk.X, side=tk.BOTTOM)
            self.style.apply_styles_to_widget(bottom_frame, self.style.frame_style)

            # Display folder and image name
            image_paths = sorted(self.get_image_paths(folder))
            if image_paths:
                filename = os.path.basename(image_paths[0])
                folder_name = os.path.basename(folder)
                display_text = f"{folder_name}/{filename}"
            else:
                display_text = "No Images"

            # Show filename (with truncation)
            filename_label = tk.Label(bottom_frame, text=display_text, anchor="w")
            filename_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            self.style.style_label(filename_label)
            
            # Ensure the label will truncate with ellipsis if too long
            filename_label.bind('<Configure>', lambda e: self.truncate_label(filename_label, e.width-10))

            # Button frame for download and close buttons
            button_frame = tk.Frame(bottom_frame)
            button_frame.pack(side=tk.RIGHT)
            
            # Remove button
            remove_button = tk.Button(button_frame, text="Move", command=lambda f=folder: self.remove_images(f))
            remove_button.pack(side=tk.LEFT, padx=2)
            self.style.style_button(remove_button)
            
            # Download button with arrow symbol
            download_button = tk.Button(button_frame, text="↓", command=lambda img_path=image_paths[0] if image_paths else None: 
                                        self.save_specific_image(img_path))
            download_button.pack(side=tk.LEFT, padx=2)
            self.style.style_button(download_button)
            
            # Close button
            close_button = tk.Button(button_frame, text="X", command=lambda f=frame: self.remove_folder(f, folder))
            close_button.pack(side=tk.LEFT, padx=2)
            self.style.style_button(close_button)

            # Bind image click event
            canvas.bind("<Button-1>", lambda e, f=folder, fr=frame: self.select_folder(f, fr))

            # Store folder info but don't display yet
            self.folder_frames.append((frame, folder, image_paths, canvas, 0, filename_label, download_button))
            self.all_images.extend(image_paths)
            
            # Check if we need to go to a new page
            folders_count = len(self.folder_frames)
            new_page = (folders_count - 1) // self.folders_per_page
            if new_page > self.current_page:
                self.current_page = new_page
            
            # Update dimensions and display folders
            self.recalculate_dimensions()
            self.display_folders()
            self.update_navigation()
            
            # Automatically select the first image of the new folder
            if len(self.folder_frames) == 1:
                self.select_folder(folder, frame)
            
            # Log the action
            self.log_update(f"Added folder: {folder}")
            
            # Save application data
            self.save_app_data()
            
            # Update status
            self.status_bar.config(text=f"Added folder: {folder}")

    def remove_images(self, folder):
        """Move the currently displayed image from the specified folder to the target directory"""
        if not hasattr(self, 'target_folder') or not self.target_folder:
            messagebox.showwarning("Warning", "请先设置目标文件夹路径")
            return

        # Find the folder in folder_frames
        for i, (frame, fld, images, canvas, current_index, filename_label, download_button) in enumerate(self.folder_frames):
            if fld == folder:
                # Check if there are any images in the folder
                if not images:
                    messagebox.showwarning("Warning", "文件夹中没有图片")
                    return
                
                # Get the currently displayed image
                current_image_path = images[current_index]
                
                try:
                    # Move only the current image
                    new_path = os.path.join(self.target_folder, os.path.basename(current_image_path))
                    os.rename(current_image_path, new_path)
                    
                    # Remove the moved image from the images list
                    del images[current_index]
                    
                    # Update the display to show the next image (or previous if at end)
                    if current_index >= len(images):
                        current_index = max(0, len(images) - 1)
                    
                    # Update the display
                    if images:
                        self.display_image(canvas, images[current_index], filename_label)
                        # Update stored index
                        self.folder_frames[i] = (frame, fld, images, canvas, current_index, filename_label, download_button)
                    else:
                        # If no images left, remove the folder
                        self.remove_folder(frame, folder)
                    
                except Exception as e:
                    messagebox.showerror("Error", f"移动文件失败: {str(e)}")
                return
        
        messagebox.showwarning("Warning", "未找到指定的文件夹")

    def create_top_menu_bar(self):
        """创建包含所有功能的菜单栏"""
        # 创建主菜单栏
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        # 文件菜单
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="文件", menu=self.file_menu)
        self.file_menu.add_command(label="添加文件夹", command=self.add_folder, accelerator="Ctrl+A")
        self.file_menu.add_command(label="保存当前图片", command=self.save_image, accelerator="Ctrl+S")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="设置目标文件夹", command=self.set_target_folder)
        self.file_menu.add_command(label="移除选中文件夹", command=self.delete_selected_folder, accelerator="Delete")
        self.file_menu.add_separator()
        self.file_menu.add_command(label="退出", command=self.root.quit)

    def set_target_folder(self):
        """Set the target folder for moving images"""
        folder = filedialog.askdirectory()
        if folder:
            self.target_folder = folder
            self.status_bar.config(text=f"目标文件夹已设置为: {folder}")
            # Log the action
            self.log_update(f"Target folder set: {folder}")
            
            # Save application data
            self.save_app_data()

    def truncate_label(self, label, max_width):
        """Truncate label text if it's too long for available width"""
        text = label.cget("text")
        font = label.cget("font")
        
        # If text is already short, do nothing
        if label.winfo_reqwidth() <= max_width:
            return
            
        # Truncate and add ellipsis if needed
        while len(text) > 3:
            text = text[:-1]
            label.config(text=text + "...")
            label.update_idletasks()
            if label.winfo_reqwidth() <= max_width:
                break

    def display_folders(self):
        """Display folders for the current page with proper layout"""
        # Clear all existing folder frames
        for widget in self.folder_container.winfo_children():
            widget.grid_forget()
        
        # Calculate start and end indices for current page
        start_idx = self.current_page * self.folders_per_page
        end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
        
        # Display folders for current page
        for i in range(start_idx, end_idx):
            frame, folder, images, canvas, current_index, filename_label, download_button = self.folder_frames[i]
            
            # Calculate row and column for this folder
            row = (i - start_idx) // self.cols
            col = (i - start_idx) % self.cols
            
            # Configure frame size
            frame.config(width=self.folder_width, height=self.folder_height)
            canvas.config(width=self.folder_width, height=self.folder_height-25)
            
            # Position the frame in the grid
            frame.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            
            # Configure grid to allow folder expansion
            self.folder_container.grid_rowconfigure(row, weight=1)
            self.folder_container.grid_columnconfigure(col, weight=1)
            
            # Display the image if available
            if images:
                current_img_path = images[current_index]
                self.display_image(canvas, current_img_path, filename_label)
                
                # Update download button command with current image
                download_button.config(command=lambda img_path=current_img_path: self.save_specific_image(img_path))
            
            # Update selected folder highlight if needed
            if folder == self.selected_folder:
                self.style.style_frame(frame, is_selected=True)
            else:
                self.style.style_frame(frame, is_selected=False)

    def get_image_paths(self, folder):
        """Get sorted image paths from the folder"""
        try:
            image_files = [filename for filename in os.listdir(folder) 
                          if filename.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".bmp"))]
            image_files.sort()  # Sort filenames to ensure consistent order
            return [os.path.join(folder, filename) for filename in image_files]
        except (FileNotFoundError, PermissionError) as e:
            self.log_update(f"Error accessing folder {folder}: {str(e)}")
            return []

    def display_image(self, canvas, image_path, filename_label):
        """Display image on the canvas with optimization for performance"""
        # Measure performance
        start_time = time.time()
        
        try:
            # Clear previous image
            canvas.delete("all")
            
            # Check if image was displayed in the last 100ms (prevent too frequent updates)
            if time.time() - self.last_render_time < 0.1:
                time.sleep(0.1)  # Small delay to prevent UI freeze
                
            # Try to open the image
            img = Image.open(image_path)
            
            # Get canvas dimensions (these will be updated on window resize)
            canvas_width = canvas.winfo_width()
            canvas_height = canvas.winfo_height()
            
            # If canvas has no size yet, use the calculated folder dimensions
            if canvas_width <= 1 or canvas_height <= 1:
                canvas_width = self.folder_width
                canvas_height = self.folder_height
            
            # Calculate scaling to fit while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(canvas_width / img_width, canvas_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize with high-quality downsampling for thumbnails
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            img_tk = ImageTk.PhotoImage(img)
            
            # Center the image in the canvas
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            
            # Display the image
            canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=img_tk)
            canvas.image = img_tk  # Keep a reference to prevent garbage collection
            
        except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
            # Display error message if image can't be loaded
            canvas.create_text(canvas_width // 2, canvas_height // 2, 
                              text="Image not available", anchor=tk.CENTER)
            self.log_update(f"Error loading image {image_path}: {str(e)}")

        # Get the last three parts of the image path
        path_parts = os.path.normpath(image_path).split(os.sep)[-3:]
        display_text = "/".join(path_parts)

        # Update file path label
        filename_label.config(text=display_text)
        # Ensure text fits
        self.truncate_label(filename_label, filename_label.winfo_width()-10)
        
        # Update last render time
        self.last_render_time = time.time()
        
        # Log performance if it takes too long
        load_time = time.time() - start_time
        if load_time > 0.5:  # Log if loading takes more than 500ms
            self.log_update(f"Slow image load: {image_path} took {load_time:.2f}s")
            
        # Update status bar
        self.status_bar.config(text=f"Displaying: {display_text}")

    def save_specific_image(self, image_path):
        """Save the specified image to a new location"""
        if not image_path:
            self.log_update("No image available to save")
            self.status_bar.config(text="No image available to save")
            return
            
        try:
            # Extract the current image's filename
            default_filename = os.path.basename(image_path)
            
            # Ask user for the file path and name to save the image
            save_path = filedialog.asksaveasfilename(
                defaultextension=".jpg", 
                initialfile=default_filename,
                filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), 
                          ("GIF files", "*.gif"), ("All files", "*.*")]
            )
            
            if save_path:
                img = Image.open(image_path)
                img.save(save_path)
                self.log_update(f"Image saved to {save_path}")
                self.status_bar.config(text=f"Saved: {os.path.basename(save_path)}")
        except Exception as e:
            error_msg = f"Failed to save image: {str(e)}"
            self.log_update(error_msg)
            self.status_bar.config(text=error_msg)

    def remove_folder(self, frame, folder):
        """Remove a folder from the browser"""
        # Find and remove the folder
        for i, (frm, fld, _, _, _, _, _) in enumerate(self.folder_frames):
            if fld == folder:
                del self.folder_frames[i]
                break
                
        # Update all images list
        self.all_images = [img for frm, fld, imgs, _, _, _, _ in self.folder_frames for img in imgs]
        
        # Update if selected folder was removed
        if self.selected_folder == folder:
            self.selected_folder = None
            self.current_image_index = 0
        
        # Check if current page is now empty
        if self.current_page > 0 and self.current_page * self.folders_per_page >= len(self.folder_frames):
            self.current_page -= 1
            
        # Update the display
        self.recalculate_dimensions()
        self.display_folders()
        self.update_navigation()
        
        # Log the action
        self.log_update(f"Removed folder: {folder}")
        
        # Save application data
        self.save_app_data()

    def select_folder(self, folder, frame):
        """Select a folder for single folder mode"""
        # Remove highlight from previously selected folder
        if self.selected_folder:
            for fr, fld, _, _, _, _, _ in self.folder_frames:
                if fld == self.selected_folder:
                    self.style.style_frame(fr, is_selected=False)

        # Set new selected folder
        self.selected_folder = folder
        self.style.style_frame(frame, is_selected=True)

        # Restore the current index of the folder
        for fr, fld, images, canvas, current_index, filename_label, _ in self.folder_frames:
            if fld == folder:
                self.current_image_index = current_index
                self.display_image(canvas, images[self.current_image_index], filename_label)
                break
                
        # Log the action
        self.log_update(f"Selected folder: {folder}")

    def delete_selected_folder(self, event=None):
        """Delete the currently selected folder"""
        if self.selected_folder:
            for frame, folder, _, _, _, _, _ in self.folder_frames:
                if folder == self.selected_folder:
                    self.remove_folder(frame, folder)
                    break

    def toggle_mode(self, event=None):
        """Toggle between single folder and global mode"""
        self.single_mode = not self.single_mode
        mode = "Single Folder" if self.single_mode else "Global"
        self.log_update(f"Switched to {mode} Mode")
        self.update_context_menu_mode()

    def toggle_mode_from_context_menu(self):
        """Toggle mode from context menu"""
        self.toggle_mode()

    def update_context_menu_mode(self):
        """Update context menu mode text"""
        mode_label = "切换到全局模式" if self.single_mode else "切换到单文件夹模式"
        existing_label = "切换到全局模式" if self.single_mode else "切换到单文件夹模式"
        self.context_menu.entryconfigure(1, label=mode_label)

    def next_image(self, event=None):
        """Navigate to next image in selected folder or all folders"""
        if self.single_mode and self.selected_folder:
            # Find the selected folder
            for i, (frame, folder, images, canvas, current_index, filename_label, download_button) in enumerate(self.folder_frames):
                if folder == self.selected_folder and images:
                    # Calculate new index
                    self.current_image_index = (self.current_image_index + 1) % len(images)
                    # Get the new image path
                    new_image_path = images[self.current_image_index]
                    # Display the image
                    self.display_image(canvas, new_image_path, filename_label)
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, self.current_image_index, filename_label, download_button)
                    # Update download button
                    download_button.config(command=lambda img_path=new_image_path: self.save_specific_image(img_path))
                    break
        else:
            # In global mode, operate on every visible folder
            start_idx = self.current_page * self.folders_per_page
            end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
            
            for i in range(start_idx, end_idx):
                frame, folder, images, canvas, current_index, filename_label, download_button = self.folder_frames[i]
                if images:
                    # Calculate new index
                    new_index = (current_index + 1) % len(images)
                    # Get the new image path
                    new_image_path = images[new_index]
                    # Display the image
                    self.display_image(canvas, new_image_path, filename_label)
                    # Update download button
                    download_button.config(command=lambda img_path=new_image_path: self.save_specific_image(img_path))
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, new_index, filename_label, download_button)

    def prev_image(self, event=None):
        """Navigate to previous image in selected folder or all folders"""
        if self.single_mode and self.selected_folder:
            # Find the selected folder
            for i, (frame, folder, images, canvas, current_index, filename_label, download_button) in enumerate(self.folder_frames):
                if folder == self.selected_folder and images:
                    # Calculate new index
                    self.current_image_index = (self.current_image_index - 1) % len(images)
                    # Get the new image path
                    new_image_path = images[self.current_image_index]
                    # Display the image
                    self.display_image(canvas, new_image_path, filename_label)
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, self.current_image_index, filename_label, download_button)
                    # Update download button
                    download_button.config(command=lambda img_path=new_image_path: self.save_specific_image(img_path))
                    break
        else:
            # In global mode, operate on every visible folder
            start_idx = self.current_page * self.folders_per_page
            end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
            
            for i in range(start_idx, end_idx):
                frame, folder, images, canvas, current_index, filename_label, download_button = self.folder_frames[i]
                if images:
                    # Calculate new index
                    new_index = (current_index - 1) % len(images)
                    # Get the new image path
                    new_image_path = images[new_index]
                    # Display the image
                    self.display_image(canvas, new_image_path, filename_label)
                    # Update download button
                    download_button.config(command=lambda img_path=new_image_path: self.save_specific_image(img_path))
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, new_index, filename_label, download_button)

    def save_image(self, event=None):
        """Save the current image from selected folder to a new location"""
        if self.selected_folder:
            for _, folder, images, _, current_index, _, _ in self.folder_frames:
                if folder == self.selected_folder and images:
                    current_image_path = images[self.current_image_index]
                    self.save_specific_image(current_image_path)
                    break

    def show_context_menu(self, event):
        """Show the context menu at the cursor position"""
        self.context_menu.post(event.x_root, event.y_root)

    def save_app_data(self):
        """Save application data to a JSON file"""
        try:
            # Create a list of folder paths
            folder_data = [folder for _, folder, _, _, _, _, _ in self.folder_frames]
            
            # Create data dictionary
            app_data = {
                "folders": folder_data,
                "single_mode": self.single_mode,
                "selected_folder": self.selected_folder
            }
            
            # Save to JSON file
            with open("app_data.json", "w") as f:
                json.dump(app_data, f)
                
        except Exception as e:
            self.log_update(f"Failed to save application data: {str(e)}")

    def load_app_data(self):
        """Load application data from a JSON file"""
        try:
            if os.path.exists("app_data.json"):
                with open("app_data.json", "r") as f:
                    app_data = json.load(f)
                    
                # Restore folders
                for folder_path in app_data.get("folders", []):
                    if os.path.exists(folder_path):
                        # Create a simulated event to add the folder
                        self.add_folder()
                        # We need to immediately select the dialog result
                        # This isn't possible, so we'll just log it
                        self.log_update(f"Attempted to restore folder: {folder_path}")
                
                # Restore mode
                self.single_mode = app_data.get("single_mode", True)
                
                # Update UI
                self.update_context_menu_mode()
                self.display_folders()
                self.update_navigation()
                
        except Exception as e:
            self.log_update(f"Failed to load application data: {str(e)}")

    def log_update(self, message):
        """Log an update to the update log file"""
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open("update_log.txt", "a") as f:
                f.write(f"{timestamp} - {message}\n")
        except Exception as e:
            print(f"Failed to write to update log: {str(e)}")
            self.status_bar.config(text=f"Log error: {str(e)}")

    def create_folder_status_area(self):
        """创建文件夹状态显示区域"""
        self.folder_status_frame = tk.Frame(self.main_frame)
        self.folder_status_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=5)
        self.style.apply_styles_to_widget(self.folder_status_frame, self.style.frame_style)
        
        # 当前文件夹信息
        self.folder_info_label = tk.Label(self.folder_status_frame, text="未选择文件夹", anchor="w")
        self.folder_info_label.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.style.style_label(self.folder_info_label)
        
        # 图片导航工具条
        self.nav_toolbar = tk.Frame(self.folder_status_frame)
        self.nav_toolbar.pack(side=tk.RIGHT)
        
        # 图片缩放控件
        self.zoom_out_btn = tk.Button(self.nav_toolbar, text="−", width=2, command=self.zoom_out)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        self.style.style_button(self.zoom_out_btn)
        
        self.zoom_label = tk.Label(self.nav_toolbar, text="100%", width=5)
        self.zoom_label.pack(side=tk.LEFT, padx=2)
        self.style.style_label(self.zoom_label)
        
        self.zoom_in_btn = tk.Button(self.nav_toolbar, text="+", width=2, command=self.zoom_in)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        self.style.style_button(self.zoom_in_btn)
        
        self.zoom_reset_btn = tk.Button(self.nav_toolbar, text="1:1", width=3, command=self.reset_zoom)
        self.zoom_reset_btn.pack(side=tk.LEFT, padx=2)
        self.style.style_button(self.zoom_reset_btn)

    def zoom_in(self, event=None):
        """放大当前图片"""
        self.zoom_factor *= 1.2
        self.update_zoom_display()
        self.redisplay_current_images()
        self.log_update(f"放大图片: {self.zoom_factor:.2f}x")
        
    def zoom_out(self, event=None):
        """缩小当前图片"""
        self.zoom_factor /= 1.2
        # 防止过度缩小
        if self.zoom_factor < 0.1:
            self.zoom_factor = 0.1
        self.update_zoom_display()
        self.redisplay_current_images()
        self.log_update(f"缩小图片: {self.zoom_factor:.2f}x")
        
    def reset_zoom(self, event=None):
        """重置缩放到100%"""
        self.zoom_factor = 1.0
        self.update_zoom_display()
        self.redisplay_current_images()
        self.log_update("重置图片缩放")
        
    def update_zoom_display(self):
        """更新缩放百分比显示"""
        self.zoom_label.config(text=f"{int(self.zoom_factor * 100)}%")
        
    def redisplay_current_images(self):
        """使用当前缩放因子重新显示所有可见图片"""
        # 仅重绘可见的文件夹图片，避免不必要的计算
        if self.throttle_redisplay():
            # 重新显示当前页面的所有图片
            start_idx = self.current_page * self.folders_per_page
            end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
            
            for i in range(start_idx, end_idx):
                frame, folder, images, canvas, current_index, filename_label, download_button = self.folder_frames[i]
                if images:
                    current_img_path = images[current_index]
                    self.display_image(canvas, current_img_path, filename_label)

    def throttle_redisplay(self):
        """限制重绘频率，防止卡顿"""
        current_time = time.time()
        if current_time - self.last_render_time > 0.1:  # 限制为每100ms最多一次重绘
            self.last_render_time = current_time
            return True
        return False

    def refresh_folders(self):
        """刷新所有文件夹的图片列表"""
        updated_count = 0
        for i, (frame, folder, old_images, canvas, current_index, filename_label, download_button) in enumerate(self.folder_frames):
            # 重新获取图片列表
            new_images = sorted(self.get_image_paths(folder))
            if new_images != old_images:
                updated_count += 1
                # 更新图片列表
                self.folder_frames[i] = (frame, folder, new_images, canvas, 
                                         min(current_index, len(new_images)-1) if new_images else 0, 
                                         filename_label, download_button)
                
                # 如果有图片，更新显示
                if new_images:
                    idx = min(current_index, len(new_images)-1)
                    self.display_image(canvas, new_images[idx], filename_label)
        
        # 更新全局图片列表
        self.all_images = [img for _, _, imgs, _, _, _, _ in self.folder_frames for img in imgs]
        
        # 显示刷新结果
        self.status_bar.config(text=f"刷新完成: {updated_count}个文件夹内容已更新")
        self.log_update(f"刷新文件夹: {updated_count}个文件夹内容已更新")

    def clean_invalid_paths(self):
        """清除不存在的文件夹和图片路径"""
        invalid_folders = []
        
        # 检查每个文件夹是否仍然存在
        for i, (frame, folder, _, _, _, _, _) in enumerate(self.folder_frames):
            if not os.path.exists(folder):
                invalid_folders.append(i)
        
        # 从后向前删除无效的文件夹(避免索引变化影响)
        for idx in sorted(invalid_folders, reverse=True):
            frame, folder, _, _, _, _, _ = self.folder_frames[idx]
            del self.folder_frames[idx]
            # 如果这是当前选中的文件夹，取消选择
            if self.selected_folder == folder:
                self.selected_folder = None
                self.current_image_index = 0

        # 检查并更新所有图片列表，移除不存在的图片
        for i, (frame, folder, images, canvas, current_index, filename_label, download_button) in enumerate(self.folder_frames):
            valid_images = [img for img in images if os.path.exists(img)]
            if len(valid_images) != len(images):
                # 更新图片列表
                new_index = min(current_index, len(valid_images)-1) if valid_images else 0
                self.folder_frames[i] = (frame, folder, valid_images, canvas, new_index, filename_label, download_button)
                # 如果有图片，更新显示
                if valid_images:
                    self.display_image(canvas, valid_images[new_index], filename_label)
                else:
                    canvas.delete("all")
                    canvas.create_text(self.folder_width//2, self.folder_height//2, 
                                    text="No Images", anchor=tk.CENTER)
        
        # 更新全局图片列表
        self.all_images = [img for _, _, imgs, _, _, _, _ in self.folder_frames for img in imgs]
        
        # 重新显示文件夹
        self.recalculate_dimensions()
        self.display_folders()
        self.update_navigation()
        
        # 显示清理结果
        removed_count = len(invalid_folders)
        self.status_bar.config(text=f"清理完成: 已移除{removed_count}个无效文件夹")
        self.log_update(f"清理无效路径: 已移除{removed_count}个无效文件夹")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")  # Set initial window size
    app = PhotoBrowser(root)
    root.mainloop() 