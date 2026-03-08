import re
import yaml
import json
from pathlib import Path
from markdown.extensions import Extension
from markdown.preprocessors import Preprocessor

class BusinessExtension(Extension):
    def __init__(self, **kwargs):
        self.config = {
            'business_data': [{}, 'Business data dictionary'],
        }
        super().__init__(**kwargs)
        if not self.config['business_data'][0]:
             self.config['business_data'][0] = load_business_data()

    def extendMarkdown(self, md):
        # Register with high priority to ensure it runs before other extensions
        md.preprocessors.register(BusinessPreprocessor(md, self.getConfigs()), 'business', 175)

class BusinessPreprocessor(Preprocessor):
    def __init__(self, md, config):
        super().__init__(md)
        self.business_data = config.get('business_data', {})
        self.locations = self.business_data.get('locations', [])
        # Create a lookup map for locations by ID
        self.location_map = {loc.get('id'): loc for loc in self.locations if 'id' in loc}
        self.default_location = self.locations[0] if self.locations else {}
        self.schema_injected = False

    def run(self, lines):
        new_lines = []
        # Regex to match {% business [location_id] "field" %} or {% business "field" %}
        pattern = re.compile(r'\{%\s*business\s+(?:["\'](?P<id>[^"\']+)["\']\s+)?["\'](?P<field>[^"\']+)["\']\s*%\}')

        for line in lines:
            def replace_shortcode(match):
                loc_id = match.group('id')
                field = match.group('field')
                
                location = self.location_map.get(loc_id) if loc_id else self.default_location
                
                if not location:
                    return f"<!-- Business location '{loc_id or 'default'}' not found -->"
                
                if field == 'map':
                    embed_id = location.get('google_map_embed_id')
                    if not embed_id:
                        return "<!-- Map embed ID missing -->"
                    return (
                        f'<div class="business-map-container" style="position: relative; padding-bottom: 56.25%; height: 0; overflow: hidden; max-width: 100%; margin: 1em 0;">'
                        f'<iframe src="https://www.google.com/maps/embed?pb={embed_id}" '
                        f'width="600" height="450" style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: 0;" '
                        f'allowfullscreen="" loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>'
                        f'</div>'
                    )
                
                if field == 'address':
                    addr = location.get('address', {})
                    if isinstance(addr, dict):
                        parts = [
                            addr.get('street'),
                            addr.get('city'),
                            f"{addr.get('state', '')} {addr.get('postal_code', '')}".strip(),
                            addr.get('country')
                        ]
                        return ", ".join([p for p in parts if p])
                    return str(addr)

                if field == 'hours':
                    hours = location.get('hours', [])
                    if isinstance(hours, list):
                        return "<br>".join([f"{h.get('days')}: {h.get('opens')}-{h.get('closes')}" for h in hours])
                    return str(hours)

                val = location.get(field)
                if val is None:
                    return f"<!-- Field '{field}' not found in location '{location.get('id', 'default')}' -->"
                return str(val)

            new_lines.append(pattern.sub(replace_shortcode, line))
        
        # Task 4.0: Schema injection if enabled and not already injected for this file
        if not self.schema_injected and self.business_data.get('inject_schema', True) and self.locations:
            schema_json = generate_local_business_schema(self.locations)
            new_lines.append(f'\n<script type="application/ld+json">\n{json.dumps(schema_json, indent=2)}\n</script>\n')
            self.schema_injected = True
            
        return new_lines

def generate_local_business_schema(locations):
    """Generate Schema.org LocalBusiness JSON-LD."""
    if not locations:
        return {}
    
    schema_list = []
    for loc in locations:
        addr = loc.get('address', {})
        hours = loc.get('hours', [])
        
        item = {
            "@context": "https://schema.org",
            "@type": "LocalBusiness",
            "name": loc.get('name'),
            "email": loc.get('email'),
            "telephone": loc.get('phone'),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": addr.get('street'),
                "addressLocality": addr.get('city'),
                "addressRegion": addr.get('state'),
                "postalCode": addr.get('postal_code'),
                "addressCountry": addr.get('country')
            }
        }
        
        if hours:
            opening_hours = []
            for h in hours:
                opening_hours.append(f"{h.get('days')} {h.get('opens')}-{h.get('closes')}")
            item["openingHours"] = opening_hours
            
        schema_list.append(item)
    
    return schema_list[0] if len(schema_list) == 1 else schema_list

def load_business_data():
    """Load business data from business.yaml or zensical.toml."""
    # Check business.yaml
    paths = [Path("business.yaml"), Path("../../../business.yaml")]
    for p in paths:
        if p.exists():
            with open(p, "r") as f:
                return yaml.safe_load(f)
    
    # Check zensical.toml
    config_paths = [Path("zensical.toml"), Path("../../../zensical.toml")]
    for cp in config_paths:
        if cp.exists():
            try:
                import tomllib
            except ImportError:
                try:
                    import tomli as tomllib
                except ImportError:
                    return {}
            
            with open(cp, "rb") as f:
                config = tomllib.load(f)
                if "project" in config:
                    config = config["project"]
                return config.get("plugins", {}).get("business", {}) or config.get("extra", {}).get("business", {})
            
    return {}

def makeExtension(**kwargs):
    return BusinessExtension(**kwargs)

if __name__ == "__main__":
    data = load_business_data()
    print("Loaded Business Data:")
    print(yaml.dump(data))
