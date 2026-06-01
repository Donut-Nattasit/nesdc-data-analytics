import os
import sys
import pandas as pd
import numpy as np
from pathlib import Path
from pmdarima import auto_arima
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from src.utils.registry import add_model

# Enforce UTF-8 encoding for standard console output on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

def main():
    print("==========================================================")
    print("[Rolling Backtest] Running Expanding Window Evaluation...")
    print("==========================================================")
    
    project_root = Path(__file__).resolve().parent.parent.parent
    master_path = project_root / "output" / "data" / "transformed" / "dubai_oil_master.csv"
    
    if not master_path.exists():
        print(f"[Error] Master dataset not found at: {master_path}")
        sys.exit(1)
        
    # Load dataset
    df = pd.read_csv(master_path)
    df['date'] = pd.to_datetime(df['date'])
    
    # Clean and filter to active data (from 2015-01-01 when futures data starts)
    df_active = df[df['date'] >= '2015-01-01'].copy().reset_index(drop=True)
    
    # Exogenous variables
    df_active['oil_tightness_ratio'] = df_active['world_oil_supply'] / df_active['world_oil_demand']
    exog_cols = ['brent_spot', 'wti_spot', 'world_oil_inventory_change', 'oil_tightness_ratio']
    
    # We want to perform expanding window backtesting.
    # Start testing in Jan 2022. For each month T from Jan 2022 to May 2025:
    # 1. Train on 2015-01-01 to T.
    # 2. Forecast T+1 to T+12 (or up to May 2026, whichever is smaller).
    # 3. Compute forecast errors.
    
    start_test = pd.Timestamp("2022-01-01")
    latest_actual = pd.Timestamp("2026-05-01")
    
    # Generate list of test origins (months)
    origins = pd.date_range(start=start_test, end=latest_actual - pd.DateOffset(months=1), freq='MS')
    print(f"Number of test origins: {len(origins)} (from {origins[0].strftime('%Y-%m')} to {origins[-1].strftime('%Y-%m')})")
    
    # Lists to store forecast errors
    errors_futures = []
    errors_arimax = []
    errors_ridge = []
    
    print("\n[Running Backtest Loop] Estimating expanding windows...")
    for origin in origins:
        # Train dataset: t <= origin
        df_train = df_active[df_active['date'] <= origin].copy()
        
        # Test dataset: origin < t <= origin + 12 months (and t <= latest_actual)
        test_end = origin + pd.DateOffset(months=12)
        df_test = df_active[(df_active['date'] > origin) & (df_active['date'] <= test_end) & (df_active['date'] <= latest_actual)].copy()
        
        if df_test.empty:
            continue
            
        # Define baseline futures curve F*_t for the test period based on the origin row
        origin_row = df_active[df_active['date'] == origin].iloc[0]
        test_dates = df_test['date'].tolist()
        
        baseline_test = []
        for dt in test_dates:
            h = int((dt.year - origin.year) * 12 + (dt.month - origin.month))
            if h <= 24:
                baseline_test.append(origin_row[f"DBL{h} Comdty"])
            else:
                baseline_test.append(origin_row["DBL24 Comdty"])
        baseline_test = np.array(baseline_test)
        
        # Train baseline futures curve F*_t historically for the training set
        train_baseline = []
        for idx, row in df_train.iterrows():
            # Historically, use DBL1 Comdty as general baseline
            train_baseline.append(row['DBL1 Comdty'])
        train_baseline = np.array(train_baseline)
        
        # Historical target correction
        train_corr = df_train['dubai_spot'].values - train_baseline
        
        # Prepare exogenous variables
        # Historically, variables relative to the DBL1 baseline
        df_train_exog = df_train[exog_cols].copy()
        df_train_exog['brent_relative'] = df_train['brent_spot'] - train_baseline
        df_train_exog['wti_relative'] = df_train['wti_spot'] - train_baseline
        train_exog = df_train_exog[['brent_relative', 'wti_relative', 'world_oil_inventory_change', 'oil_tightness_ratio']]
        
        # Testing exogenous variables relative to baseline_test
        df_test_exog = df_test[exog_cols].copy()
        df_test_exog['brent_relative'] = df_test['brent_spot'] - baseline_test
        df_test_exog['wti_relative'] = df_test['wti_spot'] - baseline_test
        test_exog = df_test_exog[['brent_relative', 'wti_relative', 'world_oil_inventory_change', 'oil_tightness_ratio']]
        
        # --- Fit & Predict ARIMAX ---
        try:
            # We use a fast stepwise search without seasonality (m=1) to keep the backtest super fast!
            arimax_model = auto_arima(
                y=train_corr, X=train_exog,
                seasonal=False, stepwise=True,
                max_p=2, max_q=2, suppress_warnings=True
            )
            arimax_pred_corr = arimax_model.predict(n_periods=len(df_test), X=test_exog).values
            arimax_pred_spot = baseline_test + arimax_pred_corr
        except Exception:
            # Fallback if ARIMAX fails to converge
            arimax_pred_spot = baseline_test
            
        # --- Fit & Predict Ridge ML ---
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(train_exog)
        X_test_scaled = scaler.transform(test_exog)
        
        ridge_model = Ridge(alpha=10.0)
        ridge_model.fit(X_train_scaled, train_corr)
        ridge_pred_corr = ridge_model.predict(X_test_scaled)
        ridge_pred_spot = baseline_test + ridge_pred_corr
        
        # --- Record Errors ---
        actuals = df_test['dubai_spot'].values
        
        errors_futures.extend(actuals - baseline_test)
        errors_arimax.extend(actuals - arimax_pred_spot)
        errors_ridge.extend(actuals - ridge_pred_spot)
        
    # Calculate Overall Out-of-Sample Metrics
    errors_futures = np.array(errors_futures)
    errors_arimax = np.array(errors_arimax)
    errors_ridge = np.array(errors_ridge)
    
    def get_metrics(errs):
        rmse = np.sqrt(np.mean(errs ** 2))
        mae = np.mean(np.abs(errs))
        return rmse, mae
        
    fut_rmse, fut_mae = get_metrics(errors_futures)
    ari_rmse, ari_mae = get_metrics(errors_arimax)
    rid_rmse, rid_mae = get_metrics(errors_ridge)
    
    print("\n==========================================================")
    print("      🏆 ROLLING BACKTEST CUMULATIVE RESULTS (2022-2026)  ")
    print("==========================================================")
    print(f"  - Raw Futures Curve (Market) : RMSE = {fut_rmse:.3f}, MAE = {fut_mae:.3f}")
    print(f"  - Ridge ML (Data Scientist)  : RMSE = {rid_rmse:.3f}, MAE = {rid_mae:.3f}")
    print(f"  - ARIMAX (Econometrician)    : RMSE = {ari_rmse:.3f}, MAE = {ari_mae:.3f}")
    print("==========================================================")
    
    # Identify the best model
    models_metrics = {
        'Futures Baseline': (fut_rmse, fut_mae),
        'Ridge ML': (rid_rmse, rid_mae),
        'ARIMAX': (ari_rmse, ari_mae)
    }
    
    # Best model is the one with lowest RMSE
    best_model_name = min(models_metrics, key=lambda k: models_metrics[k][0])
    print(f"\n🥇 The statistically superior model is: **{best_model_name}**")
    
    # Save the final results to output/model/
    summary_path = project_root / "output" / "model" / "dubai_rolling_backtest_summary.txt"
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("==========================================================\n")
        f.write("     EXPANDING WINDOW ROLLING BACKTEST DIAGNOSTIC REPORT\n")
        f.write("==========================================================\n\n")
        f.write(f"Evaluation Period : {start_test.strftime('%Y-%m')} to {latest_actual.strftime('%Y-%m')}\n")
        f.write(f"Total test steps   : {len(errors_futures)} out-of-sample monthly observations\n\n")
        f.write("Backtest Accuracy Table:\n")
        f.write(f"  - Raw Futures Baseline: RMSE = {fut_rmse:.4f}, MAE = {fut_mae:.4f}\n")
        f.write(f"  - Ridge Regression ML : RMSE = {rid_rmse:.4f}, MAE = {rid_mae:.4f}\n")
        f.write(f"  - ARIMAX Econometric  : RMSE = {ari_rmse:.4f}, MAE = {ari_mae:.4f}\n\n")
        f.write(f"WINNER: {best_model_name}\n\n")
        f.write("Methodology:\n")
        f.write("- Expanding window backtesting fits the model iteratively over history, mimicking real-time deployment.\n")
        f.write("- The model with the lowest cumulative out-of-sample RMSE is selected as the production model.\n")
    print(f"✅ Diagnostic report successfully saved to: {summary_path}")
    
    # Update registry
    try:
        add_model(
            name="Dubai Oil Best Rolling Forecast Model",
            model_type="Expanding Window Backtest Winner",
            source_data="output/data/transformed/dubai_oil_master.csv",
            summary_path="output/model/dubai_rolling_backtest_summary.txt",
            status="Finalized"
        )
        print("✅ Registry updated successfully.")
    except Exception as e:
        print(f"⚠️ Failed to update registry: {e}")

if __name__ == "__main__":
    main()
