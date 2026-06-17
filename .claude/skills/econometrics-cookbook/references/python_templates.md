# Econometrics Python Cookbook

This reference provides standardized code snippets for the `statsmodels` and `pmdarima` libraries.

## 1. Stationarity Testing (ADF Test)
```python
from statsmodels.tsa.stattools import adfuller

def check_stationarity(series):
    result = adfuller(series.dropna())
    print(f'ADF Statistic: {result[0]}')
    print(f'p-value: {result[1]}')
    return result[1] <= 0.05
```

## 2. ARDL Model Template
```python
from statsmodels.tsa.ardl import ARDL

# Assuming df has columns 'y' (target) and 'x1', 'x2' (exogenous)
model = ARDL(df['y'], lags=2, exog=df[['x1', 'x2']], order={'x1': 1, 'x2': 1})
results = model.fit()
print(results.summary())
```

## 3. Auto-ARIMA Forecasting
```python
import pmdarima as pm

model = pm.auto_arima(series, seasonal=True, m=4, suppress_warnings=True) # m=4 for quarterly
forecast, conf_int = model.predict(n_periods=8, return_conf_int=True)
```

## 4. Residual Diagnostics (Mandatory)
```python
from statsmodels.stats.diagnostic import acorr_ljungbox

def check_residuals(results):
    # Ljung-Box test for white noise
    lb_test = acorr_ljungbox(results.resid, lags=[10], return_df=True)
    print(f"Ljung-Box p-value: {lb_test['lb_pvalue'].values[0]}")
    # If p > 0.05, residuals are white noise (Success)
```
