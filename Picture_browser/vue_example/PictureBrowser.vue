<template>
  <div class="picture-browser">
    <header class="app-header">
      <h1>Picture Browser</h1>
    </header>
    
    <main class="main-content">
      <div class="folder-container">
        <div 
          v-for="(folder, index) in displayedFolders" 
          :key="folder.id" 
          class="folder-frame"
          :class="{ selected: folder.id === selectedFolderId }"
          @click="selectFolder(folder.id)"
        >
          <div class="image-container">
            <img 
              v-if="folder.images.length > 0" 
              :src="folder.images[folder.currentIndex]" 
              :alt="getImageName(folder.images[folder.currentIndex])"
              class="folder-image"
            />
            <div v-else class="no-images">
              No Images
            </div>
          </div>
          
          <div class="folder-footer">
            <span class="folder-path">{{ getFolderPathDisplay(folder) }}</span>
            <button @click.stop="removeFolder(folder.id)" class="close-btn">×</button>
          </div>
        </div>
      </div>
      
      <div v-if="totalFolders === 0" class="empty-state">
        <p>No folders added yet. Click "Add Folder" to get started.</p>
      </div>
    </main>
    
    <footer class="app-footer">
      <div class="controls-left">
        <button @click="addFolder" class="control-btn primary">
          Add Folder
        </button>
        
        <div class="pagination-controls">
          <button 
            @click="prevPage" 
            class="control-btn" 
            :disabled="currentPage === 0"
          >
            ← Prev
          </button>
          <span class="page-indicator">Page {{ currentPage + 1 }}/{{ totalPages }}</span>
          <button 
            @click="nextPage" 
            class="control-btn" 
            :disabled="currentPage >= totalPages - 1"
          >
            Next →
          </button>
        </div>
      </div>
      
      <div class="controls-right">
        <button @click="toggleMode" class="control-btn">
          {{ singleMode ? 'Switch to Global Mode' : 'Switch to Single Folder Mode' }}
        </button>
        <button @click="saveCurrentImage" class="control-btn" :disabled="!canSaveImage">
          Save Image
        </button>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'PictureBrowser',
  data() {
    return {
      folders: [],
      selectedFolderId: null,
      singleMode: true,
      currentPage: 0,
      foldersPerPage: 16
    }
  },
  computed: {
    totalFolders() {
      return this.folders.length;
    },
    totalPages() {
      return Math.max(1, Math.ceil(this.totalFolders / this.foldersPerPage));
    },
    displayedFolders() {
      const start = this.currentPage * this.foldersPerPage;
      const end = Math.min(start + this.foldersPerPage, this.totalFolders);
      return this.folders.slice(start, end);
    },
    selectedFolder() {
      return this.folders.find(folder => folder.id === this.selectedFolderId) || null;
    },
    canSaveImage() {
      return this.selectedFolder && this.selectedFolder.images.length > 0;
    }
  },
  methods: {
    addFolder() {
      // In a real implementation, this would open a native file dialog
      // For demonstration, we'll simulate adding a folder
      const newFolder = {
        id: Date.now().toString(),
        name: `Folder ${this.folders.length + 1}`,
        path: `/Users/example/Pictures/Folder${this.folders.length + 1}`,
        images: [
          // Sample image paths
          `/sample/image1.jpg`,
          `/sample/image2.jpg`,
          `/sample/image3.jpg`
        ],
        currentIndex: 0
      };
      
      this.folders.push(newFolder);
      
      // Auto-select if it's the first folder
      if (this.folders.length === 1) {
        this.selectFolder(newFolder.id);
      }
      
      // Navigate to the page where the new folder is shown
      this.currentPage = Math.floor((this.folders.length - 1) / this.foldersPerPage);
      
      this.logUpdate(`Added folder: ${newFolder.path}`);
    },
    
    removeFolder(folderId) {
      const index = this.folders.findIndex(folder => folder.id === folderId);
      if (index !== -1) {
        const folderPath = this.folders[index].path;
        this.folders.splice(index, 1);
        
        // Update selected folder if the removed folder was selected
        if (this.selectedFolderId === folderId) {
          this.selectedFolderId = this.folders.length > 0 ? this.folders[0].id : null;
        }
        
        // Check if current page is now empty
        if (this.currentPage > 0 && this.currentPage * this.foldersPerPage >= this.folders.length) {
          this.currentPage--;
        }
        
        this.logUpdate(`Removed folder: ${folderPath}`);
      }
    },
    
    selectFolder(folderId) {
      this.selectedFolderId = folderId;
      const folder = this.folders.find(f => f.id === folderId);
      if (folder) {
        this.logUpdate(`Selected folder: ${folder.path}`);
      }
    },
    
    nextPage() {
      if (this.currentPage < this.totalPages - 1) {
        this.currentPage++;
        this.logUpdate(`Navigated to page ${this.currentPage + 1}`);
      }
    },
    
    prevPage() {
      if (this.currentPage > 0) {
        this.currentPage--;
        this.logUpdate(`Navigated to page ${this.currentPage + 1}`);
      }
    },
    
    toggleMode() {
      this.singleMode = !this.singleMode;
      const mode = this.singleMode ? 'Single Folder' : 'Global';
      this.logUpdate(`Switched to ${mode} Mode`);
    },
    
    nextImage() {
      if (this.singleMode && this.selectedFolder) {
        // In single mode, navigate only the selected folder
        const folder = this.selectedFolder;
        folder.currentIndex = (folder.currentIndex + 1) % folder.images.length;
      } else {
        // In global mode, navigate all visible folders
        this.displayedFolders.forEach(folder => {
          if (folder.images.length > 0) {
            folder.currentIndex = (folder.currentIndex + 1) % folder.images.length;
          }
        });
      }
    },
    
    prevImage() {
      if (this.singleMode && this.selectedFolder) {
        // In single mode, navigate only the selected folder
        const folder = this.selectedFolder;
        folder.currentIndex = (folder.currentIndex - 1 + folder.images.length) % folder.images.length;
      } else {
        // In global mode, navigate all visible folders
        this.displayedFolders.forEach(folder => {
          if (folder.images.length > 0) {
            folder.currentIndex = (folder.currentIndex - 1 + folder.images.length) % folder.images.length;
          }
        });
      }
    },
    
    saveCurrentImage() {
      if (this.selectedFolder && this.selectedFolder.images.length > 0) {
        const imagePath = this.selectedFolder.images[this.selectedFolder.currentIndex];
        // In a real implementation, this would open a native save dialog
        this.logUpdate(`Saved image: ${imagePath}`);
      }
    },
    
    getImageName(path) {
      return path.split('/').pop();
    },
    
    getFolderPathDisplay(folder) {
      if (folder.images.length === 0) return "No Images";
      
      const imageName = this.getImageName(folder.images[folder.currentIndex]);
      return `${folder.name}/${imageName}`;
    },
    
    logUpdate(message) {
      console.log(`${new Date().toISOString()} - ${message}`);
      // In a real implementation, this would write to a log file
    }
  },
  mounted() {
    // Set up keyboard shortcuts
    window.addEventListener('keydown', (e) => {
      switch(e.key) {
        case 'ArrowLeft':
          this.prevImage();
          break;
        case 'ArrowRight':
          this.nextImage();
          break;
        case 'Tab':
          e.preventDefault();
          this.toggleMode();
          break;
      }
    });
    
    // Load saved application data
    this.logUpdate('Application started');
  },
  beforeDestroy() {
    // Clean up event listeners
    window.removeEventListener('keydown');
  }
}
</script>

<style scoped>
.picture-browser {
  display: flex;
  flex-direction: column;
  height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  color: #333;
  background-color: #f5f5f5;
}

.app-header {
  padding: 1rem;
  background-color: #ffffff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  z-index: 10;
}

.app-header h1 {
  margin: 0;
  font-weight: 500;
  font-size: 1.5rem;
  color: #333;
  text-align: center;
}

.main-content {
  flex: 1;
  padding: 1rem;
  overflow: auto;
}

.folder-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-auto-rows: 250px;
  gap: 1rem;
}

.folder-frame {
  display: flex;
  flex-direction: column;
  border: 1px solid #ddd;
  border-radius: 8px;
  overflow: hidden;
  background-color: white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: all 0.2s ease;
}

.folder-frame:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.folder-frame.selected {
  border: 2px solid #0066CC;
  box-shadow: 0 0 0 2px rgba(0, 102, 204, 0.3);
}

.image-container {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background-color: #f5f5f5;
}

.folder-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.no-images {
  color: #999;
  font-style: italic;
}

.folder-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem;
  background-color: #f9f9f9;
  border-top: 1px solid #eee;
}

.folder-path {
  font-size: 0.85rem;
  color: #666;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.close-btn {
  background: none;
  border: none;
  color: #999;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0 0.3rem;
  line-height: 1;
  border-radius: 50%;
  transition: all 0.2s;
}

.close-btn:hover {
  color: #ff3b30;
  background-color: rgba(255, 59, 48, 0.1);
}

.app-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #ffffff;
  box-shadow: 0 -2px 4px rgba(0, 0, 0, 0.05);
}

.controls-left, .controls-right {
  display: flex;
  align-items: center;
}

.pagination-controls {
  display: flex;
  align-items: center;
  margin-left: 1rem;
}

.page-indicator {
  margin: 0 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.control-btn {
  background-color: #f1f1f1;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  margin: 0 0.25rem;
  color: #333;
  transition: all 0.2s;
}

.control-btn:hover {
  background-color: #e1e1e1;
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.control-btn.primary {
  background-color: #0066CC;
  color: white;
}

.control-btn.primary:hover {
  background-color: #0055AA;
}

.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #999;
  font-style: italic;
  text-align: center;
  padding: 2rem;
}

@media (max-width: 768px) {
  .app-footer {
    flex-direction: column;
    gap: 1rem;
  }
  
  .controls-left, .controls-right {
    width: 100%;
    justify-content: center;
  }
}

/* OS-specific adjustments */
@media screen and (min-height: 800px) {
  /* Adjust for macOS dock */
  .picture-browser {
    height: calc(100vh - 70px);
  }
}

/* Adjust for Windows taskbar */
@media screen and (min-height: 800px) and (min-width: 800px) {
  .picture-browser {
    height: calc(100vh - 40px);
  }
}
</style> 