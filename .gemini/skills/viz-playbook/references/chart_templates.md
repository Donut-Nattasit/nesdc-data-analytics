# Professional Visualization Templates (Altair & Matplotlib)

This reference provides pre-tested charting code to ensure consistency across economic reports.

## 1. Altair Line Chart (Standard)
```python
import altair as alt

def create_economic_line_chart(df, x_col, y_col, color_col, title):
    chart = alt.Chart(df).mark_line(strokeWidth=3).encode(
        x=alt.X(f'{x_col}:T', title='Date'),
        y=alt.Y(f'{y_col}:Q', title='Value', scale=alt.Scale(zero=False)),
        color=alt.Color(f'{color_col}:N', legend=alt.Legend(title="Series")),
        tooltip=[x_col, y_col, color_col]
    ).properties(title=title, width=600, height=400).interactive()
    return chart
```

## 2. Matplotlib Stacked Bar (Decomposition)
```python
import matplotlib.pyplot as plt

def plot_decomposition(df, date_col, components, title, output_path):
    plt.figure(figsize=(10, 6))
    df.plot(x=date_col, y=components, kind='bar', stacked=True, ax=plt.gca())
    plt.title(title)
    plt.ylabel('Contribution')
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
```

## 3. Thai Localization (Mandatory when requested)
Use `src/visualization/thai_utils.py` and the following configuration:
```python
import matplotlib.pyplot as plt
from src.visualization.thai_utils import to_thai_year

# Set Thai Font
plt.rcParams['font.family'] = 'TH Sarabun New'
plt.rcParams['font.size'] = 16

# Convert years to B.E.
df = to_thai_year(df, 'date') # adds 'thai_year_label'
```
