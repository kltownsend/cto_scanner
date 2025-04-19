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

## Prerequisites

- Python 3.x
- OpenAI API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kltownsend/cto_scanner.git
cd cto_scanner
```

2. Install required packages:
```bash
pip install openai python-dotenv feedparser requests beautifulsoup4 httpx
```

## Configuration

1. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your-openai-api-key
GPT_MODEL=gpt-3.5-turbo
```

## Usage

Run the scanner:
```bash
python -m cto_signal_scanner.main
```

When prompted:
1. Enter the number of days to look back (1-30)
2. The scanner will process all articles published within that timeframe

### Output Format

For each article, you'll receive:
