import os
import json
from pathlib import Path
from .drive import DriveClient

class GalleryPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        self.root_folder_id = self.config.get("root_folder_id")
        self.docs_dir = Path(self.config.get("docs_dir", "docs"))
        self.galleries_dir = self.docs_dir / "galleries"
        self.cache_path = Path(".cache/gallery_metadata.json")
        self.drive_client = DriveClient(
            credentials_path=self.config.get("credentials_path"),
            token_path=self.config.get("token_path", ".cache/token.pickle")
        )

    def load_cache(self):
        """Loads metadata from the local cache file."""
        if self.cache_path.exists():
            with open(self.cache_path, "r") as f:
                return json.load(f)
        return None

    def run(self, force_refresh=False):
        """Main execution flow for the plugin."""
        if not self.root_folder_id:
            print("Warning: root_folder_id not configured for GalleryPlugin.")
            return

        galleries = None
        if not force_refresh:
            galleries = self.load_cache()
            if galleries:
                print("Loaded galleries from cache.")

        if not galleries:
            print(f"Syncing galleries from root folder ID: {self.root_folder_id}")
            self.drive_client.authenticate()
            
            # Phase 2: Discovery
            galleries = self.discover_galleries()
            
            # Phase 2.3: Caching
            self.save_cache(galleries)
        
        # Phase 3: Generation
        self.generate_files(galleries)

    def discover_galleries(self):
        """Scans the root folder for subfolders and their media files."""
        folders = self.drive_client.list_folders(self.root_folder_id)
        galleries = []
        
        for folder in folders:
            gallery_name = folder.get("name")
            print(f"Found gallery: {gallery_name}")
            
            files = self.drive_client.list_files(folder.get("id"))
            media = []
            
            for f in files:
                mime = f.get("mimeType", "")
                name = f.get("name", "")
                
                # Supported extensions from PRD: .png, .jpg, .mp4
                is_supported = (
                    name.lower().endswith((".png", ".jpg", ".mp4")) or
                    mime.startswith(("image/", "video/"))
                )
                
                if is_supported:
                    media.append({
                        "id": f.get("id"),
                        "name": name,
                        "description": f.get("description", ""),
                        "mimeType": mime,
                        "webContentLink": f.get("webContentLink"),
                        "webViewLink": f.get("webViewLink")
                    })
            
            galleries.append({
                "id": folder.get("id"),
                "name": gallery_name,
                "description": folder.get("description", ""),
                "media": media
            })
            
        return galleries

    def save_cache(self, galleries):
        """Saves discovered metadata to a local cache file."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.cache_path, "w") as f:
            json.dump(galleries, f, indent=2)

    def generate_files(self, galleries):
        """Generates Markdown files for each gallery in the docs directory."""
        self.galleries_dir.mkdir(parents=True, exist_ok=True)
        
        for gallery in galleries:
            # Create a safe filename from the gallery name
            safe_name = "".join(c if c.isalnum() else "_" for c in gallery["name"]).lower()
            file_path = self.galleries_dir / f"{safe_name}.md"
            
            content = self.render_gallery_markdown(gallery)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Generated gallery file: {file_path}")

    def render_gallery_markdown(self, gallery):
        """Renders the Markdown content for a single gallery."""
        # We'll use frontmatter to store the gallery data and the default template will handle it
        markdown = f"""---
title: "{gallery['name']}"
description: "{gallery['description']}"
gallery_id: "{gallery['id']}"
layout: "gallery"
media:
"""
        for item in gallery["media"]:
            markdown += f"  - id: \"{item['id']}\"\n"
            markdown += f"    name: \"{item['name']}\"\n"
            markdown += f"    description: \"{item['description']}\"\n"
            markdown += f"    mimeType: \"{item['mimeType']}\"\n"
            markdown += f"    url: \"{item['webContentLink'] or item['webViewLink']}\"\n"
            
        markdown += f"""---

# {gallery['name']}

{gallery['description']}

<!-- The actual gallery UI will be rendered by the 'gallery' layout/template -->
"""
        return markdown

def main():
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib

    # Load config from zensical.toml
    config_path = Path("zensical.toml")
    if not config_path.exists():
        print("zensical.toml not found.")
        return

    with open(config_path, "rb") as f:
        full_config = tomllib.load(f)
    
    # Extract gallery plugin config
    # Zensical config structure: [plugins.gallery]
    plugin_config = full_config.get("plugins", {}).get("gallery", {})
    
    # We also need docs_dir from project config
    project_config = full_config.get("project", {})
    plugin_config["docs_dir"] = project_config.get("docs_dir", "docs")

    plugin = GalleryPlugin(plugin_config)
    plugin.run()

if __name__ == "__main__":
    main()
