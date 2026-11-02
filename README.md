# SwitchFlow: Voice-Driven Multi-Agent Orchestration

Built for the Flip the Switch Hackathon (WeMakeDevs x DevTools Academy x Switch AI).  
Tracks: Best Business Workflow & Code with Wispr.

SwitchFlow bridges Team Chat (Switch Rooms / Mattermost) with GitHub Issue Boards, allowing engineers to coordinate autonomous coding agents using voice input (via Wispr Flow) on zero-cost free-tier AI infrastructure.

---

## Key Capabilities

1. Voice-Directed Orchestration (Wispr Flow): Dictate architecture specs, features, and task assignments. SwitchFlow captures spoken instructions and delegates them to the appropriate agent.
2. Team Chat Integration (Switch AI): Agents join the local Switch room, providing real-time status updates, pull request links, and approval notifications.
3. Asynchronous Coordination Bus (GitHub Issue Board): Agents use a single pinned GitHub Issue as a persistent, rate-limited message bus to coordinate handoffs without merge conflicts.
4. Zero-Cost Infrastructure: Runs entirely on free Gemini 1.5 Flash (via Google AI Studio), GitHub CLI, and local open-source Docker runtimes.

---

## Quickstart

### 1. Environment Setup
```bash
git clone <your-repo>
cd switchflow
pip install -r requirements.txt
cp .env.example .env
```

### 2. Configure Credentials in `.env`
- Provide Gemini API key from Google AI Studio.
- Ensure GitHub CLI is authenticated: `gh auth login`.

### 3. Voice Command Mode (Wispr Flow)
Hold your Wispr Flow hotkey, speak your instruction, and release:
```bash
python orchestrator.py --voice
```

### 4. Background Board Watcher
```bash
python orchestrator.py --loop
```
