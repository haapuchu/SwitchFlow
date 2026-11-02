import sys
import os
import re
from typing import Dict, Optional, List
from pathlib import Path

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from llm_client import GeminiClient
from github_board import GitHubBoard
from switch_client import SwitchClient
from config import Config

class AgentWorker:
    """
    Autonomous agent worker that:
    1. Reads board tasks and chat instructions.
    2. Uses Gemini Flash to generate implementation plans and code.
    3. Strictly writes files only within its assigned directory.
    4. Performs self-contained file generation on disk.
    5. Posts status updates back to the GitHub board and Switch room.
    """
    def __init__(self, name: str, role: str, handle: str, owned_folder: str):
        self.name = name                      # e.g. "BackendBot"
        self.role = role                      # e.g. "FastAPI and database developer"
        self.handle = handle                  # e.g. "backend-bot"
        self.owned_folder = Path(__file__).resolve().parent / owned_folder
        self.owned_folder.mkdir(parents=True, exist_ok=True)
        
        self.llm = GeminiClient()
        self.board = GitHubBoard()
        self.switch = SwitchClient()
        self.human = Config.HUMAN_NAME

    def get_system_instruction(self) -> str:
        return f"""You are {self.name}, an autonomous software engineer specialized as: {self.role}.
You work on a development team led by '{self.human}' alongside other autonomous bots.
You strictly own and write files inside the directory: '{self.owned_folder.name}/'.
Never touch files outside your assigned directory.

When writing code:
1. Provide a 1-sentence technical summary.
2. Put each file in a fenced code block with a filename header on the first line inside or right above the code block.
   Example:
   ```python
   # filename: {self.owned_folder.name}/main.py
   ...
   ```
3. Provide complete, runnable code (no placeholders or truncated snippets).
4. End with a handoff message indicating what you built and who should pick up next."""

    def extract_and_write_files(self, response_text: str) -> List[str]:
        """
        Parses code blocks from the LLM response and saves them to the owned folder.
        """
        written_files = []
        # Match code blocks with an optional filename indicator
        pattern = r"```(?:python|javascript|typescript|json|html|css|bash|markdown)?\s*\n(?:#\s*filename:\s*([^\n]+)\n)?(.*?)```"
        matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)

        for idx, (filename_hint, code_content) in enumerate(matches):
            code_content = code_content.strip()
            if not code_content:
                continue

            # Resolve target filename
            if filename_hint and filename_hint.strip():
                clean_name = filename_hint.strip().replace("\\", "/").split("/")[-1]
            else:
                # Fallback naming based on role
                ext = ".py" if "backend" in self.handle or "test" in self.handle else ".js"
                clean_name = f"generated_module_{idx+1}{ext}"

            target_path = self.owned_folder / clean_name
            try:
                target_path.write_text(code_content, encoding="utf-8")
                written_files.append(str(target_path.relative_to(self.owned_folder.parent)))
                print(f"[{self.name}] Wrote file: {target_path.name} ({len(code_content)} bytes)")
            except Exception as e:
                print(f"[{self.name}] Failed to write {clean_name}: {e}")

        return written_files

    def handle_task(self, task_description: str, sender: str) -> str:
        print(f"\n[{self.name}] Processing task from @{sender}...")
        prompt = f"""Task assigned by @{sender}:
{task_description}

Remember to output working code for files that belong inside '{self.owned_folder.name}/'."""

        response = self.llm.generate(prompt, system_instruction=self.get_system_instruction())
        
        # Write generated code blocks directly to disk in the agent's folder
        files_created = self.extract_and_write_files(response)

        # Prepare summary for GitHub Board and Switch Room
        file_summary = f"Created/Updated: {', '.join(files_created)}" if files_created else "Task processed."
        board_msg = f"[{self.human}'s {self.name}] @{sender} {file_summary}\n\nPlan & Details:\n{response[:300]}..."
        self.board.post(f"{self.human}'s {self.name}", board_msg)

        # Post real-time update into the Switch Room
        chat_msg = f"[{self.name}] Task finished for @{sender}. {file_summary}. Detailed log pushed to Board Issue #{self.board.issue}."
        self.switch.send_room_message(self.name, chat_msg)

        return response
