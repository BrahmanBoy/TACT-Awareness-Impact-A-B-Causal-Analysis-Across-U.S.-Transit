import streamlit as st
import pandas as pd
from pathlib import Path
import os, sys

# make sure project root is importable if you later add src/* imports
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

st.set_page_config(page_title="TACT Awareness – Results", layout="wide")
st.title("TACT Awareness – A/B Results")

csv = Path("outputs/ab_summary.csv")
if csv.exists():
    df = pd.read_csv(csv)
    st.write("### Summary table")
    st.dataframe(df, use_container_width=True)

    st.write("### Figures")
    for p in [
        "outputs/figures/lift_ci.png",
        "outputs/figures/abs_lift_vs_mde.png",
        "outputs/figures/sample_size_gap.png",
    ]:
        if Path(p).exists():
            st.image(p, caption=p)
else:
    st.warning("Run: python scripts/tact_analysis.py --excel data/raw/awareness_survey.xlsx --outdir outputs")
