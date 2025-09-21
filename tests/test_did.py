import pandas as pd
from src.stats.did import run_did

def test_did_runs():
    df = pd.DataFrame({
        "region": ["A","A","B","B"],
        "after": [0,1,0,1],
        "treated": [1,1,0,0],
        "y": [0.3,0.5,0.4,0.45],
        "n_total": [100,100,100,100],
        "count": [30,50,40,45],
    })
    res = run_did(df)
    assert "did_coef" in res
