import argparse, pandas as pd
from src.stats.ab_tests import two_proportion_ztest
from src.config import TIDY_CSV

ap = argparse.ArgumentParser()
ap.add_argument("--question_contains", type=str, required=True)
ap.add_argument("--option", type=str, default="yes")
args = ap.parse_args()

df = pd.read_csv(TIDY_CSV)
f = df[df["question"].str.contains(args.question_contains, case=False, na=False)]
f = f[f["option"].str.contains(args.option, case=False, na=False)]

agg = (f.groupby(["phase"], as_index=False).agg(count=("count","sum"), n_total=("n_total","sum")))
before = agg[agg["phase"]=="before"].iloc[0]
after = agg[agg["phase"]=="after"].iloc[0]

res = two_proportion_ztest(int(before["count"]), int(before["n_total"]),
                           int(after["count"]), int(after["n_total"]))
print(res)
