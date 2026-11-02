import time
import sys
from typing import Dict

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from agent_worker import AgentWorker
from github_board import GitHubBoard
from switch_client import SwitchClient
from config import Config

class SwitchBoardOrchestrator:
    """
    SwitchBoard: Voice-Driven Multi-Agent War Room Orchestrator.
    Connects:
      - Voice input (Wispr Flow)
      - Chat Room (Switch / Mattermost)
      - Code Collaboration Bus (GitHub Pinned Board)
      - Autonomous Workers (Free Gemini LLM)
    """
    def __init__(self):
        self.board = GitHubBoard()
        self.switch = SwitchClient()
        
        # Instantiate the agent team with designated folder ownership
        self.agents: Dict[str, AgentWorker] = {
            "backend-bot": AgentWorker(
                name="BackendBot",
                role="FastAPI and database developer",
                handle="backend-bot",
                owned_folder="backend"
            ),
            "frontend-bot": AgentWorker(
                name="FrontendBot",
                role="React & Tailwind UI developer",
                handle="frontend-bot",
                owned_folder="frontend"
            ),
            "test-bot": AgentWorker(
                name="TestBot",
                role="QA and integration test engineer",
                handle="test-bot",
                owned_folder="tests"
            )
        }

    def process_voice_instruction(self, voice_text: str):
        """
        Receives text dictated via Wispr Flow and dispatches it
        to the Switch Room and the GitHub Board.
        """
        print(f"\n[Wispr Voice Command]: \"{voice_text}\"")
        
        # Broadcast into Switch Chat
        self.switch.send_room_message(Config.HUMAN_NAME, f"[Voice Command]: {voice_text}")
        
        # Triage and post to GitHub Board
        board_post = f"[{Config.HUMAN_NAME}'s Voice] @all New instruction: {voice_text}"
        self.board.post(f"{Config.HUMAN_NAME}'s Voice", board_post)
        
        # Determine target agent by keyword or default to backend
        target_handle = "backend-bot"
        if any(k in voice_text.lower() for k in ["ui", "frontend", "css", "component", "page"]):
            target_handle = "frontend-bot"
        elif any(k in voice_text.lower() for k in ["test", "verify", "coverage", "assert"]):
            target_handle = "test-bot"

        agent = self.agents[target_handle]
        res = agent.handle_task(voice_text, sender=Config.HUMAN_NAME)
        print(f"\n[Done] Response from {agent.name}:\n{res}\n")

    def run_poll_cycle(self):
        """Poll the GitHub Board for mentions of our agents."""
        for handle, agent in self.agents.items():
            unreads = self.board.fetch_unread(agent_handle=handle)
            for item in unreads:
                if item.get("is_mention"):
                    print(f"[Alert] Mention detected for @{handle} from @{item['author']}")
                    agent.handle_task(item["body"], sender=item["author"])

    def start_loop(self, interval: int = 15):
        print("\n[Init] SwitchFlow Orchestrator started.")
        print("[Info] Use Wispr Flow to dictate prompts directly into this console or chat app.")
        print(f"[Info] Polling GitHub issue #{Config.BOARD_ISSUE} every {interval}s (Ctrl+C to stop)...\n")
        
        try:
            while True:
                self.run_poll_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n[Halt] Orchestrator stopped.")

def main():
    orch = SwitchBoardOrchestrator()

    if len(sys.argv) > 1 and sys.argv[1] == "--voice":
        print("\n[Wispr Flow Dictation Mode]")
        print("Hold your Wispr hotkey, speak your prompt, and press Enter:")
        prompt = input("> ")
        if prompt.strip():
            orch.process_voice_instruction(prompt.strip())
    elif len(sys.argv) > 1 and sys.argv[1] == "--demo":
        print("\n[Demo] Running multi-agent test scenario...")
        sample_task = "Create a health-check API endpoint in FastAPI and an accompanying test case."
        orch.process_voice_instruction(sample_task)
    else:
        print("""
==================================================
   SWITCHFLOW - Multi-Agent Orchestration Engine
==================================================
Usage:
  python orchestrator.py --voice    Dictate or type an instruction via Wispr
  python orchestrator.py --demo     Run an end-to-end multi-agent test
  python orchestrator.py --loop     Start the autonomous board watcher loop
""")

if __name__ == "__main__":
    main()
