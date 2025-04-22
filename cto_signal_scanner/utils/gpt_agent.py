import os
import logging
from openai import OpenAI
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Set up logger
gpt_logger = logging.getLogger('gpt_agent')
gpt_logger.setLevel(logging.INFO)

class GPTAgent:
    def __init__(self):
        load_dotenv()
        # Detect whether to use a local Ollama model
        use_ollama_env = os.getenv('USE_OLLAMA', 'false').lower() in ('true', '1', 'yes')
        llm_provider = os.getenv('LLM_PROVIDER', '').lower()
        self.use_ollama = use_ollama_env or llm_provider == 'ollama'

        if self.use_ollama:
            # Configure Ollama endpoint — defaults to local instance
            base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434/v1')
            # The OpenAI client still needs an api_key, but Ollama ignores it – we use a dummy value
            self.client = OpenAI(base_url=base_url, api_key=os.getenv('OLLAMA_API_KEY', 'ollama'))
            self.model = os.getenv('OLLAMA_MODEL', os.getenv('GPT_MODEL', 'qwen2:7b'))
            gpt_logger.info(f"GPTAgent configured to use local Ollama model: {self.model} at {base_url}")
        else:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OpenAI API key not found and USE_OLLAMA not enabled")

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
        self.logger = logging.getLogger('gpt_agent')

    def get_current_prompt(self) -> str:
        """
        Returns the current prompt template being used for evaluations.
        This is used for cache invalidation when the prompt changes.
        """
        return self.prompt_template

    def evaluate_post(self, title: str, summary: str, link: str) -> Dict[str, str]:
        """
        Evaluate a blog post using GPT.
        Returns a dictionary with the evaluation results.
        """
        try:
            # Format the prompt with the article details
            prompt = self.prompt_template.format(
                title=title,
                summary=summary,
                link=link
            )

            self.logger.info(f"Evaluating post: {title}")
            self.logger.debug(f"Prompt: {prompt}")

            # Get response from GPT / Ollama
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technology analyst specializing in cloud computing and enterprise technology."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower temperature for more consistent responses
                max_tokens=500
            )

            gpt_response = response.choices[0].message.content.strip()
            self.logger.debug(f"GPT Response: {gpt_response}")

            # Parse the response
            result = {
                'summary': '',
                'rating': '',
                'rationale': ''
            }

            lines = gpt_response.split('\n')
            current_section = None

            for line in lines:
                line = line.strip()
                if not line:
                    continue

                if line.startswith('Summary:'):
                    current_section = 'summary'
                    result['summary'] = line.replace('Summary:', '').strip()
                elif line.startswith('Rating:'):
                    current_section = 'rating'
                    result['rating'] = line.replace('Rating:', '').strip()
                elif line.startswith('Rationale:'):
                    current_section = 'rationale'
                    result['rationale'] = line.replace('Rationale:', '').strip()
                elif current_section:
                    # Append to current section if it's a continuation
                    result[current_section] += ' ' + line

            # Validate the response
            if not all(result.values()):
                self.logger.warning(f"Incomplete response for article: {title}")
                self.logger.warning(f"Response: {gpt_response}")
                self.logger.warning(f"Parsed result: {result}")

            return result

        except Exception as e:
            self.logger.error(f"Error evaluating post '{title}': {str(e)}", exc_info=True)
            return {
                'summary': f"Error: {str(e)}",
                'rating': 'Error',
                'rationale': 'Failed to analyze article'
            }
