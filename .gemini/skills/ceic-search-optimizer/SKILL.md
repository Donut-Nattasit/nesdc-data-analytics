---
name: ceic-search-optimizer
description: Advanced strategies for searching and selecting high-quality macroeconomic data from the CEIC database. Use when @ceic_fetcher needs to find the most comparable, standardized, or specific series across millions of entries.
---

# CEIC Search Optimizer

This skill optimizes the data discovery process in CEIC, ensuring that agents select the highest quality series while minimizing "search noise."

## Core Workflow

1.  **Analyze Request**: Identify if the user needs cross-country comparability (standardized) or country-specific depth (localized).
2.  **Strategic Search & Auto-Refinement**:
    - Use optimized keywords based on [search-heuristics.md](references/search-heuristics.md).
    - **Noise Reduction**: If results contain high "Trade Partner" noise (e.g., "to [Country]" or "from [Country]"), automatically perform a refined search using exclusionary keywords or specific GEM patterns.
    - Prioritize databases according to the [database-prioritization.md](references/database-prioritization.md) hierarchy.
3.  **GEM Pattern Proactivity**:
    - For regional or cross-country requests (e.g., ASEAN, G20), identify the **Global Economic Monitor (GEM)** pattern for one pilot country.
    - **Pattern Replication**: Once a pattern is confirmed (e.g., `Real GDP: YoY: Quarterly: Thailand`), proactively generate and search for matching series for all requested countries to ensure perfect data comparability.
4.  **Verification & Data Quality**:
    - **Unit Check**: Ensure the selected Series ID matches the requested metric (e.g., % YoY vs. Index level).
    - **Frequency Check**: Confirm the frequency aligns with the research goal (e.g., Quarterly for GDP, Monthly for CPI).

## Database Prioritization
Refer to [database-prioritization.md](references/database-prioritization.md) to choose the right database tier:
- **Tier 1**: World Trend Plus / GEM (Standardized)
- **Tier 2**: Premium Databases (Depth/China)
- **Tier 3**: Global Database (National Sources)

## Search Heuristics
Refer to [search-heuristics.md](references/search-heuristics.md) to refine keywords and apply exclusionary logic.

## Selection Criteria
When presenting results to the user, the agent should favor series that:
1.  Have the longest historical coverage.
2.  Are updated within the last 1-3 months (for monthly data).
3.  Are part of the World Trend Plus database.
