from __future__ import annotations
import pandas as pd
from .ab_tests import two_proportion_ztest

def subgroup_lifts(tidy: pd.DataFrame, question_contains: str, option: str, subgroup: str) -> pd.DataFrame:
    df = tidy.copy()
    df = df[df["question"].str.contains(question_contains, case=False, na=False)]
    df = df[df["option"].str.contains(option, case=False, na=False)]
    if subgroup not in df.columns:
        return pd.DataFrame(columns=[subgroup, "effect", "pvalue", "n_before","n_after"])

    agg = (df.groupby([subgroup, "phase"], as_index=False)
             .agg(count=("count","sum"), n_total=("n_total","sum")))

    out = []
    for val, g in agg.groupby(subgroup):
        g = g.set_index("phase")
        if {"before","after"}.issubset(g.index) and g.loc["before","n_total"]>0 and g.loc["after","n_total"]>0:
            r = two_proportion_ztest(
                int(g.loc["before","count"]), int(g.loc["before","n_total"]),
                int(g.loc["after","count"]), int(g.loc["after","n_total"])
            )
            out.append({subgroup: val, "effect": r["effect"], "pvalue": r["pvalue"],
                        "n_before": int(g.loc["before","n_total"]), "n_after": int(g.loc["after","n_total"])})
    return pd.DataFrame(out).sort_values("pvalue")
