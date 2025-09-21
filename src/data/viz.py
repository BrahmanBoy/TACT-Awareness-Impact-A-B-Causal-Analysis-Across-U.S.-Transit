from __future__ import annotations
import pandas as pd
import plotly.express as px
from .ab_tests import wilson_ci

def bar_before_after(df: pd.DataFrame, title: str = ""):
    d = df.copy()
    if {"proportion","n_total","phase"}.issubset(d.columns):
        cis = d.apply(lambda r: wilson_ci(r["proportion"], int(r["n_total"])) if r["n_total"] else (None,None), axis=1)
        d["ci_low"] = [c[0] if c[0] is not None else None for c in cis]
        d["ci_high"] = [c[1] if c[1] is not None else None for c in cis]
    fig = px.bar(d, x="phase", y="proportion",
                 error_y=(d["ci_high"]-d["proportion"]) if "ci_high" in d else None,
                 error_y_minus=(d["proportion"]-d["ci_low"]) if "ci_low" in d else None,
                 title=title)
    return fig
