import os
import requests
import json
import time
from pathlib import Path

class GooglePlacesClient:
    def __init__(self, api_key, place_id):
        self.api_key = api_key
        self.place_id = place_id
        self.base_url = f"https://places.googleapis.com/v1/places/{place_id}"

    def fetch_reviews(self):
        """Fetches reviews from the Google Places API (New)."""
        if not self.api_key:
            raise ValueError("GOOGLE_MAPS_API_KEY environment variable not set.")

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "reviews"
        }

        try:
            response = requests.get(self.base_url, headers=headers)
            response.raise_for_status()
            data = response.json()
            return data.get("reviews", [])
        except requests.exceptions.RequestException as e:
            print(f"Error fetching reviews from Google: {e}")
            return []

    def filter_reviews(self, reviews, min_rating=4.0, max_count=5):
        """Filters reviews based on rating, count, and content."""
        filtered = []
        for r in reviews:
            # Check for text (skip rating-only reviews as per PRD suggestion)
            text_content = r.get("text", {}).get("text", "")
            if not text_content:
                continue

            rating = r.get("rating", 0)
            if rating >= min_rating:
                # Format the review for Zensical frontmatter
                attribution = r.get("authorAttribution", {})
                filtered.append({
                    "author": str(attribution.get("displayName") or ""),
                    "author_uri": str(attribution.get("uri") or ""),
                    "photo_uri": str(attribution.get("photoUri") or ""),
                    "rating": str(rating),
                    "text": str(text_content),
                    "relative_time": str(r.get("relativePublishTimeDescription") or ""),
                    "publish_time": str(r.get("publishTime") or "")
                })

        # Return only the top reviews up to max_count
        return filtered[:max_count]

class ReviewCache:
    def __init__(self, cache_path, expiry_hours=24):
        self.cache_path = Path(cache_path)
        self.expiry_seconds = expiry_hours * 3600

    def get(self):
        """Retrieves cached reviews if they haven't expired."""
        if not self.cache_path.exists():
            return None

        try:
            with open(self.cache_path, "r") as f:
                cached_data = json.load(f)
                timestamp = cached_data.get("timestamp", 0)
                if (time.time() - timestamp) < self.expiry_seconds:
                    return cached_data.get("reviews")
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading cache: {e}")
        
        return None

    def set(self, reviews):
        """Saves reviews to the cache with a timestamp."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.cache_path, "w") as f:
                json.dump({
                    "timestamp": time.time(),
                    "reviews": reviews
                }, f, indent=2)
        except IOError as e:
            print(f"Error saving cache: {e}")
