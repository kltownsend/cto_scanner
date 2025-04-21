from flask import Flask, render_template, request, jsonify, send_file
import os
import json
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from cto_signal_scanner.utils.feed_manager import FeedManager
from cto_signal_scanner.utils.gpt_agent import GPTAgent, gpt_logger
from cto_signal_scanner.utils.pdf_generator import ReportGenerator
from cto_signal_scanner.utils.logging_config import setup_logging
from urllib.parse import unquote

# Set up logging
logger = setup_logging()

# Load environment variables
load_dotenv()

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['REPORTS_FOLDER'] = BASE_DIR / 'reports'
app.config['SETTINGS_FILE'] = BASE_DIR / 'settings.json'

def load_settings():
    """Load settings from JSON file or return defaults"""
    if app.config['SETTINGS_FILE'].exists():
        with open(app.config['SETTINGS_FILE'], 'r') as f:
            return json.load(f)
    
    # Default settings
    return {
        'openai_key': os.getenv('OPENAI_API_KEY', ''),
        'gpt_model': os.getenv('GPT_MODEL', 'gpt-3.5-turbo'),
        'gpt_prompt': '''You are Keith Townsend, the CTO Advisor — a technology analyst and enterprise architect with 25+ years of experience in enterprise IT. You specialize in helping CTOs and technology executives make practical decisions on cloud transformation, infrastructure modernization, and operational resilience.

For the article below, provide:

Executive Summary — A sharp, 3-5 sentence breakdown of the article's core message and key takeaways, emphasizing implications for large enterprises or regulated industries.

CTO Relevance Rating — Rate the article as High, Medium, or Low based on its strategic value to CTOs and senior tech decision-makers.

Rationale — In 1-2 paragraphs, explain your rating. Focus on whether the article provides actionable insights, strategic framing, or thought leadership relevant to decision-makers navigating multicloud, digital risk, or enterprise architecture challenges.

If the article includes vendor messaging, assess how realistic the claims are in enterprise-scale environments.

Article:
Title: {title}
Summary: {summary}
Link: {link}

Format your response as:
Summary: [your summary]
Rating: [High/Medium/Low]
Rationale: [your rationale]'''
    }

def save_settings(settings):
    """Save settings to JSON file"""
    with open(app.config['SETTINGS_FILE'], 'w') as f:
        json.dump(settings, f)
    
    # Update environment variables
    os.environ['OPENAI_API_KEY'] = settings.get('openai_key', '')
    os.environ['GPT_MODEL'] = settings.get('gpt_model', 'gpt-3.5-turbo')
    os.environ['GPT_PROMPT'] = settings.get('gpt_prompt', '')

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Exempt JSON endpoints from CSRF protection
@csrf.exempt
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        app.logger.debug(f"Received POST request to /settings")
        app.logger.debug(f"Request headers: {dict(request.headers)}")
        app.logger.debug(f"Request content type: {request.content_type}")
        
        try:
            if not request.is_json:
                app.logger.error("Request is not JSON")
                return jsonify({'success': False, 'error': 'Request must be JSON'}), 400
                
            app.logger.debug(f"Request JSON data: {request.json}")
            data = request.json
            settings = {
                'openai_key': data.get('openai_key', ''),
                'gpt_model': data.get('gpt_model', 'gpt-3.5-turbo'),
                'gpt_prompt': data.get('gpt_prompt', '')
            }
            save_settings(settings)
            app.logger.debug("Settings saved successfully")
            return jsonify({'success': True})
        except Exception as e:
            app.logger.error(f"Error saving settings: {str(e)}", exc_info=True)
            return jsonify({'success': False, 'error': str(e)})
    
    # GET request - display settings form
    app.logger.debug("Received GET request to /settings")
    current_settings = load_settings()
    feeds = feed_manager.get_feeds()
    return render_template('settings.html', 
                         openai_key=current_settings.get('openai_key', ''),
                         gpt_model=current_settings.get('gpt_model', 'gpt-3.5-turbo'),
                         gpt_prompt=current_settings.get('gpt_prompt', ''),
                         feeds=feeds)

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Talisman for security headers
talisman = Talisman(
    app,
    content_security_policy={
        'default-src': "'self'",
        'script-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'style-src': ["'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'img-src': ["'self'", "data:", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
        'font-src': ["'self'", "cdn.jsdelivr.net", "cdnjs.cloudflare.com"],
    },
    force_https=False  # Set to True in production
)

# Ensure reports directory exists with proper permissions
os.makedirs(app.config['REPORTS_FOLDER'], mode=0o700, exist_ok=True)

# Initialize managers
feed_manager = FeedManager(str(BASE_DIR / 'feeds.json'))

# Load initial settings into environment variables
initial_settings = load_settings()
os.environ['OPENAI_API_KEY'] = initial_settings.get('openai_key', '')
os.environ['GPT_MODEL'] = initial_settings.get('gpt_model', 'gpt-3.5-turbo')
os.environ['GPT_PROMPT'] = initial_settings.get('gpt_prompt', '')

# Initialize GPT agent after setting environment variables
gpt_agent = GPTAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test_feed', methods=['POST'])
def test_feed():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        is_valid, message = feed_manager.validate_feed(url)
        return jsonify({
            'success': is_valid,
            'error': None if is_valid else message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_feed', methods=['POST'])
def add_feed():
    try:
        data = request.json
        url = data.get('url')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'})
        
        success, message, feed_data = feed_manager.add_feed(url)
        return jsonify({
            'success': success,
            'error': None if success else message,
            'feed': feed_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_feed', methods=['POST'])
def remove_feed():
    try:
        data = request.json
        feed_id = data.get('feed_id')
        
        if not feed_id:
            return jsonify({'success': False, 'error': 'Feed ID is required'})
        
        success, message = feed_manager.remove_feed(feed_id)
        return jsonify({
            'success': success,
            'error': None if success else message
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/scan', methods=['POST'])
@limiter.limit("10 per minute")  # Limit scan requests
def scan_feeds():
    try:
        logger.info("Starting scan_feeds endpoint")
        logger.debug(f"Request form data: {request.form}")
        
        days_back = int(request.form.get('days_back', 7))
        if not 1 <= days_back <= 30:
            logger.warning(f"Invalid days_back value: {days_back}")
            return jsonify({'success': False, 'error': 'Days must be between 1 and 30'}), 400

        # Create timezone-aware cutoff date
        cutoff_date = datetime.now().astimezone() - timedelta(days=days_back)
        logger.debug(f"Cutoff date: {cutoff_date}")
        
        results = []
        pdf_gen = ReportGenerator()
        pdf_gen.add_header(days_back)
        
        # Get enabled feeds from feed manager
        enabled_feeds = feed_manager.get_enabled_feeds()
        logger.debug(f"Enabled feeds: {enabled_feeds}")
        
        if not enabled_feeds:
            logger.warning("No enabled feeds found")
            return jsonify({
                'success': False,
                'error': 'No valid feed sources available. Please add and enable feeds in settings.',
                'results': []
            })
        
        feed_count = 0
        for url in enabled_feeds:
            try:
                feed_count += 1
                feed = feedparser.parse(url)
                
                for entry in feed.entries:
                    try:
                        # Parse entry date
                        entry_date = datetime.strptime(entry.published, "%a, %d %b %Y %H:%M:%S %z")
                        
                        # Skip if entry is older than cutoff date
                        if entry_date < cutoff_date:
                            continue
                            
                        # Get GPT evaluation
                        result = gpt_agent.evaluate_post(entry.title, entry.summary, entry.link)
                        
                        # Parse the GPT response
                        lines = result.strip().split('\n')
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
                        
                        article_data = {
                            'title': entry.title,
                            'link': entry.link,
                            'summary': summary,
                            'rating': rating,
                            'rationale': rationale,
                            'date': entry_date.isoformat()
                        }
                        
                        results.append(article_data)
                        pdf_gen.add_article(article_data)
                        
                    except Exception as e:
                        logger.error(f"Error processing entry: {str(e)}", exc_info=True)
                        continue
                        
            except Exception as e:
                logger.error(f"Error processing feed {url}: {str(e)}", exc_info=True)
                continue

        # Generate PDF report
        try:
            pdf_path = pdf_gen.generate()
            if pdf_path and pdf_path.exists():
                # Get relative path from reports directory and convert to string
                pdf_filename = str(pdf_path.relative_to(app.config['REPORTS_FOLDER']))
                logger.info(f"PDF report generated: {pdf_filename}")
            else:
                logger.error("PDF generation failed - no path returned")
                pdf_filename = None
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}", exc_info=True)
            pdf_filename = None

        # Return response
        if not results:
            return jsonify({
                'success': False,
                'error': f'No new articles found in the last {days_back} days.',
                'results': [],
                'pdf_path': pdf_filename
            })
        
        return jsonify({
            'success': True,
            'results': results,
            'pdf_path': pdf_filename
        })

    except Exception as e:
        logger.error(f"Unexpected error in scan_feeds: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'error': f'An unexpected error occurred: {str(e)}'
        }), 500

@app.route('/download/<path:filename>')
@limiter.limit("30 per minute")  # Limit download requests
def download_file(filename):
    try:
        # Decode the URL-encoded filename
        decoded_filename = unquote(filename)
        
        # Validate filename format (allow alphanumeric, dash, underscore, dot, and forward slash)
        if not all(c.isalnum() or c in '._-/ ' for c in decoded_filename):
            logger.warning(f"Invalid filename format: {decoded_filename}")
            return jsonify({'error': 'Invalid filename format'}), 400
            
        # Construct the file path
        file_path = app.config['REPORTS_FOLDER'] / decoded_filename
        
        # Ensure the file is within the reports directory (path traversal prevention)
        try:
            file_path = file_path.resolve()
            reports_dir = app.config['REPORTS_FOLDER'].resolve()
            if not str(file_path).startswith(str(reports_dir)):
                logger.warning(f"Path traversal attempt: {file_path}")
                return jsonify({'error': 'Invalid file path'}), 400
        except Exception as e:
            logger.error(f"Error resolving path: {str(e)}")
            return jsonify({'error': 'Invalid file path'}), 400
        
        # Check if file exists
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return jsonify({'error': 'Report file not found. It may have been deleted or not generated yet.'}), 404
            
        # Check file size to prevent large file downloads
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"File too large: {file_path}")
            return jsonify({'error': 'File too large'}), 413
            
        # Get the filename for download (just the basename)
        download_name = file_path.name
            
        logger.info(f"Sending file: {file_path} as {download_name}")
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=download_name
        )
    except Exception as e:
        logger.error(f"Error downloading file: {str(e)}", exc_info=True)
        return jsonify({'error': 'An error occurred while downloading the file'}), 500

if __name__ == '__main__':
    app.run(debug=True) 