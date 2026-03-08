import os
import yaml
import json
from pathlib import Path

class AnnouncementsPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        self.announcements_file = Path(self.config.get("announcements_file", "announcements.yaml"))
        self.docs_dir = Path(self.config.get("docs_dir", "docs"))
        self.output_dir = self.docs_dir / "assets"
        self.output_file = self.output_dir / "announcements.json"

    def run(self):
        """Main execution flow for the plugin."""
        if not self.announcements_file.exists():
            print(f"Announcements file {self.announcements_file} not found. Skipping AnnouncementsPlugin.")
            return

        print(f"Reading announcements from {self.announcements_file}")
        with open(self.announcements_file, "r") as f:
            try:
                announcements = yaml.safe_load(f)
                if not announcements:
                    announcements = []
            except yaml.YAMLError as e:
                print(f"Error parsing {self.announcements_file}: {e}")
                return

        # Phase 3: Generation
        self.generate_json(announcements)

    def generate_json(self, announcements):
        """Generates a JSON file containing all announcements."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # We save all announcements because client-side filtering will handle the display
        with open(self.output_file, "w") as f:
            json.dump(announcements, f, indent=2)
        print(f"Generated announcements JSON: {self.output_file}")

def main():
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            print("Error: tomllib or tomli not found. Please install tomli for Python < 3.11.")
            return

    # Load config from zensical.toml
    config_path = Path("zensical.toml")
    if not config_path.exists():
        print("zensical.toml not found.")
        return

    with open(config_path, "rb") as f:
        full_config = tomllib.load(f)
    
    # Extract announcements plugin config
    plugin_config = full_config.get("plugins", {}).get("announcements", {})
    
    # We also need docs_dir from project config
    project_config = full_config.get("project", {})
    plugin_config["docs_dir"] = project_config.get("docs_dir", "docs")

    plugin = AnnouncementsPlugin(plugin_config)
    plugin.run()

if __name__ == "__main__":
    main()
