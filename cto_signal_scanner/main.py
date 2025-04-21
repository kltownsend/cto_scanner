import os
import ssl
import logging
import feedparser
from datetime import datetime, timedelta
import json
from pathlib import Path
from cto_signal_scanner.utils.gpt_agent import GPTAgent
from cto_signal_scanner.utils.feed_sources import FEEDS
from cto_signal_scanner.utils.pdf_generator import ReportGenerator
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("\n=== Starting CTO Signal Scanner ===")
load_dotenv()

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Cache setup
CACHE_FILE = BASE_DIR / "processed_entries.json"

def clear_cache():
    """Clear the cache file."""
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()  # Delete the file
    return {}

def load_cache():
    if CACHE_FILE.exists():
        with open(CACHE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f)

def parse_date(entry):
    """Parse date from feed entry."""
    date_fields = ['published_parsed', 'updated_parsed', 'created_parsed']
    for field in date_fields:
        if hasattr(entry, field) and getattr(entry, field):
            return datetime(*getattr(entry, field)[:6])
    return None

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
    # Get user input for days to look back
    while True:
        try:
            days_back = int(input("Enter number of days to look back (1-30): "))
            if 1 <= days_back <= 30:
                break
            print("Please enter a number between 1 and 30.")
        except ValueError:
            print("Please enter a valid number.")
    
    cutoff_date = datetime.now() - timedelta(days=days_back)
    print(f"\nLooking for posts since: {cutoff_date.strftime('%Y-%m-%d')}")
    
    # Initialize PDF generator and GPT agent
    pdf_gen = ReportGenerator()
    gpt_agent = GPTAgent()
    pdf_gen.add_header(days_back)
    
    # Clear and initialize new cache
    processed_cache = clear_cache()
    
    logger.debug("Starting feed processing")
    try:
        for url in FEEDS:
            logger.debug(f"Processing feed: {url}")
            try:
                feed = fetch_and_validate_feed(url)
                if not feed:
                    continue
                    
                logger.debug(f"Feed parsed, found {len(feed.entries)} entries")
                
                for entry in feed.entries:
                    entry_date = parse_date(entry)
                    if not entry_date:
                        logger.warning(f"Could not parse date for entry: {entry.title}")
                        continue
                        
                    # Skip if entry is too old
                    if entry_date < cutoff_date:
                        continue
                        
                    # Skip if already processed
                    entry_id = entry.get('id', entry.link)
                    if entry_id in processed_cache:
                        continue
                    
                    logger.debug(f"Processing entry: {entry.title}")
                    try:
                        result = gpt_agent.evaluate_post(entry.title, entry.summary, entry.link)
                        
                        # Parse the GPT response
                        lines = result.strip().split('\n')
                        link = entry.link
                        summary = ""
                        rating = ""
                        rationale = ""
                        
                        for line in lines:
                            if line.startswith('Summary:'):
                                summary = line.replace('Summary:', '').strip()
                            elif line.startswith('Rating:'):
                                rating = line.replace('Rating:', '').strip()
                            elif line.startswith('Rationale:'):
                                rationale = line.replace('Rationale:', '').strip()
                        
                        # Add to PDF
                        pdf_gen.add_article(
                            title=entry.title,
                            link=link,
                            summary=summary,
                            rating=rating,
                            rationale=rationale
                        )
                        
                        # Console output for monitoring
                        print("\nEvaluation Result:")
                        print("=" * 50)
                        print(result)
                        print("=" * 50)
                        
                        # Add to processed cache
                        processed_cache[entry_id] = {
                            'title': entry.title,
                            'date': entry_date.isoformat(),
                            'processed_at': datetime.now().isoformat()
                        }
                    except Exception as e:
                        logger.error(f"Error evaluating post: {str(e)}", exc_info=True)
            except Exception as e:
                logger.error(f"Error processing feed {url}: {str(e)}", exc_info=True)
    except Exception as e:
        logger.error(f"Main process error: {str(e)}", exc_info=True)
    finally:
        # Generate PDF
        pdf_gen.generate()
        # Save cache
        save_cache(processed_cache)

if __name__ == "__main__":
    fetch_and_process_feeds()
    logger.debug("Processing complete")