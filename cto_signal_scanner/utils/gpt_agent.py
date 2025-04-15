import os
import sys
import httpx
from openai import OpenAI

MODEL = os.getenv("GPT_MODEL", "gpt-4-turbo-preview")

def evaluate_post(title, summary, url):
    try:
        # Create a clean transport without any proxy configuration
        transport = httpx.HTTPTransport(proxy=None)
        client = httpx.Client(transport=transport)
        
        # Initialize OpenAI client with our clean HTTP client
        openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=client
        )

        messages = [
            {
                "role": "system",
                "content": "You are a technology strategist and social media expert who writes in the tone of the CTO Advisor. Evaluate tech news for relevance to enterprise tech and suggest tweet drafts. When creating tweet drafts, always include the actual URL provided, not just [URL]."
            },
            {
                "role": "user",
                "content": f"Here's a blog post:\n\nTitle: {title}\nSummary: {summary}\nURL: {url}\n\nPlease:\n1. Score this post from 1-10 based on relevance to enterprise tech leaders.\n2. Briefly explain why.\n3. Generate 2 tweet drafts in the CTO Advisor style, including the actual URL provided."
            }
        ]

        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error type: {type(e)}")
        print(f"Error details: {str(e)}")
        raise
