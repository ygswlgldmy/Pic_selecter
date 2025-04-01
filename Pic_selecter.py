import os
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageTk, ImageFile, UnidentifiedImageError
ImageFile.LOAD_TRUNCATED_IMAGES = True
from screeninfo import get_monitors

class PhotoBrowser:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Browser")
        self.folder_frames = []
        self.current_image_index = 0
        self.all_images = []
        self.selected_folder = None
        self.single_mode = True  # Default to single folder mode

        # Get screen dimensions
        monitor = get_monitors()[0]
        self.screen_width = monitor.width
        self.screen_height = monitor.height

        # Default folder width and height
        self.folder_width = self.screen_width // 4 - 10
        self.folder_height = self.screen_height // 4 - 10

        # Set main frame
        self.main_frame = Frame(self.root)
        self.main_frame.pack(fill=BOTH, expand=True)

        # Add top control panel
        self.control_panel = Frame(self.root)
        self.control_panel.pack(fill=X, side=TOP)
        
        # Add folder button in the top control panel
        self.add_folder_button = Button(self.control_panel, text="Add Folder", command=self.add_folder)
        self.add_folder_button.pack(side=LEFT, padx=5, pady=5)
        
        # Toggle mode button in the top control panel
        self.toggle_mode_button = Button(self.control_panel, text="Toggle Mode", command=self.toggle_mode)
        self.toggle_mode_button.pack(side=LEFT, padx=5, pady=5)

        # Bind events
        self.root.bind("<Left>", self.prev_image)
        self.root.bind("<Right>", self.next_image)
        self.root.bind("<Tab>", self.toggle_mode)
        self.root.bind("<Control-a>", self.add_folder)
        self.root.bind("<Delete>", self.delete_selected_folder)
        self.root.bind("<Control-s>", self.save_image)  # Bind Ctrl+S to save image
        self.root.bind("<Button-3>", self.show_context_menu)  # Bind right-click to show context menu
        
        # Bind window resize event to update image sizing
        self.root.bind("<Configure>", self.on_window_resize)

        # Initialize context menu
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Save As", command=self.save_image)
        
        # Add Toggle Mode menu item
        self.toggle_mode_index = self.context_menu.add_command(
            label="Switch to Global Mode",
            command=self.toggle_mode_from_context_menu
        )

    def on_window_resize(self, event=None):
        """Update folder dimensions and resize images when window is resized"""
        # Only respond to actual window resize events, not other configure events
        if event and event.widget == self.root:
            # Update folder dimensions based on new window size
            new_width = self.root.winfo_width()
            new_height = self.root.winfo_height()
            
            # Only proceed if dimensions are valid (not during initial setup)
            if new_width > 100 and new_height > 100:
                # Calculate new folder dimensions
                self.folder_width = (new_width // 4) - 10
                self.folder_height = (new_height // 4) - 10
                
                # Resize all displayed images
                for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                    if images and current_index < len(images):
                        # Resize the frame
                        canvas.config(width=self.folder_width, height=self.folder_height)
                        # Redisplay the current image at the new size
                        self.display_image(canvas, images[current_index], filename_label)

    def add_folder(self, event=None):
        if len(self.folder_frames) >= 16:
            print("Cannot add more than 16 folders.")
            return

        folder = filedialog.askdirectory()
        if folder:
            frame = Frame(self.main_frame, relief=SOLID, bd=2, width=self.folder_width, height=self.folder_height)
            row = len(self.folder_frames) // 4
            col = len(self.folder_frames) % 4
            frame.grid(row=row, column=col, padx=5, pady=5)

            # Top control frame for filename and buttons
            top_frame = Frame(frame)
            top_frame.pack(fill=X, side=TOP)
            
            # Display folder and image name
            image_paths = sorted(self.get_image_paths(folder))
            if image_paths:
                filename = os.path.basename(image_paths[0])
                folder_name = os.path.basename(folder)
                display_text = f"{folder_name}/{filename}"
            else:
                display_text = "No Images"

            # Show filename
            filename_label = Label(top_frame, text=display_text)
            filename_label.pack(side=LEFT, padx=5)

            # Download button
            download_button = Button(top_frame, text="↓", command=lambda f=folder: self.save_specific_image(f))
            download_button.pack(side=RIGHT, padx=2)
            
            # Close button
            close_button = Button(top_frame, text="X", command=lambda f=frame: self.remove_folder(f, folder))
            close_button.pack(side=RIGHT, padx=2)

            # Canvas for image display
            canvas = Canvas(frame, width=self.folder_width, height=self.folder_height)
            canvas.pack(fill=BOTH, expand=True)

            # Bind image click event
            canvas.bind("<Button-1>", lambda e, f=folder, fr=frame: self.select_folder(f, fr))

            self.folder_frames.append((frame, folder, image_paths, canvas, 0, filename_label))
            self.all_images.extend(image_paths)

            # Automatically select the first image of the new folder
            if len(self.folder_frames) == 1:
                self.select_folder(folder, frame)
            else:
                self.current_image_index = 0

    def get_image_paths(self, folder):
        """Get sorted image paths from the folder"""
        image_files = [filename for filename in os.listdir(folder) if filename.lower().endswith((".png", ".jpg", ".jpeg"))]
        image_files.sort()  # Sort filenames to ensure consistent order
        return [os.path.join(folder, filename) for filename in image_files]

    def display_image(self, canvas, image_path, filename_label):
        """Display image on the canvas and update file path label with error handling."""
        try:
            # Try to open the image
            img = Image.open(image_path)
            
            # Calculate the aspect ratio to maintain proportions
            img_width, img_height = img.size
            aspect_ratio = img_width / img_height
            
            # Determine target dimensions to fit the canvas while maintaining aspect ratio
            target_width = self.folder_width
            target_height = self.folder_height
            
            # Adjust dimensions to maintain aspect ratio
            if img_width / target_width > img_height / target_height:
                # Width is the limiting factor
                new_width = target_width
                new_height = int(new_width / aspect_ratio)
            else:
                # Height is the limiting factor
                new_height = target_height
                new_width = int(new_height * aspect_ratio)
            
            # Resize image to fit canvas while maintaining aspect ratio
            img = img.resize((new_width, new_height), Image.LANCZOS)
            
            img_tk = ImageTk.PhotoImage(img)
            
            # Clear the canvas
            canvas.delete("all")
            
            # Calculate position to center the image on the canvas
            x_position = (target_width - new_width) // 2
            y_position = (target_height - new_height) // 2
            
            # Create the image centered on the canvas
            canvas.create_image(x_position, y_position, anchor=NW, image=img_tk)
            canvas.image = img_tk
            
        except UnidentifiedImageError:
            # If the image cannot be opened, display a placeholder or clear the canvas
            canvas.delete("all")  # Clear the canvas
            # Optionally, display a message or placeholder (empty space for now)
            canvas.create_text(self.folder_width // 2, self.folder_height // 2, text="Image not available", anchor=CENTER)

        # Get the last three parts of the image path
        path_parts = os.path.normpath(image_path).split(os.sep)[-3:]
        display_text = "/".join(path_parts)

        # Update file path label
        filename_label.config(text=display_text)

    def remove_folder(self, frame, folder):
        for i, (frm, fld, _, _, _, _) in enumerate(self.folder_frames):
            if fld == folder:
                del self.folder_frames[i]
                break
        self.all_images = [img for frm, fld, imgs, _, _, _ in self.folder_frames for img in imgs]
        frame.destroy()
        if self.selected_folder == folder:
            self.selected_folder = None
            self.current_image_index = 0
            self.display_current_image()

    def select_folder(self, folder, frame):
        if self.selected_folder:
            for fr, fld, _, _, _, _ in self.folder_frames:
                if fld == self.selected_folder:
                    fr.config(relief=SOLID, bd=2, highlightbackground="white", highlightthickness=0)

        self.selected_folder = folder
        frame.config(relief=RIDGE, bd=5, highlightbackground="blue", highlightthickness=2)

        # Restore the current index of the folder
        for fr, fld, images, canvas, current_index, filename_label in self.folder_frames:
            if fld == folder:
                self.current_image_index = current_index  # Restore the current image index
                self.display_image(canvas, images[self.current_image_index], filename_label)  # Update image and file path
                break

    def delete_selected_folder(self, event=None):
        if self.selected_folder:
            for frame, folder, _, _, _, _ in self.folder_frames:
                if folder == self.selected_folder:
                    self.remove_folder(frame, folder)
                    break

    def toggle_mode(self, event=None):
        self.single_mode = not self.single_mode
        mode = "Single Folder" if self.single_mode else "Global"
        print(f"Switched to {mode} Mode")
        self.update_context_menu_mode()

    def toggle_mode_from_context_menu(self):
        self.toggle_mode()

    def update_context_menu_mode(self):
        mode_label = "Switch to Global Mode" if self.single_mode else "Switch to Single Folder Mode"
        self.context_menu.entryconfigure(self.toggle_mode_index, label=mode_label)

    def next_image(self, event=None):
        if self.single_mode and self.selected_folder:
            for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                if folder == self.selected_folder:
                    self.current_image_index = (self.current_image_index + 1) % len(images)
                    self.display_image(canvas, images[self.current_image_index], filename_label)
                    for i, (frm, fld, imgs, cnv, idx, lbl) in enumerate(self.folder_frames):
                        if fld == folder:
                            self.folder_frames[i] = (frm, fld, imgs, cnv, self.current_image_index, lbl)
                    break
        else:
            # In global mode, operate on every folder
            for i, (frame, folder, images, canvas, current_index, filename_label) in enumerate(self.folder_frames):
                if images:
                    current_index = (current_index + 1) % len(images)
                    self.display_image(canvas, images[current_index], filename_label)
                    # Update current index
                    self.folder_frames[i] = (frame, folder, images, canvas, current_index, filename_label)

    def prev_image(self, event=None):
        if self.single_mode and self.selected_folder:
            for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                if folder == self.selected_folder:
                    self.current_image_index = (self.current_image_index - 1) % len(images)
                    self.display_image(canvas, images[self.current_image_index], filename_label)
                    for i, (frm, fld, imgs, cnv, idx, lbl) in enumerate(self.folder_frames):
                        if fld == folder:
                            self.folder_frames[i] = (frm, fld, imgs, cnv, self.current_image_index, lbl)
                    break
        else:
            # In global mode, operate on every folder
            for i, (frame, folder, images, canvas, current_index, filename_label) in enumerate(self.folder_frames):
                if images:
                    current_index = (current_index - 1) % len(images)
                    self.display_image(canvas, images[current_index], filename_label)
                    # Update current index
                    self.folder_frames[i] = (frame, folder, images, canvas, current_index, filename_label)

    def save_image(self, event=None):
        if self.selected_folder:
            for _, folder, images, _, current_index, _ in self.folder_frames:
                if folder == self.selected_folder and images:
                    current_image_path = images[self.current_image_index]
                    # Extract the current image's filename
                    default_filename = os.path.basename(current_image_path)
                    
                    # Ask user for the file path and name to save the image, pre-fill the filename
                    save_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                                            initialfile=default_filename,  # Pre-fill with current filename
                                                            filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
                    if save_path:
                        try:
                            img = Image.open(current_image_path)
                            img.save(save_path)  # Save the image
                            print(f"Image saved to {save_path}")
                        except Exception as e:
                            print(f"Failed to save the image: {e}")
                    break

    def display_current_image(self):
        if self.selected_folder:
            for frame, folder, images, canvas, current_index, filename_label in self.folder_frames:
                if folder == self.selected_folder and images:
                    self.display_image(canvas, images[self.current_image_index], filename_label)
                    break

    def show_context_menu(self, event):
        self.context_menu.post(event.x_root, event.y_root)

    def save_specific_image(self, folder):
        """Save the current image from the specified folder"""
        for _, fld, images, _, current_index, _ in self.folder_frames:
            if fld == folder and images and current_index < len(images):
                current_image_path = images[current_index]
                # Extract the current image's filename
                default_filename = os.path.basename(current_image_path)
                
                # Ask user for the file path and name to save the image, pre-fill the filename
                save_path = filedialog.asksaveasfilename(defaultextension=".jpg", 
                                                        initialfile=default_filename,  # Pre-fill with current filename
                                                        filetypes=[("JPEG files", "*.jpg"), ("PNG files", "*.png")])
                if save_path:
                    try:
                        img = Image.open(current_image_path)
                        img.save(save_path)  # Save the image
                        print(f"Image saved to {save_path}")
                    except Exception as e:
                        print(f"Failed to save the image: {e}")
                break


if __name__ == "__main__":
    root = Tk()
    app = PhotoBrowser(root)
    root.mainloop()
