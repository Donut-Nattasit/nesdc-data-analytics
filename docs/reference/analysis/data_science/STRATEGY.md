# Data Science & Nowcasting Strategy

This document outlines the specialized modeling workflows for the `data_scientist` agent.

## 1. Nowcasting Framework

### MIDAS (Mixed-Data Sampling)
- **Use Case**: Predicting low-frequency (Quarterly GDP) using high-frequency (Monthly Retail Sales, Weekly Electricity).
- **Implementation**: Prefer the `statsmodels` implementation or custom weight functions (Exponential Almon, Beta).
- **Validation**: Compare against an AR(1) benchmark.

### Dynamic Factor Models (DFM)
- **Use Case**: Extracting a "Global Economic Indicator" from dozens of series.
- **Workflow**:
    1. Standardize all series.
    2. Extract principal components (static) or estimate using Kalman Filter (dynamic).
    3. Use the extracted factor as a feature in bridge equations.

## 2. Machine Learning Workflow

### Algorithm Selection
- **Tabular Data**: XGBoost, LightGBM, or Random Forest.
- **Small Datasets**: LASSO/Ridge regression to prevent overfitting.
- **Sequence Data**: LSTM if history > 200 observations.

### Validation Standards
- **TimeSeriesSplit**: Always use a temporal split to avoid data leakage.
- **Feature Selection**: Use Recursive Feature Elimination (RFE) or SHAP values to prune irrelevant features.

## 3. Tooling
- **Primary Libraries**: `scikit-learn`, `xgboost`, `statsmodels`, `pandas`.
- **Plotting**: Feature importance plots should be saved alongside model results.
