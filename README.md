# CTO Signal Scanner

An intelligent RSS feed scanner that monitors major tech companies' blogs, evaluates content relevance for enterprise technology leaders, and provides concise summaries with ratings.

## Features

- **Advanced Feed Management:**
  - Default feeds from major tech companies (AWS, Azure, GCP, etc.)
  - Custom feed support with separate storage
  - Feed validation and health monitoring
  - Protected default feeds with flexible custom feed management
- **Automated Feed Monitoring:** Scans RSS feeds from:
  - AWS
  - Microsoft Azure
  - Google Cloud
  - Cloudflare
  - Cisco
  - Red Hat
  - Custom sources (add your own RSS feeds)
- **Smart Content Evaluation:** Uses GPT to analyze and rate content relevance
- **Date-Based Filtering:** Customizable date range for content scanning (1-30 days)
- **Cache Management:** Prevents duplicate processing within each run
- **Robust Feed Parsing:** Handles various RSS/Atom formats with fallback mechanisms
- **PDF Report Generation:** Creates detailed PDF reports of all processed articles
- **Web Interface:** User-friendly web UI for scanning and viewing results
- **Dark Mode Support:** Toggle between light and dark themes
- **Mobile Responsive:** Works well on all device sizes
- **Enhanced Security:** CSRF protection and secure session management
- **Results Management:** Filter and sort articles by rating and date
- **Settings Management:** Configure API keys and feed sources through web interface
- **GPT Response Caching:** Improves performance and handles rate limits
- **Real-time Progress Updates:** Shows article processing progress during scans
- **Detailed Error Handling:** Clear error messages and proper error recovery
- **Configurable Port:** Set through environment variables (default: 5001)

## Installation Guide

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI's website](https://platform.openai.com/api-keys))

### Quick Installation

1. **Install Python Development Tools**
   - On macOS:
     ```bash
     brew install python@3.12
     ```
   - On Ubuntu/Debian:
     ```bash
     sudo apt-get install python3-venv
     ```

2. **Download and Install**
   - Download the latest release from GitHub
   - Or clone the repository:
     ```bash
     git clone https://github.com/kltownsend/cto_scanner.git
     cd cto_scanner
     ```

3. **Run Installation Script**
   - On macOS/Linux:
     ```bash
     ./install.sh
     ```
   - On Windows:
     ```bash
     python install.py
     ```

   The installation script will:
   - Create a virtual environment
   - Install dependencies
   - Set up configuration files
   - Configure the appropriate port (5001 for macOS, 5000 for others)

### Manual Installation

If you prefer to install manually:

1. **Set Up Virtual Environment**
   - Windows:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the Application**
   - Create a `.env` file in the project root
   - Add your configuration:
     ```
     OPENAI_API_KEY=your-api-key-here
     GPT_MODEL=gpt-4.1  # Default model, can be changed to gpt-3.5-turbo or gpt-4
     PORT=5001  # Default port, change if needed
     FLASK_SECRET_KEY=your-secret-key-here  # Optional, will be auto-generated if not provided
     ```

4. **Run the Application**
   ```bash
   python -m cto_signal_scanner.run_web
   ```

   The application will be available at `http://localhost:5001` by default.

## Usage

1. **Start a Scan**
   - Open the web interface
   - Enter the number of days to look back (1-30)
   - Click "Start Scan"
   - Monitor progress in real-time
   - View results when complete

2. **View and Filter Results**
   - Filter articles by rating (High/Medium/Low)
   - Sort by date or rating
   - Download PDF report
   - View article details and links

3. **Configure Settings**
   - Access settings through the gear icon
   - Update API keys
   - Manage feed sources:
     - View default feeds (protected from removal)
     - Add custom RSS feeds
     - Remove custom feeds
     - Monitor feed health status
   - Configure GPT model and prompts

4. **Managing Feeds**
   - Default feeds are protected and automatically maintained
   - Custom feeds can be added using any valid RSS feed URL
   - Custom feeds are stored separately and preserved during updates
   - All feeds are automatically validated and monitored for health
   - Invalid feeds are clearly marked in the interface

## Troubleshooting

- **Port Conflicts:** If port 5001 is in use, change the `PORT` value in your `.env` file
- **API Key Issues:** Ensure your OpenAI API key is valid and has sufficient credits
- **Feed Issues:**
  - Default feeds cannot be removed but will be automatically updated
  - Custom feeds can be removed if they're no longer needed
  - Invalid feed URLs will be marked as such in the interface
  - Check feed URLs in settings if articles aren't being processed
- **Session Issues:** Clear browser cookies if experiencing session-related problems

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
