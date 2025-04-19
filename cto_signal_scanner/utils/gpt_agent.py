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
                "content": "You are a technology analyst specializing in enterprise technology. Your task is to evaluate tech news and provide concise summaries with relevance ratings for enterprise tech leaders."
            },
            {
                "role": "user",
                "content": f"Here's a blog post:\n\nTitle: {title}\nSummary: {summary}\nURL: {url}\n\nPlease provide:\n1. A concise 2-3 sentence summary of the key points\n2. Rate this post from 1-10 based on relevance to enterprise tech leaders\n3. One sentence explaining the rating\n4. Include the article URL\n\nFormat:\nLink: [article URL]\nSummary: [your summary]\nRating: [1-10]\nRationale: [explanation]"
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
