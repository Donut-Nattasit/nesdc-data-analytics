import os
import sys
import pandas as pd
from datetime import datetime

# Add project root to sys.path to allow src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from src.api.bot_client import BOTClient
from src.api.ceic_client import CeicSession
from src.utils.registry import add_dataset

# Configuration
START_DATE = "2000-01-01"

# BOT Series mapping
BOT_SERIES = {
    "EIEXUSDM00158": "bot_export_price_index",
    "EIIMUSDM00160": "bot_import_price_index",
    "EIEXUSDM00159": "bot_export_value_index",
    "EIIMUSDM00161": "bot_import_value_index"
}

# CEIC Series mapping (Index and Weights)
CEIC_SERIES = {
    # Export Composite Price Index
    "352376202": "ceic_expi_composite",
    # Import Composite Price Index
    "352376302": "ceic_impi_composite",
    # Export Indices
    "352376802": "ceic_expi_agro_industrial",
    "352376402": "ceic_expi_agricultural",
    "352383502": "ceic_expi_mineral_fuel",
    "352378602": "ceic_expi_principal_manuf",
    # Export Weights
    "486332027": "wgt_expi_agro_industrial",
    "486331987": "wgt_expi_agricultural",
    "486332187": "wgt_expi_mineral_fuel",
    "486332077": "wgt_expi_principal_manuf",
    # Import Indices
    "352385202": "ceic_impi_capital_goods",
    "352389102": "ceic_impi_consumer_goods",
    "352384602": "ceic_impi_fuel",
    "352386502": "ceic_impi_raw_materials",
    "352391802": "ceic_impi_vehicle_equip",
    # Import Weights
    "486332277": "wgt_impi_capital_goods",
    "48633437": "wgt_impi_consumer_goods",
    "486332437": "wgt_impi_consumer_goods",
    "486332237": "wgt_impi_fuel",
    "486332337": "wgt_impi_raw_materials",
    "486332497": "wgt_impi_vehicle_equip",
    
    # Export Sub-component Weights
    "486331997": "wgt_expi_ap_agriculture",
    "486332007": "wgt_expi_ap_fishery",
    "486332017": "wgt_expi_ap_livestock",
    "486332037": "wgt_expi_aip_preserved_aquatic",
    "486332047": "wgt_expi_aip_cane_sugar",
    "486332057": "wgt_expi_aip_canned_fruit",
    "486332067": "wgt_expi_aip_canned_veg",
    "486332087": "wgt_expi_mp_textile",
    "486332097": "wgt_expi_mp_gems_jewelry",
    "486332107": "wgt_expi_mp_electrical_equip",
    "486332117": "wgt_expi_mp_electronic_machine",
    "486332127": "wgt_expi_mp_iron_steel",
    "486332137": "wgt_expi_mp_polymer",
    "486332147": "wgt_expi_mp_plastic_product",
    "486332157": "wgt_expi_mp_chemical_product",
    "486332167": "wgt_expi_mp_rubber_product",
    "486332177": "wgt_expi_mp_vehicles_parts",
    "486332197": "wgt_expi_mf_lpg",
    "486332207": "wgt_expi_mf_crude_oil",
    "486332217": "wgt_expi_mf_refined_fuel",

    # Import Sub-component Weights
    "486332247": "wgt_impi_fp_crude_oil",
    "486332257": "wgt_impi_fp_finished_oil",
    "486332267": "wgt_impi_fp_natural_gas",
    "486332287": "wgt_impi_ca_metal_manufacture",
    "486332297": "wgt_impi_ca_machinery",
    "486332307": "wgt_impi_ca_electrical_machinery",
    "486332317": "wgt_impi_ca_computer_parts",
    "486332327": "wgt_impi_ca_scientific_appliances",
    "486332347": "wgt_impi_rm_aquatic_animal",
    "486332357": "wgt_impi_rm_vegetable_product",
    "486332367": "wgt_impi_rm_chemical_product",
    "486332377": "wgt_impi_rm_plastic_product",
    "486332387": "wgt_impi_rm_gems_jewelry",
    "486332397": "wgt_impi_rm_iron_steel",
    "486332407": "wgt_impi_rm_other_metal",
    "486332417": "wgt_impi_rm_fertilizer_pesticide",
    "486332427": "wgt_impi_rm_electrical_electronic",
    "486332447": "wgt_impi_co_dairy_product",
    "486332457": "wgt_impi_co_apparel",
    "486332467": "wgt_impi_co_pharmaceutical",
    "486332477": "wgt_impi_co_manufactured_article",
    "486332487": "wgt_impi_co_household_appliance",
    "486332507": "wgt_impi_ve_bus_truck",
    "486332517": "wgt_impi_ve_vehicle_parts"
}

def main():
    print("Initializing BOT and CEIC API sessions...")
    from pathlib import Path
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    db_path = str(project_root / "database" / "ex_im_price_forecast" / "ex_im_price_forecast.db")
    bot_client = BOTClient(db_path=db_path)
    ceic_session = CeicSession()
    
    # ------------------ 1. Fetch BOT Data ------------------
    print("\nFetching BOT series...")
    bot_dfs = []
    for code, col_name in BOT_SERIES.items():
        print(f"Fetching BOT series: {code} -> {col_name}")
        try:
            df = bot_client.get_data(code, start_period=START_DATE)
            if not df.empty:
                # The BOTClient.get_data returns columns ['date', original_series_name]
                # Let's find the non-date column and rename it
                val_cols = [c for c in df.columns if c != 'date']
                if val_cols:
                    df = df.rename(columns={val_cols[0]: col_name})
                    df['date'] = pd.to_datetime(df['date'])
                    df = df[['date', col_name]].set_index('date')
                    bot_dfs.append(df)
            else:
                print(f"Warning: BOT series {code} returned empty data.")
        except Exception as e:
            print(f"Error fetching BOT series {code}: {e}")

    if bot_dfs:
        bot_combined = pd.concat(bot_dfs, axis=1)
        print(f"BOT combined shape: {bot_combined.shape}")
    else:
        print("Error: No BOT data fetched.")
        bot_combined = pd.DataFrame()

    # ------------------ 2. Fetch CEIC Data ------------------
    print("\nFetching CEIC series...")
    ceic_ids = list(CEIC_SERIES.keys())
    ceic_combined = pd.DataFrame()
    
    try:
        # get_data handles parallel fetching for historical extensions
        ceic_raw_df = ceic_session.get_data(ceic_ids, with_historical_extension=True, count=10000)
        if not ceic_raw_df.empty:
            print(f"CEIC raw observations fetched: {len(ceic_raw_df)}")
            
            # CEIC raw df columns: ['date', 'value', 'series_id', 'series_name', 'source']
            # We convert series_id to string to match keys
            ceic_raw_df['series_id'] = ceic_raw_df['series_id'].astype(str)
            
            # Pivot to wide format: index='date', columns='series_id', values='value'
            ceic_pivot = ceic_raw_df.pivot(index='date', columns='series_id', values='value')
            ceic_pivot.index = pd.to_datetime(ceic_pivot.index)
            
            # Rename columns using CEIC_SERIES mapping
            rename_dict = {sid: name for sid, name in CEIC_SERIES.items() if sid in ceic_pivot.columns}
            ceic_combined = ceic_pivot.rename(columns=rename_dict)
            
            # Keep only the mapped columns
            mapped_cols = [c for c in ceic_combined.columns if c in CEIC_SERIES.values()]
            ceic_combined = ceic_combined[mapped_cols]
            
            print(f"CEIC combined wide shape: {ceic_combined.shape}")
        else:
            print("Warning: CEIC fetch returned empty data.")
    except Exception as e:
        print(f"Error fetching CEIC data: {e}")

    # ------------------ 3. Merge Datasets ------------------
    if bot_combined.empty and ceic_combined.empty:
        print("Error: Both BOT and CEIC datasets are empty. Aborting.")
        sys.exit(1)

    print("\nMerging BOT and CEIC datasets...")
    # Outer join to preserve all date observations, then sort
    merged_monthly = pd.merge(bot_combined, ceic_combined, left_index=True, right_index=True, how='outer').sort_index()
    
    # Ensure all columns are numeric
    for col in merged_monthly.columns:
        merged_monthly[col] = pd.to_numeric(merged_monthly[col], errors='coerce')
        
    # ------------------ 3a. Compute Quantity and Value Indices ------------------
    print("\nComputing quantity and value indices for weighted aggregation...")
    # Compute BOT Quantity Indices using CEIC Composite Prices: Q = (V / P) * 100
    merged_monthly["bot_export_quantity_index"] = (merged_monthly["bot_export_value_index"] / merged_monthly["ceic_expi_composite"]) * 100
    merged_monthly["bot_import_quantity_index"] = (merged_monthly["bot_import_value_index"] / merged_monthly["ceic_impi_composite"]) * 100

    # Compute CEIC export component values and quantities
    export_comps = ["agro_industrial", "agricultural", "mineral_fuel", "principal_manuf"]
    for comp in export_comps:
        price_col = f"ceic_expi_{comp}"
        wgt_col = f"wgt_expi_{comp}"
        val_col = f"val_expi_{comp}"
        q_col = f"q_expi_{comp}"
        
        # Component value index = total export value index * component share
        merged_monthly[val_col] = merged_monthly["bot_export_value_index"] * (merged_monthly[wgt_col] / 100)
        # Component quantity index = (component value index / component price index) * 100
        merged_monthly[q_col] = (merged_monthly[val_col] / merged_monthly[price_col]) * 100

    # Correct Vehicle and Equipment (VE) weight using reverse engineering:
    # Weight of VE = 100 - sum(weight of other components)
    print("Correcting import weight for Vehicle and Equipment (VE) to ensure sum of weights is exactly 100...")
    mask = merged_monthly["wgt_impi_fuel"].notna()
    merged_monthly.loc[mask, "wgt_impi_vehicle_equip"] = 100.0 - (
        merged_monthly.loc[mask, "wgt_impi_fuel"] +
        merged_monthly.loc[mask, "wgt_impi_capital_goods"] +
        merged_monthly.loc[mask, "wgt_impi_raw_materials"] +
        merged_monthly.loc[mask, "wgt_impi_consumer_goods"]
    )

    # Compute CEIC import component values and quantities
    import_comps = ["capital_goods", "consumer_goods", "fuel", "raw_materials", "vehicle_equip"]
    for comp in import_comps:
        price_col = f"ceic_impi_{comp}"
        wgt_col = f"wgt_impi_{comp}"
        val_col = f"val_impi_{comp}"
        q_col = f"q_impi_{comp}"
        
        # Component value index = total import value index * component share
        merged_monthly[val_col] = merged_monthly["bot_import_value_index"] * (merged_monthly[wgt_col] / 100)
        # Component quantity index = (component value index / component price index) * 100
        merged_monthly[q_col] = (merged_monthly[val_col] / merged_monthly[price_col]) * 100

    # Save monthly wide dataset
    os.makedirs("output/data/ex_im_price_forecast", exist_ok=True)
    monthly_path = "output/data/ex_im_price_forecast/export_import_price_monthly_wide.csv"
    merged_monthly.to_csv(monthly_path)
    print(f"Saved monthly wide dataset to {monthly_path} (Shape: {merged_monthly.shape})")

    # ------------------ 4. Resample to Quarterly ------------------
    # Quarterly Aggregation Standard:
    # - Values, Quantities, and Weights: Arithmetic Mean over the quarter
    # - Prices: Volume-Weighted average, computed as (Value_Q / Quantity_Q) * 100
    # - Alignment: Quarter-End ('QE')
    print("\nResampling monthly dataset to quarterly frequency (using volume-weighted average for prices)...")
    
    # 1. Base resampling of all columns using mean
    merged_quarterly = merged_monthly.resample('QE').mean()
    
    # 2. Re-compute volume-weighted Price indices for CEIC Composite
    merged_quarterly["ceic_expi_composite"] = (merged_quarterly["bot_export_value_index"] / merged_quarterly["bot_export_quantity_index"]) * 100
    merged_quarterly["ceic_impi_composite"] = (merged_quarterly["bot_import_value_index"] / merged_quarterly["bot_import_quantity_index"]) * 100

    # 3. Re-compute volume-weighted Price indices for CEIC export components
    for comp in export_comps:
        price_col = f"ceic_expi_{comp}"
        val_col = f"val_expi_{comp}"
        q_col = f"q_expi_{comp}"
        
        # P_Q = (V_Q / Q_Q) * 100
        weighted_price = (merged_quarterly[val_col] / merged_quarterly[q_col]) * 100
        # Replace mean-aggregated price with volume-weighted price. Fall back to mean-aggregated if weighted_price is NaN.
        merged_quarterly[price_col] = weighted_price.fillna(merged_quarterly[price_col])

    # 4. Re-compute volume-weighted Price indices for CEIC import components
    for comp in import_comps:
        price_col = f"ceic_impi_{comp}"
        val_col = f"val_impi_{comp}"
        q_col = f"q_impi_{comp}"
        
        weighted_price = (merged_quarterly[val_col] / merged_quarterly[q_col]) * 100
        merged_quarterly[price_col] = weighted_price.fillna(merged_quarterly[price_col])
    
    quarterly_path = "output/data/ex_im_price_forecast/export_import_price_quarterly_wide.csv"
    merged_quarterly.to_csv(quarterly_path)
    print(f"Saved quarterly wide dataset to {quarterly_path} (Shape: {merged_quarterly.shape})")

    # ------------------ 5. Register in Central Registry ------------------
    print("\nRegistering datasets in central registry...")
    try:
        # Register monthly dataset
        add_dataset(
            series_id="Export & Import Prices - Monthly Wide",
            source="BOT (EC_EI_020) & CEIC (18 Series)",
            raw_path="",
            transformed_path=monthly_path,
            status="Ready",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        # Register quarterly dataset
        add_dataset(
            series_id="Export & Import Prices - Quarterly Wide",
            source="BOT (EC_EI_020) & CEIC (18 Series) Resampled",
            raw_path=monthly_path,
            transformed_path=quarterly_path,
            status="Ready",
            last_update=datetime.now().strftime('%Y-%m-%d')
        )
        print("Registration successful.")
    except Exception as e:
        print(f"Error updating registry: {e}")

if __name__ == "__main__":
    main()
