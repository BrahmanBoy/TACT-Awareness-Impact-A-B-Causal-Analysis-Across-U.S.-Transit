import argparse, pandas as pd
from src.stats.psm import cell_level_psm
from src.config import TIDY_CSV

ap = argparse.ArgumentParser()
ap.add_argument("--features", type=str, required=True)
ap.add_argument("--question_contains", type=str, required=True)
ap.add_argument("--option", type=str, default="yes")
args = ap.parse_args()

df = pd.read_csv(TIDY_CSV)
f = df[df["question"].str.contains(args.question_contains, case=False, na=False)]
f = f[f["option"].str.contains(args.option, case=False, na=False)]

features = [x.strip() for x in args.features.split(",")]
needed = set(features + ["phase", "proportion", "n_total"])
missing = [c for c in needed if c not in f.columns]
if missing:
    raise SystemExit(f"Missing columns for PSM: {missing}")

psm_df = (f.groupby(features + ["phase"], as_index=False)
            .agg(y=("proportion","mean"), n_total=("n_total","sum")))
psm_df["after"] = (psm_df["phase"]=="after").astype(int)

print(cell_level_psm(psm_df, features=features, outcome_col="y", treat_col="after", weight_col="n_total"))
