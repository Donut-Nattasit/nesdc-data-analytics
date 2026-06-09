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

from src.utils.registry import add_dataset, add_model

def main():
    print("==========================================================")
    print("[CPI Modeling] Training auto_ARIMA and forecasting components...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    master_path = project_root / "output" / "data" / "cpi_forecast" / "cpi_historical_master.csv"
    dubai_path = project_root / "output" / "data" / "energy_price_forecast" / "dubai_oil_forecast_production.csv"
    
    # Check paths
    if not master_path.exists():
        print(f"[FAIL] Historical master dataset not found at: {master_path}")
        sys.exit(1)
    if not dubai_path.exists():
        print(f"[FAIL] Exogenous Dubai crude oil forecast not found at: {dubai_path}")
        sys.exit(1)
        
    # 1. Load historical master data
    df_master = pd.read_csv(master_path, index_col='date', parse_dates=True).sort_index()
    print(f"Loaded Historical Master data. Shape: {df_master.shape}")
    print(f"Historical date range: {df_master.index.min().strftime('%Y-%m-%d')} to {df_master.index.max().strftime('%Y-%m-%d')}")
    
    # 2. Load exogenous Dubai Crude Oil forecast
    df_dubai = pd.read_csv(dubai_path, index_col=0, parse_dates=True).sort_index()
    print(f"Loaded Dubai Crude Oil forecast. Shape: {df_dubai.shape}")
    
    # Define target range for forecasting
    last_hist_date = df_master.index.max()
    forecast_start = last_hist_date + pd.DateOffset(months=1)
    forecast_end = pd.to_datetime("2027-12-01")
    
    forecast_dates = pd.date_range(start=forecast_start, end=forecast_end, freq='MS')
    h = len(forecast_dates)
    print(f"Forecast Horizon: {h} months (from {forecast_start.strftime('%Y-%m-%d')} to {forecast_end.strftime('%Y-%m-%d')})")
    
    # Create output folders
    data_out_dir = project_root / "output" / "data" / "cpi_forecast"
    model_out_dir = project_root / "output" / "model_summary" / "cpi_forecast"
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
                    
                # Register model
                add_model(
                    name=col,
                    model_type=f"ARIMAX {model.order}x{model.seasonal_order}",
                    source_data="cpi_historical_master.csv",
                    summary_path=f"output/model_summary/cpi_forecast/{col}_summary.txt",
                    status="Finalized"
                )
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
                    
                # Register model
                add_model(
                    name=col,
                    model_type=f"ARIMA {model.order}x{model.seasonal_order}",
                    source_data="cpi_historical_master.csv",
                    summary_path=f"output/model_summary/cpi_forecast/{col}_summary.txt",
                    status="Finalized"
                )
            except Exception as e:
                print(f"  [FAIL] auto_arima failed for {col}: {e}")
                sys.exit(1)
                
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
        # Sum of weights for components at each point in time
        w_cols = [f"weight_{c}" for c in components]
        i_cols = [f"index_{c}" for c in components]
        
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
    
    # Select columns to resample (indices and weights, drop is_forecast flag for resampling)
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
    db_path = project_root / "database" / "cpi_forecast" / "cpi_forecast.db"
    conn = sqlite3.connect(str(db_path))
    try:
        # Save monthly
        df_monthly_write = df_all.copy()
        df_monthly_write.index = df_monthly_write.index.strftime('%Y-%m-%d')
        df_monthly_write.to_sql("cpi_forecast_monthly", conn, if_exists="replace", index=True, index_label='date')
        
        # Save quarterly
        df_quarterly_write = df_quarterly.copy()
        df_quarterly_write.index = df_quarterly_write.index.strftime('%Y-%m-%d')
        df_quarterly_write.to_sql("cpi_forecast_quarterly", conn, if_exists="replace", index=True, index_label='date')
        
        # Save annual
        df_annual_write = df_annual.copy()
        df_annual_write.index = df_annual_write.index.strftime('%Y-%m-%d')
        df_annual_write.to_sql("cpi_forecast_annual", conn, if_exists="replace", index=True, index_label='date')
        
        conn.commit()
        print("[OK] Saved monthly, quarterly, and annual forecast tables to SQLite database.")
    except Exception as e:
        print(f"[Warning] Failed to write forecast tables to database: {e}")
    finally:
        conn.close()
        
    # 10. Register datasets in PROJECT_STATE.json
    try:
        add_dataset(
            series_id="CPI Forecast Monthly",
            source="auto_ARIMA Forecast",
            raw_path="output/data/cpi_forecast/cpi_historical_master.csv",
            transformed_path="output/data/cpi_forecast/cpi_forecast_monthly.csv",
            forecast_path="output/data/cpi_forecast/cpi_forecast_monthly.csv",
            status="Finalized"
        )
        add_dataset(
            series_id="CPI Forecast Quarterly",
            source="auto_ARIMA Forecast & QE Resampling",
            raw_path="output/data/cpi_forecast/cpi_historical_master.csv",
            transformed_path="output/data/cpi_forecast/cpi_forecast_quarterly.csv",
            forecast_path="output/data/cpi_forecast/cpi_forecast_quarterly.csv",
            status="Finalized"
        )
        add_dataset(
            series_id="CPI Forecast Annual",
            source="auto_ARIMA Forecast & YE Resampling",
            raw_path="output/data/cpi_forecast/cpi_historical_master.csv",
            transformed_path="output/data/cpi_forecast/cpi_forecast_annual.csv",
            forecast_path="output/data/cpi_forecast/cpi_forecast_annual.csv",
            status="Finalized"
        )
        print("[OK] Registered forecast datasets in PROJECT_STATE.json.")
    except Exception as e:
        print(f"[Warning] Failed to update PROJECT_STATE.json: {e}")

if __name__ == "__main__":
    main()
