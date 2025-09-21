# 🚇 Measuring Impact of the TACT Campaign on Public Transit Riders’ Awareness

[![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml?label=CI)]()
![Python](https://img.shields.io/badge/Python-3.11-blue)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-brightgreen)]()
[![FastAPI](https://img.shields.io/badge/API-FastAPI-teal)]()

**Business takeaway (placeholder):** Across six regions, most before→after changes were **not statistically significant** after FDR correction. Observed lifts (~−10pp…+10pp) were **smaller than detectability** (MDE), so the study is **underpowered** to confirm modest effects. Recommendation: scale sample sizes 2–4× and consider **Difference-in-Differences**.

---

## 1) Problem Statement
Did the TACT campaign measurably increase transit riders’ awareness/behavior regarding trafficking?

## 2) Hypotheses
- **H₀:** No change in “Yes” proportions between Before and After.
- **H₁:** There is a change (two-sided).

## 3) Questions & Yes/No Mapping
- **Q1 Impacted decision:** Yes = “Yes, I altered or reduced trips”; No = “No”.
- **Q2 Importance (Top-2):** Yes = “Very important” + “Important”.
- **Q3 Think (Top-2 freq):** Yes = “On all” + “On most”.
- **Q4 Share (Top-2 freq):** Yes = “Every time” + “Most of the time”.

## 4) Methods
- **A/B testing:** Two-proportion z-tests per (Region × Question), 95% CI, p-values.
- **Multiple testing:** Benjamini–Hochberg **FDR** per region.
- **Power:** **MDE** (80% power, α=0.05) and **n per group** for ±3pp.
- **Causal framing:** Before/After limits → plan for **DiD** / **PSM**.

## Repo Tour
