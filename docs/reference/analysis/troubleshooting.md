# Econometric Analysis Troubleshooting

This document records known pitfalls, diagnostic failures, and solutions for statistical modeling.

## Stationarity & Unit Roots
- **ADF Test**: If the p-value is > 0.05, the series is non-stationary.
- **Solution**: Apply first-differencing (`df.diff()`) or log-differencing. Re-test stationarity after transformation.

## Model Estimation
- **ARDL/VAR**: Ensure there are no missing values (`NaN`) in the dataset before fitting, as these will cause the estimation to fail.
- **Singular Matrix**: Occurs in VAR if series are perfectly collinear or if the number of variables exceeds the number of observations.
- **Overfitting**: Be cautious with high lag orders (max_p, max_q). Check AIC/BIC to ensure the model is parsimonious.

## Forecasting
- **Confidence Intervals**: Always provide confidence intervals (usually 95%) to communicate forecast uncertainty.
- **StatsForecast**: Requires data in "Long" format with specific column names (`unique_id`, `ds`, `y`). Ensure the DataFrame is prepared correctly before calling `fast_batch_forecast()`.

## Diagnostics
- **Serial Correlation**: Check residuals for white noise. If residuals are correlated, the model lags are likely underspecified.
- **Normality**: Check if residuals are normally distributed for valid inference.
