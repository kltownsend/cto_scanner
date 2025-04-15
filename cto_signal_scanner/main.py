import os
import ssl
import logging
import feedparser
from cto_signal_scanner.utils.gpt_agent import evaluate_post
from cto_signal_scanner.utils.feed_sources import FEEDS
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n=== Starting CTO Signal Scanner ===")
load_dotenv()

def fetch_and_validate_feed(url):
    """Fetch and validate feed content with better error handling."""
    try:
        # First try direct request to see what we're getting
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get('content-type', '').lower()
        
        if 'html' in content_type:
            # Try to find the actual RSS feed URL from HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            feed_links = soup.find_all('link', type='application/rss+xml') or \
                        soup.find_all('link', type='application/atom+xml')
            
            if feed_links:
                actual_feed_url = feed_links[0].get('href')
                if not actual_feed_url.startswith('http'):
                    # Handle relative URLs
                    actual_feed_url = f"{'/'.join(url.split('/')[:3])}{actual_feed_url}"
                logger.info(f"Found actual feed URL: {actual_feed_url}")
                return feedparser.parse(actual_feed_url)
        
        # Try parsing as RSS/Atom
        feed = feedparser.parse(response.text)
        if feed.entries:
            return feed
            
        # If no entries found, try XML parsing
        try:
            root = ET.fromstring(response.text)
            # Handle different XML structures
            items = root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry')
            if items:
                return feedparser.parse(response.text)
        except ET.ParseError:
            logger.error(f"XML parsing failed for {url}")
            
        logger.error(f"Could not parse feed from {url}")
        return None
        
    except Exception as e:
        logger.error(f"Error fetching feed {url}: {str(e)}")
        return None

def fetch_and_process_feeds():
    logger.debug("Starting feed processing")
    try:
        for url in FEEDS:
            logger.debug(f"Processing feed: {url}")
            try:
                feed = fetch_and_validate_feed(url)
                logger.debug(f"Feed parsed, found {len(feed.entries)} entries")
                
                for entry in feed.entries[:5]:
                    logger.debug(f"Processing entry: {entry.title}")
                    try:
                        result = evaluate_post(entry.title, entry.summary, entry.link)
                        print("\nEvaluation Result:")
                        print("=" * 50)
                        print(result)
                        print("=" * 50)
                    except Exception as e:
                        logger.error(f"Error evaluating post: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Error processing feed {url}: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Main process error: {str(e)}", exc_info=True)

if __name__ == "__main__":
    fetch_and_process_feeds()
    logger.debug("Processing complete")
