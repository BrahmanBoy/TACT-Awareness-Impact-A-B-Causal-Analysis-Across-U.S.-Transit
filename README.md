# 🚇 Measuring Impact of the TACT Campaign on Public Transit Riders’ Awareness

[![Build](https://img.shields.io/github/actions/workflow/status/USER/REPO/ci.yml?label=CI)]()
![Python](https://img.shields.io/badge/Python-3.11-blue)
[![Streamlit](https://img.shields.io/badge/App-Streamlit-brightgreen)]()
[![FastAPI](https://img.shields.io/badge/API-FastAPI-teal)]()

**Business takeaway (placeholder): Across six transit regions, **before→after awareness lifts were small (≈ −10pp…+10pp)** and **not statistically reliable after FDR correction.** Most observed changes were **below the study’s detectable threshold (MDE)**, meaning the data are **underpowered** to confirm modest effects.
**Recommendation:** increase per-wave sample sizes **2–4×** and/or run a **stronger design** (e.g., DiD with controls, PSM).

---
## 1) Problem Statement
Did the TACT campaign measurably increase riders’ awareness and related behaviors about child trafficking on public transit?
## 2) Hypotheses
- **H₀(no effect):** The Yes rate is the same Before and After the campaign.
- **H₁(effect):** The Yes rate differs between Before and After (two-sided test).

## 3) Questions & Yes/No Mapping
- **Q1 Has your awareness of crime on public transportation ever impacted your decision to use public transportation in your region?:** Yes = “Yes, I altered or reduced trips”; No = “No”.
- **Q2 How important of a public safety issue is human trafficking on public transportation in your region?(Top-2):** Yes = “Very important” + “Important”.
- **Q3 How often do these awareness campaigns make you think about potential human trafficking while using public transportation in your region?(Top-2 freq):** Yes = “On all” + “On most”.
- **Q4 How often do you share what you learned from these human trafficking awareness campaigns? (Top-2 freq):** Yes = “Every time” + “Most of the time”.

## 4) Methods
- **A/B testing:** Two-proportion z-tests per (Region × Question), 95% CI, p-values.
- **Multiple testing:** Benjamini–Hochberg **FDR** per region.
- **Power:** **MDE** (80% power, α=0.05) and **n per group** for ±3pp.
- **Causal framing:** Before/After limits → plan for **DiD** / **PSM**.

## Repo Tour
