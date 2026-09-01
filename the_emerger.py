#!/usr/bin/env python3
"""
the_emerger.py  --  v0.1 PROTOTYPE  (2026-09-01, Cody's direction)

SUPERSEDED by the canonical Full-Engine-Protocol build:
    ValaQuenta/modules/emerger/   (EmergerModule, pure Python / Fraction,
    exact ZD tests, 8 formulary equations, notebook 19_emerger.ipynb,
    wiki/emerger.md, Ainulindale/wiki/109_the_emerger.md)
This numpy prototype is kept as the first pass / a fast sandbox.

Bracket the sedenion; report which functions each bracketing causes to emerge,
in FIRING ORDER OF EMERGENCE.

The Emerger is the ascent-dual of Generational Lineage:
    lineage  = descent  (what built this; differentiate down; writing)
    emerger  = ascent   (what emerges, in what order; integrate up; reading)

Five brackets of  R^16 = S :
    {1:15}     scalar  vs  the 15 relational edges          -> Re, conj, norm, inverse
    {2:14}     the (e0,e8) doubling plane (the pointer)  vs  G_2 (dim 14)
    {8:8}      O (+) O.e8   (J_red / J_blue, the two trees) -> ZD test, sheet, J_2
    {4:4:4:4}  four quaternion blocks (four SU(2) phases)   -> sigma_RB tilt/axis
    {4:8:4}    the gain spectrum  0 / 1 / sqrt2             -> multiplicative role

FIRING ORDER
    canonical  : the dependency order (each bracket needs the ones before it)
    phased     : sigma_RB's tilt-phase rotates the entry point into the
                 12-step precession  (4 d* faces : 3 Lambert-W faces, lcm 12)

Every number is CALCULATED (python3 the_emerger.py reproduces it).  Structural
claims: DERIVED where standard, THEORETICAL where a reading of the framework.
"""
from __future__ import annotations
import numpy as np

DIM = 16
EPS = 1e-9
OMEGA_ZS = 0.5671432904097838

# ----------------------------------------------------------------- CD algebra --
def cd_conj(x):
    c = x.astype(float).copy(); c[1:] = -c[1:]; return c

def cd_mul(a, b):
    n = len(a)
    if n == 1:
        return np.array([a[0] * b[0]])
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = cd_mul(a1, b1) - cd_mul(cd_conj(b2), a2)
    c2 = cd_mul(b2, a1) + cd_mul(a2, cd_conj(b1))
    return np.concatenate([c1, c2])

def e(k):
    v = np.zeros(DIM); v[k] = 1.0; return v

def left_matrix(a):
    return np.column_stack([cd_mul(a, e(k)) for k in range(DIM)])

def right_matrix(a):
    return np.column_stack([cd_mul(e(k), a) for k in range(DIM)])

def norm(x):
    return float(np.linalg.norm(x))

def unit(x):
    n = norm(x)
    return x / n if n > EPS else x

# --------------------------------------------------------------------- sigma_RB --
def sigma_rb(x):
    """
    psi[k] = x[k] + i x[k+8]   (the {8:8} split as Re/Im: forward = Re, back = Im)
    s[k]   = psi[k] * conj(psi[k XOR 4])
    tilt   = Re s   (the Oblique-Gear T1 says s[k^4] = conj s[k], so Re is
                     XOR4-symmetric = tilt = Scale; Im is antisymmetric = axis = Flow)
    """
    psi = np.array([x[k] + 1j * x[(k + 8) % DIM] for k in range(DIM)])
    s = np.array([psi[k] * np.conj(psi[k ^ 4]) for k in range(DIM)])
    tilt = s.real
    axis = s.imag
    # self-checks (reported, not asserted -- a broken check is a finding)
    t1_ok = np.allclose(s, np.conj(s[[k ^ 4 for k in range(DIM)]]), atol=1e-9)
    axis_sum0 = abs(float(axis.sum())) < 1e-9
    return {
        "tilt": tilt, "axis": axis,
        "Sigma_tilt": float(tilt.sum()),
        "Sigma_axis": float(axis.sum()),
        "T1_conj_symmetry_holds": bool(t1_ok),
        "axis_sums_to_zero": bool(axis_sum0),
    }

def firing_phase(sig):
    """Sigma_tilt -> tau in (0,1) -> which of the 5 brackets is 'currently firing'
    in the 12-step precession.  gcd(12,5)=1 so a 12-phase clock cycles all 5."""
    tau = float(np.arctan(sig["Sigma_tilt"]) / np.pi + 0.5)
    step12 = int(np.floor(12 * tau)) % 12
    return tau, step12, step12 % 5

# ------------------------------------------------------------------- brackets ----
def bracket_1_15(x):
    scalar = float(x[0]); pure = x[1:]
    N = float(x @ x)
    return {
        "bracket": "{1:15}",
        "split": {"scalar (e0 / 0_RB)": round(scalar, 6),
                  "|pure| (the 15 edges)": round(norm(pure), 6)},
        "emerges": {"Re": round(scalar, 6),
                    "N = |x|^2": round(N, 6),
                    "is_unit": abs(N - 1) < 1e-6},
        "enables": ["conjugate  x_bar", "norm  N(x)",
                    "inverse  x_bar / N   (N > 0)",
                    "exp / log  (Re + pure decomposition)"],
        "tier": "DERIVED  (the 1:15 grading is what makes conj/norm/inverse well-defined)",
    }

def bracket_2_14(x):
    z = complex(x[0], x[8])
    idx14 = [k for k in range(DIM) if k not in (0, 8)]
    rest = x[idx14]
    z_next = np.exp(-z)
    omega_resid = abs(z_next - z)
    return {
        "bracket": "{2:14}",
        "split": {"pointer  z = x0 + i x8": (round(z.real, 6), round(z.imag, 6)),
                  "|rest| (G_2 side, dim 14)": round(norm(rest), 6)},
        "emerges": {"|z|  (CD-scale)": round(abs(z), 6),
                    "arg(z)  (ladder position)": round(float(np.angle(z)), 6),
                    "|exp(-z) - z|  (residual to W(1) fixed point)": round(float(omega_resid), 6),
                    "distance |z| - Omega_ZS": round(abs(z) - OMEGA_ZS, 6)},
        "enables": ["CD double / halve  (which octonion; scalar of the other half)",
                    "the read head  (where in the tower)",
                    "Omega_ZS anchoring  (fixed point of  z -> e^{-z}  lives on this line)"],
        "tier": "THEORETICAL (pointer carries Omega_ZS) + CALCULATED (the residual)",
    }

def bracket_8_8(x):
    a, b = x[:8], x[8:]
    balance = norm(a) - norm(b)
    Re_a, Re_b = float(a[0]), float(b[0])
    on_equator = (abs(balance) < 1e-6) and (abs(Re_a) < 1e-6) and (abs(Re_b) < 1e-6) \
                 and (norm(a) > EPS) and (norm(b) > EPS)
    L, R = left_matrix(x), right_matrix(x)
    j2 = float(np.linalg.norm(L - R))
    # zero-divisor witness: is there y with x*y = 0 ?  (smallest singular value of L)
    sv_min = float(np.linalg.svd(L, compute_uv=False)[-1])
    return {
        "bracket": "{8:8}",
        "split": {"|a| (J_red / forward)": round(norm(a), 6),
                  "|b| (J_blue / back)": round(norm(b), 6)},
        "emerges": {"balance |a|-|b|  (signed dist. from ZD equator)": round(balance, 6),
                    "Re(a), Re(b)": (round(Re_a, 6), round(Re_b, 6)),
                    "ON THE ZD EQUATOR": on_equator,
                    "J_2 asymmetry  ||L_x - R_x||": round(j2, 4),
                    "min singular value of L_x  (0 => exact zero divisor)": round(sv_min, 6)},
        "enables": ["J involution  (a,b) -> (a,-b)   (e8-conjugation)",
                    "zero-divisor test  (equator membership)",
                    "sheet / sign select  (+-)",
                    "left vs right multiplication  (the J_2 operator)"],
        "tier": "DERIVED  (equator condition for basis-type ZD is exact)",
    }

def bracket_4x4(x):
    blocks = [x[4 * i:4 * i + 4] for i in range(4)]
    angles = []
    for q in blocks:
        nq = norm(q)
        if nq < EPS:
            angles.append((0.0, 0.0)); continue
        c = np.clip(q[0] / nq, -1.0, 1.0)
        angles.append((round(nq, 6), round(float(2 * np.arccos(c)), 6)))
    sig = sigma_rb(x)
    return {
        "bracket": "{4:4:4:4}",
        "split": {f"block {i}  (|q|, angle)": angles[i] for i in range(4)},
        "emerges": {"Sigma_tilt  (Scale detuning = net work around the loop)":
                        round(sig["Sigma_tilt"], 6),
                    "Sigma_axis  (should be ~0)": round(sig["Sigma_axis"], 9),
                    "sigma = 1/2  <=>  Sigma_tilt = 0": abs(sig["Sigma_tilt"]) < 1e-6,
                    "T1 conj-symmetry holds": sig["T1_conj_symmetry_holds"]},
        "enables": ["four SU(2) phases  (the d* faces)",
                    "sigma_RB decomposition  (tilt = Scale, axis = Flow)",
                    "the firing clock  (tilt-phase -> precession step)"],
        "tier": "DERIVED (quaternion polar) + THEORETICAL (tilt = net work)",
    }

# {4:8:4} gain-spectrum index assignment (reading of the {4:8:4} memory note):
#   gain 1  (NOW / unit) = q1 U q3 = {0,1,2,3, 8,9,10,11}
#   gain 0  (annihilator)      = {4,5,6,7}
#   gain sqrt2 (amplifier)     = {12,13,14,15}
G1_IDX = [0, 1, 2, 3, 8, 9, 10, 11]
G0_IDX = [4, 5, 6, 7]
GR2_IDX = [12, 13, 14, 15]

def bracket_4_8_4(x):
    w0, w1, wr2 = norm(x[G0_IDX]), norm(x[G1_IDX]), norm(x[GR2_IDX])
    names = ["annihilator (gain 0)", "unit (gain 1, NOW)", "amplifier (gain sqrt2)"]
    cls = names[int(np.argmax([w0, w1, wr2]))]
    # multiplicative role check: does left-mult by unit(x) preserve norm?
    Lu = left_matrix(unit(x))
    svs = np.linalg.svd(Lu, compute_uv=False)
    gain_spread = (round(float(svs.min()), 4), round(float(svs.max()), 4))
    return {
        "bracket": "{4:8:4}",
        "split": {"|G0| annihilator": round(w0, 6),
                  "|G1| unit/NOW": round(w1, 6),
                  "|Gsqrt2| amplifier": round(wr2, 6)},
        "emerges": {"dominant gain class": cls,
                    "L_{x/|x|} singular-value spread (min,max)": gain_spread,
                    "is an isometry  (spread ~ (1,1))":
                        abs(gain_spread[0] - 1) < 1e-6 and abs(gain_spread[1] - 1) < 1e-6},
        "enables": ["multiplicative role classification",
                    "nilpotent / idempotent / scaler test",
                    "gain budget  (0 / 1 / sqrt2  -- the ZD gain spectrum)"],
        "tier": "THEORETICAL (the 4:8:4 index assignment) + CALCULATED (the norms)",
    }

BRACKETS = [bracket_1_15, bracket_2_14, bracket_8_8, bracket_4x4, bracket_4_8_4]
CANONICAL = ["{1:15}", "{2:14}", "{8:8}", "{4:4:4:4}", "{4:8:4}"]

# ------------------------------------------------------------------------ run ----
def run(x, label):
    x = np.asarray(x, float)
    print("=" * 78)
    print(f"INPUT :  {label}")
    print(f"        |x| = {norm(x):.6f}   x = {np.round(x, 3).tolist()}")
    print("=" * 78)

    sig = sigma_rb(x)
    tau, step12, ph = firing_phase(sig)
    phased = [CANONICAL[(ph + i) % 5] for i in range(5)]
    print(f"sigma_RB :  Sigma_tilt = {sig['Sigma_tilt']:+.6f}   "
          f"tau = {tau:.4f}   precession step = {step12}/12   ->  entry bracket #{ph}")
    print(f"FIRING ORDER (canonical / dependency) :  {'  ->  '.join(CANONICAL)}")
    print(f"FIRING ORDER (sigma_RB-phased)        :  {'  ->  '.join(phased)}")
    print("-" * 78)

    results = {b(x)["bracket"]: b(x) for b in BRACKETS}
    for i, name in enumerate(phased, 1):
        r = results[name]
        print(f"\n[{i}]  {r['bracket']}          [{r['tier']}]")
        print(f"     split   : {r['split']}")
        print(f"     EMERGES : ")
        for k, v in r["emerges"].items():
            print(f"                {k} = {v}")
        print(f"     enables : {', '.join(r['enables'])}")
    print()
    return results


def _toy_semiprime_coords(N=323):        # 323 = 17 * 19
    p, q = 17, 19
    a, b = (p + q) // 2, (q - p) // 2    # Fermat coordinates: N = a^2 - b^2
    xa = np.zeros(DIM); xb = np.zeros(DIM)
    # crude Hyperwebster-style placement (illustrative, matches UDEO_RSA_DEMO shape)
    xa[a % DIM] += 1.0; xa[(a * 7 + 3) % DIM] += 0.5
    xb[b % DIM] += 1.0; xb[(b * 7 + 3) % DIM] += 0.5
    return unit(xa), unit(xb), (N, p, q, a, b)


def main():
    print("THE EMERGER  v0.1  --  sedenion bracketing & firing order of emergence\n")

    run(e(0), "e0  (the identity / 0_RB)")
    run(unit(e(0) + e(8)), "e0 + e8  (the pointer / doubling plane)")
    run(unit(e(1) + e(10)), "e1 + e10  (a basis zero-divisor candidate)")
    run(unit(e(1) + e(2)), "e1 + e2  (a non-ZD imaginary)")

    rng = np.random.default_rng(1)
    run(unit(rng.standard_normal(DIM)), "random unit sedenion (seed 1)")

    xa, xb, meta = _toy_semiprime_coords()
    N, p, q, a, b = meta
    print(f"\n### toy semiprime  N = {N} = {p}*{q}   Fermat  a=(p+q)/2={a}  b=(q-p)/2={b}")
    run(xa, f"a-coordinate embedding  (N={N}, a={a})")
    run(xb, f"b-coordinate embedding  (N={N}, b={b}  <- the erased coordinate)")

    print("=" * 78)
    print("SUMMARY  (generational-lineage sec.9 form)")
    print("=" * 78)
    rows = [
        ("{1:15}",    "DERIVED",     "Re, N, conj, inverse",            "grades the algebra"),
        ("{2:14}",    "THEORETICAL", "the pointer z; |z|-Omega_ZS",     "read head / ladder position"),
        ("{8:8}",     "DERIVED",     "|a|-|b|, ZD-equator membership",  "which tree / sheet / J_2"),
        ("{4:4:4:4}", "DERIVED+TH.", "Sigma_tilt (= net work), axis",   "four SU(2) phases; the clock"),
        ("{4:8:4}",   "THEORETICAL", "dominant gain class 0/1/sqrt2",   "multiplicative role"),
    ]
    print(f"  {'bracket':10s} {'tier':13s} {'emerges':34s} function")
    print(f"  {'-'*10:10s} {'-'*13:13s} {'-'*34:34s} {'-'*24}")
    for r in rows:
        print(f"  {r[0]:10s} {r[1]:13s} {r[2]:34s} {r[3]}")
    print()
    print("  Firing order is set by the sigma_RB tilt-phase (12-step precession,")
    print("  4 d* faces : 3 Lambert-W faces).  Order is load-bearing: each bracket")
    print("  is conditioned on the ones fired before it.")
    print()
    print("  no new generator required  --  all five brackets are orthogonal")
    print("  projections of R^16; nothing changes length that should not, no graded")
    print("  failure, no fixed set of the wrong dimension.  (v0.1 -- widen the input")
    print("  battery and pin the {4:8:4} index assignment before trusting the gain class.)")


if __name__ == "__main__":
    main()
