import os
import json
import time
from pathlib import Path
import sys

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from reviews_plugin.plugin import ReviewsPlugin
from reviews_plugin.client import GooglePlacesClient

class MockGooglePlacesClient(GooglePlacesClient):
    def fetch_reviews(self):
        print("Mock fetching reviews from Google...")
        return [
            {
                "authorAttribution": {"displayName": "John Doe", "uri": "https://maps.google.com/john", "photoUri": "https://lh3.googleusercontent.com/a-/1"},
                "rating": 5,
                "relativePublishTimeDescription": "a week ago",
                "text": {"text": "Excellent service and great atmosphere!"},
                "publishTime": "2024-03-01T12:00:00Z"
            },
            {
                "authorAttribution": {"displayName": "Jane Smith", "uri": "https://maps.google.com/jane", "photoUri": None},
                "rating": 4,
                "relativePublishTimeDescription": "2 weeks ago",
                "text": {"text": "Very good, but slightly expensive."},
                "publishTime": "2024-02-20T10:00:00Z"
            },
            {
                "authorAttribution": {"displayName": "Bad Reviewer", "uri": "https://maps.google.com/bad", "photoUri": None},
                "rating": 2,
                "relativePublishTimeDescription": "3 weeks ago",
                "text": {"text": "Not a great experience."},
                "publishTime": "2024-02-15T09:00:00Z"
            },
            {
                "authorAttribution": {"displayName": "No Text Reviewer", "uri": "https://maps.google.com/notext", "photoUri": None},
                "rating": 5,
                "relativePublishTimeDescription": "1 month ago",
                "text": {}, # Empty text
                "publishTime": "2024-02-10T08:00:00Z"
            }
        ]

def test_reviews_plugin():
    print("Starting ReviewsPlugin test with MockGooglePlacesClient...")
    
    # Configure the plugin
    config = {
        "place_id": "mock_place_id",
        "max_reviews": 5,
        "min_rating_filter": 4.0,
        "docs_dir": "docs"
    }
    
    plugin = ReviewsPlugin(config)
    # Inject the mock client
    plugin.client = MockGooglePlacesClient("mock_api_key", "mock_place_id")
    # Set API key to bypass check
    plugin.api_key = "mock_api_key"
    
    # Ensure cache is cleared for testing
    if plugin.cache_path.exists():
        plugin.cache_path.unlink()
    
    # Run the plugin
    plugin.run(force_refresh=True)
    
    # Verify file generation
    reviews_file = Path("docs/reviews.md")
    if not reviews_file.exists():
        print("FAILED: docs/reviews.md does not exist.")
        return
    else:
        print("SUCCESS: Found reviews.md")

    # Read the generated file and verify content
    with open(reviews_file, "r") as f:
        content = f.read()
        # Verify filtering: Bad Reviewer (rating 2) should NOT be there
        if "Bad Reviewer" in content:
            print("FAILED: Bad Reviewer found in reviews.md (should be filtered out)")
        else:
            print("SUCCESS: Bad Reviewer filtered out.")
            
        # Verify filtering: No Text Reviewer should NOT be there
        if "No Text Reviewer" in content:
            print("FAILED: No Text Reviewer found in reviews.md (should be filtered out)")
        else:
            print("SUCCESS: No Text Reviewer filtered out.")
            
        # Verify inclusion: John Doe and Jane Smith should be there
        if "John Doe" in content and "Jane Smith" in content:
            print("SUCCESS: John Doe and Jane Smith found in reviews.md")
        else:
            print("FAILED: John Doe or Jane Smith missing from reviews.md")

    # Verify cache
    if plugin.cache_path.exists():
        print("SUCCESS: Cache file created.")
        with open(plugin.cache_path, "r") as f:
            cache_data = json.load(f)
            if len(cache_data.get("reviews", [])) == 2:
                print("SUCCESS: Cache contains correct number of filtered reviews (2).")
            else:
                print(f"FAILED: Cache contains {len(cache_data.get('reviews', []))} reviews (expected 2).")
    else:
        print("FAILED: Cache file not found.")

if __name__ == "__main__":
    test_reviews_plugin()
