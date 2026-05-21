---
name: fetcher-api-optimizer
description: Optimized API patterns for BOT and EIA data retrieval. Use for @bot_fetcher and @eia_fetcher to ensure efficient batch fetching, proper pagination, and standardized output formatting.
---

# Fetcher API Optimizer Skill

## Workflow
1. **Discovery**: Use client metadata methods to find Series IDs.
2. **Batching**: Prioritize fetching multiple series in a single request (especially for EIA STEO).
3. **Format**: Ensure output CSVs are long-format for single series and wide-format for multiple series.
4. **Cleanup**: Always delete temporary Python scripts in `temp/` after execution.

## Reference Materials
- [api_patterns.md](references/api_patterns.md): Code snippets for BOT and EIA optimized retrieval.
