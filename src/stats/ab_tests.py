from __future__ import annotations
import numpy as np
from scipy.stats import norm, chi2

def two_proportion_ztest(x1: int, n1: int, x2: int, n2: int, alternative: str = "two-sided"):
    p1 = x1 / n1
    p2 = x2 / n2
    p_pool = (x1 + x2) / (n1 + n2)
    se = np.sqrt(p_pool * (1 - p_pool) * (1 / n1 + 1 / n2))
    z = (p2 - p1) / se
    if alternative == "two-sided":
        p = 2 * (1 - norm.cdf(abs(z)))
    elif alternative == "larger":
        p = 1 - norm.cdf(z)
    else:
        p = norm.cdf(z)
    return {"z": float(z), "pvalue": float(p), "effect": float(p2 - p1), "se": float(se)}

def chi_square_test(counts_before: np.ndarray, counts_after: np.ndarray):
    table = np.vstack([counts_before, counts_after])
    row_sums = table.sum(axis=1, keepdims=True)
    col_sums = table.sum(axis=0, keepdims=True)
    grand = table.sum()
    expected = row_sums @ col_sums / grand
    chi = ((table - expected) ** 2 / expected).sum()
    df = (table.shape[0] - 1) * (table.shape[1] - 1)
    p = 1 - chi2.cdf(chi, df)
    return {"chi2": float(chi), "df": int(df), "pvalue": float(p)}

def wilson_ci(p: float, n: int, alpha: float = 0.05):
    z = norm.ppf(1 - alpha / 2)
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    margin = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return float(center - margin), float(center + margin)
