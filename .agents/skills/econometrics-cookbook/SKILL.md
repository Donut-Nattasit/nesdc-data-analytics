---
name: econometrics-cookbook
description: Standardized procedures and Python templates for time-series econometrics (ADF, ARDL, VAR, ARIMA). Use for the @econometrician to ensure theoretically sound modeling and residual diagnostics.
---

# Econometrics Cookbook Skill

## Core Workflow for Modeling
1. **Stationarity**: Always run an ADF test using the template in [python_templates.md](references/python_templates.md).
2. **Estimation**: Use `statsmodels` (ARDL, VAR) or `pmdarima` (Auto-ARIMA).
3. **Diagnostics**: You MUST verify that residuals are white noise using the Ljung-Box test.
4. **Documentation**: Save the `results.summary()` to `output/model/`.

## Reference Materials
- [python_templates.md](references/python_templates.md): Ready-to-use code snippets for estimation and diagnostics.

## Strategic Mandates
- Do not estimate a model on non-stationary data without differencing or cointegration justification.
- Every model must be accompanied by a "Strategic Econometric Audit" in the final output.
