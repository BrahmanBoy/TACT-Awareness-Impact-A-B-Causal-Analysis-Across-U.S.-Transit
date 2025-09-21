from __future__ import annotations
from pathlib import Path
import re
import pandas as pd
from typing import List
from ..utils.logging import get_logger
from ..utils.io import read_excel_any
from ..config import RAW_XLSX_CANDIDATES, TIDY_CSV, REGIONS

logger = get_logger(__name__)

PHASES = ["before", "after"]

def _normalize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.replace("\n", " ", regex=False)
        .str.replace(r"\s+", "_", regex=True)
        .str.lower()
    )
    return df

def _guess_region_col(df: pd.DataFrame) -> str | None:
    cands = [c for c in df.columns if "region" in c or c in ("city", "agency", "system")]
    if cands:
        return cands[0]
    if df.columns[0] not in [*PHASES, "before", "after"]:
        return df.columns[0]
    return None

def _wide_to_long_one_sheet(df0: pd.DataFrame, question_name: str) -> pd.DataFrame:
    df0 = _normalize_cols(df0)
    region_col = _guess_region_col(df0)
    if region_col is None:
        raise ValueError("Could not infer region column.")

    n_before = [c for c in df0.columns if re.search(r"\b(n|total).*before\b", c)]
    n_after  = [c for c in df0.columns if re.search(r"\b(n|total).*after\b", c)]
    n_cols = {"before": n_before[0] if n_before else None, "after": n_after[0] if n_after else None}

    option_patterns = {}
    for c in df0.columns:
        for ph in PHASES:
            if c.endswith(f"_{ph}"):
                opt = c.replace(f"_{ph}", "")
                if opt == region_col or opt in ("n", "total"):
                    continue
                option_patterns.setdefault(opt, {})[ph] = c

    long_rows = []
    for _, r in df0.iterrows():
        region = str(r[region_col]).strip()
        for opt, cols in option_patterns.items():
            for ph in PHASES:
                if ph in cols:
                    val = r[cols[ph]]
                    try:
                        v = float(val)
                    except Exception:
                        continue
                    n_tot = r[n_cols[ph]] if n_cols[ph] is not None else None
                    n_tot = int(n_tot) if pd.notna(n_tot) else None
                    proportion = None
                    count = None
                    if n_tot is not None:
                        if 0 <= v <= 1:
                            proportion = v
                            count = round(proportion * n_tot)
                        elif 0 <= v <= 100:
                            proportion = v / 100.0
                            count = round(proportion * n_tot)
                        else:
                            count = int(round(v))
                            proportion = count / n_tot if n_tot > 0 else None
                    else:
                        if 0 <= v <= 1:
                            proportion = v
                        elif 0 <= v <= 100:
                            proportion = v / 100.0
                        else:
                            count = int(round(v))
                    long_rows.append(
                        {
                            "region": region,
                            "phase": ph,
                            "question": question_name,
                            "option": opt,
                            "count": count,
                            "n_total": n_tot,
                            "proportion": proportion,
                        }
                    )
    return pd.DataFrame(long_rows)

def parse_excel_to_tidy(out_csv: Path = TIDY_CSV) -> pd.DataFrame:
    xls = read_excel_any(RAW_XLSX_CANDIDATES)
    frames: List[pd.DataFrame] = []
    for sheet in xls.sheet_names:
        df = xls.parse(sheet_name=sheet)
        try:
            long_df = _wide_to_long_one_sheet(df, question_name=str(sheet))
            frames.append(long_df)
        except Exception as e:
            logger.warning(f"Skip sheet '{sheet}': {e}")
            continue

    tidy = pd.concat(frames, ignore_index=True)
    tidy["phase"] = tidy["phase"].str.lower().map({"before": "before", "after": "after"})
    tidy = tidy.dropna(subset=["phase", "region"])
    tidy = tidy[["region", "phase", "question", "option", "count", "n_total", "proportion"]].copy()
    return tidy
