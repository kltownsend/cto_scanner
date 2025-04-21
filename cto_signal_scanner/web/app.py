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
from cto_signal_scanner.utils.gpt_agent import GPTAgent
from cto_signal_scanner.utils.pdf_generator import ReportGenerator

# Load environment variables
load_dotenv()

# Determine base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['REPORTS_FOLDER'] = BASE_DIR / 'reports'
app.config['SETTINGS_FILE'] = BASE_DIR / 'settings.json'

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

@app.route('/scan', methods=['POST'])
@limiter.limit("10 per minute")  # Limit scan requests
def scan_feeds():
    try:
        days_back = int(request.form.get('days_back', 7))
        if not 1 <= days_back <= 30:
            return jsonify({'error': 'Days must be between 1 and 30'}), 400

        cutoff_date = datetime.now() - timedelta(days=days_back)
        results = []
        pdf_gen = ReportGenerator()
        pdf_gen.add_header(days_back)
        
        # Get enabled feeds from feed manager
        enabled_feeds = feed_manager.get_enabled_feeds()
        
        if not enabled_feeds:
            return jsonify({
                'success': False,
                'error': 'No valid feed sources available. Please add and enable feeds in settings.',
                'results': []
            })
        
        feed_count = 0
        for url in enabled_feeds:
            feed = feedparser.parse(url)
            if not feed.entries:
                continue
            
            feed_count += 1
            for entry in feed.entries:
                # Try to get the entry date
                date_fields = ['published', 'updated', 'created']
                entry_date = None
                for field in date_fields:
                    if hasattr(entry, field):
                        try:
                            entry_date = datetime.strptime(getattr(entry, field), '%a, %d %b %Y %H:%M:%S %z')
                            break
                        except (ValueError, TypeError):
                            continue
                
                if not entry_date or entry_date < cutoff_date:
                    continue

                try:
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
                    pdf_gen.add_article(**article_data)

                except Exception as e:
                    app.logger.error(f"Error evaluating post: {str(e)}")

        # Check if any feeds were processed
        if feed_count == 0:
            return jsonify({
                'success': False,
                'error': 'No feeds could be processed. Please check your feed URLs in settings.',
                'results': []
            })
        
        # Check if any results were found
        if not results:
            return jsonify({
                'success': False,
                'error': f'No new articles found in the last {days_back} days.',
                'results': []
            })

        # Generate PDF report
        pdf_path = pdf_gen.generate()
        
        return jsonify({
            'success': True,
            'results': results,
            'pdf_path': str(pdf_path)
        })

    except Exception as e:
        app.logger.error(f"Error in scan_feeds: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
        app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'error': 'An error occurred while downloading the file'}), 500

if __name__ == '__main__':
    app.run(debug=True) 