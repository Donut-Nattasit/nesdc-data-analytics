r"""
CQM monthly-indicator forecasting layer.

For every fetchable monthly indicator (and the fetchable derived ones, X_ECIFFOB /
X_MCIFFOB):

  1. clean the raw monthly series,
  2. seasonally adjust with X13-ARIMA-SEATS (bin/x13as.exe), STL fallback,
  3. forecast forward with auto_arima (re-optimised every run) to the horizon,
  4. build the 3-month moving-average variant,
  5. aggregate both to quarterly means -> the `_FQ` / `_3m_FQ` columns the bridge
     equations consume.

Output: a wide quarterly DataFrame whose columns are the seasonally-adjusted variable
names with `_FQ` and `_3m_FQ` suffixes (e.g. `X_TBPAA_SA_FQ`, `X_TIXIIB_SA_3m_FQ`),
covering history + forecast horizon.

Run:  & '.\bin\python.ps1' 'src\pipeline\cqm\forecast_indicators.py'
"""
from __future__ import annotations

import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from src.pipeline.cqm.config import load_config, project_root

warnings.filterwarnings("ignore")

OUT_DATA = project_root() / "output" / "data" / "cqm"
X13_PATH = str(project_root() / "bin")

# Forecast this many quarters beyond the last full NIPA quarter (set by orchestrator).
DEFAULT_FORECAST_QUARTERS = 5


# --------------------------------------------------------------------------- #
# Seasonal adjustment
# --------------------------------------------------------------------------- #
def seasonally_adjust(s: pd.Series, mode: str = "m") -> pd.Series:
    """X13-ARIMA-SEATS seasonal adjustment; STL fallback. Returns SA series on the
    same monthly index as the (cleaned) input."""
    s = _clean_monthly(s)
    if s is None or s.dropna().shape[0] < 36:
        return s
    # X13 needs a clean monthly PeriodIndex
    try:
        from statsmodels.tsa.x13 import x13_arima_analysis
        x = s.copy()
        x.index = pd.PeriodIndex(x.index, freq="M")
        use_log = (mode == "m") and (x.dropna() > 0).all()
        res = x13_arima_analysis(x.dropna(), x12path=X13_PATH, outlier=True,
                                 log=use_log, freq="M")
        out = res.seasadj
        out.index = out.index.to_timestamp("M")
        return out.reindex(s.index)
    except Exception:
        return _stl_sa(s, mode)


def _stl_sa(s: pd.Series, mode: str) -> pd.Series:
    from statsmodels.tsa.seasonal import STL
    x = s.dropna()
    if x.shape[0] < 24:
        return s
    mult = (mode == "m") and (x > 0).all()
    work = np.log(x) if mult else x
    try:
        res = STL(work, period=12, robust=True).fit()
        sa = work - res.seasonal
        sa = np.exp(sa) if mult else sa
        return sa.reindex(s.index)
    except Exception:
        return s


def _clean_monthly(s: pd.Series) -> pd.Series | None:
    """Trim leading/trailing NaN, interpolate interior gaps, enforce monthly freq."""
    s = s.dropna()
    if s.empty:
        return None
    s = s.asfreq("ME") if s.index.freqstr else s
    full = pd.date_range(s.index.min(), s.index.max(), freq="ME")
    s = s.reindex(full).interpolate(limit_area="inside")
    return s


# --------------------------------------------------------------------------- #
# ARIMA forecast (modernised: auto_arima re-optimised each run)
# --------------------------------------------------------------------------- #
def arima_extend(sa: pd.Series, horizon_end: pd.Timestamp) -> pd.Series:
    """Forecast `sa` monthly up to horizon_end using auto_arima; return actual+forecast."""
    sa = sa.dropna()
    if sa.empty:
        return sa
    last = sa.index.max()
    n_fore = (horizon_end.to_period("M") - last.to_period("M")).n
    if n_fore <= 0:
        return sa
    try:
        import pmdarima as pm
        model = pm.auto_arima(sa.values, seasonal=False, stepwise=True,
                              max_p=5, max_q=5, max_d=2, error_action="ignore",
                              suppress_warnings=True, with_intercept=True)
        fc = model.predict(n_periods=n_fore)
    except Exception:
        # fallback: random-walk-with-drift
        drift = sa.diff().tail(12).mean()
        fc = sa.iloc[-1] + drift * np.arange(1, n_fore + 1)
    idx = pd.date_range(last + pd.offsets.MonthEnd(1), periods=n_fore, freq="ME")
    return pd.concat([sa, pd.Series(np.asarray(fc, dtype=float), index=idx)])


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def _sa_varname(ind) -> str:
    """Canonical SA variable name as referenced by bridge equations
    (== ARIMA dependent-var base, e.g. 'X_TBDA_SA', 'X_PCI_SA', 'X_TMAAAAAA')."""
    if ind.arima and ind.arima.get("base"):
        return ind.arima["base"]
    return f"{ind.rename}_SA" if ind.x12 else ind.rename


def process_indicators(monthly: pd.DataFrame | None = None,
                       forecast_quarters: int = DEFAULT_FORECAST_QUARTERS,
                       last_nipa_q: pd.Timestamp | None = None,
                       save: bool = True) -> pd.DataFrame:
    cfg = load_config()
    if monthly is None:
        monthly = pd.read_csv(OUT_DATA / "monthly_indicators_raw.csv",
                              index_col=0, parse_dates=True)
    monthly.index = pd.to_datetime(monthly.index)

    # derived fetchable indicators (computed on raw monthly, then treated like the rest)
    formulas = {d.name: d.formula for d in cfg.derived if not d.manual}
    for name, formula in formulas.items():
        expr = formula
        for col in sorted(monthly.columns, key=len, reverse=True):
            expr = expr.replace(col, f"monthly['{col}']")
        try:
            monthly[name] = eval(expr)  # noqa: S307 - trusted config formulas
        except Exception as e:
            print(f"  derived {name} failed: {e}")

    # horizon
    if last_nipa_q is None:
        last_nipa_q = monthly.index.max().to_period("Q").to_timestamp("Q")
    horizon_end = (last_nipa_q.to_period("Q") + forecast_quarters).to_timestamp("M", how="end")
    horizon_end = pd.Timestamp(horizon_end).normalize() + pd.offsets.MonthEnd(0)
    print(f"Indicator forecast horizon -> {horizon_end:%Y-%m}")

    # build list of (column, sa_varname, mode)
    todo = []
    for ind in cfg.indicators:
        if ind.manual or ind.rename not in monthly.columns:
            continue
        mode = ind.x12["mode"] if ind.x12 else "m"
        todo.append((ind.rename, _sa_varname(ind), mode))
    for d in cfg.derived:
        if d.manual or d.name not in monthly.columns:
            continue
        base = d.arima["base"] if d.arima and d.arima.get("base") else f"{d.name}_SA"
        mode = d.x12["mode"] if d.x12 else "m"
        todo.append((d.name, base, mode))

    q_cols: dict[str, pd.Series] = {}
    n = len(todo)
    for k, (col, sa_var, mode) in enumerate(todo, 1):
        raw = monthly[col]
        sa = seasonally_adjust(raw, mode=mode)
        if sa is None or sa.dropna().empty:
            print(f"  [{k}/{n}] {col}: SKIP (no data)")
            continue
        ext = arima_extend(sa, horizon_end)
        ma3 = ext.rolling(3, min_periods=1).mean()
        # quarterly means (quarter-end aligned)
        fq = ext.resample("QE").mean()
        fq3 = ma3.resample("QE").mean()
        q_cols[f"{sa_var}_FQ"] = fq
        q_cols[f"{sa_var}_3m_FQ"] = fq3
        if k % 20 == 0 or k == n:
            print(f"  [{k}/{n}] processed (latest: {col})")

    qframe = pd.DataFrame(q_cols).sort_index()
    qframe.index = qframe.index.to_period("Q").to_timestamp("Q")
    qframe = qframe[~qframe.index.duplicated(keep="last")]

    if save:
        OUT_DATA.mkdir(parents=True, exist_ok=True)
        qframe.to_csv(OUT_DATA / "indicators_quarterly_FQ.csv")
        print(f"Saved {qframe.shape} -> {OUT_DATA / 'indicators_quarterly_FQ.csv'}")
    return qframe


if __name__ == "__main__":
    process_indicators()
