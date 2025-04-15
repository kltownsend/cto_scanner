import os
from dotenv import load_dotenv

def check_env():
    print("Loading environment variables...")
    load_dotenv()
    
    # Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        # Only show first few characters for security
        print(f"✓ OPENAI_API_KEY found: {api_key[:8]}...")
    else:
        print("✗ OPENAI_API_KEY not found!")
    
    # Check GPT Model
    model = os.getenv("GPT_MODEL")
    if model:
        print(f"✓ GPT_MODEL found: {model}")
    else:
        print("✗ GPT_MODEL not found!")
    
    # Check Assistant ID (optional)
    assistant_id = os.getenv("ASSISTANT_ID")
    if assistant_id:
        print(f"✓ ASSISTANT_ID found: {assistant_id}")
    else:
        print("ℹ ASSISTANT_ID not found (optional)")

if __name__ == "__main__":
    check_env() 