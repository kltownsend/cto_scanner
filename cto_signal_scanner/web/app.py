from flask import Flask, render_template, request, jsonify, send_file, session, Response
import os
import json
import logging
import feedparser
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask_wtf.csrf import CSRFProtect, CSRFError
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_session import Session
from cto_signal_scanner.utils.feed_manager import FeedManager
from cto_signal_scanner.utils.gpt_agent import GPTAgent
from cto_signal_scanner.utils.pdf_generator import ReportGenerator
from cto_signal_scanner.main import fetch_and_process_feeds
import time

# Load environment variables
load_dotenv()

# Default port configuration
PORT = int(os.getenv('PORT', 5001))  # Use 5001 as the default port

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cto_signal_scanner.log'),
        logging.StreamHandler()
    ]
)

# Create logger instances
app_logger = logging.getLogger('app')
feed_logger = logging.getLogger('feed_manager')

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-please-change-in-production')
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = str(BASE_DIR / 'flask_session')
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['REPORTS_FOLDER'] = BASE_DIR / 'reports'
app.config['SETTINGS_FILE'] = BASE_DIR / 'settings.json'
app.config['PORT'] = PORT  # Set the port in Flask config

# Initialize session
Session(app)

# Initialize CSRF protection
csrf = CSRFProtect(app)

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
gpt_agent = GPTAgent()

# Global variables for progress tracking
scan_progress = {
    'total_articles': 0,
    'assessed_articles': 0,
    'is_scanning': False
}

def load_settings():
    """Load settings from JSON file or return defaults"""
    if app.config['SETTINGS_FILE'].exists():
        with open(app.config['SETTINGS_FILE'], 'r') as f:
            return json.load(f)
    
    # Default settings
    return {
        'openai_key': os.getenv('OPENAI_API_KEY', ''),
        'gpt_model': os.getenv('GPT_MODEL', 'gpt-3.5-turbo'),
        'gpt_prompt': '''You are a technology analyst specializing in cloud computing and enterprise technology. 
Analyze the following article and provide:
1. A concise summary of the key points
2. A rating (High/Medium/Low) based on its relevance to CTOs and technology leaders
3. A brief rationale for the rating

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
    
    # Configure Ollama if a local model is selected
    if settings.get('gpt_model') in ['qwen2:7b', 'llama2', 'mistral']:
        os.environ['USE_OLLAMA'] = 'true'
        os.environ['OLLAMA_MODEL'] = settings.get('gpt_model')
    else:
        os.environ['USE_OLLAMA'] = 'false'
    
    # Reinitialize GPT agent with new settings
    global gpt_agent
    gpt_agent = GPTAgent()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        try:
            data = request.json
            settings = {
                'openai_key': data.get('openai_key', ''),
                'gpt_model': data.get('gpt_model', 'gpt-3.5-turbo'),
                'gpt_prompt': data.get('gpt_prompt', '')
            }
            save_settings(settings)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    
    # GET request - display settings form
    current_settings = load_settings()
    feeds = feed_manager.get_feeds()
    return render_template('settings.html', 
                         openai_key=current_settings.get('openai_key', ''),
                         gpt_model=current_settings.get('gpt_model', 'gpt-3.5-turbo'),
                         gpt_prompt=current_settings.get('gpt_prompt', ''),
                         feeds=feeds)

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

@app.route('/scan_progress')
def scan_progress_stream():
    def generate():
        while True:
            if scan_progress['is_scanning']:
                yield f"data: {json.dumps(scan_progress)}\n\n"
            else:
                yield "data: {\"is_scanning\": false}\n\n"
            time.sleep(1)
    
    return Response(generate(), mimetype='text/event-stream')

@app.route('/scan', methods=['POST'])
def scan():
    try:
        if not request.is_json:
            app_logger.warning("Invalid content type received in scan request")
            return jsonify({
                'success': False,
                'error': 'Invalid content type. Expected application/json'
            }), 400

        data = request.get_json()
        if not data or 'days_back' not in data:
            app_logger.warning("Missing days_back parameter in scan request")
            return jsonify({
                'success': False,
                'error': 'Missing required parameter: days_back'
            }), 400

        days_back = data['days_back']
        if not isinstance(days_back, int) or days_back < 1 or days_back > 30:
            app_logger.warning(f"Invalid days_back value received: {days_back}")
            return jsonify({
                'success': False,
                'error': 'days_back must be an integer between 1 and 30'
            }), 400

        app_logger.info(f"Starting scan for {days_back} days back")
        
        # Reset progress
        scan_progress['total_articles'] = 0
        scan_progress['assessed_articles'] = 0
        scan_progress['is_scanning'] = True
        
        # Fetch results
        results, pdf_path = fetch_and_process_feeds(days_back)
        app_logger.info(f"Scan completed. Found {len(results)} articles")
        
        # Create PDF report
        pdf_generator = ReportGenerator()
        pdf_generator.add_header(f"CTO Signal Scanner Report - Last {days_back} Days")
        
        # Add articles to PDF
        for article in results:
            pdf_generator.add_article(
                title=article['title'],
                link=article['link'],
                summary=article['summary'],
                rating=article['rating'],
                rationale=article['rationale']
            )
        
        # Update final progress
        scan_progress['total_articles'] = len(results)
        scan_progress['assessed_articles'] = len(results)
        scan_progress['is_scanning'] = False
        
        return jsonify({
            'success': True,
            'results': results,
            'pdf_path': pdf_path,
            'article_count': len(results),
            'assessed_count': len(results)
        })

    except Exception as e:
        app_logger.error(f"Error during scan: {str(e)}", exc_info=True)
        scan_progress['is_scanning'] = False
        return jsonify({
            'success': False,
            'error': f'An error occurred during the scan: {str(e)}'
        }), 500

@app.route('/download/<path:filename>')
@limiter.limit("30 per minute")  # Limit download requests
def download_file(filename):
    try:
        # Validate filename format (only allow alphanumeric, dash, underscore, and dot)
        if not all(c.isalnum() or c in '._-' for c in filename):
            return jsonify({'error': 'Invalid filename format'}), 400
            
        # Ensure the file is within the reports directory
        file_path = app.config['REPORTS_FOLDER'] / filename
        if not str(file_path.resolve()).startswith(str(app.config['REPORTS_FOLDER'].resolve())):
            return jsonify({'error': 'Invalid file path'}), 400
        
        # Check if file exists
        if not file_path.exists():
            return jsonify({'error': 'Report file not found. It may have been deleted or not generated yet.'}), 404
            
        # Check file size to prevent large file downloads
        if file_path.stat().st_size > 10 * 1024 * 1024:  # 10MB limit
            return jsonify({'error': 'File too large'}), 413
            
        return send_file(
            str(file_path),
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        app_logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'An error occurred while downloading the file'}), 500

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({
        'success': False,
        'error': 'Session expired. Please refresh the page and try again.'
    }), 400

@app.before_request
def before_request():
    session.permanent = True
    session.modified = True

if __name__ == '__main__':
    app.run(debug=True, port=PORT) 