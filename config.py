import os
from pathlib import Path
from dotenv import load_dotenv

# Load from .env if present
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    GITHUB_REPO = os.getenv("GITHUB_REPO", "")
    BOARD_ISSUE = int(os.getenv("BOARD_ISSUE", "1"))
    POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "15"))  # seconds
    
    # Switch room protocol endpoints
    SWITCH_SERVER_URL = os.getenv("SWITCH_SERVER_URL", "http://localhost:8080")
    SWITCH_ROOM_NAME = os.getenv("SWITCH_ROOM_NAME", "switchboard-war-room")
    
    # Human handler label for voice dictation
    HUMAN_NAME = os.getenv("HUMAN_NAME", "Developer")

