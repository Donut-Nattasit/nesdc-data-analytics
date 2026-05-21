# Visualization Troubleshooting

This document records known errors, pitfalls, and solutions for rendering charts in this workspace.

## Font Management (`TH Sarabun New`)
- **Missing Font**: If `TH Sarabun New` is not installed on the system, Altair rendering via `vl-convert` might fail or fallback to a default font.
- **Registration**: `src/visualization/charts.py` automatically registers fonts from `assets/fonts/`. Ensure the font files are present there.
- **Matplotlib Config**: For Matplotlib, use:
  ```python
  import matplotlib.pyplot as plt
  plt.rcParams['font.family'] = 'TH Sarabun New'
  ```

## Altair Specifics
- **Data Limit**: Altair has a default limit of 5,000 rows. For larger datasets, either sample the data or switch to Matplotlib/Seaborn.
- **Sorting String Labels**: When using Thai labels (e.g., "Q1-2567"), Altair sorts alphabetically. Always pass a sorted list of unique labels to the `sort` parameter of `alt.X`.

## Thai Localization
- **Melt Trap**: If using `thai_utils` functions, ensure `thai_year`, `thai_quarter`, etc., are included in `id_vars` when melting DataFrames, or they will be plotted as values.
- **Chronology**: Always ensure the DataFrame is sorted by the original `date` column before generating Thai labels to maintain correct sequence.

## PNG Rendering
- **vl-convert**: We use `vl-convert-python` for high-quality PNG export of Altair charts. Ensure the environment has this package installed.
