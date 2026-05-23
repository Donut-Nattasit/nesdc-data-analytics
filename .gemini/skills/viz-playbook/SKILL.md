---
name: viz-playbook
description: Master playbook for professional visual styling, including standardized matplotlib themes, layouts, and Thai B.E. calendar year typography.
---

# Professional Visualization Playbook

This skill consolidates all visual presentation guidelines for the `viz_expert` and `report_writer`.

## 1. Visual Templates & Styling
* **Color Palettes**: Avoid default primary colors (red/blue). Use sophisticated palettes (e.g., `#2c3e50` for primary, `#e74c3c` for highlights).
* **Layout Structure**: Charts must have clean titles, unobtrusive gridlines (e.g., `alpha=0.3`), and explicit source watermarks at the bottom right.
* **Saving Protocol**: Save all generated charts as PNGs in `output/chart/`.

## 2. Thai Localization & Typography
* **Font Standards**: If Thai localization is explicitly requested, you must configure matplotlib to use the `TH Sarabun New` font from the `assets/` directory.
* **Calendar Conversion (B.E.)**: To convert Gregorian calendar years (A.D.) to Buddhist Era (B.E.), add 543 to the year (e.g., 2026 -> 2569). Ensure x-axis labels reflect this correctly when targeting local audiences.
* **Date Parsing**: If date data contains mixed AD/BE years, use the helper scripts inside this skill to parse and align them before plotting.
