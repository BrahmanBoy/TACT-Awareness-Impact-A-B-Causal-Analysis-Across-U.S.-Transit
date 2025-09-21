import argparse, pandas as pd
from src.stats.heterogeneity import subgroup_lifts
from src.config import TIDY_CSV

ap = argparse.ArgumentParser()
ap.add_argument("--question_contains", type=str, required=True)
ap.add_argument("--option", type=str, default="yes")
ap.add_argument("--subgroup", type=str, required=True)
args = ap.parse_args()

df = pd.read_csv(TIDY_CSV)
print(subgroup_lifts(df, args.question_contains, args.option, args.subgroup).to_string(index=False))
