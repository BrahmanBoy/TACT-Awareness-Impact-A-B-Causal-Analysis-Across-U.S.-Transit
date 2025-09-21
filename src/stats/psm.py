from __future__ import annotations
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors

def cell_level_psm(df: pd.DataFrame, features: list[str], outcome_col: str = "y",
                   treat_col: str = "after", weight_col: str = "n_total",
                   k: int = 1, random_state: int = 42) -> dict:
    work = df.copy().dropna(subset=features + [outcome_col, treat_col, weight_col])
    X = pd.get_dummies(work[features], drop_first=True)
    treat = work[treat_col].astype(int)
    w = work[weight_col].fillna(1).astype(float)
    y = work[outcome_col].astype(float)

    logit = LogisticRegression(max_iter=1000, random_state=random_state)
    logit.fit(X, treat, sample_weight=w)
    ps = logit.predict_proba(X)[:,1]
    work["ps"] = ps

    treated_idx = work[treat_col] == 1
    control_idx = work[treat_col] == 0

    X_t = work.loc[treated_idx, ["ps"]].values
    X_c = work.loc[control_idx, ["ps"]].values
    nbrs = NearestNeighbors(n_neighbors=k).fit(X_c)
    dists, idxs = nbrs.kneighbors(X_t)

    y_t = work.loc[treated_idx, outcome_col].values
    y_c_pool = work.loc[control_idx, outcome_col].values
    w_t = work.loc[treated_idx, weight_col].values

    matched_c = y_c_pool[idxs]
    diffs = y_t - matched_c.mean(axis=1)
    att = np.average(diffs, weights=w_t)
    return {"ATT": float(att), "n_treated": int(treated_idx.sum())}
