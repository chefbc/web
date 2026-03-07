import os
import json
from pathlib import Path
import sys

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from gallery_plugin.plugin import GalleryPlugin
from gallery_plugin.drive import DriveClient

class MockDriveClient(DriveClient):
    def authenticate(self):
        print("Mock Authentication successful.")

    def list_folders(self, parent_id):
        return [
            {"id": "folder1", "name": "Nature", "description": "Beautiful nature photos"},
            {"id": "folder2", "name": "Travel", "description": "My travel adventures"}
        ]

    def list_files(self, folder_id):
        if folder_id == "folder1":
            return [
                {"id": "img1", "name": "forest.jpg", "description": "Deep forest", "mimeType": "image/jpeg", "webContentLink": "https://example.com/forest.jpg", "webViewLink": None},
                {"id": "img2", "name": "mountain.png", "description": "High mountain", "mimeType": "image/png", "webContentLink": "https://example.com/mountain.png", "webViewLink": None},
                {"id": "vid1", "name": "river.mp4", "description": "Flowing river", "mimeType": "video/mp4", "webContentLink": "https://example.com/river.mp4", "webViewLink": None}
            ]
        elif folder_id == "folder2":
            return [
                {"id": "img3", "name": "paris.jpg", "description": "Eiffel Tower", "mimeType": "image/jpeg", "webContentLink": "https://example.com/paris.jpg", "webViewLink": None},
                {"id": "img4", "name": "london.jpg", "description": "Big Ben", "mimeType": "image/jpeg", "webContentLink": "https://example.com/london.jpg", "webViewLink": None}
            ]
        return []

def test_plugin():
    print("Starting GalleryPlugin test with MockDriveClient...")
    
    # Configure the plugin
    config = {
        "root_folder_id": "mock_root",
        "docs_dir": "docs"
    }
    
    plugin = GalleryPlugin(config)
    # Inject the mock client
    plugin.drive_client = MockDriveClient()
    
    # Run the plugin
    plugin.run(force_refresh=True)
    
    # Verify file generation
    galleries_dir = Path("docs/galleries")
    if not galleries_dir.exists():
        print("FAILED: docs/galleries/ does not exist.")
        return

    expected_files = ["nature.md", "travel.md"]
    for expected in expected_files:
        if (galleries_dir / expected).exists():
            print(f"SUCCESS: Found {expected}")
        else:
            print(f"FAILED: {expected} not found.")

    # Verify cache
    cache_path = Path(".cache/gallery_metadata.json")
    if cache_path.exists():
        print("SUCCESS: Cache file created.")
    else:
        print("FAILED: Cache file not found.")

if __name__ == "__main__":
    test_plugin()
