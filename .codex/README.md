# Codex Claude Compatibility Layer

This directory tells Codex how to perform like the Claude setup already present in this
workspace.

`.claude/` remains the source of truth. These files are adapters and indexes for Codex,
not independent copies of the Claude configuration.

## Files

- `../AGENTS.md`: primary Codex-discoverable workspace instructions.
- `CLAUDE_COMPATIBILITY.md`: operating protocol for imitating Claude.
- `commands/README.md`: routing table for Claude slash commands.
- `agents/README.md`: routing table for Claude sub-agent emulation.
- `skills/README.md`: routing table for Claude skill loading.

## Runtime Rule

Before executing meaningful work, Codex should read:

1. `../CLAUDE.md`
2. Any matching `.claude/commands/*.md`
3. Any relevant `.claude/skills/*/SKILL.md`
4. Any relevant `.claude/agents/*.md`

This keeps Codex aligned with future edits to `.claude`.
