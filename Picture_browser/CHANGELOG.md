# Changelog

All notable changes to the Picture Browser application will be documented in this file.

## [1.0.0] - 2023-09-20

### Added

- Adaptive folder grid layout that changes based on number of folders (1x1, 2x1, 3x1, 4x1, 4x2, etc.)
- Pagination system for handling more than 16 folders
- OS-specific adjustments for macOS (Dock) and Windows 11 (Taskbar)
- Performance optimizations to prevent UI lag:
  - Throttling for rapid image changes
  - Proper image scaling using high-quality algorithms
  - Center-positioning of images within frames
- Application state persistence using JSON storage
- Detailed logging system for troubleshooting
- Improved error handling for file/folder access issues
- Support for more image formats (BMP, GIF)
- Clean, modern UI with navigation controls
- README with comprehensive usage instructions

### Changed

- Reorganized folder display code for better maintainability
- Improved the image loading and display process
- Enhanced context menu with clearer options
- More responsive UI with better keyboard shortcuts
- Improved handling of screen dimensions
- Better error messages when images cannot be loaded

### Fixed

- Fixed potential memory leaks with image loading
- Improved error handling for invalid or corrupted images
- Fixed layout issues when resizing the application window
- Addressed potential file path issues across different operating systems 

请将文件夹内部结构中的底部栏置于顶部，并修复终端出现的异常，输出产品原型图到单独日志中并且在原来的更新日志中更新新版本的日志，目前版本放缩功能存在异常