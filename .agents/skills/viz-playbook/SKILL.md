---
name: viz-playbook
description: >
  Provides visual styling rules, professional color palettes, matplotlib configuration themes, and Thai B.E. localization standards. Use when rendering figures, charts, or styling report tables.
---

# Professional Visualization Playbook Skill

## Purpose
This playbook defines the standardized themes and layout rules for rendering all charts and visual figures in the workspace. It enforces clean aesthetics, high-quality typography, and local (Thai B.E.) calendar conversions.

## Decision Tree: Theme & Localization Selection
Select the correct color palette and layout theme based on target locale and audience:

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
* Prior to plotting, import and apply the visual configuration helper.
* The default font for both English and Thai visualizations is **FC Vision**.
* Do not use raw primary colors (solid red/blue). Utilize professional, low-saturation hexadecimal palettes (e.g. Navy `#2c3e50`, Grey `#718096`, Accent Red `#e74c3c`).

### Step 2 — Font and Calendar Setup
* Ensure **FC Vision** is registered using matplotlib's font manager (fallback is configured automatically in `charts.py`).
* If "Thai localization" is requested:
  - Convert A.D. timeline indices to B.E. by adding 543 to the year list before labeling axes.

### Step 3 — Export Standard
* Set visual figures to standard sizes (e.g. `10x6` inches).
* Save the output PNGs to `output/chart/[pipeline_name]/`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `FC Vision not found` | The font files are missing in local directory | Check `assets/fonts/` contains correct `.ttf` files and clear matplotlib cache if needed. |
| `Overlapping tick labels` | Excess dates or long labels on x-axis | Rotate labels (e.g., `rotation=35`) or resample density of ticks using `ax.xaxis.set_major_locator`. |
| `Cutoff legend or titles` | Bounding box too tight during export | Use `plt.savefig(..., bbox_inches='tight')` to preserve legend boundaries. |
