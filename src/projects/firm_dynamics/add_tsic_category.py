"""
add_tsic_category.py
----------------------
Adds two new columns to hhi_tsic4.csv by joining against the
TSIC_descriptions.xlsx data dictionary:

  - tsic_category      : Section letter (e.g. 'A', 'B', 'C', ...)
  - tsic_category_desc : English description of the category section
                         (e.g. 'Agriculture, forestry and fishing')

Join logic:
  mapping sheet  : กิจการ (5-digit sub-class) → หมวดใหญ่ (Section letter)
                   We extract the first 4 chars of กิจการ to get the TSIC4 key.
  หมวดใหญ่ sheet : Section letter → English Description
"""

import pandas as pd
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT      = Path.cwd()
XLSX_PATH = ROOT / "input" / "งบการเงิน" / "TSIC_descriptions.xlsx"
HHI_CSV   = ROOT / "output" / "data" / "hhi_tsic4.csv"

# ── 1. Load mapping sheet ─────────────────────────────────────────────────────
# Columns by position (headers are garbled Thai in terminal, but structure is fixed):
#   col[0] = หมวดใหญ่  (Section letter A-U)
#   col[1] = หมวด      (Division, 2-digit)
#   col[2] = หมู่       (Group, 3-digit)
#   col[3] = ประเภท    (Class, 4-digit)
#   col[4] = กิจการ    (Sub-class, 5-digit)
df_map = pd.read_excel(XLSX_PATH, sheet_name="mapping", dtype=str)
df_map.columns = ["section", "division", "group", "class4", "subclass5"]

# Derive tsic4 from first 4 characters of the 4-digit class column
# (The class4 column is already 4-digit; use it directly for the join)
df_tsic4_to_section = df_map[["class4", "section"]].drop_duplicates(subset="class4")
df_tsic4_to_section = df_tsic4_to_section.rename(columns={"class4": "tsic4"})

print(f"Mapping table: {len(df_tsic4_to_section)} unique TSIC4 codes")
print(df_tsic4_to_section.head(10).to_string())

# ── 2. Load section descriptions ─────────────────────────────────────────────
# Columns by position:
#   col[0] = หมวดใหญ่ (Section letter)
#   col[1] = Thai description
#   col[2] = English description
df_sec = pd.read_excel(XLSX_PATH, sheet_name="หมวดใหญ่", dtype=str)
df_sec.columns = ["section", "desc_th_section", "tsic_category_desc"]
df_sec = df_sec[["section", "tsic_category_desc"]].drop_duplicates(subset="section")

print(f"\nSection table: {len(df_sec)} sections")
print(df_sec.to_string(index=False))

# ── 3. Load HHI CSV ───────────────────────────────────────────────────────────
df_hhi = pd.read_csv(HHI_CSV, dtype={"tsic4": str})

# Strip the natural_monopoly column temporarily if it already has tsic_category cols
# (idempotent: drop old category cols if re-running)
for drop_col in ["tsic_category", "tsic_category_desc"]:
    if drop_col in df_hhi.columns:
        df_hhi = df_hhi.drop(columns=[drop_col])

print(f"\nHHI CSV: {len(df_hhi)} rows")
print("Columns:", df_hhi.columns.tolist())

# ── 4. Join ───────────────────────────────────────────────────────────────────
df_hhi = df_hhi.merge(df_tsic4_to_section, on="tsic4", how="left")
df_hhi = df_hhi.merge(df_sec, on="section", how="left")
df_hhi = df_hhi.rename(columns={"section": "tsic_category"})

# ── 5. Check for unmatched ────────────────────────────────────────────────────
unmatched = df_hhi[df_hhi["tsic_category"].isna()]
if len(unmatched) > 0:
    print(f"\nWARNING: {len(unmatched)} TSIC4 codes had no match:")
    print(unmatched[["tsic4", "desc_en"]].to_string())
else:
    print(f"\nAll {len(df_hhi)} TSIC4 codes matched successfully.")

# ── 6. Reorder: put new cols right after tsic4 ────────────────────────────────
cols = df_hhi.columns.tolist()
for c in ["tsic_category", "tsic_category_desc"]:
    cols.remove(c)
idx = cols.index("tsic4") + 1
cols.insert(idx, "tsic_category_desc")
cols.insert(idx, "tsic_category")
df_hhi = df_hhi[cols]

# ── 7. Summary ────────────────────────────────────────────────────────────────
print(f"\nFinal columns: {df_hhi.columns.tolist()}")
print("\nCategory distribution (industries per section):")
dist = (df_hhi.groupby(["tsic_category", "tsic_category_desc"])
              .size()
              .reset_index(name="num_tsic4_industries")
              .sort_values("tsic_category"))
print(dist.to_string(index=False))

# ── 8. Save ───────────────────────────────────────────────────────────────────
df_hhi.to_csv(HHI_CSV, index=False)
print(f"\nSaved --> {HHI_CSV}")
