from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import pandas as pd
from src.config import TIDY_CSV
from .schemas import ABRequest, DIDRequest, PSMRequest
from src.stats.ab_tests import two_proportion_ztest
from src.stats.did import prepare_did_frame, run_did
from src.stats.psm import cell_level_psm

app = FastAPI(title="TACT Awareness API", version="1.0")

# CORS (loose for demo; tighten for prod)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

def load_tidy() -> pd.DataFrame:
    if not Path(TIDY_CSV).exists():
        raise HTTPException(status_code=400, detail=f"Tidy CSV not found at {TIDY_CSV}")
    return pd.read_csv(TIDY_CSV)

@app.post("/ab")
def ab_endpoint(req: ABRequest):
    df = load_tidy()
    f = df[df["question"].str.contains(req.question_contains, case=False, na=False)]
    f = f[f["option"].str.contains(req.option, case=False, na=False)]
    if req.region:
        f = f[f["region"]==req.region]
    agg = (f.groupby("phase", as_index=False).agg(count=("count","sum"), n_total=("n_total","sum")))
    try:
        b = agg[agg["phase"]=="before"].iloc[0]
        a = agg[agg["phase"]=="after"].iloc[0]
        return two_proportion_ztest(int(b["count"]), int(b["n_total"]), int(a["count"]), int(a["n_total"]))
    except Exception:
        raise HTTPException(status_code=400, detail="Insufficient data for AB test.")

@app.post("/did")
def did_endpoint(req: DIDRequest):
    df = load_tidy()
    long = prepare_did_frame(df, req.question_contains, req.treated_regions, req.control_regions, option=req.option)
    if long.empty:
        raise HTTPException(status_code=400, detail="No data for DiD.")
    return run_did(long)

@app.post("/psm")
def psm_endpoint(req: PSMRequest):
    df = load_tidy()
    f = df[df["question"].str.contains(req.question_contains, case=False, na=False)]
    f = f[f["option"].str.contains(req.option, case=False, na=False)]
    needed = set(req.features + ["phase", "proportion", "n_total"])
    missing = [c for c in needed if c not in f.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns for PSM: {missing}")
    psm_df = (f.groupby(req.features + ["phase"], as_index=False)
                .agg(y=("proportion","mean"), n_total=("n_total","sum")))
    psm_df["after"] = (psm_df["phase"]=="after").astype(int)
    return cell_level_psm(psm_df, features=req.features, outcome_col="y", treat_col="after", weight_col="n_total")
