Convert a Markdown report to a self-contained HTML file with all images embedded as base64.

**Show the user recent reports** by listing files in `report/` (and pipeline subdirectories) sorted by modification date, then ask which one to convert.

**Follow the instructions in `.claude/skills/md-to-html/SKILL.md`** for the exact command to run.

The script produces a single `.html` file where all chart images are embedded — suitable for email or sharing without needing the chart files.

**Output:** Same directory as the source `.md` file, with `.html` extension.
