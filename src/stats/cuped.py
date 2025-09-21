from __future__ import annotations
import numpy as np

def cuped_adjust(y_after, x_before):
    x = np.asarray(x_before, dtype=float)
    y = np.asarray(y_after, dtype=float)
    x_centered = x - x.mean()
    var = np.var(x, ddof=1)
    theta = np.cov(y, x, ddof=1)[0,1] / var if var > 0 else 0.0
    y_adj = y - theta * x_centered
    return y_adj, float(theta)

def cuped_lift(before_prop, after_prop):
    y_adj, theta = cuped_adjust(after_prop, before_prop)
    return {
        "naive_mean_after": float(np.mean(after_prop)),
        "naive_mean_before": float(np.mean(before_prop)),
        "naive_lift": float(np.mean(after_prop) - np.mean(before_prop)),
        "cuped_mean_after": float(np.mean(y_adj)),
        "cuped_theta": theta,
        "cuped_lift": float(np.mean(y_adj) - np.mean(before_prop)),
    }
