# SwitchFlow Team Rules & Governance

## 1. Collaborative Protocol
- Humans over Agents: Human decisions always take precedence.
- The Message Board: All inter-agent tasks are logged to the designated GitHub Issue Board.
- Schema Format: Every post begins with [<Human>'s <AgentName>].
- No Acknowledgement Spam: If an agent is not directly mentioned, it notes the change but does not reply simply to acknowledge.
- Strict Boundaries: An agent must never modify code outside its assigned folder without an explicit handoff on the board.

## 2. Directory Ownership Matrix

| Area | Agent Handle | Role | Owned Directory |
|---|---|---|---|
| Backend | @backend-bot | FastAPI, schemas, database models | backend/ |
| Frontend | @frontend-bot | React, UI components, Tailwind CSS | frontend/ |
| Testing & QA | @test-bot | Pytest, validation, test coverage | tests/ |

## 3. Voice Direction with Wispr Flow
- Human leads issue voice instructions via Wispr Flow into the Switch Room or Orchestrator terminal.
- Dictated commands are automatically triaged, assigned, and tracked on GitHub.
