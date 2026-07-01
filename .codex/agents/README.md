# Claude Agent Emulation Index

Read the listed `.claude/agents/*.md` file before performing work in that role.

| Agent | Read when the task involves |
|---|---|
| `.claude/agents/data-fetcher.md` | CEIC, BOT, EIA, IMF, MOC, WorldBank, PortWatch, GTA SQL, S&P Global Connect retrieval |
| `.claude/agents/data-transformer.md` | Cleaning, resampling, seasonal adjustment, wide-format outputs |
| `.claude/agents/econometrician.md` | ADF, ARIMA, ARDL, VAR, ECM, cointegration, statistical model interpretation |
| `.claude/agents/data-scientist.md` | XGBoost, MIDAS, DFM, ML nowcasting, model comparison |
| `.claude/agents/viz-expert.md` | Any chart, figure, visualization, Thai/English chart localization |
| `.claude/agents/report-writer.md` | Formal Markdown or HTML economic reports |
| `.claude/agents/qualitative-analyst.md` | Web research, policy analysis, research briefs |
| `.claude/agents/weekly-news-writer.md` | Thai-language weekly international economic briefs |
| `.claude/agents/db-manager.md` | SQLite schema, indexes, VACUUM, optimization, database hygiene |

For chart work, `viz-expert` is mandatory even if another role is doing the broader task.
