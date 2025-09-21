import numpy as np
from scripts.tact_analysis import bh_adjust, mde_two_proportions, two_prop_test

def test_bh_is_monotone():
    p = np.array([0.001, 0.02, 0.03, 0.2])
    q = bh_adjust(p)
    assert (q >= 0).all() and (q <= 1).all()
    assert q[p.argmin()] == q.min()

def test_mde_decreases_with_n():
    p1 = 0.5
    mde_small = mde_two_proportions(p1, n1=100, n2=100)
    mde_large = mde_two_proportions(p1, n1=400, n2=400)
    assert mde_large < mde_small

def test_two_prop_ci_defined():
    z, pval, lo, hi, xb, xa = two_prop_test(0.5, 100, 0.5, 100)
    assert np.isfinite([z, pval, lo, hi]).all()
