# Codex Instructions

This repository's Codex behavior is defined by `../AGENTS.md`.

In short: act as the Claude workspace agent by reading and following `../CLAUDE.md` and
the relevant files under `../.claude/`.

For every substantive task:

1. Read `../CLAUDE.md`.
2. Read matching command instructions from `../.claude/commands/` when the user invokes
   or implies a slash command.
3. Read matching skill instructions from `../.claude/skills/*/SKILL.md` before complex
   data, model, chart, report, or pipeline work.
4. Read matching agent instructions from `../.claude/agents/` and emulate that specialist
   role.

Keep `.claude/` canonical. Do not fork or manually copy its detailed content into
`.codex/`.
