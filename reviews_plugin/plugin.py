import os
import json
import yaml
from pathlib import Path
from .client import GooglePlacesClient, ReviewCache

class ReviewsPlugin:
    def __init__(self, config=None):
        self.config = config or {}
        self.place_id = self.config.get("place_id")
        self.max_reviews = self.config.get("max_reviews", 5)
        self.min_rating_filter = float(self.config.get("min_rating_filter", 4.0))
        self.cache_expiry = self.config.get("cache_expiry", 24) # in hours
        self.docs_dir = Path(self.config.get("docs_dir", "docs"))
        self.cache_path = Path(".cache/reviews_metadata.json")
        self.reviews_file = self.docs_dir / "reviews.md"
        
        # Load API key from environment
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        self.client = GooglePlacesClient(self.api_key, self.place_id)
        self.cache = ReviewCache(self.cache_path, self.cache_expiry)

    def run(self, force_refresh=False):
        """Main execution flow for the plugin."""
        if not self.place_id:
            print("Warning: place_id not configured for ReviewsPlugin.")
            return

        reviews = None
        if not force_refresh:
            reviews = self.cache.get()
            if reviews:
                print("ReviewsPlugin: Loaded reviews from cache.")

        if not reviews:
            print(f"ReviewsPlugin: Syncing reviews from Google for place_id: {self.place_id}")
            if not self.api_key:
                print("Warning: GOOGLE_MAPS_API_KEY not set. Skipping review sync.")
                return

            # Phase 2: Implementation of API client
            raw_reviews = self.client.fetch_reviews()
            reviews = self.client.filter_reviews(
                raw_reviews, 
                min_rating=self.min_rating_filter, 
                max_count=self.max_reviews
            )
            
            # Phase 2.3: Caching
            self.cache.set(reviews)
        
        # Phase 3: Generation
        self.generate_files(reviews)

    def generate_files(self, reviews):
        """Generates the reviews.md file in the docs directory."""
        if not reviews:
            print("ReviewsPlugin: No reviews found or filtered. Skipping file generation.")
            return

        self.docs_dir.mkdir(parents=True, exist_ok=True)
        
        frontmatter = {
            "title": "Reviews",
            "description": "What our customers are saying about us on Google.",
            "layout": "reviews",
            "reviews": reviews
        }
        
        content = f"---\n{yaml.dump(frontmatter, sort_keys=False)}---\n\n"
        content += "# Customer Reviews\n\n"
        content += "We are proud of our customer feedback! Here are some of our latest reviews from Google.\n"
        
        with open(self.reviews_file, "w") as f:
            f.write(content)
        
        print(f"ReviewsPlugin: Generated reviews file: {self.reviews_file}")

def main():
    try:
        import tomllib
    except ImportError:
        try:
            import tomli as tomllib
        except ImportError:
            # Fallback for systems without tomllib or tomli
            return

    # Load config from zensical.toml
    config_path = Path("zensical.toml")
    if not config_path.exists():
        print("zensical.toml not found.")
        return

    with open(config_path, "rb") as f:
        full_config = tomllib.load(f)
    
    # Extract reviews plugin config
    plugin_config = full_config.get("plugins", {}).get("reviews", {})
    
    # We also need docs_dir from project config
    project_config = full_config.get("project", {})
    plugin_config["docs_dir"] = project_config.get("docs_dir", "docs")

    plugin = ReviewsPlugin(plugin_config)
    plugin.run()

if __name__ == "__main__":
    main()
