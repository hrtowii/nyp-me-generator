import requests
import random
import time

class GelbooruSearcher:
    def __init__(self):
        self.base_url = "https://gelbooru.com/index.php"
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    def search_images(self, tags, limit=20):
        """Search for images with given tags"""
        if isinstance(tags, str):
            tags = [tags]

        # Normalize tags: lowercase, replace spaces with underscores
        tags = [tag.strip().lower().replace(' ', '_') for tag in tags if tag.strip()]
        tag_string = '+'.join(tags)

        params = {
            'page': 'dapi',
            's': 'post',
            'q': 'index',
            'tags': tag_string,
            'limit': limit,
            'json': '1'
        }
        try:
            response = requests.get(self.base_url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()  # Raise error for bad status codes
            data = response.json()

            # Handle gelbooru JSON format
            if isinstance(data, dict) and 'post' in data:
                return data['post']  # Properly extracted posts
            return []  # Fail-safe for unexpected formats
        except Exception as e:
            print(f"Error searching Gelbooru: {e}")
            return []

    def get_best_image_url(self, posts):
        """Get the best quality image URL from posts"""
        if not posts:
            return None

        # Filter valid posts with file_url
        valid_posts = [post for post in posts if post.get('file_url')]
        if not valid_posts:
            return None

        # Sort by score (descending) for best quality
        valid_posts.sort(key=lambda x: int(x.get('score', 0)), reverse=True)

        # Pick randomly from top 5 results
        top_posts = valid_posts[:5]
        return random.choice(top_posts).get('file_url') if top_posts else None

    def search_with_fallback(self, tags, max_attempts=None):
        """Search for images, gradually reducing tags if no results found"""
        # Convert to list and normalize tags
        if isinstance(tags, str):
            tags = tags.split()
        current_tags = [tag.strip().lower().replace(' ', '_') for tag in tags]

        # Set max attempts to number of tags + 1 (for the 1girl fallback)
        if max_attempts is None:
            max_attempts = len(current_tags) + 2  # +1 for 1girl fallback, +1 extra attempt

        for attempt in range(max_attempts):
            if not current_tags:
                break

            print(f"Searching with tags: {current_tags}")
            posts = self.search_images(current_tags)
            print(posts)
            if posts:
                url = self.get_best_image_url(posts)
                if url:
                    return url

            # Remove least important tag (last element)
            if len(current_tags) > 1:
                current_tags.pop()
            else:
                if current_tags and current_tags[0] != "1girl":
                    current_tags = ["1girl"]  # Final fallback tag
                else:
                    break  # Already tried 1girl with no results

            time.sleep(0.1)  # Respect API rate limits

        return None  # No results after all attempts

def search_anime_character(tags):
    """Main function to search for anime character images"""
    searcher = GelbooruSearcher()

    # Add common anime tags if not present
    if isinstance(tags, str):
        tag_list = [tag.strip() for tag in tags.split() if tag.strip()]
    else:
        tag_list = [str(tag).strip() for tag in tags if str(tag).strip()]

    # Ensure we have a base tag for filtering
    # if not any(tag in ['1girl', '1boy'] for tag in tag_list):
    #     tag_list.insert(0, '1girl')

    return searcher.search_with_fallback(tag_list)
