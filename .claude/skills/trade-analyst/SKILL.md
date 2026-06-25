---
name: trade-analyst
description: >
  Enables agents to query the Global Trade Atlas (GTA) SQL database and calculate trade competitiveness metrics. Make sure to use this skill whenever the user asks about bilateral trade flows, calculating RCA, market concentration (HHI), or performing export growth decomposition (CMSA), even if they don't explicitly name the trade analyst skill.
---

# Trade Analyst Skill

## Purpose
This skill equips the agent to perform database audits and structural trade competitiveness analysis. It queries regional/partner trade indices using SQL schemas, aggregates classifications, and calculates standardized export growth models.

## Decision Tree: Competitiveness Metrics Selection
Select the correct trade metric based on the analysis goal. **Why?** Using the academically correct index prevents misleading economic advice.

```
                            What is the objective of the study?
                                             │
                  ┌──────────────────────────┼──────────────────────────┐
                  ▼                          ▼                          ▼
      [Assess Supply Risk / Concentration] [Analyze Country Advantage] [Explain Export Growth]
                  │                          │                          │
                  ▼                          ▼                          ▼
     [Herfindahl-Hirschman (HHI)]   [Revealed Comparative (RCA)]  [Constant Market Share (CMSA)]
```

1. **Market Concentration (HHI)**:
   - Use when evaluating import dependencies or supply chain vulnerability.
   - Formula: $HHI = \sum (s_i)^2$ where $s_i$ is the market share of country $i$.
2. **Revealed Comparative Advantage (RCA)**:
   - Use to assess if a country has a comparative export strength in a specific product group.
   - Formula: $RCA = \frac{X_{c,p} / X_c}{X_{w,p} / X_w}$.
3. **Growth Decomposition (CMSA)**:
   - Use when explaining changes in export values over time (decoupling global demand vs. competitiveness).

## Execution Protocol

### Step 1 — Check SQL Database Availability
* Connect to `database/core/GTA.db` using standard sqlite libraries.
* Verify availability of metadata tables: `meta_hs2` (HS descriptions) and `meta_iso` (Country descriptors).
* **Why?** Validating table structures upfront prevents complex analytic queries from failing midway.

### Step 2 — Run Queries (Filter Mandate)
* Always filter SQL queries by `Year` and `Flow` (Import vs. Export).
* **Why?** The GTA database contains raw bilateral entries. Failing to filter by flow causes duplicate sums and invalidates RCA calculations.
* Pad HS-codes with leading zeros if they are represented as strings using:
  ```sql
  printf('%02d', HS_Code)
  ```

### Step 3 — Report Generation
* Group codes into logical aggregates (e.g. Agri-products, Automotive) for high-level brief synthesis.
* Map ISO3 codes to full country names before rendering tables or text to the user.
* **Why?** Policymakers and stakeholders find raw ISO3 codes unreadable. Presenting clear country names is a hard requirement for all deliverables.

## Examples

**Example 1:**
*Input:* "Calculate the market concentration for Thai rice exports."
*Action:* Notice that market concentration requires the HHI index. Connect to `GTA.db`, query the partner shares for HS code for rice (filtering by Flow='Export'), compute the sum of squared shares, and map ISO3 codes to partner names for the final output.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `Database Locked` | Concurrent process holding file handle on `GTA.db` | Close any open DB visualizers or scripts and retry. |
| `ZeroDivisionError in RCA` | Global export value for a product is zero or missing | Catch nulls/zeros in the denominator and return an RCA of 0. |
| `Mismatched ISO3 mapping` | Outdated country code dictionary | Fallback to raw ISO3 code if full name mapping is missing in `meta_iso`. |
