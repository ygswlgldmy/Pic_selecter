# Photo_selecter

## 介绍

Photo_selecter 是一个基于 Python 的Windows桌面应用程序，使用 `Tkinter` 实现图片浏览功能。用户可以通过该程序添加多个图片文件夹，并在其中浏览、管理图片。该应用支持多文件夹模式以及单文件夹模式切换，用户还可以通过快捷键控制图片切换、保存图片等操作。 
这个程序适用于从多个图像中进行筛选的场景，解决了传统方法需要在各个文件夹中切换频繁切换的问题

## 功能特性

1. **添加文件夹**: 用户可以添加最多 16 个文件夹，每个文件夹会自动显示第一张图片。
2. **图片浏览**: 支持通过键盘左/右键切换图片浏览，用户可以通过tab键在单文件夹模式(左右键仅切换一个文件夹中图片)和全局模式(同时切换所有展示的文件夹中图片)之间切换。
3. **删除文件夹**: 可删除已选中的展示文件夹。
4. **图片保存**: 可以通过右键或快捷键保存当前图片到指定目录。
5. **快捷键支持**:
   - `Ctrl + A`: 添加文件夹
   - `键盘左/右键`: 切换图片
   - `Tab`: 在单文件夹模式和全局模式之间切换
   - `Delete`: 删除选中的文件夹
   - `Ctrl + S`: 保存当前选中图片
   - `右键点击`: 显示图片保存的上下文菜单，点击Save as可保存当前选中的图片
   - `左键点击`: 选中点击的文件夹

### 环境配置

1. 安装必要的 Python 库：
   ```bash
   pip install Pillow screeninfo
