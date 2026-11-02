import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from config import Config

import shutil

class GitHubBoard:
    """Interface to the Pinned GitHub Issue Board using the GitHub CLI (gh)."""
    
    def __init__(self, repo: str = "", issue_number: int = 1):
        self.gh_bin = shutil.which("gh") or r"C:\Program Files\GitHub CLI\gh.exe"
        self.repo = repo or Config.GITHUB_REPO
        self.issue = issue_number or Config.BOARD_ISSUE
        self.state_dir = Path(__file__).resolve().parent / ".board_state"
        self.state_dir.mkdir(exist_ok=True)
        self.cursor_file = self.state_dir / f"cursor_{self.issue}.txt"
        
        # Auto-detect repo if not configured
        if not self.repo:
            self.repo = self._detect_repo()

    def _detect_repo(self) -> str:
        try:
            res = subprocess.run(
                [self.gh_bin, "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"],
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip()
        except Exception:
            return ""

    def whoami(self) -> str:
        try:
            res = subprocess.run(
                [self.gh_bin, "api", "user", "-q", ".login"],
                capture_output=True, text=True, check=True
            )
            return res.stdout.strip()
        except Exception as e:
            return f"Error: gh CLI not authenticated ({e})"

    def _get_cursor(self) -> tuple[int, str]:
        if self.cursor_file.exists():
            content = self.cursor_file.read_text(encoding="utf-8").strip()
            if " " in content:
                cid, cts = content.split(" ", 1)
                return int(cid), cts
        return 0, ""

    def _set_cursor(self, comment_id: int, created_at: str):
        cur_id, _ = self._get_cursor()
        if comment_id > cur_id:
            self.cursor_file.write_text(f"{comment_id} {created_at}", encoding="utf-8")

    def post(self, sender_label: str, message: str) -> bool:
        """
        Post to the board following the strict schema: [<Human>'s <Agent>] <body text>
        """
        if not self.repo:
            print("[Board Error] GITHUB_REPO is not set.")
            return False

        if not message.startswith("[") or "'s " not in message.split("]")[0]:
            body = f"[{sender_label}] {message}"
        else:
            body = message

        try:
            cmd = [
                self.gh_bin, "api",
                f"repos/{self.repo}/issues/{self.issue}/comments",
                "-f", f"body={body}"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[Board Error] Failed to post to GitHub: {e.stderr}")
            return False

    def fetch_unread(self, agent_handle: str = "") -> List[Dict]:
        """
        Fetch comments created since the last recorded cursor and check for mentions.
        """
        if not self.repo:
            return []

        last_id, last_ts = self._get_cursor()
        
        endpoint = f"repos/{self.repo}/issues/{self.issue}/comments?per_page=50"
        if last_ts:
            endpoint += f"&since={last_ts}"

        try:
            res = subprocess.run(
                [self.gh_bin, "api", "--paginate", endpoint],
                capture_output=True, text=True, check=True
            )
            raw_comments = json.loads(res.stdout or "[]")
        except Exception as e:
            # gh may output nothing or error if network fails
            return []

        unread = []
        max_id = last_id
        max_ts = last_ts

        my_login = self.whoami().lower()

        for c in raw_comments:
            cid = c.get("id", 0)
            cts = c.get("created_at", "")
            author = c.get("user", {}).get("login", "")
            body = c.get("body", "")

            if cid <= last_id:
                continue

            if cid > max_id:
                max_id = cid
                max_ts = cts

            # Check if mentioned
            is_mention = False
            target_handles = [h.lower() for h in [agent_handle, my_login, "all"] if h]
            for handle in target_handles:
                pattern = rf"(^|[^A-Za-z0-9_-])@{re.escape(handle)}([^A-Za-z0-9_-]|$)"
                if re.search(pattern, body, re.IGNORECASE):
                    is_mention = True
                    break

            unread.append({
                "id": cid,
                "author": author,
                "created_at": cts,
                "body": body,
                "is_mention": is_mention
            })

        if max_id > last_id:
            self._set_cursor(max_id, max_ts)

        return unread

