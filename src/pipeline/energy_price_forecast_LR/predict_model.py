import os
import sys
import sqlite3
import pandas as pd
import numpy as np
import pmdarima as pm
from pathlib import Path
from datetime import datetime

# Override print to automatically flush stdout for background log visibility
_print = print
def print(*args, **kwargs):
    _print(*args, **kwargs)
    sys.stdout.flush()

# Add project root to sys.path to allow src imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

def main():
    print("==========================================================")
    print("[LR Modeling] Training auto_ARIMA and forecasting components (LR)...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    master_path = project_root / "output" / "data" / "energy_price_forecast_LR" / "cpi_historical_master.csv"
    dubai_path = project_root / "input" / "oil_price_forecast_LR" / "dubai_oil_price_forecast_LR.xlsx"
    
    # Check paths
    if not master_path.exists():
        print(f"[FAIL] Historical master dataset not found at: {master_path}")
        raise RuntimeError("Pipeline step failed")
    if not dubai_path.exists():
        print(f"[FAIL] Exogenous Dubai crude oil forecast not found at: {dubai_path}")
        raise RuntimeError("Pipeline step failed")
        
    # 1. Load historical master data
    df_master = pd.read_csv(master_path, index_col='date', parse_dates=True).sort_index()
    print(f"Loaded Historical Master data. Shape: {df_master.shape}")
    print(f"Historical date range: {df_master.index.min().strftime('%Y-%m-%d')} to {df_master.index.max().strftime('%Y-%m-%d')}")
    
    # 2. Load exogenous Dubai Crude Oil forecast
    df_dubai = pd.read_excel(dubai_path, sheet_name="Sheet1")
    df_dubai = df_dubai.rename(columns={"Unnamed: 0": "date"})
    df_dubai["date"] = pd.to_datetime(df_dubai["date"])
    df_dubai = df_dubai.set_index("date").sort_index()
    print(f"Loaded Dubai Crude Oil forecast. Shape: {df_dubai.shape}")
    
    # Define target range for forecasting (to Dec 2031)
    last_hist_date = df_master.index.max()
    forecast_start = last_hist_date + pd.DateOffset(months=1)
    forecast_end = pd.to_datetime("2031-12-01")
    
    forecast_dates = pd.date_range(start=forecast_start, end=forecast_end, freq='MS')
    h = len(forecast_dates)
    print(f"Forecast Horizon: {h} months (from {forecast_start.strftime('%Y-%m-%d')} to {forecast_end.strftime('%Y-%m-%d')})")
    
    # Create output folders
    data_out_dir = project_root / "output" / "data" / "energy_price_forecast_LR"
    model_out_dir = project_root / "output" / "model_summary" / "energy_price_forecast_LR"
    data_out_dir.mkdir(parents=True, exist_ok=True)
    model_out_dir.mkdir(parents=True, exist_ok=True)
    
    # Lists of target variables
    index_cols = [col for col in df_master.columns if col.startswith('index_')]
    weight_cols = [col for col in df_master.columns if col.startswith('weight_')]
    
    df_forecast_indices = pd.DataFrame(index=forecast_dates)
    
    # 3. Forecast Indices using auto_ARIMA
    for col in index_cols:
        print(f"\n--- Forecasting Index: {col} ---")
        y = df_master[col].dropna()
        print(f"  Historical observations: {len(y)} (Start: {y.index.min().strftime('%Y-%m-%d')})")
        
        # Check if we need exogenous variables
        if col == "index_Transport_Communication_Motor_Fuel":
            print("  Applying ARIMAX model with exogenous Dubai spot price...")
            # Match exogenous data with history y
            valid_idx = y.index.intersection(df_master['exog_dubai_crude'].dropna().index)
            y_clean = y.loc[valid_idx]
            X_clean = df_master.loc[valid_idx, ['exog_dubai_crude']]
            
            # Prepare future exogenous values
            X_future = df_dubai.loc[forecast_dates, ['dubai_spot_forecast']].rename(columns={'dubai_spot_forecast': 'exog_dubai_crude'})
            
            # Fit auto_arima with exogenous variable
            try:
                model = pm.auto_arima(
                    y_clean, X=X_clean,
                    seasonal=True, m=12,
                    stepwise=True,
                    error_action='ignore',
                    suppress_warnings=True
                )
                print(f"  Best ARIMA order: {model.order} {model.seasonal_order}")
                
                # Predict future
                y_pred = model.predict(n_periods=h, X=X_future)
                df_forecast_indices[col] = y_pred
                
                # Save model summary
                summary_path = model_out_dir / f"{col}_summary.txt"
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(str(model.summary()))
                    
            except Exception as e:
                print(f"  [Warning] ARIMAX fit failed for {col}: {e}. Falling back to univariate auto_arima...")
                model = pm.auto_arima(
                    y, seasonal=True, m=12,
                    stepwise=True,
                    error_action='ignore',
                    suppress_warnings=True
                )
                y_pred = model.predict(n_periods=h)
                df_forecast_indices[col] = y_pred
        else:
            # Univariate auto_arima
            try:
                model = pm.auto_arima(
                    y, seasonal=True, m=12,
                    stepwise=True,
                    error_action='ignore',
                    suppress_warnings=True
                )
                print(f"  Best ARIMA order: {model.order} {model.seasonal_order}")
                
                # Predict
                y_pred = model.predict(n_periods=h)
                df_forecast_indices[col] = y_pred
                
                # Save model summary
                summary_path = model_out_dir / f"{col}_summary.txt"
                with open(summary_path, "w", encoding="utf-8") as f:
                    f.write(str(model.summary()))
                    
            except Exception as e:
                print(f"  [FAIL] auto_arima failed for {col}: {e}")
                raise RuntimeError("Pipeline step failed")

    # 3.5 Splicing and propagating Prepared Food shock index
    pf_shock_path = project_root / "output" / "data" / "prepared_food_shock" / "prepared_food_shock_comparison.csv"
    if not pf_shock_path.exists():
        print(f"[FAIL] Prepared Food shock dataset not found at: {pf_shock_path}")
        raise RuntimeError("Pipeline step failed")
        
    print(f"\n--- Splicing & Propagating Prepared Food Shock index ---")
    df_pf_shock = pd.read_csv(pf_shock_path)
    df_pf_shock['date'] = pd.to_datetime(df_pf_shock['date'])
    df_pf_shock = df_pf_shock.set_index('date').sort_index()
    
    # Identify splicing range: June 2026 to December 2027
    splice_start = pd.to_datetime("2026-06-01")
    splice_end = pd.to_datetime("2027-12-01")
    
    # Save a copy of the baseline auto-ARIMA forecast of Prepared Food for MoM growth rate calculation
    baseline_pf_forecast = df_forecast_indices['index_Prepared_Food'].copy()
    
    # Slice the shocked Prepared Food index for the range
    pf_shock_range = df_pf_shock.loc[splice_start:splice_end, 'Prepared_Food_Index_shock']
    print(f"Splicing {len(pf_shock_range)} months of shocked Prepared Food index ({splice_start.strftime('%Y-%m-%d')} to {splice_end.strftime('%Y-%m-%d')})")
    
    # Overwrite the forecast df
    df_forecast_indices.loc[pf_shock_range.index, 'index_Prepared_Food'] = pf_shock_range.values
    
    # Propagate from Jan 2028 through Dec 2031 smoothly using baseline MoM growth rates
    prop_start = pd.to_datetime("2028-01-01")
    prop_dates = pd.date_range(start=prop_start, end=forecast_end, freq='MS')
    
    print(f"Propagating shocked level forward for {len(prop_dates)} months ({prop_start.strftime('%Y-%m-%d')} to {forecast_end.strftime('%Y-%m-%d')})")
    for dt in prop_dates:
        # Prev date
        prev_dt = dt - pd.DateOffset(months=1)
        # Baseline growth: (I_base_t / I_base_t-1)
        growth_ratio = baseline_pf_forecast.loc[dt] / baseline_pf_forecast.loc[prev_dt]
        # Apply to previous shocked index
        prev_shock_val = df_forecast_indices.loc[prev_dt, 'index_Prepared_Food']
        df_forecast_indices.loc[dt, 'index_Prepared_Food'] = prev_shock_val * growth_ratio
        
    print(f"  Dec 2027 Baseline: {baseline_pf_forecast.loc[pd.to_datetime('2027-12-01')]:.4f} | Shocked: {df_forecast_indices.loc[pd.to_datetime('2027-12-01'), 'index_Prepared_Food']:.4f}")
    print(f"  Jan 2028 Baseline: {baseline_pf_forecast.loc[pd.to_datetime('2028-01-01')]:.4f} | Shocked: {df_forecast_indices.loc[pd.to_datetime('2028-01-01'), 'index_Prepared_Food']:.4f}")
    print(f"  Dec 2031 Baseline: {baseline_pf_forecast.loc[pd.to_datetime('2031-12-01')]:.4f} | Shocked: {df_forecast_indices.loc[pd.to_datetime('2031-12-01'), 'index_Prepared_Food']:.4f}")

    # 3.6 Adjust growth trajectories of Core CPI components to target 2.0% annual long-run growth (BoT target)
    print(f"\n--- Adjusting Growth Trajectories to Target 2.0% Core CPI Growth ---")
    core_target_annual = 0.02
    pre_adjusted = {
        'index_Medical_Personal_Care': 0.010,
        'index_Apparel_Footwears': 0.002
    }
    core_components = [
        "Seasoning_Condiments", "Non_Alcoholic_Beverages", "Sugar_Product", "Prepared_Food",
        "Apparel_Footwears", "Housing_Furnishing_ex_Utility", "Medical_Personal_Care",
        "Transport_Communication_ex_Motor_Fuel", "Recreation_Reading_Education_Religion",
        "Tobacco_Alcoholic_Beverages"
    ]
    core_cols = [f"index_{c}" for c in core_components]
    
    # 1. Retrieve weights
    weights = {}
    for c in core_components:
        w_col = f"weight_{c}"
        weights[f"index_{c}"] = df_master[w_col].dropna().iloc[-1]
        
    w_core = sum(weights.values())
    w_adj = sum(weights[col] for col in pre_adjusted)
    w_unconstrained = sum(weights[col] for col in core_cols if col not in pre_adjusted)
    
    # 2. Compute target monthly growth rates
    target_core_mom = (1 + core_target_annual) ** (1/12) - 1
    target_mom = {col: (1 + target_annual) ** (1/12) - 1 for col, target_annual in pre_adjusted.items()}
    
    # 3. Compute baseline MoM average growth rates for unconstrained components in the terminal year (2031)
    # to avoid transient dynamics and short-run shocks contaminating the long-run offset calibration.
    avg_base_mom = {}
    ws_unconstrained = 0.0
    terminal_dates = pd.date_range(start="2031-01-01", end="2031-12-01", freq='MS')
    for col in core_cols:
        if col in pre_adjusted:
            continue
        full_baseline = pd.concat([df_master[col], df_forecast_indices[col]]).sort_index()
        mom_growth = full_baseline.pct_change()
        avg_base_mom[col] = mom_growth.loc[terminal_dates].mean()
        ws_unconstrained += weights[col] * avg_base_mom[col]
        
    # 4. Compute weighted sum of target MoM growth rates for pre-adjusted components
    ws_adj = sum(weights[col] * target_mom[col] for col in pre_adjusted)
    
    # 5. Compute the required long-run growth offset delta
    delta = (w_core * target_core_mom - ws_adj - ws_unconstrained) / w_unconstrained
    
    print(f"Core CPI Growth Adjustment Parameters (Calibrated on Year 2031 Steady-State):")
    print(f"  Core Target Annual Growth: {core_target_annual*100:.2f}%")
    print(f"  Total Core Weight: {w_core:.6f}")
    print(f"  Pre-adjusted Core Weight (Apparel & Medical): {w_adj:.6f}")
    print(f"  Unconstrained Core Weight: {w_unconstrained:.6f}")
    print(f"  Target Core MoM growth: {target_core_mom*100:.6f}%")
    print(f"  Pre-adjusted target MoM weighted sum: {ws_adj*100:.6f}%")
    print(f"  Unconstrained baseline MoM weighted sum: {ws_unconstrained*100:.6f}%")
    print(f"  Calculated uniform MoM offset (delta): {delta*100:.6f}% (Annualized: {((1 + delta)**12 - 1)*100:+.4f}%)")
    
    # 6. Set up long-run offsets for all Core components (using steady-state baseline in 2031)
    offsets_lr = {}
    for col in core_cols:
        if col in pre_adjusted:
            full_baseline = pd.concat([df_master[col], df_forecast_indices[col]]).sort_index()
            mom_growth = full_baseline.pct_change()
            col_avg_base_mom = mom_growth.loc[terminal_dates].mean()
            offsets_lr[col] = target_mom[col] - col_avg_base_mom
        else:
            offsets_lr[col] = delta
            
    # 7. Apply the adjustments with exponential transition
    lam = np.log(2) / 12.0  # 12-month half-life
    print("\nApplying transition adjustments (12-month half-life)...")
    for col in core_cols:
        offset_lr = offsets_lr[col]
        baseline_col = df_forecast_indices[col].copy()
        
        full_baseline = pd.concat([df_master[col], baseline_col]).sort_index()
        mom_growth = full_baseline.pct_change()
        
        for k, dt in enumerate(forecast_dates):
            prev_dt = dt - pd.DateOffset(months=1)
            base_g = mom_growth.loc[dt]
            
            # Exponential offset factor
            offset_t = offset_lr * (1.0 - np.exp(-lam * k))
            adj_g = base_g + offset_t
            
            if prev_dt in df_forecast_indices.index:
                prev_val = df_forecast_indices.loc[prev_dt, col]
            else:
                prev_val = df_master.loc[prev_dt, col]
                
            df_forecast_indices.loc[dt, col] = prev_val * (1 + adj_g)
            
        print(f"  {col.replace('index_', '').replace('_', ' ')}:")
        print(f"    Dec 2027 Index: {baseline_col.loc[pd.to_datetime('2027-12-01')]:.4f} | Adjusted: {df_forecast_indices.loc[pd.to_datetime('2027-12-01'), col]:.4f}")
        print(f"    Dec 2031 Index: {baseline_col.loc[pd.to_datetime('2031-12-01')]:.4f} | Adjusted: {df_forecast_indices.loc[pd.to_datetime('2031-12-01'), col]:.4f}")
                
    # 4. Forecast Weights using Naive method (last value)
    print("\n--- Forecasting Weights (Naive) ---")
    df_forecast_weights = pd.DataFrame(index=forecast_dates)
    for col in weight_cols:
        last_val = df_master[col].dropna().iloc[-1]
        df_forecast_weights[col] = last_val
        print(f"  Weight {col}: Projected forward with constant weight {last_val:.6f}")
        
    # 5. Assemble Continuous Wide Dataset
    # Build complete forecast df
    df_forecast = pd.concat([df_forecast_indices, df_forecast_weights], axis=1)
    
    # Merge future exog values
    X_future_exog = df_dubai.loc[forecast_dates, 'dubai_spot_forecast']
    df_forecast['exog_dubai_crude'] = X_future_exog
    
    # Concatenate historical and forecasted datasets
    df_all = pd.concat([df_master, df_forecast], axis=0).sort_index()
    df_all.index.name = 'date'
    
    # 6. Compute Composite CPI Aggregates
    print("\n--- Computing Composite CPI Aggregates ---")
    
    # Core CPI
    core_components = [
        "Seasoning_Condiments", "Non_Alcoholic_Beverages", "Sugar_Product", "Prepared_Food",
        "Apparel_Footwears", "Housing_Furnishing_ex_Utility", "Medical_Personal_Care",
        "Transport_Communication_ex_Motor_Fuel", "Recreation_Reading_Education_Religion",
        "Tobacco_Alcoholic_Beverages"
    ]
    # Non-Core CPI: Raw Food
    raw_food_components = ["Rice_Flour_Cereal", "Meats_Poultry_Fish", "Eggs_Dairy_Products", "Vegetables_Fruits"]
    # Non-Core CPI: Energy
    energy_components = ["Housing_Furnishing_Utility", "Transport_Communication_Motor_Fuel"]
    # Headline CPI (all 16 components)
    all_components = core_components + raw_food_components + energy_components
    
    def calculate_weighted_composite(df, components):
        w_cols = [f"weight_{c}" for c in components]
        weight_sum = df[w_cols].sum(axis=1)
        weighted_sum = sum(df[f"index_{c}"] * df[f"weight_{c}"] for c in components)
        return weighted_sum / weight_sum
        
    df_all['Core_CPI'] = calculate_weighted_composite(df_all, core_components)
    df_all['Raw_Food_CPI'] = calculate_weighted_composite(df_all, raw_food_components)
    df_all['Energy_CPI'] = calculate_weighted_composite(df_all, energy_components)
    df_all['Headline_CPI'] = calculate_weighted_composite(df_all, all_components)
    
    # Fill forecasted flags
    df_all['is_forecast'] = 0
    df_all.loc[forecast_dates, 'is_forecast'] = 1
    
    # 7. Resample to Quarterly and Annual frequencies
    print("\n--- Resampling to Quarterly (QE mean) and Annual (YE mean) ---")
    
    # Select columns to resample
    resample_cols = [c for c in df_all.columns if c != 'is_forecast']
    
    # Quarterly resampling
    df_quarterly = df_all[resample_cols].resample('QE').mean()
    df_quarterly.index.name = 'date'
    
    # Annual resampling
    df_annual = df_all[resample_cols].resample('YE').mean()
    df_annual.index.name = 'date'
    
    # 8. Save CSV files
    monthly_path = data_out_dir / "cpi_forecast_monthly.csv"
    quarterly_path = data_out_dir / "cpi_forecast_quarterly.csv"
    annual_path = data_out_dir / "cpi_forecast_annual.csv"
    
    df_all.to_csv(monthly_path, index=True)
    df_quarterly.to_csv(quarterly_path, index=True)
    df_annual.to_csv(annual_path, index=True)
    
    print(f"\n[OK] Saved Monthly Forecast CSV: {monthly_path}")
    print(f"[OK] Saved Quarterly Forecast CSV: {quarterly_path}")
    print(f"[OK] Saved Annual Forecast CSV: {annual_path}")
    
    # 9. Save tables to SQLite Database
    db_path = project_root / "database" / "energy_price_forecast_LR" / "energy_price_forecast_LR.db"
    conn = sqlite3.connect(str(db_path))
    try:
        df_monthly_write = df_all.copy()
        df_monthly_write.index = df_monthly_write.index.strftime('%Y-%m-%d')
        df_monthly_write.to_sql("cpi_forecast_monthly", conn, if_exists="replace", index=True, index_label='date')
        
        df_quarterly_write = df_quarterly.copy()
        df_quarterly_write.index = df_quarterly_write.index.strftime('%Y-%m-%d')
        df_quarterly_write.to_sql("cpi_forecast_quarterly", conn, if_exists="replace", index=True, index_label='date')
        
        df_annual_write = df_annual.copy()
        df_annual_write.index = df_annual_write.index.strftime('%Y-%m-%d')
        df_annual_write.to_sql("cpi_forecast_annual", conn, if_exists="replace", index=True, index_label='date')
        
        conn.commit()
        print("[OK] Saved monthly, quarterly, and annual forecast tables to SQLite database.")
    except Exception as e:
        print(f"[Warning] Failed to write forecast tables to database: {e}")
    finally:
        conn.close()
        
    try:
    except Exception as e:

if __name__ == "__main__":
    main()
