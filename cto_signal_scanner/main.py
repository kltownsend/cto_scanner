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

def load_gpt_cache():
    """Load the GPT response cache."""
    cache_file = BASE_DIR / "gpt_cache.json"
    if cache_file.exists():
        with open(cache_file, 'r') as f:
            return json.load(f)
    return {'prompt': '', 'responses': {}}

def save_gpt_cache(cache):
    """Save the GPT response cache."""
    cache_file = BASE_DIR / "gpt_cache.json"
    with open(cache_file, 'w') as f:
        json.dump(cache, f)

def fetch_and_process_feeds(days_back=7):
    """Fetch and process feeds for the specified number of days back."""
    cutoff_date = datetime.now() - timedelta(days=days_back)
    logger.info(f"Looking for posts since: {cutoff_date.strftime('%Y-%m-%d')}")
    
    # Initialize PDF generator and GPT agent
    pdf_gen = ReportGenerator()
    gpt_agent = GPTAgent()
    pdf_gen.add_header(days_back)
    
    # Load GPT cache
    gpt_cache = load_gpt_cache()
    current_prompt = gpt_agent.get_current_prompt()
    
    # Check if we need to invalidate cache
    if gpt_cache['prompt'] != current_prompt:
        logger.info("Prompt changed, invalidating GPT cache")
        gpt_cache = {'prompt': current_prompt, 'responses': {}}
    
    # Initialize empty results list
    results = []
    
    logger.info("Starting feed processing")
    try:
        for url in FEEDS:
            logger.info(f"Processing feed: {url}")
            try:
                feed = fetch_and_validate_feed(url)
                if not feed:
                    logger.warning(f"Could not fetch or parse feed: {url}")
                    continue
                    
                logger.info(f"Feed parsed, found {len(feed.entries)} entries")
                
                for entry in feed.entries:
                    try:
                        entry_date = parse_date(entry)
                        if not entry_date:
                            logger.warning(f"Could not parse date for entry: {entry.title}")
                            continue
                            
                        # Skip if entry is too old
                        if entry_date < cutoff_date:
                            continue
                        
                        logger.info(f"Processing entry: {entry.title}")
                        try:
                            # Create cache key from article content
                            cache_key = f"{entry.title}:{entry.summary}:{entry.link}"
                            
                            # Check cache first
                            if cache_key in gpt_cache['responses']:
                                logger.info(f"Using cached GPT response for: {entry.title}")
                                result = gpt_cache['responses'][cache_key]
                            else:
                                # Get new evaluation from GPT
                                result = gpt_agent.evaluate_post(entry.title, entry.summary, entry.link)
                                # Cache the response
                                gpt_cache['responses'][cache_key] = result
                            
                            # Add to results
                            results.append({
                                'title': entry.title,
                                'link': entry.link,
                                'summary': result['summary'],
                                'rating': result['rating'],
                                'rationale': result['rationale'],
                                'date': entry_date.isoformat()
                            })
                            
                            # Add to PDF
                            pdf_gen.add_article(
                                title=entry.title,
                                link=entry.link,
                                summary=result['summary'],
                                rating=result['rating'],
                                rationale=result['rationale']
                            )
                        except Exception as e:
                            logger.error(f"Error evaluating post: {str(e)}", exc_info=True)
                            continue
                    except Exception as e:
                        logger.error(f"Error processing entry: {str(e)}", exc_info=True)
                        continue
            except Exception as e:
                logger.error(f"Error processing feed {url}: {str(e)}", exc_info=True)
                continue
    except Exception as e:
        logger.error(f"Main process error: {str(e)}", exc_info=True)
        raise  # Re-raise the exception to be caught by the web app
    finally:
        try:
            # Save GPT cache
            save_gpt_cache(gpt_cache)
            # Generate PDF
            pdf_path = pdf_gen.generate()
            return results, pdf_path
        except Exception as e:
            logger.error(f"Error in final steps: {str(e)}", exc_info=True)
            raise  # Re-raise the exception to be caught by the web app

if __name__ == "__main__":
    fetch_and_process_feeds()
    logger.debug("Processing complete")