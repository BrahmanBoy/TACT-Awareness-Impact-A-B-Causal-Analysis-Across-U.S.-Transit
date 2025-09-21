import pandas as pd
from src.stats.psm import cell_level_psm

def test_psm_cell_level():
    df = pd.DataFrame({
        "age":[25,25,40,40],
        "gender":["F","F","M","M"],
        "y":[0.3,0.5,0.4,0.6],
        "after":[0,1,0,1],
        "n_total":[100,100,100,100],
    })
    res = cell_level_psm(df, features=["age","gender"], outcome_col="y", treat_col="after", weight_col="n_total")
    assert "ATT" in res
