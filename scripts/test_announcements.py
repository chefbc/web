import unittest
from pathlib import Path
import json
import yaml
import sys
import os

# Add the project root to sys.path so we can import announcements_plugin
sys.path.append(str(Path(__file__).resolve().parent.parent))

from announcements_plugin.plugin import AnnouncementsPlugin

class TestAnnouncementsPlugin(unittest.TestCase):
    def setUp(self):
        self.test_yaml = Path("test_announcements.yaml")
        self.test_docs = Path("test_docs")
        self.test_output = self.test_docs / "assets" / "announcements.json"
        
        # Create test data
        self.test_docs.mkdir(parents=True, exist_ok=True)
        with open(self.test_yaml, "w") as f:
            yaml.dump([
                {"text": "Test 1", "start_date": "2026-03-01", "end_date": "2026-03-10"},
                {"html": "<strong>Test 2</strong>", "start_date": "2026-03-05", "end_date": "2026-03-15"}
            ], f)

    def tearDown(self):
        if self.test_yaml.exists():
            self.test_yaml.unlink()
        if self.test_output.exists():
            self.test_output.unlink()
        if (self.test_docs / "assets").exists():
            (self.test_docs / "assets").rmdir()
        if self.test_docs.exists():
            self.test_docs.rmdir()

    def test_run(self):
        config = {
            "announcements_file": str(self.test_yaml),
            "docs_dir": str(self.test_docs)
        }
        plugin = AnnouncementsPlugin(config)
        plugin.run()
        
        self.assertTrue(self.test_output.exists())
        with open(self.test_output, "r") as f:
            data = json.load(f)
            self.assertEqual(len(data), 2)
            self.assertEqual(data[0]["text"], "Test 1")
            self.assertEqual(data[1]["html"], "<strong>Test 2</strong>")

if __name__ == "__main__":
    unittest.main()
