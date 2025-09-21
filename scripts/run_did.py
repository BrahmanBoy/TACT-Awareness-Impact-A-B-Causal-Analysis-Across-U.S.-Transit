import argparse, pandas as pd
from src.stats.did import prepare_did_frame, run_did
from src.config import TIDY_CSV

ap = argparse.ArgumentParser()
ap.add_argument("--question_contains", type=str, required=True)
ap.add_argument("--treated_regions", type=str, required=True)
ap.add_argument("--control_regions", type=str, required=True)
ap.add_argument("--option", type=str, default="yes")
args = ap.parse_args()

df = pd.read_csv(TIDY_CSV)
treated = [r.strip() for r in args.treated_regions.split(",")]
control = [r.strip() for r in args.control_regions.split(",")]

long = prepare_did_frame(df, args.question_contains, treated, control, option=args.option)
print(run_did(long))
