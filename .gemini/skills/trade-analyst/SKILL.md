---
name: trade-analyst
description: Expert in global trade analysis using the GTA database. Use when searching for HS-code descriptions, calculating trade metrics (RCA, market share), or analyzing bilateral trade flows and competitiveness.
---

# Trade Analyst Skill

## Overview
This skill empowers the `trade_analyst` to perform high-fidelity trade research using the **Global Trade Atlas (GTA)** database and specialized economic formulas.

## Key Workflows

### 1. GTA Data Exploration
When queried about trade flows or HS codes, use the schema and SQL patterns defined in [references/gta_reference.md](references/gta_reference.md).

### 2. Trade Competitiveness Analysis
*   **RCA (Revealed Comparative Advantage)**: Calculate this to determine if a country has a structural advantage in a product.
*   **Market Concentration (HHI)**: Use to assess supply chain risk.
*   **Growth Decomposition**: Analyze if export growth is driven by market share gains or global demand growth.

### 3. Reporting Standards
*   Always use ISO3 country codes for data processing, but translate to full names in final reports.
*   Group HS codes into logical clusters (e.g., Electronics, Agri-products) for better synthesis.
*   Highlight "Top 5" partners or products unless specified otherwise.

## Specialized Tools
- **GTA Database**: `output/data/database/GTA.db`
- **Metadata**: `meta_hs2` (HS descriptions), `meta_iso` (Country names)

## SQL Best Practices for Trade
*   Always filter by `Year` and `Flow` (Import/Export) to avoid double-counting.
*   Use `printf('%02d', HS_Code)` to ensure HS2 codes have leading zeros for correct string matching if necessary.
*   Perform aggregations (SUM) on `Value` when grouping by year or region.
