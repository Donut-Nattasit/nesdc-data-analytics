"""
CQM pipeline configuration loader.

Parses the legacy EViews model specification (`input/CQM/EViews Codes/metadata.xlsx`)
plus the CEIC numeric series-ID mapping embedded in the Master Excel headers, into
clean Python structures the rest of the pipeline consumes.

Nothing here hits the network or fits models — it is pure config parsing so it can be
imported cheaply and inspected.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

import pandas as pd


def project_root() -> Path:
    # src/pipeline/cqm/config.py -> parents[3] == project root
    return Path(__file__).resolve().parents[3]


CQM_INPUT = project_root() / "input" / "CQM" / "EViews Codes"
METADATA_XLSX = CQM_INPUT / "metadata.xlsx"
MASTER_M = CQM_INPUT / "15_T_MasterM_20240501.xls"
MASTER_Q = CQM_INPUT / "16_T_MasterQ_20240405.xls"

# Internal / manual-update series with no CEIC numeric ID (the GIFDATA group).
# These get an ARIMA/hold-growth placeholder until NESDC supplies real disbursement data.
MANUAL_SERIES = {"GCONCUR", "GEQCUR", "GCONCAP", "GEQCAP", "SOECON", "RTI", "WSI"}


# --------------------------------------------------------------------------- #
# CEIC numeric ID extraction from Master Excel headers
# --------------------------------------------------------------------------- #
def _extract_id_map(xls: Path, sheets: list[str]) -> dict[str, dict]:
    """mnemonic(upper) -> {'ceic_id': str|None, 'name': str}.

    Header carries a 'Series ID' row with numeric ids (sometimes '12345 (MNEMONIC)')
    and, in the monthly file, a second 'Series ID' row holding the bare mnemonic.
    Columns are aligned across both rows.
    """
    out: dict[str, dict] = {}
    for sheet in sheets:
        try:
            raw = pd.read_excel(xls, sheet_name=sheet, header=None, nrows=15)
        except Exception:
            continue
        id_rows = [i for i in range(len(raw))
                   if str(raw.iloc[i, 0]).strip().lower() == "series id"]
        if not id_rows:
            continue
        ncols = raw.shape[1]
        numeric: dict[int, str] = {}
        mnem: dict[int, str] = {}
        for r in id_rows:
            for col in range(1, ncols):
                val = raw.iloc[r, col]
                if pd.isna(val):
                    continue
                s = str(val).strip()
                m = re.match(r"^(\d{6,})\s*(?:\((\w+)\))?", s)
                if m:
                    numeric[col] = m.group(1)
                    if m.group(2):
                        mnem[col] = m.group(2)
                elif re.match(r"^[A-Za-z]\w+$", s):
                    mnem[col] = s
        for col in range(1, ncols):
            if col in mnem:
                key = mnem[col].upper()
                name = str(raw.iloc[0, col]) if raw.shape[0] else ""
                # keep first non-null ceic id seen for a mnemonic
                if key not in out or (out[key]["ceic_id"] is None and numeric.get(col)):
                    out[key] = {"ceic_id": numeric.get(col), "name": name.strip()}
    return out


@lru_cache(maxsize=1)
def id_map_monthly() -> dict[str, dict]:
    return _extract_id_map(MASTER_M, ["sheet1", "1-81 New", "82-155 new"])


@lru_cache(maxsize=1)
def id_map_quarterly() -> dict[str, dict]:
    return _extract_id_map(MASTER_Q, ["Data", "sheet1"])


# --------------------------------------------------------------------------- #
# Spec parsers (EViews syntax -> structured)
# --------------------------------------------------------------------------- #
def parse_arima(spec) -> dict | None:
    """'e_X_TBDA_SA.LS D(X_TBDA_SA) C ar(1) ar(2) ar(8)' ->
    {'lhs_raw': 'D(X_TBDA_SA)', 'diff': 1, 'base': 'X_TBDA_SA', 'ar': [1,2,8], 'ma': []}.
    Legacy fixed orders kept for reference; the modern engine uses auto_arima."""
    if not isinstance(spec, str) or not spec.strip():
        return None
    s = spec.strip()
    ar = [int(x) for x in re.findall(r"ar\((\d+)\)", s)]
    ma = [int(x) for x in re.findall(r"ma\((\d+)\)", s)]
    # dependent variable token is the first thing after '.ls'/'.LS'
    m = re.search(r"\.ls\s+(\S+)", s, re.IGNORECASE)
    lhs = m.group(1) if m else None
    diff, base = _parse_diff(lhs) if lhs else (0, lhs)
    return {"lhs_raw": lhs, "diff": diff, "base": base, "ar": ar, "ma": ma, "raw": s}


def _parse_diff(token: str | None) -> tuple[int, str | None]:
    """'D(X_TBDA_SA)'->(1,'X_TBDA_SA'); 'D(X_PCI_SA,2,0)'->(2,'X_PCI_SA');
    'D4ZNS060'->(4,'ZNS060'); 'D1YRS010'->(1,'YRS010'); 'ZNS060'->(0,'ZNS060')."""
    if not token:
        return 0, token
    t = token.strip()
    m = re.match(r"^D(\d+)(.+)$", t)            # D1X.., D4X..
    if m:
        return int(m.group(1)), m.group(2)
    m = re.match(r"^D\((.+?)(?:,(\d+).*)?\)$", t)  # D(x) or D(x,2,0)
    if m:
        return (int(m.group(2)) if m.group(2) else 1), m.group(1)
    return 0, t


def parse_x12(spec) -> dict | None:
    """'X_TBDA.X12' -> {'mode':'m'}; 'X_TJUGTL.X12(mode=a)' -> {'mode':'a'}.
    None/blank -> series already seasonally adjusted (no X12)."""
    if not isinstance(spec, str) or ".x12" not in spec.lower():
        return None
    mode = "a" if re.search(r"mode\s*=\s*a", spec, re.IGNORECASE) else "m"
    return {"mode": mode}


def parse_bridge(spec) -> dict | None:
    """'e_TH_Prod6n.ls D4ZNS060 C D4X_GCON_SA_FQ ar(1)' ->
    {'name':'e_TH_Prod6n','lhs':'D4ZNS060','lhs_base':'ZNS060','lhs_diff':4,
     'rhs':['D4X_GCON_SA_FQ'], 'ar':[1], 'ma':[], 'raw':...}.
    Inline comments after a quote (') are dropped. Handles simple (a*x+b*y) terms."""
    if not isinstance(spec, str) or ".ls" not in spec.lower():
        return None
    s = spec.split("'")[0].strip()  # drop trailing EViews comment
    m = re.match(r"^(\S+?)\.ls\s+(.*)$", s, re.IGNORECASE)
    if not m:
        return None
    name, body = m.group(1), m.group(2)
    ar = [int(x) for x in re.findall(r"ar\((\d+)\)", body)]
    ma = [int(x) for x in re.findall(r"ma\((\d+)\)", body)]
    body = re.sub(r"\b(?:ar|ma)\(\d+\)", "", body, flags=re.IGNORECASE)
    # tokens: respect parentheses groups as single regressors
    tokens = _split_terms(body)
    lhs = tokens[0]
    rhs = [t for t in tokens[1:] if t.upper() != "C"]
    has_const = any(t.upper() == "C" for t in tokens[1:])
    lhs_diff, lhs_base = _parse_diff(lhs)
    return {
        "name": name, "lhs": lhs, "lhs_base": lhs_base, "lhs_diff": lhs_diff,
        "rhs": rhs, "const": has_const, "ar": ar, "ma": ma, "raw": spec.strip(),
    }


def _split_terms(body: str) -> list[str]:
    """Split on whitespace but keep parenthesised groups intact."""
    terms, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1; cur += ch
        elif ch == ")":
            depth -= 1; cur += ch
        elif ch.isspace() and depth == 0:
            if cur.strip():
                terms.append(cur.strip())
            cur = ""
        else:
            cur += ch
    if cur.strip():
        terms.append(cur.strip())
    return terms


# --------------------------------------------------------------------------- #
# Public config structures
# --------------------------------------------------------------------------- #
@dataclass
class Indicator:
    mnemonic: str
    ceic_id: str | None
    rename: str            # e.g. X_TBDA
    name: str
    x12: dict | None
    arima: dict | None
    manual: bool = False


@dataclass
class Derived:
    """An indicator computed from other indicators (Series-ID cell starts with X_,
    Rename cell holds the formula, e.g. X_GCON = X_Gconcur + X_Gconcap)."""
    name: str              # e.g. X_GCON
    formula: str           # e.g. 'X_Gconcur + X_Gconcap'
    x12: dict | None
    arima: dict | None
    manual: bool = False   # True if any input is a manual/GIFDATA series


@dataclass
class CQMConfig:
    indicators: list[Indicator] = field(default_factory=list)
    derived: list[Derived] = field(default_factory=list)
    nipa: pd.DataFrame = None          # raw NIPA sheet (rename/recalc/bridge cols)
    bridges: list[dict] = field(default_factory=list)
    identities: list[dict] = field(default_factory=list)  # {'target','expr'}

    def indicator_ids(self, include_manual=False) -> dict[str, str]:
        """rename -> ceic_id for fetchable indicators."""
        return {i.rename: i.ceic_id for i in self.indicators
                if i.ceic_id and (include_manual or not i.manual)}


def _clean_rename(val) -> str | None:
    """Rename cell can be 'X_TBDA' or 'X_TIYZDAAAAAAAAB  X_PPITIYZDAB' (two names).
    Take the FIRST token as the canonical rename used downstream."""
    if not isinstance(val, str) or not val.strip():
        return None
    return val.split()[0].strip()


@lru_cache(maxsize=1)
def load_config() -> CQMConfig:
    ind_df = pd.read_excel(METADATA_XLSX, sheet_name="Indicators")
    nipa_df = pd.read_excel(METADATA_XLSX, sheet_name="NIPA")
    mmap = id_map_monthly()

    indicators: list[Indicator] = []
    derived: list[Derived] = []
    seen_renames: set[str] = set()
    for _, row in ind_df.iterrows():
        sid = row.get("Series ID")
        if not isinstance(sid, str) or not sid.strip():
            continue
        sid = sid.strip()
        x12 = parse_x12(row.get("X12 (Seasonality)"))
        arima = parse_arima(row.get("ARIMA"))

        if sid.upper().startswith("X_"):
            # Derived series: Series-ID cell IS the new name; Rename cell is a formula.
            formula = row.get("Rename")
            if not isinstance(formula, str) or not formula.strip():
                continue
            inputs = re.findall(r"X_\w+", formula)
            is_manual = any(inp.upper().lstrip("X_").upper().rstrip()
                            in MANUAL_SERIES or inp.upper() in
                            {"X_" + m for m in MANUAL_SERIES} for inp in inputs)
            # X_GCON / X_GEQ depend on Gconcur/Geqcur etc -> manual
            is_manual = is_manual or any(
                k in formula.upper() for k in ("GCONCUR", "GCONCAP", "GEQCUR", "GEQCAP"))
            derived.append(Derived(name=sid, formula=formula.strip(),
                                   x12=x12, arima=arima, manual=is_manual))
            continue

        # Fetched series: Series-ID is a CEIC mnemonic.
        rename = _clean_rename(row.get("Rename"))
        if not rename or rename in seen_renames:
            continue
        mnem = sid.upper()
        info = mmap.get(mnem, {})
        manual = mnem in MANUAL_SERIES or (info.get("ceic_id") is None)
        seen_renames.add(rename)
        indicators.append(Indicator(
            mnemonic=mnem,
            ceic_id=info.get("ceic_id"),
            rename=rename,
            name=info.get("name", "") or str(row.get("Unnamed: 0", "")),
            x12=x12, arima=arima, manual=manual,
        ))

    bridges, identities = [], []
    for _, row in nipa_df.iterrows():
        b = parse_bridge(row.get("Estimate Bridge Equation"))
        if b:
            bridges.append(b)
        identities.extend(_parse_identity(row.get("Re-Calculate"),
                                          _clean_rename(row.get("Rename"))))

    return CQMConfig(indicators=indicators, derived=derived, nipa=nipa_df,
                     bridges=bridges, identities=identities)


def _parse_identity(rc, rename) -> list[dict]:
    """Accept only clean algebraic identities 'TARGET = expr' where TARGET is a bare
    identifier. Reject EViews X12 commands (e.g. 'YNS040_U.X12(mode=a) YNS043')."""
    if not isinstance(rc, str) or "=" not in rc:
        return []
    target, expr = rc.split("=", 1)
    target = target.strip()
    if not re.fullmatch(r"\w+", target):   # has '.', '(', spaces -> not an identity
        return []
    if ".x12" in rc.lower():
        return []
    return [{"target": target, "expr": expr.strip(), "rename": rename}]


def nipa_id_map() -> dict[str, str]:
    """rename (YNS010 etc.) -> ceic_id, for series that exist in CEIC quarterly file.
    The NIPA mnemonic is in the metadata 'Series ID' col; numeric id from Q header."""
    nipa_df = pd.read_excel(METADATA_XLSX, sheet_name="NIPA")
    qmap = id_map_quarterly()
    out = {}
    for _, row in nipa_df.iterrows():
        mnem = row.get("Series ID")
        rename = _clean_rename(row.get("Rename"))
        if isinstance(mnem, str) and rename:
            info = qmap.get(mnem.strip().upper())
            if info and info.get("ceic_id"):
                out[rename] = info["ceic_id"]
    return out


if __name__ == "__main__":
    cfg = load_config()
    n_fetch = sum(1 for i in cfg.indicators if i.ceic_id and not i.manual)
    n_manual = sum(1 for i in cfg.indicators if i.manual)
    print(f"Indicators parsed: {len(cfg.indicators)}")
    print(f"  fetchable (CEIC): {n_fetch}")
    print(f"  manual/placeholder: {n_manual} -> "
          f"{[i.rename for i in cfg.indicators if i.manual]}")
    print(f"  with ARIMA spec: {sum(1 for i in cfg.indicators if i.arima)}")
    print(f"  with X12: {sum(1 for i in cfg.indicators if i.x12)}")
    print(f"Derived series: {len(cfg.derived)} -> "
          f"{[(d.name, d.formula, 'MANUAL' if d.manual else '') for d in cfg.derived]}")
    print(f"Bridge equations parsed: {len(cfg.bridges)}")
    print(f"Identities parsed: {len(cfg.identities)}")
    print(f"NIPA fetchable ids: {len(nipa_id_map())}")
    # sanity: TJAM/TJAL must be fetchable now
    byrename = {i.rename: i for i in cfg.indicators}
    for r in ("X_TJAM", "X_TJAL"):
        print(f"  check {r}: ceic_id={byrename.get(r).ceic_id if r in byrename else 'MISSING'}")
    print("\nSample bridge:", cfg.bridges[0])
    print("Sample identities:", cfg.identities[:4])
