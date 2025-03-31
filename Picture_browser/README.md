# Picture Browser

A simple yet powerful application for browsing and viewing images from multiple folders.

## Features

- Add multiple image folders and browse through their contents
- Adaptive grid layout that adjusts based on the number of folders (1x1, 2x1, 3x1, 4x1, 4x2, etc.)
- Pagination system for more than 16 folders
- OS-specific adjustments for macOS and Windows 11
- Performance optimizations to prevent UI lag
- Session persistence (remembers folders between runs)
- Single folder mode or global browsing mode

## Requirements

- Python 3.6 or higher
- Required packages:
  - tkinter
  - Pillow (PIL)
  - screeninfo
  
## Installation

1. Ensure Python 3.6+ is installed on your system
2. Install the required packages:
   ```
   pip install pillow screeninfo
   ```
3. Run the application:
   ```
   python updated_main.py
   ```

## Usage

### Adding Folders

- Click the "Add Folder" button or press `Ctrl+A`
- Select a folder containing images from the dialog

### Navigation

- Use the left and right arrow keys to navigate between images
- Click on a folder to select it in single folder mode
- Use "Prev" and "Next" buttons to navigate between pages when you have more than 16 folders

### Modes

- Toggle between "Single Folder" and "Global" modes by pressing `Tab` or clicking the "Toggle Mode" button
  - In Single Folder mode, arrow keys navigate through images in the selected folder only
  - In Global mode, arrow keys navigate through images in all visible folders simultaneously

### Saving Images

- Press `Ctrl+S` or right-click and select "Save As" to save the current image to a new location

### Removing Folders

- Press the "X" button on a folder to remove it
- Select a folder and press `Delete` to remove the selected folder

## Keyboard Shortcuts

- `Left Arrow`: Previous image
- `Right Arrow`: Next image
- `Tab`: Toggle between Single Folder and Global modes
- `Ctrl+A`: Add a new folder
- `Delete`: Delete the selected folder
- `Ctrl+S`: Save the current image to a new location
- `Right Click`: Show context menu

## Customization

The application automatically adjusts to your screen resolution and operating system.

## Troubleshooting

If you encounter any issues, check the `update_log.txt` file for detailed information about what happened and when.

## Future Migration to Vue.js

A Vue.js version of the application is planned for future development. The Vue version will offer several advantages:

- Modern, component-based architecture
- Improved responsiveness and performance
- Better cross-platform compatibility
- Easier to extend and maintain
- More modern UI with transitions and animations
- Support for mobile devices

An example Vue component implementation can be found in the `vue_example` directory, which demonstrates how the application will look and function once migrated.

To run the Vue version in the future:

1. Install Node.js and npm
2. Install Vue CLI: `npm install -g @vue/cli`
3. Run the development server: `npm run serve` 