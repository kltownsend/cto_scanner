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
pip install -r requirements.txt
```

For development:
```bash
pip install -r requirements-dev.txt
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

- **Title:** The original article title
- **Link:** Direct URL to the article
- **Summary:** A concise summary of the article's content
- **Rating:** Relevance rating for CTOs and technology leaders
- **Rationale:** Explanation of the rating and key points

The results are:
1. Displayed in the console in real-time
2. Saved to a PDF report in the `reports/` directory
3. Cached to prevent duplicate processing in future runs

### Cache Management

The scanner maintains a cache of processed entries in `processed_entries.json`. This ensures:
- No duplicate processing of articles
- Efficient subsequent runs
- Tracking of processed content

To clear the cache and reprocess all articles, simply delete the `processed_entries.json` file.
