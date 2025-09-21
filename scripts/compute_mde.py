import argparse, pandas as pd
from pathlib import Path
from math import sqrt
from scipy.stats import norm
from src.config import TIDY_CSV

def mde_two_proportions(p0: float, n1: int, n2: int, alpha: float = 0.05, power: float = 0.8) -> float:
    z_alpha = norm.ppf(1 - alpha / 2)
    z_beta = norm.ppf(power)
    se = sqrt(p0 * (1 - p0) * (1 / n1 + 1 / n2))
    return float((z_alpha + z_beta) * se)

ap = argparse.ArgumentParser()
ap.add_argument("--question_contains", type=str, required=True)
ap.add_argument("--option", type=str, default="yes")
ap.add_argument("--alpha", type=float, default=0.05)
ap.add_argument("--power", type=float, default=0.8)
ap.add_argument("--in_csv", type=Path, default=TIDY_CSV)
args = ap.parse_args()

df = pd.read_csv(args.in_csv)
f = df[df["question"].str.contains(args.question_contains, case=False, na=False)]
f = f[f["option"].str.contains(args.option, case=False, na=False)]
agg = (f.groupby(["region","phase"], as_index=False).agg(count=("count","sum"), n_total=("n_total","sum")))
rows = []
for region, g in agg.groupby("region"):
    g = g.set_index("phase")
    if {"before","after"}.issubset(g.index):
        p0 = g.loc["before","count"] / g.loc["before","n_total"]
        n1 = int(g.loc["before","n_total"]); n2 = int(g.loc["after","n_total"])
        rows.append({"region": region, "baseline_p": float(p0),
                     "n_before": n1, "n_after": n2,
                     "MDE_at_power": mde_two_proportions(p0, n1, n2, args.alpha, args.power)})
print(pd.DataFrame(rows).sort_values("MDE_at_power").to_string(index=False))

