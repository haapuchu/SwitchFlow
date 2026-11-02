import json
import urllib.request
import urllib.error
import time
from config import Config

class GeminiClient:
    """
    Zero-cost LLM client using Google Gemini free tier via REST API.
    Features automatic retry and fallback across models if high demand (503/429) occurs.
    """
    FALLBACK_MODELS = [
        "gemini-2.5-flash",
        "gemini-flash-latest",
        "gemini-2.5-flash-lite",
        "gemini-3.5-flash",
        "gemini-2.5-pro"
    ]

    def __init__(self, api_key: str = None, model: str = "gemini-2.5-flash"):
        self.api_key = api_key or Config.GEMINI_API_KEY
        self.model = model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    def generate(self, prompt: str, system_instruction: str = "") -> str:
        if not self.api_key:
            return "[Error: GEMINI_API_KEY not configured. Please add it to your .env file.]"

        # Try designated model first, then fallback models on 503/429
        models_to_try = [self.model] + [m for m in self.FALLBACK_MODELS if m != self.model]

        last_error = ""
        for model_name in models_to_try:
            endpoint = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
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
                last_error = f"[Gemini API HTTP Error {e.code}: {err_body}]"
                # If high demand (503) or rate limit (429), try next fallback model
                if e.code in (503, 429, 404):
                    print(f"[LLM] Model '{model_name}' busy ({e.code}). Falling back to next model...")
                    time.sleep(1)
                    continue
                return last_error
            except Exception as e:
                last_error = f"[Gemini API Request Error: {e}]"
                continue

        return last_error

