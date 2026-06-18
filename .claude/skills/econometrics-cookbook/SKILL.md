---
name: econometrics-cookbook
description: >
  Provides standardized econometric modeling procedures, Python templates, and diagnostics for timeseries analysis. Use when fitting ARIMA, VAR, ARDL, or performing ADF stationarity and residual checks.
---

# Econometrics Cookbook Skill

## Purpose
This cookbook defines the mandatory statistical and econometric procedures for forecasting and nowcasting models in this workspace. It ensures all estimated models are theoretically sound, statistically verified, and properly audited.

## Decision Tree: Model Selection
Follow this pathway when choosing the appropriate econometric model:

```
                           Is the time-series stationary?
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼ (Yes)                                       ▼ (No)
        Are there exogenous variables?             Do they cointegrate?
                  │                                             │
          ┌───────┴───────┐                             ┌───────┴───────┐
          ▼ (No)          ▼ (Yes)                       ▼ (Yes)         ▼ (No)
     [Auto-ARIMA]    [SARIMAX / ARIMAX]             [ARDL / ECM]    [Difference first,
                                                                    then re-test]
```

1. **Univariate Stationary**:
   - Apply **Auto-ARIMA / Auto-ETS** using `pmdarima` or `statsforecast`.
2. **Exogenous Variables (Stationary Inputs)**:
   - Apply **ARIMAX / SARIMAX** from `statsmodels`.
3. **Non-Stationary Inputs with Cointegration**:
   - Apply **Engle-Granger Two-Stage Error Correction Model (ECM)** or **Autoregressive Distributed Lag (ARDL)**.
4. **Non-Stationary Inputs without Cointegration**:
   - Take first-differences ($\Delta Y_t$) to achieve stationarity, then re-estimate as an ARIMA/ARIMAX model.

## Execution Protocol

### Step 1 — Verify Stationarity (ADF Test)
* Run the Augmented Dickey-Fuller (ADF) test on all target variables and regressors.
* Consult code snippets in [python_templates.md](references/python_templates.md) to implement ADF checks.
* If p-value > 0.05, the series is non-stationary.

### Step 2 — Model Estimation & Diagnostic Checks
* Estimate model parameters using `statsmodels` or `pmdarima`.
* Perform the **Ljung-Box test** on residuals to check for autocorrelation. Residuals **must** be white noise (p-value > 0.05).
* Perform **Jarque-Bera test** to assess normality of residuals.

### Step 3 — Strategic Audit & Output
* Save model coefficients and diagnostic metrics using `results.summary()` to the folder `output/model_summary/[pipeline_name]/`.

## Troubleshooting

| Issue / Error | Cause | Resolution |
| :--- | :--- | :--- |
| `Singular Matrix / ConvergenceWarning` | High multicollinearity or over-parameterization | Drop redundant exogenous regressors, reduce lag orders, or simplify model structure. |
| `Residuals fail Ljung-Box (p < 0.05)` | Autocorrelation remains in residuals | Increase lag structures or include an auto-regressive (AR) term. |
| `Unit root present in residuals` | Non-stationary residuals (no cointegration) | Do not use level variables. First-difference the series and estimate in differences. |
