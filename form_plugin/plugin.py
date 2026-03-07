import os
import yaml
from pathlib import Path

class FormPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        self.forms_dir = Path(self.config.get("forms_dir", "forms"))
        self.docs_dir = Path(self.config.get("docs_dir", "docs"))
        self.output_dir = self.docs_dir / "forms"

    def run(self):
        """Main execution flow for the plugin."""
        if not self.forms_dir.exists():
            print(f"Forms directory {self.forms_dir} not found. Skipping FormPlugin.")
            return

        # Find all YAML files in forms_dir
        form_files = list(self.forms_dir.glob("*.yaml")) + list(self.forms_dir.glob("*.yml"))
        
        if not form_files:
            print(f"No form configuration files found in {self.forms_dir}.")
            return

        forms = []
        for form_file in form_files:
            print(f"Found form configuration: {form_file}")
            with open(form_file, "r") as f:
                try:
                    form_config = yaml.safe_load(f)
                    if form_config:
                        form_config["_source_file"] = str(form_file)
                        forms.append(form_config)
                except yaml.YAMLError as e:
                    print(f"Error parsing {form_file}: {e}")

        # Phase 3: Generation
        self.generate_files(forms)

    def generate_files(self, forms):
        """Generates Markdown files for each form in the docs directory."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Cleanup orphaned files
        existing_files = set(self.output_dir.glob("*.md"))
        generated_files = set()
        
        for form in forms:
            # Create a safe filename from the source file name
            source_file = Path(form.get("_source_file", "unknown"))
            safe_name = source_file.stem
            file_path = self.output_dir / f"{safe_name}.md"
            generated_files.add(file_path)
            
            content = self.render_form_markdown(form)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Generated form file: {file_path}")
            
        # Delete files that were not generated in this run
        for orphaned_file in existing_files - generated_files:
            orphaned_file.unlink()
            print(f"Deleted orphaned form file: {orphaned_file}")

    def render_form_markdown(self, form):
        """Renders the Markdown content for a single form."""
        # Map configuration to Markdown frontmatter
        frontmatter = {
            "title": form.get("title", "Form"),
            "template": "form.html",
            "form_config": {
                "webhook_url": form.get("webhook_url"),
                "on_success": form.get("on_success", {"type": "message", "value": "Thank you for your submission!"}),
                "fields": form.get("fields", []),
                "recaptcha_site_key": os.getenv("RECAPTCHA_SITE_KEY", ""),
            }
        }
        
        # Copy other top-level keys if any
        for key, value in form.items():
            if key not in ["title", "layout", "form_config", "_source_file"]:
                frontmatter["form_config"][key] = value

        markdown = f"---\n{yaml.dump(frontmatter, sort_keys=False)}---\n\n"
        markdown += f"# {form.get('title', 'Form')}\n\n"
        if form.get("description"):
            markdown += f"{form.get('description')}\n\n"
            
        markdown += "<!-- The actual form UI will be rendered by the 'form' layout/template -->\n"
        return markdown

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
    
    # Extract form plugin config
    plugin_config = full_config.get("plugins", {}).get("form", {})
    
    # We also need docs_dir from project config
    project_config = full_config.get("project", {})
    plugin_config["docs_dir"] = project_config.get("docs_dir", "docs")

    plugin = FormPlugin(plugin_config)
    plugin.run()

if __name__ == "__main__":
    main()
