# CTO Signal Scanner

An intelligent RSS feed scanner that monitors major tech companies' blogs, evaluates content relevance for enterprise technology leaders, and provides concise summaries with ratings.

## Features

- **Automated Feed Monitoring:** Scans RSS feeds from:
  - AWS
  - Microsoft Azure
  - Google Cloud
  - Cloudflare
  - Cisco
  - Red Hat
- **Smart Content Evaluation:** Uses GPT to analyze and rate content relevance
- **Date-Based Filtering:** Customizable date range for content scanning
- **Cache Management:** Prevents duplicate processing within each run
- **Robust Feed Parsing:** Handles various RSS/Atom formats with fallback mechanisms
- **PDF Report Generation:** Creates detailed PDF reports of all processed articles
- **Web Interface:** User-friendly web UI for scanning and viewing results

## Installation Guide

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI's website](https://platform.openai.com/api-keys))

### Step-by-Step Installation

1. **Install Python**
   - Download and install Python from [python.org](https://www.python.org/downloads/)
   - During installation, make sure to check "Add Python to PATH"
   - Verify installation by opening a terminal/command prompt and typing:
     ```bash
     python --version
     ```

2. **Download the Application**
   - Download the latest release from GitHub
   - Or clone the repository:
     ```bash
     git clone https://github.com/kltownsend/cto_scanner.git
     cd cto_scanner
     ```

3. **Set Up Virtual Environment** (recommended)
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

4. **Install Dependencies**
   - Run the following command:
     ```bash
     pip install -r requirements.txt
     ```

5. **Configure the Application**
   - Create a `.env` file in the project root
   - Add your OpenAI API key:
     ```
     OPENAI_API_KEY=your-api-key-here
     GPT_MODEL=gpt-3.5-turbo
     ```

6. **Start the Application**
   - Run the web interface:
     ```bash
     python run_web.py
     ```
   - Open your browser and go to: http://localhost:5000

### Troubleshooting

#### Common Issues

1. **"Python not found" error**
   - Make sure Python is installed and added to PATH
   - Try using `python3` instead of `python`

2. **"Module not found" errors**
   - Make sure you're in the virtual environment (you should see `(venv)` in your terminal)
   - Try reinstalling dependencies: `pip install -r requirements.txt`

3. **Port 5000 already in use**
   - On macOS, port 5000 might be used by AirPlay
   - Change the port in `run_web.py` to 5001 or another available port

4. **OpenAI API errors**
   - Verify your API key is correct in the `.env` file
   - Check your OpenAI account for any usage limits or issues

#### Getting Help

- Check the [Issues](https://github.com/kltownsend/cto_scanner/issues) page
- Create a new issue if you encounter a problem
- Join our [Discord community](link-to-discord) for real-time support

## Usage Guide

### Web Interface

1. **First Time Setup**
   - Open http://localhost:5000 in your browser
   - Click the settings icon (⚙️) in the top right
   - Enter your OpenAI API key
   - Select your preferred GPT model
   - Save settings

2. **Running a Scan**
   - Enter the number of days to look back (1-30)
   - Click "Start Scan"
   - Wait for the scan to complete
   - View and filter results
   - Download PDF report if desired

3. **Managing Feeds**
   - Go to Settings
   - Add or remove RSS feeds
   - Test feed URLs before adding
   - Enable/disable specific feeds

### Command Line Usage

For advanced users, you can also use the command-line interface:

```bash
python -m cto_signal_scanner.main
```

## Development

### Setting Up Development Environment

```bash
pip install -r requirements-dev.txt
```

### Running Tests

```bash
python -m test_env
```

### Project Structure

```
cto_signal_scanner/
├── main.py                 # Command-line entry point
├── utils/
│   ├── gpt_agent.py        # GPT integration
│   ├── feed_sources.py     # RSS feed definitions
│   ├── pdf_generator.py    # PDF report generation
│   └── feed_manager.py     # Feed management
├── web/
│   ├── app.py              # Flask web application
│   ├── static/             # Static files
│   └── templates/          # HTML templates
└── reports/                # Generated PDF reports
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
