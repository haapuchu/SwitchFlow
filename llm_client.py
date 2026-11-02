import json
import urllib.request
import urllib.error
from config import Config

class GeminiClient:
    """Zero-cost LLM client using Google Gemini free tier via REST API."""
    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        if not self.api_key:
            return "[Error: GEMINI_API_KEY not configured. Please add it to your .env file.]"

        endpoint = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.4,
                "maxOutputTokens": 2048,
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                candidates = result.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "")
                return "[LLM returned empty response]"
        except urllib.error.HTTPError as e:
            err_body = e.read().decode("utf-8")
            return f"[Gemini API HTTP Error {e.code}: {err_body}]"
        except Exception as e:
            return f"[Gemini API Request Error: {e}]"

