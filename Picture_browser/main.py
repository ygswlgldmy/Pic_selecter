import os
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True
from screeninfo import get_monitors
import platform
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
        
        # Apply styling
        self.style = AppStyle(root)

        # Get screen dimensions and adjust for OS
        self.detect_screen_size()

        # Set main frame
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        self.style.apply_styles_to_widget(self.main_frame, self.style.frame_style)

        # Create container for folder frames
        self.folder_container = tk.Frame(self.main_frame)
        self.folder_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.style.apply_styles_to_widget(self.folder_container, self.style.folder_container_style)

        # Create navigation frame
        self.nav_frame = tk.Frame(self.main_frame)
        self.nav_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=5)
        self.style.apply_styles_to_widget(self.nav_frame, self.style.nav_frame_style)

        # Add title
        self.title_label = tk.Label(self.main_frame, text="Picture Browser")
        self.title_label.pack(side=tk.TOP, pady=10)
        self.style.style_label(self.title_label, is_title=True)

        # Add and create navigation buttons
        self.create_navigation()

        # Bind events
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Tab>", self.toggle_mode)
        self.root.bind("<Control-a>", self.add_folder)
        self.root.bind("<Delete>", self.delete_selected_folder)
        self.root.bind("<Control-s>", self.save_image)
        self.root.bind("<Button-3>", self.show_context_menu)

        # Initialize context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Save As", command=self.save_image)
        self.toggle_mode_index = self.context_menu.add_command(
            label="Switch to Global Mode",
            command=self.toggle_mode_from_context_menu
        )

        # Load application data if exists
        self.load_app_data()
        
        # Log startup to update log
        self.log_update("Application started")

    def detect_screen_size(self):
        """Detect screen dimensions and adjust for OS specifics"""
        monitor = get_monitors()[0]
        self.screen_width = monitor.width
        self.screen_height = monitor.height
        
        # Adjust for OS-specific elements
        os_type = platform.system()
        if os_type == "Darwin":  # macOS
            # Account for Dock height (estimated at 70px)
            self.screen_height -= 70
        elif os_type == "Windows":
            # Account for taskbar height (estimated at 40px)
            self.screen_height -= 40
            
        # Calculate dimensions based on adaptive layout
        self.recalculate_dimensions()
        
    def recalculate_dimensions(self):
        """Calculate folder dimensions based on current page layout"""
        # Calculate padding and margins
        horizontal_padding = 20  # Total horizontal padding
        vertical_padding = 20    # Total vertical padding
        
        # Calculate available space
        available_width = self.screen_width - horizontal_padding
        available_height = self.screen_height - vertical_padding - 50  # 50px for navigation
        
        # Calculate folder dimensions based on number of folders displayed
        folders_on_page = len(self.folder_frames[self.current_page*self.folders_per_page:
                                              (self.current_page+1)*self.folders_per_page])
        
        # Determine layout
        if folders_on_page <= 4:
            self.cols = max(1, folders_on_page)  # Ensure cols is at least 1
            self.rows = 1 if folders_on_page > 0 else 0
        else:
            self.cols = 4
            self.rows = (folders_on_page + 3) // 4  # Ceiling division
            
        # Calculate folder dimensions with spacing
        self.folder_width = (available_width // max(1, self.cols)) - 10  # Ensure no division by zero
        self.folder_height = (available_height // max(1, self.rows)) - 10 if self.rows > 0 else available_height - 10

    def create_navigation(self):
        """Create navigation buttons"""
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
        self.mode_btn.pack(side=tk.RIGHT, padx=5)
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

            # Filename and close button frame
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

            # Show filename
            filename_label = tk.Label(bottom_frame, text=display_text, anchor="w")
            filename_label.pack(side=tk.LEFT, padx=5)
            self.style.style_label(filename_label)

            # Close button
            close_button = tk.Button(bottom_frame, text="X", command=lambda f=frame: self.remove_folder(f, folder))
            close_button.pack(side=tk.RIGHT, padx=5)
            self.style.style_button(close_button)

            # Bind image click event
            canvas.bind("<Button-1>", lambda e, f=folder, fr=frame: self.select_folder(f, fr))

            # Store folder info but don't display yet
            self.folder_frames.append((frame, folder, image_paths, canvas, 0, filename_label))
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
            frame, folder, images, canvas, current_index, filename_label = self.folder_frames[i]
            
            # Calculate row and column for this folder
            row = (i - start_idx) // self.cols
            col = (i - start_idx) % self.cols
            
            # Configure frame size
            frame.config(width=self.folder_width, height=self.folder_height)
            canvas.config(width=self.folder_width, height=self.folder_height)
            
            # Position the frame in the grid
            frame.grid(row=row, column=col, padx=5, pady=5)
            
            # Display the image if available
            if images:
                self.display_image(canvas, images[current_index], filename_label)
            
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
            
            # Calculate scaling to fit while maintaining aspect ratio
            img_width, img_height = img.size
            scale = min(self.folder_width / img_width, self.folder_height / img_height)
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            # Resize with high-quality downsampling for thumbnails
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Convert to PhotoImage
            img_tk = ImageTk.PhotoImage(img)
            
            # Center the image in the canvas
            x_offset = (self.folder_width - new_width) // 2
            y_offset = (self.folder_height - new_height) // 2
            
            # Display the image
            canvas.create_image(x_offset, y_offset, anchor=tk.NW, image=img_tk)
            canvas.image = img_tk  # Keep a reference to prevent garbage collection
            
        except (UnidentifiedImageError, FileNotFoundError, OSError) as e:
            # Display error message if image can't be loaded
            canvas.create_text(self.folder_width // 2, self.folder_height // 2, 
                              text="Image not available", anchor=tk.CENTER)
            self.log_update(f"Error loading image {image_path}: {str(e)}")

        # Get the last three parts of the image path
        path_parts = os.path.normpath(image_path).split(os.sep)[-3:]
        display_text = "/".join(path_parts)

        # Update file path label
        filename_label.config(text=display_text)
        
        # Update last render time
        self.last_render_time = time.time()
        
        # Log performance if it takes too long
        load_time = time.time() - start_time
        if load_time > 0.5:  # Log if loading takes more than 500ms
            self.log_update(f"Slow image load: {image_path} took {load_time:.2f}s")

    def remove_folder(self, frame, folder):
        """Remove a folder from the browser"""
        # Find and remove the folder
        for i, (frm, fld, _, _, _, _) in enumerate(self.folder_frames):
            if fld == folder:
                del self.folder_frames[i]
                break
                
        # Update all images list
        self.all_images = [img for frm, fld, imgs, _, _, _ in self.folder_frames for img in imgs]
        
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
            for fr, fld, _, _, _, _ in self.folder_frames:
                if fld == self.selected_folder:
                    self.style.style_frame(fr, is_selected=False)

        # Set new selected folder
        self.selected_folder = folder
        self.style.style_frame(frame, is_selected=True)

        # Restore the current index of the folder
        for fr, fld, images, canvas, current_index, filename_label in self.folder_frames:
            if fld == folder:
                self.current_image_index = current_index
                self.display_image(canvas, images[self.current_image_index], filename_label)
                break
                
        # Log the action
        self.log_update(f"Selected folder: {folder}")

    def delete_selected_folder(self, event=None):
        """Delete the currently selected folder"""
        if self.selected_folder:
            for frame, folder, _, _, _, _ in self.folder_frames:
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
        mode_label = "Switch to Global Mode" if self.single_mode else "Switch to Single Folder Mode"
        self.context_menu.entryconfigure(self.toggle_mode_index, label=mode_label)

    def next_image(self, event=None):
        """Navigate to next image in selected folder or all folders"""
        if self.single_mode and self.selected_folder:
            # Find the selected folder
            for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                if folder == self.selected_folder and images:
                    # Calculate new index
                    self.current_image_index = (self.current_image_index + 1) % len(images)
                    # Display the image
                    self.display_image(canvas, images[self.current_image_index], filename_label)
                    # Update stored index
                    for i, (frm, fld, imgs, cnv, idx, lbl) in enumerate(self.folder_frames):
                        if fld == folder:
                            self.folder_frames[i] = (frm, fld, imgs, cnv, self.current_image_index, lbl)
                    break
        else:
            # In global mode, operate on every visible folder
            start_idx = self.current_page * self.folders_per_page
            end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
            
            for i in range(start_idx, end_idx):
                frame, folder, images, canvas, current_index, filename_label = self.folder_frames[i]
                if images:
                    # Calculate new index
                    new_index = (current_index + 1) % len(images)
                    # Display the image
                    self.display_image(canvas, images[new_index], filename_label)
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, new_index, filename_label)

    def prev_image(self, event=None):
        """Navigate to previous image in selected folder or all folders"""
        if self.single_mode and self.selected_folder:
            # Find the selected folder
            for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                if folder == self.selected_folder and images:
                    # Calculate new index
                    self.current_image_index = (self.current_image_index - 1) % len(images)
                    # Display the image
                    self.display_image(canvas, images[self.current_image_index], filename_label)
                    # Update stored index
                    for i, (frm, fld, imgs, cnv, idx, lbl) in enumerate(self.folder_frames):
                        if fld == folder:
                            self.folder_frames[i] = (frm, fld, imgs, cnv, self.current_image_index, lbl)
                    break
        else:
            # In global mode, operate on every visible folder
            start_idx = self.current_page * self.folders_per_page
            end_idx = min(start_idx + self.folders_per_page, len(self.folder_frames))
            
            for i in range(start_idx, end_idx):
                frame, folder, images, canvas, current_index, filename_label = self.folder_frames[i]
                if images:
                    # Calculate new index
                    new_index = (current_index - 1) % len(images)
                    # Display the image
                    self.display_image(canvas, images[new_index], filename_label)
                    # Update stored index
                    self.folder_frames[i] = (frame, folder, images, canvas, new_index, filename_label)

    def save_image(self, event=None):
        """Save the current image to a new location"""
        if self.selected_folder:
            for _, folder, images, _, current_index, _ in self.folder_frames:
                if folder == self.selected_folder and images:
                    current_image_path = images[self.current_image_index]
                    # Extract the current image's filename
                    default_filename = os.path.basename(current_image_path)
                    
                    # Ask user for the file path and name to save the image
                    save_path = filedialog.asksaveasfilename(
                        defaultextension=".jpg", 
                        initialfile=default_filename,
                        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png"), 
                                  ("GIF files", "*.gif"), ("All files", "*.*")]
                    )
                    
                    if save_path:
                        try:
                            img = Image.open(current_image_path)
                            img.save(save_path)
                            self.log_update(f"Image saved to {save_path}")
                        except Exception as e:
                            self.log_update(f"Failed to save image: {str(e)}")
                    break

    def show_context_menu(self, event):
        """Show the context menu at the cursor position"""
        self.context_menu.post(event.x_root, event.y_root)

    def save_app_data(self):
        """Save application data to a JSON file"""
        try:
            # Create a list of folder paths
            folder_data = [folder for _, folder, _, _, _, _ in self.folder_frames]
            
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


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")  # Set initial window size
    app = PhotoBrowser(root)
    root.mainloop() 