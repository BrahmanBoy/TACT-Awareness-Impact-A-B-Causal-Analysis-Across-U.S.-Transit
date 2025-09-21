import argparse, pandas as pd
from pathlib import Path

# Minimal placeholder so pipeline doesn't break if you don't use tidy yet.
# (Streamlit shows ab_summary.csv from outputs; this script is optional.)
ap = argparse.ArgumentParser()
ap.add_argument("--out_csv", type=Path, default=Path("data/processed/tidy_awareness.csv"))
args = ap.parse_args()

args.out_csv.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(columns=["region","phase","question","option","count","n_total","proportion"]).to_csv(args.out_csv, index=False)
print(f"Created empty tidy CSV -> {args.out_csv}")

