# Walkthrough: Gallery Plugin (CHE-15)

## Summary

### The Problem
Zensical users needed a way to automate the creation of image and video galleries without manually uploading files or writing individual Markdown pages. The goal was to source content directly from Google Drive, where folders represent galleries and files within those folders (images and videos) are automatically rendered.

### The Solution
We implemented a robust Gallery Plugin that integrates with the Google Drive API. At build time, the plugin scans a specified root folder, identifies subfolders as individual galleries, and extracts media metadata (including descriptions for captions). It then generates Zensical-compatible Markdown files with rich YAML frontmatter, which are rendered using a dedicated, responsive gallery template.

### Key Changes
- **Core Plugin Logic:** A new `gallery_plugin/` package handles authenticated API requests, recursive discovery, and local metadata caching for performance.
- **Dynamic Generation:** A synchronization script converts Google Drive structures into a structured `docs/galleries/` hierarchy.
- **Responsive UI:** A custom Jinja2 template in `overrides/gallery.html` provides a modern grid layout with support for images (`.png`, `.jpg`) and HTML5 video playback (`.mp4`).
- **Developer Flexibility:** The system fully supports Zensical's override mechanism, allowing developers to easily customize the gallery UI.

## 🎬 Visual Storyboard

### Walkthrough Animation
![Walkthrough GIF](./walkthrough.gif)

### 1. Nature Gallery
Successfully generated from Google Drive folder "Nature". Shows responsive grid with mixed media and captions.
![Nature Gallery](./walkthrough/01_nature_gallery.png)

### 2. Travel Gallery
Successfully generated from Google Drive folder "Travel". Demonstrates automatic title and metadata extraction.
![Travel Gallery](./walkthrough/02_travel_gallery.png)
