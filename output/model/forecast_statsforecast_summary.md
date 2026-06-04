# statsforecast & Exogenous Projections Summary

This document summarizes the model selection diagnostics and performance metrics for the univariate and exogenous forecasts generated for the Export & Import price component indices.

## 📝 Model Selection & Validation Metrics (12-Month-Ahead RMSE)

Evaluated using an **Expanding Rolling Window** starting in **January 2023** and ending in **April 2025** (out-of-sample evaluation up to April 2026). The model achieving the lowest RMSE at the 12th-month horizon was selected.

| Component | Selected Model | Method Type | 12-Month-Ahead Validation RMSE | Model/Lag Order Details |
|---|---|---|---|---|
| Export: Agro-Industrial Product (AIP) | **AutoARIMA** | Univariate | 1.3112 | AutoARIMA (seasonal search) |
| Export: Agricultural Product (AP) | **ARIMA with trend** | Univariate (Override) | 7.1771 | ARIMA(2,1,0)x(2,1,0)12 with drift |
| Export: Mineral Product & Fuel (MF) | **ARDL (Exog: Dubai)** | Exogenous | 5.4335 | ARDL (lags=12, order=1) |
| Export: Principal Manufacturing (MP) | **AutoARIMA** | Univariate | 1.1575 | AutoARIMA (seasonal search) |
| Import: Capital Goods (CA) | **AutoARIMA** | Univariate | 3.0628 | AutoARIMA (seasonal search) |
| Import: Consumer Goods (CO) | **AutoETS** | Univariate | 4.7128 | AutoETS (seasonal search) |
| Import: Fuel Product (FP) | **ARDL (Exog: Dubai)** | Exogenous | 7.4199 | ARDL (lags=12, order=1) |
| Import: Raw Materials (RM) | **AutoARIMA** | Univariate | 4.7882 | AutoARIMA (seasonal search) |
| Import: Vehicle & Equipment (VE) | **AutoETS** | Univariate | 1.1737 | AutoETS (seasonal search) |

> [!TIP]
> By integrating the forecasted path of **Dubai Crude Spot Price** as an exogenous regressor, we resolved the limitation of Naive flat forecasts for key energy-linked sectors, reducing the out-of-sample prediction error for **Import Fuel (FP)** and **Export Mineral Fuel (MF)**.


## 🔍 Strategic Audit & Diagnostics (Exogenous Models)

### Export: Mineral Product & Fuel (MF)
- **Winner Model**: `ARDL`
- **ARIMAX RMSE**: 8.4337
- **ARDL RMSE**: 5.4335
- **Diagnostic Notes**: Dubai crude spot predictions act as a highly significant leading exogenous driver. Incorporating this cointegrating relationship captures the structural downturn in energy indices predicted for 2026-2027.

### Import: Fuel Product (FP)
- **Winner Model**: `ARDL`
- **ARIMAX RMSE**: 8.1440
- **ARDL RMSE**: 7.4199
- **Diagnostic Notes**: Dubai crude spot predictions act as a highly significant leading exogenous driver. Incorporating this cointegrating relationship captures the structural downturn in energy indices predicted for 2026-2027.

