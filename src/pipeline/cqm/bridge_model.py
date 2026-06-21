r"""
CQM bridge-equation + identity engine.

Inputs:
  * NIPA quarterly actuals (levels, sa renames: ZNS010.., ZRS010.., YNS010.., ...)
  * indicator quarterly frame (X_..._FQ / X_..._3m_FQ, actual + forecast)

Pipeline:
  1. apply accounting identities to NIPA actuals -> derived actual series
     (ZPS = ZNS/ZRS*100, YPS, service aggregates, etc.) needed as bridge LHS.
  2. estimate each bridge equation (OLS on the differenced transforms) on the
     historical overlap. Regressors are resolved from indicators + NIPA lags;
     unresolvable terms (manual GIFDATA, dummies, unbuilt financials) are dropped.
     If an equation has no usable regressor it is marked for univariate fallback.
  3. forecast quarter-by-quarter (iterative, to satisfy self-lag terms); integrate
     the predicted differences back to levels.
  4. univariate auto_arima forecast for fallback equations and for any NIPA leaf
     component lacking a bridge equation.
  5. re-apply identities over the full (actual+forecast) frame to rebuild aggregates.

The result is a full NIPA frame (levels) spanning history + forecast.
"""
from __future__ import annotations

import re
import warnings

import numpy as np
import pandas as pd
import statsmodels.api as sm

from src.pipeline.cqm.config import load_config

warnings.filterwarnings("ignore")

_ATOM = re.compile(r"^(D\d)?([A-Za-z_]\w*)(?:\(-(\d+)\))?$")


# --------------------------------------------------------------------------- #
# term resolution
# --------------------------------------------------------------------------- #
def _resolve_atom(token: str, ns: dict[str, pd.Series], index: pd.DatetimeIndex):
    """'D1ZRS160(-1)' -> diff then lag of ns['ZRS160']; returns Series or None."""
    m = _ATOM.match(token.strip())
    if not m:
        return None
    dpref, name, lag = m.groups()
    if name not in ns:
        return None
    s = ns[name].reindex(index)
    if dpref:
        k = int(dpref[1])
        s = s - s.shift(k)
    if lag:
        s = s.shift(int(lag))
    return s


def _resolve_term(term: str, ns: dict[str, pd.Series], index: pd.DatetimeIndex):
    """Resolve a regressor term, possibly an arithmetic group like
    '(0.6*D1X_PCIM_SA_FQ + 0.4*D1X_PCIO_SA_FQ)'. Returns Series or None if any
    referenced variable is unresolvable."""
    term = term.strip()
    atoms = re.findall(r"(?:D\d)?[A-Za-z_]\w*(?:\(-\d+\))?", term)
    local = {}
    expr = term
    for i, a in enumerate(sorted(set(atoms), key=len, reverse=True)):
        if re.fullmatch(r"\d+", a):
            continue
        s = _resolve_atom(a, ns, index)
        if s is None:
            return None
        key = f"__v{i}"
        local[key] = s
        expr = expr.replace(a, f"local['{key}']")
    if not local:
        return None
    try:
        out = eval(expr, {"local": local, "np": np})  # noqa: S307 trusted config
        return out if isinstance(out, pd.Series) else None
    except Exception:
        return None


# --------------------------------------------------------------------------- #
# identities
# --------------------------------------------------------------------------- #
def apply_identities(df: pd.DataFrame, identities: list[dict], passes: int = 6) -> pd.DataFrame:
    """Evaluate 'target = expr' identities against df columns (multi-pass for deps).
    Skips the contradictory duplicate service-aggregate rows (handled separately)."""
    df = df.copy()
    skip_targets = {"ZNS540", "ZRS540", "ZPS540"}  # duplicated/conflicting in source
    for _ in range(passes):
        changed = False
        for idn in identities:
            tgt, expr = idn["target"], idn["expr"]
            if tgt in skip_targets:
                continue
            names = [n for n in re.findall(r"[A-Za-z_]\w*", expr) if n != "np"]
            if any(n not in df.columns for n in set(names)):
                continue
            try:
                local = {n: df[n] for n in set(names)}
                val = eval(expr, {"np": np}, local)  # noqa: S307
                if tgt not in df.columns or not df[tgt].equals(val):
                    df[tgt] = val
                    changed = True
            except Exception:
                continue
        if not changed:
            break
    return df


# --------------------------------------------------------------------------- #
# engine
# --------------------------------------------------------------------------- #
class BridgeEngine:
    def __init__(self, nipa_actual: pd.DataFrame, ind_fq: pd.DataFrame, cfg=None):
        self.cfg = cfg or load_config()
        # unify both frames to normalised quarter-END timestamps
        self.ind = ind_fq.copy()
        self.ind.index = pd.PeriodIndex(self.ind.index, freq="Q").to_timestamp(how="end").normalize()
        self.ind = self.ind[~self.ind.index.duplicated(keep="last")].sort_index()
        nipa_actual = nipa_actual.copy()
        nipa_actual.index = pd.PeriodIndex(nipa_actual.index, freq="Q").to_timestamp(how="end").normalize()
        self.nipa_actual = apply_identities(nipa_actual, self.cfg.identities)
        self.last_actual_q = self.nipa_actual.dropna(how="all").index.max()
        self.fq_index = self.ind.index[self.ind.index > self.last_actual_q]
        self.results = {}     # eqn name -> dict(params, terms, base, diff)
        self.fallback = []    # list of (lhs_base, diff)

    # -- namespace for a given working NIPA frame --
    def _ns(self, nipa: pd.DataFrame) -> dict[str, pd.Series]:
        ns = {c: nipa[c] for c in nipa.columns}
        for c in self.ind.columns:
            ns[c] = self.ind[c]
        return ns

    def estimate(self):
        full_index = self.nipa_actual.index
        ns = self._ns(self.nipa_actual)
        for b in self.cfg.bridges:
            lhs = _resolve_atom(b["lhs"], ns, full_index)
            if lhs is None:
                continue
            cols, names = [], []
            for term in b["rhs"]:
                s = _resolve_term(term, ns, full_index)
                if s is not None:
                    cols.append(s.rename(term)); names.append(term)
            if not cols:
                self.fallback.append((b["lhs_base"], b["lhs_diff"]))
                continue
            X = pd.concat(cols, axis=1)
            data = pd.concat([lhs.rename("_y"), X], axis=1).dropna()
            if len(data) < 12:
                self.fallback.append((b["lhs_base"], b["lhs_diff"]))
                continue
            y = data["_y"]; Xd = data[names]
            if b["const"]:
                Xd = sm.add_constant(Xd, has_constant="add")
            try:
                model = sm.OLS(y, Xd).fit()
            except Exception:
                self.fallback.append((b["lhs_base"], b["lhs_diff"]))
                continue
            self.results[b["name"]] = {
                "params": model.params, "terms": names, "const": b["const"],
                "base": b["lhs_base"], "diff": b["lhs_diff"], "rsq": model.rsquared,
            }
        return self

    def forecast(self) -> pd.DataFrame:
        """Iteratively forecast bridged components; return full NIPA frame (levels)."""
        # working frame = actual extended with NaN rows for forecast quarters
        nipa = self.nipa_actual.reindex(self.nipa_actual.index.union(self.fq_index))
        # order equations: nominal/real before price (P), so contemporaneous P deps resolve
        ordered = sorted(self.results.items(),
                         key=lambda kv: (0 if kv[1]["base"][2] != "P" else 1))
        for t in self.fq_index:
            ns = self._ns(nipa)
            for _name, r in ordered:
                base, k = r["base"], r["diff"]
                val = r["params"].get("const", 0.0) if r["const"] else 0.0
                ok = True
                for term in r["terms"]:
                    s = _resolve_term(term, ns, nipa.index)
                    if s is None or pd.isna(s.get(t, np.nan)):
                        ok = False; break
                    val += r["params"][term] * s.loc[t]
                if not ok:
                    continue
                prev = nipa[base].shift(k).get(t, np.nan) if base in nipa.columns else np.nan
                if pd.isna(prev):
                    continue
                nipa.loc[t, base] = prev + val
                ns[base] = nipa[base]  # update namespace for contemporaneous deps
        # univariate fallback for marked components + non-bridged leaves handled by caller
        nipa = self._univariate_fill(nipa)
        nipa = apply_identities(nipa, self.cfg.identities)
        return nipa

    def _univariate_fill(self, nipa: pd.DataFrame) -> pd.DataFrame:
        """auto_arima fallback on LEVELS for fallback components that are still NaN
        in the forecast window."""
        import pmdarima as pm
        targets = {base for base, _ in self.fallback}
        for base in sorted(targets):
            if base not in nipa.columns:
                continue
            col = nipa[base]
            actual = col.loc[:self.last_actual_q].dropna()
            need = nipa.index[(nipa.index > self.last_actual_q) & col.isna()]
            if actual.shape[0] < 12 or len(need) == 0:
                continue
            try:
                m = pm.auto_arima(actual.values, seasonal=False, stepwise=True,
                                  max_p=4, max_q=4, max_d=2, error_action="ignore",
                                  suppress_warnings=True)
                fc = m.predict(n_periods=len(need))
            except Exception:
                drift = actual.diff().tail(8).mean()
                fc = actual.iloc[-1] + drift * np.arange(1, len(need) + 1)
            nipa.loc[need, base] = np.asarray(fc, dtype=float)
        return nipa


def univariate_forecast_levels(nipa: pd.DataFrame, cols: list[str],
                               last_actual_q: pd.Timestamp,
                               fq_index: pd.DatetimeIndex) -> pd.DataFrame:
    """Fill any remaining NIPA columns (no bridge) over the forecast window via
    auto_arima on the level."""
    import pmdarima as pm
    nipa = nipa.copy()
    for c in cols:
        if c not in nipa.columns:
            continue
        actual = nipa[c].loc[:last_actual_q].dropna()
        need = fq_index[nipa[c].reindex(fq_index).isna()]
        if actual.shape[0] < 12 or len(need) == 0:
            continue
        try:
            m = pm.auto_arima(actual.values, seasonal=False, stepwise=True,
                              max_p=4, max_q=4, max_d=2, error_action="ignore",
                              suppress_warnings=True)
            fc = m.predict(n_periods=len(need))
        except Exception:
            drift = actual.diff().tail(8).mean()
            fc = actual.iloc[-1] + drift * np.arange(1, len(need) + 1)
        nipa.loc[need, c] = np.asarray(fc, dtype=float)
    return nipa
