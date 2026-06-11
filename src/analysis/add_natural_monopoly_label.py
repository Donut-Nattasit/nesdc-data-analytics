"""
add_natural_monopoly_label.py
-------------------------------
Adds a 'natural_monopoly' column to hhi_tsic4.csv based on sector-based
classification of industries with natural monopoly characteristics.

Classification Criteria (TSIC 4-digit sector-based, real-world economic theory):
  - Railway: 4911 (Passenger rail), 4912 (Freight rail)
  - Pipeline transport: 4940 (Transport via pipeline)
  - Electricity: 3510 (Electric power generation, transmission and distribution)
  - Gas distribution: 3520 (Manufacture of gas; distribution of gaseous fuels)
  - Water supply: 3600 (Water collection, treatment and supply)
  - Wired Telecommunications: 6110 (Wired telecommunications)
  - Wireless Telecommunications: 6120 (Wireless telecommunications)
  - Satellite Telecommunications: 6130 (Satellite telecommunications)
  - Airport operations: 5223 (Service activities incidental to air transportation)

Label values:
  - 'Natural Monopoly' : industry is classified as a natural monopoly sector
  - '-'               : not classified as a natural monopoly
"""

import pandas as pd
from pathlib import Path

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path.cwd()
INPUT_CSV  = ROOT / "output" / "data" / "hhi_tsic4.csv"
OUTPUT_CSV = ROOT / "output" / "data" / "hhi_tsic4.csv"   # overwrite in-place

# ── Natural Monopoly TSIC 4-digit codes ──────────────────────────────────────
NATURAL_MONOPOLY_TSIC = {
    # Railway
    "4911",   # Passenger rail transport, interurban
    "4912",   # Freight rail transport
    # Pipeline transport (water, gas, oil)
    "4940",   # Transport via pipeline
    # Electricity generation, transmission and distribution
    "3510",
    # Gas distribution
    "3520",   # Manufacture of gas; distribution of gaseous fuels through mains
    # Water supply
    "3600",   # Water collection, treatment and supply
    # Telecommunications (fixed-line / wired)
    "6110",   # Wired telecommunications activities
    # Telecommunications (wireless / mobile)
    "6120",   # Wireless telecommunications activities
    # Satellite telecommunications
    "6130",   # Satellite telecommunications activities
    # Airport operations & air traffic support infrastructure
    "5223",   # Service activities incidental to air transportation
}

# ── Load ─────────────────────────────────────────────────────────────────────
df = pd.read_csv(INPUT_CSV, dtype={"tsic4": str})
print(f"Loaded {len(df):,} rows from {INPUT_CSV.name}")

# ── Classify ──────────────────────────────────────────────────────────────────
df["natural_monopoly"] = df["tsic4"].apply(
    lambda code: "Natural Monopoly" if code in NATURAL_MONOPOLY_TSIC else "-"
)

# ── Summary ───────────────────────────────────────────────────────────────────
labelled = df[df["natural_monopoly"] == "Natural Monopoly"]
print(f"\n{'='*70}")
print(f"Natural Monopoly Industries Identified: {len(labelled)}")
print(f"{'='*70}")
print(
    labelled[["tsic4", "desc_en", "hhi", "cr1", "active_firms", "natural_monopoly"]]
    .sort_values("tsic4")
    .to_string(index=False)
)
print(f"\nTotal industries NOT labelled: {len(df) - len(labelled)}")

# ── Save ─────────────────────────────────────────────────────────────────────
df.to_csv(OUTPUT_CSV, index=False)
print(f"\nSaved updated CSV --> {OUTPUT_CSV}")
