import sys
from typing import Dict, Optional
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from llm_client import GeminiClient
from github_board import GitHubBoard
from switch_client import SwitchClient
from config import Config

class AgentWorker:
    """
    An autonomous agent worker that:
    1. Reads board tasks and chat messages.
    2. Executes tasks using free Gemini Flash.
    3. Respects folder ownership rules from AGENTS.md.
    4. Posts status updates back to the GitHub board and Switch room.
    """
    def __init__(self, name: str, role: str, handle: str, owned_folder: str):
        self.name = name                      # e.g. "BackendBot"
        self.role = role                      # e.g. "FastAPI Backend Developer"
        self.handle = handle                  # e.g. "backend-bot"
        self.owned_folder = Path(__file__).resolve().parent / owned_folder
        self.owned_folder.mkdir(parents=True, exist_ok=True)
        
        self.llm = GeminiClient()
        self.board = GitHubBoard()
        self.switch = SwitchClient()
        self.human = Config.HUMAN_NAME

    def get_system_instruction(self) -> str:
        return f"""You are {self.name}, an AI software developer specialized as: {self.role}.
You work on a hackathon team with human lead '{self.human}' and other autonomous agents.
You strictly own and write files in the directory: '{self.owned_folder.name}/'.
Never edit files outside your assigned directory.
Always keep responses concise, code-centric, and actionable.
When asked to write code, provide full working code blocks with filenames."""

    def handle_task(self, task_description: str, sender: str) -> str:
        print(f"\n[{self.name}] Processing task from @{sender}...")
        prompt = f"""Task assigned by @{sender}:
{task_description}

Provide:
1. A 1-2 sentence plan.
2. The exact code or files to create/update.
3. A handoff message for the next agent or human."""

        response = self.llm.generate(prompt, system_instruction=self.get_system_instruction())
        
        # Post back to the GitHub Issue Board
        board_msg = f"[{self.human}'s {self.name}] @{sender} Finished task. Summary:\n{response[:250]}..."
        self.board.post(f"{self.human}'s {self.name}", board_msg)

        # Notify the Switch Chat Room for the human team to see in real-time
        chat_msg = f"[{self.name}] Task complete for @{sender}. Updated {self.owned_folder.name}/. Details logged to Board."
        self.switch.send_room_message(self.name, chat_msg)

        return response
