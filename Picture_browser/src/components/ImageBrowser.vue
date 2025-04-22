<template>
  <div class="image-browser">
    <div class="toolbar">
      <button @click="openFolder">打开文件夹</button>
      <input type="text" v-model="targetFolder" placeholder="设置目标文件夹路径" />
      <button @click="moveImages">移动</button>
      <button @click="removeImages">移除</button>
      <button @click="downloadImages">下载</button>
    </div>
    <div class="image-grid">
      <div v-for="(image, index) in images" :key="index" class="image-item">
        <img :src="image.url" alt="image" />
      </div>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      images: [],
      targetFolder: ''
    };
  },
  methods: {
    openFolder() {
      // 打开文件夹的逻辑
    },
    moveImages() {
      if (!this.targetFolder) {
        alert('请先设置目标文件夹路径');
        return;
      }
      this.images.forEach(image => {
        // 假设image.path是图像的完整路径
        const newPath = this.targetFolder + '/' + image.name;
        // 调用后端API或使用Node.js的fs模块来移动文件
        this.moveImage(image.path, newPath);
      });
      this.images = []; // 清空当前展示的图像
    },
    removeImages() {
      if (!this.targetFolder) {
        alert('请先设置目标文件夹路径');
        return;
      }
      this.images.forEach(image => {
        // 假设image.path是图像的完整路径
        const newPath = this.targetFolder + '/' + image.name;
        // 调用后端API或使用Node.js的fs模块来移动文件
        this.moveImage(image.path, newPath);
      });
      this.images = []; // 清空当前展示的图像
    },
    downloadImages() {
      // 下载图像的逻辑
    },
    moveImage(oldPath, newPath) {
      // 调用后端API移动文件
      fetch('/api/move-image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ oldPath, newPath }),
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('Image moved successfully');
        } else {
          console.error('Failed to move image');
        }
      })
      .catch(error => {
        console.error('Error:', error);
      });
    }
  }
};
</script>

<style scoped>
.image-browser {
  display: flex;
  flex-direction: column;
}
.toolbar {
  margin-bottom: 10px;
}
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 10px;
}
.image-item img {
  width: 100%;
  height: auto;
}
</style>