# Claude Slash Command Index

When the user invokes one of these commands, read the corresponding command file before
doing anything else.

| User request | Claude command file |
|---|---|
| `/energy-forecast`, energy forecast, Dubai oil forecast | `.claude/commands/energy-forecast.md` |
| `/cpi-forecast`, CPI forecast | `.claude/commands/cpi-forecast.md` |
| `/food-shock`, prepared food shock | `.claude/commands/food-shock.md` |
| `/energy-forecast-lr`, long-run energy forecast | `.claude/commands/energy-forecast-lr.md` |
| `/ex-im-forecast`, export/import price forecast | `.claude/commands/ex-im-forecast.md` |
| `/deflator_prediction`, deflator prediction | No Claude command file exists; use `.claude/skills/deflator_prediction/SKILL.md` |
| `/thailand-price-system`, Thailand price system | `.claude/commands/thailand-price-system.md` |
| `/weekly-news`, weekly news brief | `.claude/commands/weekly-news.md` |
| `/export-html`, Markdown to HTML export | `.claude/commands/export-html.md` |
| `/maintain`, maintenance | `.claude/commands/maintain.md` |

Follow each command's confirmation, pre-check, execution, output, and next-step
instructions.
