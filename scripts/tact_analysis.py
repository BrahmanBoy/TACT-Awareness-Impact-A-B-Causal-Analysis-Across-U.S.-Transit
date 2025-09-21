#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TACT Campaign Analysis: End-to-End Workflow (Portfolio Narrative)
Creates: outputs/ab_summary.csv and 3 figures in outputs/figures/
Usage:
    python scripts/tact_analysis.py --excel data/raw/awareness_survey.xlsx --outdir outputs
"""
import argparse, math, os
import numpy as np, pandas as pd, matplotlib.pyplot as plt
from scipy.stats import norm

QUESTION_BINARY_MAP = {
    "Q1 Impacted decision": {
        "section_template": "Has your awareness of crime on public transportation ever impacted your decision to use public transportation in your region? by {label}",
        "yes_items": ["Yes"],
        "note": "Yes = 'Yes, I have altered or reduced trips due to concerns about crime'; No = 'No'",
    },
    "Q2 Importance (Top-2)": {
        "section_template": "How important of a public safety issue is human trafficking on public transportation in your region? by {label}",
        "yes_items": ["Very important", "Important"],
        "note": "Yes = 'Very important' + 'Important'; No = remaining categories",
    },
    "Q3 Think (Top-2 freq)": {
        "section_template": "How often do these awareness campaigns make you think about potential human trafficking while using public transportation in your region? by {label}",
        "yes_items": ["On all of my trips", "On most of my trips"],
        "note": "Yes = 'On all of my trips' + 'On most of my trips'; No = remaining categories",
    },
    "Q4 Share (Top-2 freq)": {
        "section_template": "How often do you share what you learned from these human trafficking awareness campaigns? by {label}",
        "yes_items": ["Every time I see one", "Most of the time I see one"],
        "note": "Yes = 'Every time I see one' + 'Most of the time I see one'; No = remaining categories",
    },
}
REGION_SHEETS = {
    "Albany": "Albany",
    "Alexandria": "Alexandria (DASH)",
    "Austin": "Austin (CapMetro)",
    "Chicago": "Chicago (CTA)",
    "Portland": "Portland (TriMet)",
    "Santa Fe": "Santa Fe (Riometro)",
}

def extract_blocks(df: pd.DataFrame) -> pd.DataFrame:
    blocks = []; i = 0; nrows, _ = df.shape
    while i < nrows:
        row_vals = df.iloc[i].astype(str).fillna("")
        if ("Before Phase" in row_vals.values) and ("After Phase" in row_vals.values):
            title = None
            for k in range(i-3, i):
                if k >= 0:
                    cand = df.iloc[k, 1]
                    if isinstance(cand, str) and cand.strip() and "column" not in (cand or "").lower():
                        title = cand.strip()
            if i+1 < nrows and isinstance(df.iloc[i+1,1], str) and "Column %" in df.iloc[i+1,1]:
                try:
                    c_before = list(df.iloc[i]).index("Before Phase")
                    c_after  = list(df.iloc[i]).index("After Phase")
                except ValueError:
                    i += 1; continue
                j = i + 2; start_len = len(blocks); n_before = np.nan; n_after = np.nan
                while j < nrows:
                    label_cell = df.iloc[j, 1]
                    if isinstance(label_cell, str) and label_cell.strip().lower() == "column n":
                        n_before = df.iloc[j, c_before] if pd.notnull(df.iloc[j, c_before]) else np.nan
                        n_after  = df.iloc[j, c_after]  if pd.notnull(df.iloc[j, c_after])  else np.nan
                        j += 1; break
                    else:
                        item = str(label_cell).strip() if isinstance(label_cell, str) else None
                        p_before = df.iloc[j, c_before]; p_after  = df.iloc[j, c_after]
                        if item and pd.api.types.is_number(p_before) and pd.api.types.is_number(p_after):
                            blocks.append({"section": title,"item": item,
                                           "p_before": float(p_before),"p_after": float(p_after),
                                           "n_before": np.nan,"n_after": np.nan})
                        j += 1
                for idx in range(start_len, len(blocks)):
                    blocks[idx]["n_before"] = float(n_before) if pd.notnull(n_before) else np.nan
                    blocks[idx]["n_after"]  = float(n_after)  if pd.notnull(n_after)  else np.nan
                i = j; continue
        i += 1
    return pd.DataFrame(blocks)

def two_prop_test(p_b: float, n_b: int, p_a: float, n_a: int):
    x_b = round(p_b * n_b); x_a = round(p_a * n_a)
    if n_b <= 0 or n_a <= 0: return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan
    p_pool = (x_b + x_a) / (n_b + n_a)
    se_pooled = (p_pool*(1-p_pool)*(1/n_b + 1/n_a))**0.5
    z = (p_a - p_b) / se_pooled if se_pooled>0 else np.nan
    pval = 2*(1 - norm.cdf(abs(z))) if z==z else np.nan
    se_unpooled = (p_b*(1-p_b)/n_b + p_a*(1-p_a)/n_a)**0.5
    lo = (p_a - p_b) - 1.96*se_unpooled if se_unpooled==se_unpooled else np.nan
    hi = (p_a - p_b) + 1.96*se_unpooled if se_unpooled==se_unpooled else np.nan
    return z, pval, lo, hi, x_b, x_a

def bh_adjust(pvals: np.ndarray) -> np.ndarray:
    pvals = np.array(pvals, dtype=float); m = len(pvals)
    order = np.argsort(pvals); ranks = np.arange(1, m+1)
    q = pvals[order] * m / ranks; q = np.minimum.accumulate(q[::-1])[::-1]
    q_adj = np.empty_like(pvals); q_adj[order] = np.minimum(q, 1.0); return q_adj

def mde_two_proportions(p1: float, n1: int, n2: int, alpha=0.05, power=0.80, tol=1e-6) -> float:
    if n1<=0 or n2<=0: return np.nan
    z_alpha = norm.ppf(1 - alpha/2.0); z_power = norm.ppf(power); lo, hi = 0.0, 0.5
    def req_delta(delta):
        p2 = min(max(p1 + delta, 1e-9), 1-1e-9); pbar = (p1 + p2)/2.0
        SE0 = (pbar*(1-pbar)*(1/n1 + 1/n2))**0.5
        SE1 = (p1*(1-p1)/n1 + p2*(1-p2)/n2)**0.5
        return z_alpha*SE0 + z_power*SE1
    if hi < req_delta(hi) - tol: return hi
    for _ in range(60):
        mid = (lo + hi)/2.0
        if mid >= req_delta(mid): hi = mid
        else: lo = mid
        if hi - lo < tol: break
    return hi

def n_per_group_for_delta(p1: float, delta: float, alpha=0.05, power=0.80) -> int:
    p2 = min(max(p1 + delta, 1e-9), 1-1e-9)
    z_alpha = norm.ppf(1 - alpha/2.0); z_power = norm.ppf(power)
    pbar = (p1 + p2)/2.0
    term = z_alpha*(2*pbar*(1-pbar))**0.5 + z_power*((p1*(1-p1) + p2*(1-p2))**0.5)
    return int(math.ceil((term**2) / (delta**2)))

def analyze_workbook(excel_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    fig_dir = os.path.join(out_dir, "figures"); os.makedirs(fig_dir, exist_ok=True)
    byreg_dir = os.path.join(out_dir, "by_region"); os.makedirs(byreg_dir, exist_ok=True)
    xls = pd.ExcelFile(excel_path)
    all_rows = []
    for label, sheet in REGION_SHEETS.items():
        if sheet not in xls.sheet_names: continue
        df = pd.read_excel(excel_path, sheet_name=sheet, header=None)
        tidy = extract_blocks(df)
        tidy.to_csv(os.path.join(byreg_dir, f"{label}_items_full.csv"), index=False)
        for q_label, spec in QUESTION_BINARY_MAP.items():
            sec_name = spec["section_template"].format(label=label)
            sub = tidy[tidy["section"]==sec_name].copy()
            if sub.empty: continue
            n_b = int(sub["n_before"].dropna().iloc[0]); n_a = int(sub["n_after"].dropna().iloc[0])
            if q_label == "Q1 Impacted decision":
                p_b = float(sub.loc[sub["item"].str.startswith("Yes"), "p_before"].iloc[0])
                p_a = float(sub.loc[sub["item"].str.startswith("Yes"), "p_after"].iloc[0])
            else:
                yes_items = spec["yes_items"]
                p_b = float(sub.loc[sub["item"].isin(yes_items), "p_before"].sum())
                p_a = float(sub.loc[sub["item"].isin(yes_items), "p_after"].sum())
            z, pval, lo, hi, xb, xa = two_prop_test(p_b, n_b, p_a, n_a)
            mde = mde_two_proportions(p_b, n_b, n_a, alpha=0.05, power=0.80)
            n_req_3pp = n_per_group_for_delta(p1=p_b, delta=0.03, alpha=0.05, power=0.80)
            all_rows.append({
                "Region": label, "Question": q_label,
                "n_before": n_b, "n_after": n_a,
                "before_%_yes": round(100*p_b,1), "after_%_yes": round(100*p_a,1),
                "lift_pp": round(100*(p_a - p_b),1),
                "ci_95_pp": f"[{100*lo:.1f}, {100*hi:.1f}]",
                "p_value": pval,
                "MDE_pp_80power": round(100*mde,1) if pd.notnull(mde) else np.nan,
                "n_per_group_needed_for_±3pp": n_req_3pp,
                "current_min_group_n": min(n_b, n_a),
                "binary_rule": spec["note"]
            })
    results = pd.DataFrame(all_rows).sort_values(["Region","Question"]).reset_index(drop=True)
    results["q_value_BH_region"] = np.nan
    for reg in results["Region"].unique():
        idx = results["Region"]==reg
        results.loc[idx, "q_value_BH_region"] = bh_adjust(results.loc[idx, "p_value"].values)
    ab_summary_path = os.path.join(out_dir, "ab_summary.csv"); results.to_csv(ab_summary_path, index=False)

    def parse_ci_pp(ci_str):
        s = ci_str.strip("[]"); lo_str, hi_str = s.split(","); return float(lo_str), float(hi_str)
    plot_df = results.copy()
    plot_df[["ci_lo_pp","ci_hi_pp"]] = plot_df["ci_95_pp"].apply(parse_ci_pp).apply(pd.Series)
    plot_df["y_label"] = plot_df["Region"] + " – " + plot_df["Question"]

    p1 = plot_df.sort_values(["Region","Question"])
    y = np.arange(len(p1)); x = p1["lift_pp"].values
    lo = p1["ci_lo_pp"].values; hi = p1["ci_hi_pp"].values
    err_low = x - lo; err_high = hi - x
    plt.figure(figsize=(10, max(6, 0.35*len(p1))))
    plt.errorbar(x, y, xerr=[err_low, err_high], fmt='o', capsize=3)
    plt.axvline(0, linestyle='--'); plt.yticks(y, p1["y_label"].values)
    plt.xlabel("Lift (percentage points) with 95% CI"); plt.title("TACT: Before→After Lift by Region × Question")
    plt.tight_layout(); fig1 = os.path.join(out_dir, "figures", "lift_ci.png"); plt.savefig(fig1, dpi=200); plt.close()

    p2 = plot_df.copy(); p2["abs_lift"] = p2["lift_pp"].abs(); sizes = 20 + 0.1 * p2["current_min_group_n"]
    plt.figure(figsize=(8,6)); plt.scatter(p2["MDE_pp_80power"], p2["abs_lift"], s=sizes)
    mx = max(p2["MDE_pp_80power"].max(), p2["abs_lift"].max()) + 2
    plt.plot([0, mx], [0, mx], linestyle='--')
    plt.xlabel("MDE (pp) at 80% power"); plt.ylabel("|Observed lift| (pp)")
    plt.title("Is the observed lift big enough to be detectable?"); plt.tight_layout()
    fig2 = os.path.join(out_dir, "figures", "abs_lift_vs_mde.png"); plt.savefig(fig2, dpi=200); plt.close()

    p3 = plot_df.sort_values(["Region","Question"]).copy(); idx = np.arange(len(p3)); width = 0.4
    plt.figure(figsize=(10, max(6, 0.35*len(p3))))
    plt.barh(idx - width/2, p3["current_min_group_n"], height=width, label="Current min n (per group)")
    plt.barh(idx + width/2, p3["n_per_group_needed_for_±3pp"], height=width, label="Needed n (per group) for ±3pp")
    plt.yticks(idx, p3["y_label"].values); plt.xlabel("Sample size per group")
    plt.title("Sample size: current vs needed to detect ±3 pp (80% power)"); plt.legend(); plt.tight_layout()
    fig3 = os.path.join(out_dir, "figures", "sample_size_gap.png"); plt.savefig(fig3, dpi=200); plt.close()

    print("Wrote:", ab_summary_path)
    print("Figures:", fig1, fig2, fig3, sep="\n - ")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--excel", required=True, help="Path to the Excel workbook")
    ap.add_argument("--outdir", default="outputs")
    args = ap.parse_args()
    analyze_workbook(args.excel, args.outdir)

if __name__ == "__main__":
    main()
