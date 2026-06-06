# Baseline Univariate Forecasts Summary

This document summarizes the selection diagnostics and parameters for the baseline univariate forecasts of the export and import price component indices.

## 📝 Model Selection & Validation Metrics (12-Month-Ahead RMSE)

The models were evaluated using an **Expanding Rolling Window** starting in **January 2023** and ending in **April 2025** (providing out-of-sample evaluations against actuals up to April 2026). The model that achieved the lowest Root Mean Squared Error (RMSE) at the 12th month forecast horizon was chosen for each component.

| Component | Selected Model | SARIMAX RMSE | ETS RMSE | Random Forest RMSE | Best RMSE |
|---|---|---|---|---|---|
| Export: Agro-Industrial Product (AIP) | **ETS** | 2.6851 | 1.5704 | 1.6917 | **1.5704** |
| Export: Agricultural Product (AP) | **ETS** | 6.6241 | 5.5792 | 6.0170 | **5.5792** |
| Export: Mineral Product & Fuel (MF) | **RandomForest** | 25.4462 | 14.0861 | 13.3321 | **13.3321** |
| Export: Principal Manufacturing (MP) | **SARIMAX** | 0.8978 | 1.8655 | 1.9492 | **0.8978** |
| Import: Capital Goods (CA) | **SARIMAX** | 2.9688 | 4.2042 | 4.5336 | **2.9688** |
| Import: Consumer Goods (CO) | **SARIMAX** | 3.6236 | 7.7706 | 8.3512 | **3.6236** |
| Import: Fuel Product (FP) | **ETS** | 16.5307 | 13.9084 | 15.7605 | **13.9084** |
| Import: Raw Materials (RM) | **SARIMAX** | 4.9801 | 7.0667 | 7.3887 | **4.9801** |
| Import: Vehicle & Equipment (VE) | **ETS** | 1.7118 | 1.1737 | 1.8997 | **1.1737** |

## 🔍 Strategic Audit & Diagnostics

### Export: Agro-Industrial Product (AIP)
- **Best Model**: `ETS`
- **ARIMA Order (determined pre-validation)**: (1, 1, 1) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Export: Agricultural Product (AP)
- **Best Model**: `ETS`
- **ARIMA Order (determined pre-validation)**: (3, 1, 2) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Export: Mineral Product & Fuel (MF)
- **Best Model**: `RandomForest`
- **ARIMA Order (determined pre-validation)**: (3, 1, 0) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Export: Principal Manufacturing (MP)
- **Best Model**: `SARIMAX`
- **ARIMA Order (determined pre-validation)**: (1, 1, 1) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Import: Capital Goods (CA)
- **Best Model**: `SARIMAX`
- **ARIMA Order (determined pre-validation)**: (1, 1, 0) x (0, 1, 1, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Import: Consumer Goods (CO)
- **Best Model**: `SARIMAX`
- **ARIMA Order (determined pre-validation)**: (0, 1, 1) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Import: Fuel Product (FP)
- **Best Model**: `ETS`
- **ARIMA Order (determined pre-validation)**: (2, 1, 0) x (0, 1, 2, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Import: Raw Materials (RM)
- **Best Model**: `SARIMAX`
- **ARIMA Order (determined pre-validation)**: (1, 1, 0) x (0, 1, 1, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

### Import: Vehicle & Equipment (VE)
- **Best Model**: `ETS`
- **ARIMA Order (determined pre-validation)**: (0, 1, 0) x (2, 1, 0, 12)
- **Diagnostic Notes**: Residual analysis of the best-fitting models indicates that forecast errors represent white noise processes without remaining significant autocorrelation at standard lags.

