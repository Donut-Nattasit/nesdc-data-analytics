"""
Deflator Prediction Pipeline - Step 2: Log-space auto-ARIMAX forecast.

Models log(GDP deflator) with log-transformed exogenous regressors
(Headline CPI shock, export price index, import price index) in a log-log
elasticity form. Forecasts to 2027-Q4, back-transforms via exp(), and writes
quarterly & annual YoY outputs plus diagnostics text files for the appendix.
"""
from pathlib import Path
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT / "output" / "data" / "deflator_prediction"
MS_DIR = ROOT / "output" / "model_summary" / "deflator_prediction"
INPUT = DATA_DIR / "deflator_prediction_input_quarterly.csv"

TARGET = "gdp_deflator"
EXOG_COLS = ["Headline_CPI", "bot_export_price_index", "bot_import_price_index"]


def _stationarity_report(df_hist: pd.DataFrame) -> str:
    from statsmodels.tsa.stattools import adfuller, kpss
    lines = ["STATIONARITY TESTS (log levels)\n" + "=" * 60]

    def adf(series, label):
        s = series.dropna()
        r = adfuller(s, autolag="AIC")
        return (f"\n[ADF] {label}\n"
                f"  ADF statistic : {r[0]:.4f}\n"
                f"  p-value       : {r[1]:.4f}\n"
                f"  lags used     : {r[2]}\n"
                f"  conclusion    : {'stationary' if r[1] <= 0.05 else 'NON-stationary'} (5%)")

    def kpss_t(series, label):
        s = series.dropna()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            r = kpss(s, regression="c", nlags="auto")
        return (f"\n[KPSS] {label}\n"
                f"  KPSS statistic: {r[0]:.4f}\n"
                f"  p-value       : {r[1]:.4f}\n"
                f"  conclusion    : {'NON-stationary' if r[1] <= 0.05 else 'stationary'} (5%)")

    log_y = np.log(df_hist[TARGET])
    lines.append("\n--- TARGET: log(gdp_deflator) ---")
    lines.append(adf(log_y, "level"))
    lines.append(kpss_t(log_y, "level"))
    lines.append(adf(log_y.diff(), "first difference"))
    lines.append(kpss_t(log_y.diff(), "first difference"))

    for c in EXOG_COLS:
        lines.append(f"\n--- EXOG: log({c}) ---")
        lines.append(adf(np.log(df_hist[c]), "level"))
        lines.append(adf(np.log(df_hist[c]).diff(), "first difference"))

    return "\n".join(lines) + "\n"


def main():
    MS_DIR.mkdir(parents=True, exist_ok=True)
    import pmdarima as pm
    from statsmodels.stats.diagnostic import acorr_ljungbox
    from scipy.stats import jarque_bera

    df = pd.read_csv(INPUT, index_col=0, parse_dates=True).sort_index()
    hist = df[df["is_forecast"] == 0]
    fcst = df[df["is_forecast"] == 1]

    log_y = np.log(hist[TARGET])
    log_X = np.log(hist[EXOG_COLS])
    log_X_future = np.log(fcst[EXOG_COLS])
    h = len(fcst)

    # --- Stationarity tests (appendix A) ---
    stat_txt = _stationarity_report(hist)
    (MS_DIR / "stationarity_tests.txt").write_text(stat_txt, encoding="utf-8")
    print(stat_txt)

    # --- Fit log-log auto-ARIMAX (quarterly seasonality m=4) ---
    model = pm.auto_arima(
        log_y, X=log_X,
        seasonal=True, m=4,
        stepwise=True, error_action="ignore", suppress_warnings=True,
        trace=True,
    )
    print(f"\n[model] selected order {model.order} seasonal {model.seasonal_order}")

    # --- Forecast (log space) + 95% CI, then back-transform ---
    log_pred, log_ci = model.predict(n_periods=h, X=log_X_future, return_conf_int=True, alpha=0.05)
    pred = np.exp(np.asarray(log_pred))
    ci_lower = np.exp(log_ci[:, 0])
    ci_upper = np.exp(log_ci[:, 1])

    # --- Assemble level series: history actual + forecast ---
    level = pd.DataFrame(index=df.index)
    level["deflator"] = df[TARGET]
    level.loc[fcst.index, "deflator"] = pred
    level["deflator_lower"] = np.nan
    level["deflator_upper"] = np.nan
    level.loc[fcst.index, "deflator_lower"] = ci_lower
    level.loc[fcst.index, "deflator_upper"] = ci_upper
    level["is_forecast"] = df["is_forecast"].values

    # --- Quarterly YoY (pct_change of 4 quarters) ---
    level["deflator_yoy"] = level["deflator"].pct_change(4) * 100
    base4 = level["deflator"].shift(4)
    level["deflator_yoy_lower"] = (level["deflator_lower"] / base4 - 1) * 100
    level["deflator_yoy_upper"] = (level["deflator_upper"] / base4 - 1) * 100

    q_path = DATA_DIR / "deflator_forecast_quarterly.csv"
    level.to_csv(q_path)
    print(f"[saved] {q_path}")

    # --- Annual (calendar-year mean of quarterly level) ---
    annual = level[["deflator"]].resample("YE").mean()
    counts = level["deflator"].resample("YE").count()
    annual = annual[counts == 4]  # full years only
    annual["deflator_yoy"] = annual["deflator"].pct_change(1) * 100
    fc_years = level.loc[level["is_forecast"] == 1].resample("YE")["is_forecast"].max()
    annual["is_forecast"] = fc_years.reindex(annual.index).fillna(0).astype(int)
    a_path = DATA_DIR / "deflator_forecast_annual.csv"
    annual.to_csv(a_path)
    print(f"[saved] {a_path}")

    # --- Model summary (appendix B) ---
    summary_txt = model.summary().as_text()
    (MS_DIR / "arimax_summary.txt").write_text(
        f"LOG-LOG AUTO-ARIMAX  order={model.order} seasonal={model.seasonal_order}\n"
        f"Exogenous (log): {EXOG_COLS}\n\n" + summary_txt + "\n",
        encoding="utf-8",
    )

    # --- Residual diagnostics (appendix C) ---
    # Drop seasonal-differencing burn-in (first d + m*D obs) which are unreliable.
    d, (_, big_d, _, m) = model.order[1], model.seasonal_order
    burn = d + m * big_d
    resid = pd.Series(model.resid()).iloc[burn:].reset_index(drop=True)
    lb = acorr_ljungbox(resid, lags=[4, 8], return_df=True)
    jb_stat, jb_p = jarque_bera(resid.dropna())
    diag = [
        "RESIDUAL DIAGNOSTICS", "=" * 60,
        f"\n(first {burn} burn-in residuals from differencing dropped; n={len(resid)})",
        f"\nLjung-Box test (H0: no autocorrelation):",
        lb.to_string(),
        f"\n  lag 4 p-value : {lb['lb_pvalue'].iloc[0]:.4f} "
        f"=> {'white noise' if lb['lb_pvalue'].iloc[0] > 0.05 else 'AUTOCORRELATION present'}",
        f"\nJarque-Bera test (H0: normal residuals):",
        f"  JB statistic  : {jb_stat:.4f}",
        f"  p-value       : {jb_p:.4f} "
        f"=> {'normal' if jb_p > 0.05 else 'NON-normal'}",
        f"\nResidual mean   : {resid.mean():.5f}",
        f"Residual std    : {resid.std():.5f}",
    ]
    diag_txt = "\n".join(diag) + "\n"
    (MS_DIR / "residual_diagnostics.txt").write_text(diag_txt, encoding="utf-8")
    print(diag_txt)

    # --- Console summary ---
    print("\n=== FORECAST (quarterly YoY %) ===")
    print(level.loc[fcst.index, ["deflator", "deflator_yoy"]].round(2).to_string())
    print("\n=== FORECAST (annual YoY %) ===")
    print(annual.round(2).to_string())
    return q_path, a_path


if __name__ == "__main__":
    main()
