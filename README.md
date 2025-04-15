# CTO Signal Scanner Agent

This agent monitors RSS feeds from major technology companies, scores posts using a GPT model or Assistant, and generates tweet drafts based on audience relevance.

## Features

- RSS feed polling from AWS, Azure, GCP, etc.
- GPT-based scoring and tweet generation
- Customizable GPT model or Assistant ID
- Delivery via Slack, Notion, or CLI

## Setup

Create a `.env` file with the following:

```env
GPT_MODEL=gpt-4-0125-preview
ASSISTANT_ID=your-assistant-id-if-any
OPENAI_API_KEY=your-openai-api-key
```

## Run

```bash
python main.py
```
