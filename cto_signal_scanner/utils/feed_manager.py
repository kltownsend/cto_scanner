import json
import os
import uuid
import feedparser
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import requests
from datetime import datetime

class FeedManager:
    # Default feeds to pre-populate
    DEFAULT_FEEDS = {
        'aws': 'https://aws.amazon.com/blogs/aws/feed/',
        'azure': 'https://azure.microsoft.com/en-us/blog/feed/',
        'gcp': 'https://cloudblog.withgoogle.com/rss/',
        'cloudflare': 'https://blog.cloudflare.com/rss/',
        'cisco': 'https://blogs.cisco.com/feed',
        'redhat': 'https://www.redhat.com/en/feed'
    }

    def __init__(self, feeds_file: str = "feeds.json"):
        self.feeds_file = Path(feeds_file)
        self.feeds: Dict = self._load_feeds()

    def _load_feeds(self) -> Dict:
        """Load feeds from JSON file or create default if not exists."""
        if self.feeds_file.exists():
            with open(self.feeds_file, 'r') as f:
                return json.load(f)
        
        # Create default feeds if file doesn't exist
        feeds = {"feeds": []}
        for name, url in self.DEFAULT_FEEDS.items():
            feed_data = {
                'id': str(uuid.uuid4()),
                'url': url,
                'name': name.upper(),
                'added_at': datetime.now().isoformat(),
                'status': 'unknown'  # Will be validated when first accessed
            }
            feeds['feeds'].append(feed_data)
        
        # Save default feeds
        with open(self.feeds_file, 'w') as f:
            json.dump(feeds, f, indent=2)
        
        return feeds

    def _save_feeds(self):
        """Save feeds to JSON file."""
        with open(self.feeds_file, 'w') as f:
            json.dump(self.feeds, f, indent=2)

    def validate_feed(self, url: str) -> Tuple[bool, str]:
        """
        Validate if a URL is a valid RSS feed.
        Returns (is_valid, error_message)
        """
        try:
            # First try to fetch the URL
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            # Try to parse as feed
            feed = feedparser.parse(response.text)
            
            # Check if it's a valid feed
            if feed.bozo:  # Feed parsing error
                return False, f"Invalid feed format: {feed.bozo_exception}"
            
            if not feed.entries:
                return False, "Feed contains no entries"
            
            # Check if we can access required fields
            for entry in feed.entries[:1]:  # Check first entry only
                if not hasattr(entry, 'title') or not hasattr(entry, 'link'):
                    return False, "Feed entries missing required fields (title, link)"
                
                # Try to get date
                date_fields = ['published', 'updated', 'created']
                has_date = any(hasattr(entry, field) for field in date_fields)
                if not has_date:
                    return False, "Feed entries missing date information"
            
            return True, "Feed is valid"
            
        except requests.RequestException as e:
            return False, f"Error fetching feed: {str(e)}"
        except Exception as e:
            return False, f"Error validating feed: {str(e)}"

    def add_feed(self, url: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Add a new feed after validation.
        Returns (success, message, feed_data)
        """
        # Validate feed first
        is_valid, error_msg = self.validate_feed(url)
        if not is_valid:
            return False, error_msg, None

        # Check if feed already exists
        if any(feed['url'] == url for feed in self.feeds['feeds']):
            return False, "Feed already exists", None

        # Create new feed entry
        feed_data = {
            'id': str(uuid.uuid4()),
            'url': url,
            'name': self._extract_feed_name(url),
            'added_at': datetime.now().isoformat(),
            'status': 'valid'
        }

        # Add to feeds list
        self.feeds['feeds'].append(feed_data)
        self._save_feeds()

        return True, "Feed added successfully", feed_data

    def remove_feed(self, feed_id: str) -> Tuple[bool, str]:
        """Remove a feed by ID."""
        original_length = len(self.feeds['feeds'])
        self.feeds['feeds'] = [f for f in self.feeds['feeds'] if f['id'] != feed_id]
        
        if len(self.feeds['feeds']) == original_length:
            return False, "Feed not found"
        
        self._save_feeds()
        return True, "Feed removed successfully"

    def get_feeds(self) -> List[Dict]:
        """Get all feeds with their current status."""
        feeds = self.feeds['feeds'].copy()
        
        # Update status for each feed
        for feed in feeds:
            is_valid, _ = self.validate_feed(feed['url'])
            feed['status'] = 'valid' if is_valid else 'invalid'
        
        return feeds

    def _extract_feed_name(self, url: str) -> str:
        """Extract a readable name from the feed URL."""
        # Remove protocol and www
        name = url.replace('https://', '').replace('http://', '').replace('www.', '')
        
        # Remove path and query parameters
        name = name.split('/')[0]
        
        # Remove common TLDs
        name = name.replace('.com', '').replace('.org', '').replace('.net', '')
        
        # Capitalize words
        name = ' '.join(word.capitalize() for word in name.split('.'))
        
        return name

    def get_enabled_feeds(self) -> List[str]:
        """Get URLs of all valid feeds."""
        return [feed['url'] for feed in self.get_feeds() if feed['status'] == 'valid'] 