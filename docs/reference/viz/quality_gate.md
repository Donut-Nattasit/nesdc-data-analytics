# Visual Quality Gate & Spacing Safeguards

This reference document outlines the mandatory visual standards and code-level safeguards to prevent overlapping texts, crowded legends, and truncated elements in the workspace's economic charts.

---

## 1. Visual Quality Gate Checklist

Every visualization must undergo a visual inspection before being declared ready. Run `view_file` on the saved `.png` path and critically inspect for:

* **Overlapping Text**: Are X-axis dates colliding? Do legend labels run into each other? Are data point values overlapping?
* **Legend Truncation**: Is the legend cut off at the bottom or sides of the canvas?
* **Title Flow**: Is the title too wide, or does it overlap with the subplots?
* **Axis Head-room**: Do data labels at the peak of the lines or bars collide with the top/right axes border?

If any defects are seen, adjust sizing, wrapping, padding, or tick locators, re-run the code, and inspect again until the chart is visually perfect.

---

## 2. Programmatic Safeguards (Matplotlib / Seaborn)

### A. Long Title Wrapping
Never let long titles run off the screen. Wrap them programmatically using python's `textwrap` module:
```python
import textwrap

# Wrap to 55-65 characters depending on figsize
wrapped_title = "\n".join(textwrap.wrap(title, width=55))
ax.set_title(wrapped_title, fontsize=14, fontweight='bold', pad=15)
```

### B. X-Axis Tick Overlap Prevention
For dense dates or category series:
* **Limit Ticks**: Force a maximum number of ticks on the axis to thin out crowded dates.
  ```python
  import matplotlib.pyplot as plt
  ax.xaxis.set_major_locator(plt.MaxNLocator(8))  # Max 8 ticks on X-axis
  ```
* **Rotate Labels**: Rotate tick labels and right-align them.
  ```python
  plt.xticks(rotation=30, ha='right')
  # Or for datetime axes:
  fig.autofmt_xdate(rotation=30, ha='right')
  ```

### C. Legend Spacing & Bottom Clipping
To fit multiple series without colliding with ticks or cropping at the bottom:
* **Set Columns Dynamically**: Never let legend columns exceed the number of series. Wrap long legends cleanly.
  ```python
  # Set up to 4 columns to keep legend box thin vertically
  ncol = min(4, len(labels))
  ```
* **Lower Legend Position**: Set legend coordinates offset below the axes.
  ```python
  ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.12), ncol=ncol, frameon=True)
  ```
* **Allocate Subplot Padding**: Ensure the figure has enough bottom padding to draw the legend lower.
  ```python
  plt.tight_layout()
  # Add extra room below tight_layout (0.20 to 0.28 depending on legend height)
  fig.subplots_adjust(bottom=0.22)
  ```

### D. Value Label Head-room
When adding text labels on top of bars or lines, pad the axis limit to prevent them from hitting the chart borders:
```python
# Reserve 15% head-room at the top of the axis
max_val = df[value_col].max()
ax.set_ylim(bottom=0 if min_val >= 0 else None, top=max_val * 1.15)
```
