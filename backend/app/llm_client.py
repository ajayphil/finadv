import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

class OpenRouterClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or OPENROUTER_API_KEY
        if not self.api_key:
            raise RuntimeError("OPENROUTER_API_KEY not set in environment")
        self.url = "https://api.openrouter.ai/v1/chat/completions"

    def chat(self, messages, model="gpt-4o-mini", max_tokens=800):
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        r = requests.post(self.url, json=payload, headers=headers, timeout=60)
        r.raise_for_status()
        data = r.json()
        # Try to return assistant text in a safe way
        # OpenRouter returns choices -> message -> content similar to OpenAI Chat
        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            return data
