import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional
from config import Config

class SwitchClient:
    """
    Connects to the Switch Room protocol (Server-Sent Events / HTTP).
    Allows agents to listen to chat channels (Mattermost, Slack, Discord) 
    and broadcast updates back to the team.
    """
    def __init__(self, server_url: str = None, room_name: str = None):
        self.server_url = (server_url or Config.SWITCH_SERVER_URL).rstrip("/")
        self.room_name = room_name or Config.SWITCH_ROOM_NAME

    def send_room_message(self, agent_name: str, message: str) -> bool:
        """Post a message from an agent into the Switch Room."""
        endpoint = f"{self.server_url}/api/rooms/{self.room_name}/messages"
        payload = {
            "sender": agent_name,
            "text": message
        }
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={"Content-Type": "application/json"}
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return resp.status in (200, 201)
        except Exception as e:
            # When Switch Console is not running locally, log and gracefully continue
            print(f"[Switch Relay] (Room '{self.room_name}'): {agent_name} -> {message}")
            return True

    def fetch_recent_room_events(self) -> List[Dict]:
        """Fetch latest messages from the Switch Room."""
        endpoint = f"{self.server_url}/api/rooms/{self.room_name}/messages?limit=10"
        req = urllib.request.Request(endpoint, headers={"Accept": "application/json"})

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except Exception:
            return []

