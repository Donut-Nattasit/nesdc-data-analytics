---
name: viz-playbook
description: >
  Provides visual styling rules, professional color palettes, matplotlib configuration themes, and Thai B.E. localization standards. Make sure to use this skill whenever the user asks to plot data, render a figure, style a chart, or create visual representations of macroeconomic data, even if they don't explicitly say "use the viz-playbook."
---

# Professional Visualization Playbook Skill

## Purpose
This playbook defines the standardized themes and layout rules for rendering all charts and visual figures in the workspace. It enforces clean aesthetics, high-quality typography, and local (Thai B.E.) calendar conversions.

## Decision Tree: Theme & Localization Selection
Select the correct color palette and layout theme based on target locale and audience. **Why?** Presenting data in a format native to the audience dramatically improves comprehension and trust in the analysis.

```
                            Who is the target audience?
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (Global / International)                    ▼ (Local / Thai Policy Brief)
            [English Locale Theme]                        [Thai B.E. Localized Theme]
                  │                                             │
      ┌───────────┴───────────┐                     ┌───────────┴───────────┐
      ▼                       ▼                     ▼                       ▼
[General Macro]       [Geopolitical Event]      [Font: FC Vision]       [Calendar Conversion]
(Navy: #2c3e50,       (Add event markers &      (Set assets/fonts)       (Add 543 to Gregorian
 Accent: #e74c3c)      shaded zones)                                      e.g. 2026 -> 2569)
```

## Execution Protocol

### Step 1 — Initialize Matplotlib Theme
* Prior to plotting, import and apply the visual configuration helper if available.
* The default font for both English and Thai visualizations is **FC Vision**.
* **Why?** Do not use raw primary colors (solid red/blue). Utilizing professional, low-saturation hexadecimal palettes (e.g. Navy `#2c3e50`, Grey `#718096`, Accent Red `#e74c3c`) elevates the perceived quality of the report.

### Step 2 — Font and Calendar Setup
* Ensure **FC Vision** is registered using matplotlib's font manager (fallback is configured automatically in `charts.py`).
* If "Thai localization" is requested:
  - Convert A.D. timeline indices to B.E. by adding 543 to the year list before labeling axes.
  - **Why?** Thai policy briefs officially require the Buddhist Era calendar for chronological axes.

### Step 3 — Export Standard
* Set visual figures to standard sizes (e.g. `10x6` inches).
* Save the output PNGs to `output/chart/[pipeline_name]/`.
* **Why?** Consistent dimensions prevent layout breaks when images are embedded back into Markdown reports.

## Examples

**Example 1:**
*Input:* "Generate a line chart for the GDP forecast for our local stakeholders."
*Action:* Since it is for local stakeholders, convert the X-axis years by adding 543 (e.g., 2026 becomes 2569). Apply the FC Vision font and the professional Navy/Accent Red color palette. Save it to `output/chart/gdp/`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `FC Vision not found` | The font files are missing in local directory | Check `assets/fonts/` contains correct `.ttf` files and clear matplotlib cache if needed. |
| `Overlapping tick labels` | Excess dates or long labels on x-axis | Rotate labels (e.g., `rotation=35`) or resample density of ticks using `ax.xaxis.set_major_locator`. |
| `Cutoff legend or titles` | Bounding box too tight during export | Use `plt.savefig(..., bbox_inches='tight')` to preserve legend boundaries. |
