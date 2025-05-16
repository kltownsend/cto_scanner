# CTO Signal Scanner

A tool for scanning and analyzing technology blog posts to identify relevant content for CTOs and technology leaders.

## Features

- Scans multiple technology blogs and news sources
- Uses AI to analyze and rate content relevance
- Generates PDF reports with summaries and ratings
- Web interface for viewing and managing scans
- Configurable rating system (1-10 scale)
- Support for both OpenAI and local Ollama models

## Rating System

Articles are rated on a scale of 1-10 based on their relevance to CTOs and technology leaders:
- 1-3: Low relevance
- 4-6: Medium relevance
- 7-10: High relevance

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/cto_signal_scanner.git
cd cto_signal_scanner
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Create a `.env` file with your configuration:
```env
OPENAI_API_KEY=your_api_key_here
GPT_MODEL=gpt-3.5-turbo
```

## Usage

### Web Interface

1. Start the web server:
```bash
python run_web.py
```

2. Open your browser and navigate to `http://localhost:5000`

### Command Line

1. Run a scan:
```bash
python run_scan.py
```

2. Generate a report:
```bash
python run_report.py
```

## Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key
- `GPT_MODEL`: The GPT model to use (default: gpt-3.5-turbo)
- `USE_OLLAMA`: Set to 'true' to use local Ollama model
- `OLLAMA_BASE_URL`: URL for Ollama API (default: http://localhost:11434/v1)
- `OLLAMA_MODEL`: Model to use with Ollama (default: qwen2:7b)

### Blog Sources

Edit `cto_signal_scanner/config/blog_sources.py` to add or modify blog sources.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
