import os
from openai import OpenAI
from typing import Optional

class GPTAgent:
    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OpenAI API key not found in environment variables")
        
        # Initialize OpenAI client with minimal configuration
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv('GPT_MODEL', 'gpt-3.5-turbo')
        self.prompt_template = os.getenv('GPT_PROMPT', '''You are a technology analyst specializing in cloud computing and enterprise technology. 
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
Rationale: [your rationale]''')

    def evaluate_post(self, title: str, summary: str, link: str) -> str:
        """
        Evaluate a blog post using GPT.
        Returns a formatted string with the evaluation results.
        """
        try:
            # Format the prompt with the article details
            prompt = self.prompt_template.format(
                title=title,
                summary=summary,
                link=link
            )

            # Get response from GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technology analyst specializing in cloud computing and enterprise technology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error evaluating post: {str(e)}"
