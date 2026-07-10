"""
ainulindale_engine.modules.udeo_crypto.UDEO_RSA_DEMO
======================================================
UDEO RSA private-key-recovery engine — three candidate mechanisms (Cody's),
each implemented literally and tested against known toy RSA keys, with a
random-guess control run alongside every result.

THIS ENGINE DOES NOT ASSUME ANY OF THE THREE METHODS WORK.
Every function below is given ONLY the public key (n, e) at the point it
computes its "recovered" candidate for d. The true d is used only
afterward, to score the candidate against ground truth and against a
population of random-but-plausible wrong guesses. That control was the
missing piece in every earlier round of this work (see VAPMIP context:
the RSA cross-check control never validated across 5 prior Translator
test rounds) — it is built into every engine here, not bolted on after.

The paper's own honest-scope boundary (rsa_framework.md, Section 4.3-4.4,
Honest Scope) is the standard these engines are held to: no working
attack against a live RSA system is claimed by this file. What is
claimed is exactly what the numbers below show, no more.

Engines:
    method1_zero_divisor_shadow()   Cody's method 1: cancel e out of the
                                     equation via the kernel of left-mult
                                     by e_s in S^16; test whether d_s
                                     aligns with that kernel's geometry.
    method2_j2_involution_t256()    Cody's method 2: H_hat_RB vs H_hat_BR
                                     (left- vs right-multiplication by e_s
                                     in T_256) — the J2 asymmetry operator
                                     and its eigenspectrum ("Laplacian
                                     components"); test whether d_s aligns
                                     with a dominant eigenvector.
    method3_spectral_relativity()   Cody's method 3: treat the Hyperwebster
                                     sigma-address as an HSR coordinate,
                                     define the sigma-face metric g(sigma),
                                     and test whether the geodesic distance
                                     from e's address to d's address is a
                                     statistical outlier vs random d'.
    method4_content_public_private_hash()  Cody's method 4 (this session):
                                     Content+Public+Private=Hash. Exact
                                     vector-algebra identity IF Hash is
                                     exposed (requires d to compute) --
                                     not a public-key-only attack.
    method5_zero_lattice_paths()    Cody's method 5: trace Content/Public/
                                     Private/Hash through the 9-level CD
                                     tower (AbrikosovTree/telperion_engine.py
                                     geometry). Surfaced the proven mod4
                                     identity below; public-key-only
                                     scenario is at chance.
    mod4_identity_theorem()         d = e (mod 4) always, for any RSA key
                                     with odd primes. Proven classical
                                     number theory, unrelated to sedenions.
                                     The one ESTABLISHED-tier result here.
    rsa_control_baseline()          Positive-control sanity check: given
                                     the FULL known key (p,q,e,d), does the
                                     already-published degeneracy mechanism
                                     (private_key_degeneration_demo, from
                                     udeo_poc.py) show anything at toy
                                     scale? Reference point, not an attack.
    compare_all_methods()           Runs all five attack engines across
                                     every toy key, tabulates true-d rank
                                     vs the random-control population, and
                                     assigns an honest confidence tier per
                                     method based on the actual numbers.

Author:  Claude, at Cody's direction — 2026-07-09
Version: 0.100 — first pass, all three methods, all honestly scored
"""

import math
import random
from typing import Dict, List, Any, Tuple

import numpy as np

# ── Ainulindale constants (shared across the framework) ────────────────────
OMEGA_ZS = 0.5671432904097838
D_STAR   = 0.24600
R_H      = 1.0 / math.sqrt(2.0)

PRIMES = [2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,
          73,79,83,89,97,101,103,107,109,113]


# ══════════════════════════════════════════════════════════════════════════
# SHARED MACHINERY — Cayley-Dickson algebra, hash addresses, toy RSA
# ══════════════════════════════════════════════════════════════════════════

def cd_conj(x: np.ndarray) -> np.ndarray:
    """Cayley-Dickson conjugate: negate all but the scalar component."""
    c = x.copy()
    c[1:] = -c[1:]
    return c

def cd_mul(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Recursive Cayley-Dickson product. Works for any power-of-2 length."""
    n = len(a)
    if n == 1:
        return np.array([a[0] * b[0]])
    h = n // 2
    a1, a2, b1, b2 = a[:h], a[h:], b[:h], b[h:]
    c1 = cd_mul(a1, b1) - cd_mul(cd_conj(b2), a2)
    c2 = cd_mul(b2, a1) + cd_mul(a2, cd_conj(b1))
    return np.concatenate([c1, c2])

def e_k(k: int, dim: int) -> np.ndarray:
    v = np.zeros(dim)
    v[k] = 1.0
    return v

def _cd_conj_batch(X: np.ndarray) -> np.ndarray:
    """Conjugate a batch of CD vectors. X: (n, k) — n components, k vectors
    stacked as columns."""
    c = X.copy()
    c[1:, :] = -c[1:, :]
    return c

def _cd_mul_batch(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """
    Batched Cayley-Dickson product. A, B: (n, kA) and (n, kB) with kA==kB
    or one of them ==1 (broadcasts, e.g. a single fixed vector against a
    whole basis). Returns (n, max(kA,kB)).

    Same recursive formula as cd_mul(), but every array slot carries a
    batch dimension instead of a single vector, so one call to this
    function builds an entire dim x dim operator matrix in one recursive
    tree walk (O(dim^2) Python-level calls) instead of dim separate calls
    to the scalar cd_mul (O(dim^3) calls) — the difference between
    seconds and tens of minutes at dim=256.
    """
    n = A.shape[0]
    if n == 1:
        return A[0:1, :] * B[0:1, :]
    h = n // 2
    A1, A2 = A[:h, :], A[h:, :]
    B1, B2 = B[:h, :], B[h:, :]
    C1 = _cd_mul_batch(A1, B1) - _cd_mul_batch(_cd_conj_batch(B2), A2)
    C2 = _cd_mul_batch(B2, A1) + _cd_mul_batch(A2, _cd_conj_batch(B1))
    return np.concatenate([C1, C2], axis=0)

def left_mult_matrix(a: np.ndarray, dim: int) -> np.ndarray:
    """Matrix L_a such that L_a @ x == cd_mul(a, x). cd_mul is bilinear
    in its second argument, so this is a well-defined linear operator."""
    A = a.reshape(dim, 1)
    I = np.eye(dim)
    return _cd_mul_batch(A, I)

def right_mult_matrix(a: np.ndarray, dim: int) -> np.ndarray:
    """Matrix R_a such that R_a @ x == cd_mul(x, a)."""
    A = a.reshape(dim, 1)
    I = np.eye(dim)
    return _cd_mul_batch(I, A)

def normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v)
    return v / n if n > 1e-15 else v

def map_int_to_hypercomplex_placeholder(x: int, dim: int) -> np.ndarray:
    """
    Simplified Hyperwebster mapping, generalised from udeo_poc.py's
    map_prime_to_sedenion() to arbitrary CD dimension.

    KNOWN LIMITATION (stated explicitly in rsa_framework.md's Honest Scope
    section, inherited here unchanged): this places weight at (x mod dim)
    plus a secondary residue term. It is illustrative, not the full Horner
    bijection over Riemann zero indices. Kept only for comparison against
    map_int_to_hypercomplex() below, which uses the real P1 mechanism.
    """
    coords = [0.0] * dim
    coords[x % dim] += 1.0
    coords[(x * 7 + 3) % dim] += 0.5
    coords = np.array(coords)
    return normalize(coords)

def map_int_to_hypercomplex(x: int, dim: int) -> np.ndarray:
    """
    Sedenion/T_dim embedding via the REAL P1 mechanism (see p1_zero_index
    above), replacing the placeholder's raw (x mod dim). Primary weight at
    the P1 zero-index residue, secondary weight at the raw Horner-hash
    residue — still a 2-term composite element (matching the shape of the
    (e_i+e_j) pairs udeo_poc.py's own zero-divisor search uses), but now
    both terms are derived from the validated prime/Riemann-zero hash
    instead of arithmetic on x directly.
    """
    zidx = p1_zero_index(str(x))
    hraw = p1_horner_hash(str(x))
    coords = [0.0] * dim
    coords[zidx % dim] += 1.0
    coords[hraw % dim] += 0.5
    coords = np.array(coords)
    return normalize(coords)

def horner_prime_hash(s: str, modulus: int = 10**9 + 7) -> int:
    """Same Horner-scheme prime hash used in tier8_sedenion — applied here
    to the decimal string of an integer, per 'primes are words' / integers
    are words too. PLACEHOLDER — see the P1 hash below for the real,
    already-validated mechanism (monad.py); kept only for comparison."""
    h = 0
    for i, c in enumerate(s.lower()):
        h = (h + ord(c) * PRIMES[i % len(PRIMES)]) % modulus
    return h

def hash_to_sigma_placeholder(h: int, modulus: int = 10**9 + 7) -> float:
    return h / modulus


# ── P1 prime hash (real mechanism, copied from VAPMIP/monad.py) ────────────
# word -> Horner base-95 int -> next prime p in [2, 65536] -> pi(p) = zero
# index in [1, 6542]. This is the mechanism behind the one validated result
# in this framework (tier8_sedenion.sedenion_self_organisation: the 16
# operator names self-organise to d*/sigma_half/D*=1 through exactly this
# hash). Applied here to str(x) for an RSA integer x, same as monad.py
# applies it to any word string — 'integers are words too'.

_P1_PRIME_CAP = 1 << 16   # 65536
_p1_cap = _P1_PRIME_CAP + 2
_p1_sieve = bytearray([1]) * _p1_cap
_p1_sieve[0] = _p1_sieve[1] = 0
for _i in range(2, int(_p1_cap ** 0.5) + 1):
    if _p1_sieve[_i]:
        _p1_sieve[_i * _i :: _i] = bytearray(len(_p1_sieve[_i * _i :: _i]))
_p1_prime_pi_table: List[int] = [0] * _p1_cap
_cnt = 0
for _k in range(_p1_cap):
    if _p1_sieve[_k]:
        _cnt += 1
    _p1_prime_pi_table[_k] = _cnt
del _i, _k, _cnt

def p1_next_prime(v: int) -> int:
    v = max(2, int(v) % (_P1_PRIME_CAP + 1))
    while v <= _P1_PRIME_CAP + 1:
        if _p1_sieve[min(v, _P1_PRIME_CAP + 1)] or v > _P1_PRIME_CAP:
            return v
        v += 1
    return 65537

def p1_horner_hash(w: str, base: int = 95, offset: int = 32) -> int:
    v = 0
    for ch in w:
        v = v * base + max(0, ord(ch) - offset)
    return abs(v)

def p1_zero_index(w: str) -> int:
    """P1: word -> Horner int -> next prime p -> pi(p) = zero index in [1, 6542]."""
    v = p1_horner_hash(w)
    p = p1_next_prime(v)
    idx = _p1_prime_pi_table[min(p, _P1_PRIME_CAP + 1)]
    return max(1, idx)

_P1_MAX_ZERO_IDX = 6542

def sigma_of_int(x: int) -> float:
    """sigma address via the REAL P1 mechanism, mapped to (0, 1]."""
    return p1_zero_index(str(x)) / _P1_MAX_ZERO_IDX


# ── Toy RSA ──────────────────────────────────────────────────────────────

def rsa_keygen(p: int, q: int, e: int) -> Dict[str, int]:
    n = p * q
    phi_n = (p - 1) * (q - 1)
    assert math.gcd(e, phi_n) == 1, "e must be coprime to phi(n)"
    d = pow(e, -1, phi_n)
    return {'p': p, 'q': q, 'n': n, 'phi_n': phi_n, 'e': e, 'd': d}

TOY_KEYS = [
    rsa_keygen(11, 13, 7),
    rsa_keygen(11, 23, 7),
    rsa_keygen(7,  11, 7),
    rsa_keygen(61, 53, 17),
    rsa_keygen(101, 103, 7),
    rsa_keygen(97,  89, 5),
]

def random_wrong_d_candidates(phi_n: int, true_d: int, e: int,
                               count: int = 200, seed: int = 20260709) -> List[int]:
    """
    'Plausible wrong guesses': valid RSA private exponents (coprime to
    phi_n, in range) other than the true d. This is the control
    population every method is scored against — if a method can't beat
    this population, it has found nothing.
    """
    rng = random.Random(seed)
    candidates = set()
    tries = 0
    max_tries = count * 50
    while len(candidates) < count and tries < max_tries:
        tries += 1
        d_prime = rng.randrange(2, phi_n)
        if d_prime == true_d or d_prime == e:
            continue
        if math.gcd(d_prime, phi_n) == 1:
            candidates.add(d_prime)
    return sorted(candidates)

def percentile_rank(true_value: float, control_values: List[float]) -> float:
    """What fraction of the control population the true value beats
    (scores lower than). 50th percentile == indistinguishable from chance.
    Near 0th or 100th == the true value is a genuine outlier."""
    if not control_values:
        return 50.0
    below = sum(1 for c in control_values if true_value < c)
    return 100.0 * below / len(control_values)


# ══════════════════════════════════════════════════════════════════════════
# ENGINE — RSA CONTROL BASELINE (reference point, not an attack)
# ══════════════════════════════════════════════════════════════════════════

def rsa_control_baseline() -> Dict[str, Any]:
    """
    Reproduces udeo_poc.py's private_key_degeneration_demo() mechanism —
    given the FULL known key (p,q,e,d), check sedenion degeneracy. This is
    NOT an attack (it requires d as input). It is the reference point the
    three attack engines below are compared against: if an attack engine
    can't do better than this baseline knowing only (n,e), it has not
    found anything the original paper didn't already show.
    """
    dim = 16
    rows = []
    for key in TOY_KEYS:
        p_s = map_int_to_hypercomplex(key['p'], dim)
        q_s = map_int_to_hypercomplex(key['q'], dim)
        e_s = map_int_to_hypercomplex(key['e'], dim)
        d_s = map_int_to_hypercomplex(key['d'], dim)
        n_s = cd_mul(p_s, q_s)
        ed_s = cd_mul(e_s, d_s)
        rows.append({
            'n': key['n'], 'e': key['e'], 'd': key['d'],
            'pq_norm_in_S16': round(float(np.linalg.norm(n_s)), 6),
            'ed_norm_in_S16': round(float(np.linalg.norm(ed_s)), 6),
            'near_zero_divisor': float(np.linalg.norm(n_s)) < 0.15,
        })
    return {
        'claim': 'Reference baseline only (requires full known key) — not an attack.',
        'rows': rows,
        'confidence': 'ESTABLISHED',
        'note': 'This reproduces the already-published udeo_poc.py mechanism at toy scale. '
                'It is the floor every attack engine below must clear using (n,e) alone.',
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 1 — ZERO-DIVISOR SHADOW  (Cody's Method 1)
# ══════════════════════════════════════════════════════════════════════════

def method1_zero_divisor_shadow(dim: int = 16) -> Dict[str, Any]:
    """
    Cody's method 1: 'zero-divisor-ing out the private key into the
    geometry and recovering it from the shape of the hole it left behind.'

    Literal implementation: e_s = embedding of the PUBLIC exponent e.
    Left-multiplication by e_s, L_{e_s}: S^dim -> S^dim, x -> e_s * x, is
    a genuine linear operator (cd_mul is bilinear). Its smallest singular
    directions are the closest thing e_s has to an annihilator ('the
    hole') even when e_s is not an exact zero-divisor (exact ZD pairs are
    a measure-zero locus; almost no real e lands on one).

    Test: does the true d_s align with that shadow direction better than
    a random valid d' would? Given only (n, e) — d is used only to score,
    never to compute the candidate direction.
    """
    per_key = []
    for key in TOY_KEYS:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']

        e_s = map_int_to_hypercomplex(e, dim)
        L = left_mult_matrix(e_s, dim)
        U, S, Vt = np.linalg.svd(L)
        shadow_direction = Vt[-1]           # smallest singular value's right singular vector
        smallest_singular_value = float(S[-1])

        d_s = normalize(map_int_to_hypercomplex(d, dim))
        true_alignment = abs(float(np.dot(shadow_direction, d_s)))

        controls = random_wrong_d_candidates(phi_n, d, e)
        control_alignments = [
            abs(float(np.dot(shadow_direction, normalize(map_int_to_hypercomplex(dp, dim)))))
            for dp in controls
        ]
        rank = percentile_rank(true_alignment, control_alignments)

        per_key.append({
            'n': n, 'e': e, 'd': d,
            'smallest_singular_value': round(smallest_singular_value, 6),
            'exact_zero_divisor': smallest_singular_value < 1e-9,
            'true_d_alignment': round(true_alignment, 6),
            'control_mean_alignment': round(float(np.mean(control_alignments)), 6),
            'true_d_percentile_vs_controls': round(rank, 2),
        })

    ranks = [r['true_d_percentile_vs_controls'] for r in per_key]
    mean_rank = float(np.mean(ranks))
    # A real signal would push the true d's rank consistently toward 0 or 100.
    # Chance means it scatters around 50.
    signal_strength = abs(mean_rank - 50.0)
    if signal_strength > 30:
        verdict, confidence = 'POSSIBLE SIGNAL — worth a larger-scale follow-up', 'CONJECTURE'
    elif signal_strength > 15:
        verdict, confidence = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        verdict, confidence = 'AT CHANCE — no evidence this mechanism recovers d', 'OPEN'

    return {
        'claim': "Method 1 (zero-divisor shadow): does d_s align with e_s's near-annihilator direction?",
        'per_key': per_key,
        'mean_percentile_rank': round(mean_rank, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'mechanism_note': (
            'None of the 6 toy keys landed e on an exact zero-divisor (singular values '
            'were all bounded away from 0) — exact ZD pairs are a discrete, sparse locus '
            'in S^16, and a random small e essentially never hits one. The "shadow" tested '
            'here is therefore the soft/near-singular direction, not a true kernel.'
        ),
    }


def ptolemy_null_partner(x_s: np.ndarray) -> np.ndarray:
    """
    The actual NULL operator (modules/singularity_null/maths.py,
    circle_null_modes()): the Ptolemy inversion z -> R_H^2 / z-bar, applied
    in x_s's own dominant 2D subspace -- the same construction
    circle_null_modes() and drug_targeting's c_drug = R_H^2 * conj(c)/|c|^2
    both use. Note this is the CONFORMAL inverse (x_s . partner = R_H^2,
    not 0) -- the actual code in singularity_null verifies pre-known ZD
    pairs rather than deriving b from a by a general zero-divisor formula;
    no such closed-form exists in this repo. This is the faithful, literal
    reading of 'the shape of the hole' as the Ptolemy-inverted partner in
    e's own subspace, not an invented substitute.
    """
    idx = np.argsort(-np.abs(x_s))[:2]
    i, j = int(idx[0]), int(idx[1])
    z = complex(float(x_s[i]), float(x_s[j]))
    partner = np.zeros_like(x_s)
    if abs(z) < 1e-12:
        return partner
    z_inv = (R_H ** 2) / z.conjugate()
    partner[i] = z_inv.real
    partner[j] = z_inv.imag
    return partner


def method1b_ptolemy_null_operator(dim: int = 16, n_verification_keys: int = 40) -> Dict[str, Any]:
    """
    Rebuild of Method 1 using the actual NULL operator (Ptolemy inversion,
    modules/singularity_null/maths.py) instead of the smallest-singular-
    -vector approximation used in method1_zero_divisor_shadow(). Tested on
    the 6 toy keys AND n_verification_keys independent random keys from the
    start (Method 6 showed the 6-key sample alone can look like a signal
    that doesn't survive scale-up).
    """
    def run_on_keys(keys):
        per_key = []
        for key in keys:
            n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']
            e_s = map_int_to_hypercomplex(e, dim)
            null_partner = normalize(ptolemy_null_partner(e_s))
            d_s = normalize(map_int_to_hypercomplex(d, dim))
            true_alignment = abs(float(np.dot(null_partner, d_s)))
            controls = random_wrong_d_candidates(phi_n, d, e)
            control_alignments = [
                abs(float(np.dot(null_partner, normalize(map_int_to_hypercomplex(dp, dim)))))
                for dp in controls
            ]
            rank = percentile_rank(true_alignment, control_alignments)
            per_key.append({
                'n': n, 'e': e, 'd': d,
                'true_d_alignment': round(true_alignment, 6),
                'control_mean_alignment': round(float(np.mean(control_alignments)), 6),
                'true_d_percentile_vs_controls': round(rank, 2),
            })
        return per_key

    per_key_6 = run_on_keys(TOY_KEYS)
    mean_rank_6 = float(np.mean([r['true_d_percentile_vs_controls'] for r in per_key_6]))

    def sieve(limit):
        s = bytearray([1]) * (limit + 1)
        s[0] = s[1] = 0
        for i in range(2, int(limit ** 0.5) + 1):
            if s[i]:
                s[i * i::i] = bytearray(len(s[i * i::i]))
        return [i for i in range(3, limit + 1) if s[i]]

    rng = random.Random(99)
    verify_primes = [p for p in sieve(5000) if p > 20]
    verify_keys = [_random_toy_key(rng, verify_primes) for _ in range(n_verification_keys)]
    per_key_v = run_on_keys(verify_keys)
    ranks_v = [r['true_d_percentile_vs_controls'] for r in per_key_v]
    mean_rank_v = float(np.mean(ranks_v))
    std_rank_v = float(np.std(ranks_v))

    # CRITICAL CONTROL: repeat verification using an UNRELATED random exponent
    # in place of the true e, to check whether any apparent signal is about
    # the real (e, d) relationship or a generic artifact of the hash/embedding
    # construction that would show up for any small integer.
    rng2 = random.Random(123)
    unrelated_ranks = []
    for key in verify_keys:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']
        e_prime = rng2.randrange(3, 200)
        e_prime_s = map_int_to_hypercomplex(e_prime, dim)
        null_partner_unrelated = normalize(ptolemy_null_partner(e_prime_s))
        d_s = normalize(map_int_to_hypercomplex(d, dim))
        true_align_u = abs(float(np.dot(null_partner_unrelated, d_s)))
        controls = random_wrong_d_candidates(phi_n, d, e)
        ctrl_aligns_u = [
            abs(float(np.dot(null_partner_unrelated, normalize(map_int_to_hypercomplex(dp, dim)))))
            for dp in controls
        ]
        unrelated_ranks.append(percentile_rank(true_align_u, ctrl_aligns_u))
    mean_rank_unrelated = float(np.mean(unrelated_ranks))
    std_rank_unrelated = float(np.std(unrelated_ranks))

    # The apparent bias is only real evidence about (e,d) if it's absent (or
    # much weaker) when e is replaced by something unrelated.
    artifact_gap = abs(mean_rank_v - mean_rank_unrelated)
    signal_strength = abs(mean_rank_v - 50.0)

    if artifact_gap < 10:
        verdict = (f'GENERIC HASH ARTIFACT, NOT A SIGNAL ABOUT (e,d): true-e mean={mean_rank_v:.1f}, '
                    f'unrelated-e mean={mean_rank_unrelated:.1f} — nearly identical, so the bias away '
                    f'from chance has nothing to do with the real key relationship')
        confidence = 'OPEN'
    elif signal_strength > 30:
        verdict, confidence = 'POSSIBLE SIGNAL — survives the unrelated-e control, worth escalating', 'CONJECTURE'
    elif signal_strength > 15:
        verdict, confidence = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        verdict, confidence = f'AT CHANCE on {n_verification_keys}-key verification (6-key: {mean_rank_6:.1f})', 'OPEN'

    return {
        'claim': "Method 1b (Ptolemy NULL operator): does d_s align with e_s's Ptolemy-inversion "
                 "partner in its own 2D subspace, better than chance -- and is that specific to "
                 "the real (e,d) pairing?",
        'per_key_6_toy_keys': per_key_6,
        'six_key_mean_percentile': round(mean_rank_6, 2),
        f'verification_{n_verification_keys}_keys': {
            'mean_percentile_rank': round(mean_rank_v, 2), 'std': round(std_rank_v, 2),
            'ranks': sorted(round(r, 1) for r in ranks_v),
        },
        'unrelated_e_control': {
            'mean_percentile_rank': round(mean_rank_unrelated, 2), 'std': round(std_rank_unrelated, 2),
            'note': 'Same test, but e replaced by an unrelated random exponent unconnected to the '
                    'toy key. If this matches the true-e result, the apparent bias is a construction '
                    'artifact, not information about the real private key.',
        },
        'mean_percentile_rank': round(mean_rank_v, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'operator_note': (
            'ptolemy_null_partner() is the literal NULL operator from '
            'modules/singularity_null/maths.py: z -> R_H^2/z-bar applied in the dominant 2D '
            "subspace of e_s. Note x_s . partner = R_H^2 (a conformal inverse), not 0 -- "
            'singularity_null itself only verifies pre-known zero-divisor pairs; there is no '
            'general closed-form b=f(a) for an exact zero-divisor partner anywhere in this repo.'
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 2 — J2 INVOLUTION IN T_256  (Cody's Method 2)
# ══════════════════════════════════════════════════════════════════════════

def method2_j2_involution_t256(dim: int = 256) -> Dict[str, Any]:
    """
    Cody's method 2: the term he added, -H_hat_BR, to get the 'shadow of
    the formerly content path' — its Laplacian should show components in
    T_256.

    Working interpretation (stated explicitly, since wiki/53 leaves this
    as an unformalised open item): H_hat_RB <-> H_hat_BR is read here as
    left- vs right-multiplication by e_s in T_256 (dim=256) — the two
    channels are literally non-commutative/non-associative CD products,
    which is the only concrete, computable reading of 'both faces of the
    coin' available from the source material. The 'Laplacian' is read as
    the eigen-decomposition of the asymmetry operator Delta = L_{e_s} -
    R_{e_s}, and its 'components' as that operator's eigenvectors.

    Test: does d_s align with a dominant eigenvector of Delta better than
    a random valid d' would? Given only (n, e).
    """
    per_key = []
    for key in TOY_KEYS:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']

        e_s = map_int_to_hypercomplex(e, dim)
        L = left_mult_matrix(e_s, dim)
        R = right_mult_matrix(e_s, dim)
        Delta = L - R                        # the J2 asymmetry operator: H_hat_RB - H_hat_BR

        asymmetry_norm = float(np.linalg.norm(Delta))
        eigvals, eigvecs = np.linalg.eig(Delta)
        order = np.argsort(-np.abs(eigvals))
        top_eigvecs = [np.real(eigvecs[:, i]) for i in order[:5]]

        d_s = normalize(map_int_to_hypercomplex(d, dim))
        true_alignment = max(abs(float(np.dot(normalize(v), d_s))) for v in top_eigvecs)

        controls = random_wrong_d_candidates(phi_n, d, e)
        control_alignments = [
            max(abs(float(np.dot(normalize(v), normalize(map_int_to_hypercomplex(dp, dim)))))
                for v in top_eigvecs)
            for dp in controls
        ]
        rank = percentile_rank(true_alignment, control_alignments)

        per_key.append({
            'n': n, 'e': e, 'd': d,
            'asymmetry_operator_norm': round(asymmetry_norm, 6),
            'true_d_alignment': round(true_alignment, 6),
            'control_mean_alignment': round(float(np.mean(control_alignments)), 6),
            'true_d_percentile_vs_controls': round(rank, 2),
        })

    ranks = [r['true_d_percentile_vs_controls'] for r in per_key]
    mean_rank = float(np.mean(ranks))
    signal_strength = abs(mean_rank - 50.0)
    if signal_strength > 30:
        verdict, confidence = 'POSSIBLE SIGNAL — worth a larger-scale follow-up', 'CONJECTURE'
    elif signal_strength > 15:
        verdict, confidence = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        verdict, confidence = 'AT CHANCE — no evidence this mechanism recovers d', 'OPEN'

    return {
        'claim': "Method 2 (J2 involution / T_256): does d_s align with a dominant eigenvector of L_{e_s} - R_{e_s}?",
        'per_key': per_key,
        'mean_percentile_rank': round(mean_rank, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'interpretation_caveat': (
            "wiki/53's formal-target checklist (its own closing section) explicitly leaves "
            "'state the complexity result' and 'prove or bound this claim' as open, unchecked "
            "items. The H_hat_RB <-> H_hat_BR / J2 / T_256 machinery has no prior code "
            "implementation anywhere in the repo — this is a first, literal, and necessarily "
            "provisional reading of an underspecified theoretical note, not a validated mechanism."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 3 — SEDENION SPECTRAL RELATIVITY  (Cody's Method 3)
# ══════════════════════════════════════════════════════════════════════════

def sigma_face_metric(sigma: float) -> float:
    """
    g(sigma) per wiki/34's sigma-face table: g=1 at sigma=1/2 (flat,
    reference), g grows as sigma moves toward the boundary, g -> infinity
    at the degenerate/zero-divisor limit.

    CAVEAT (stated plainly): wiki/34's sigma is a [1/2, infinity) physical
    parameter (mass/gravity scale); the Horner hash address used elsewhere
    in this codebase produces sigma in (0,1) (a hash-derived pseudo-address,
    not the same sigma). This function treats hash-sigma's interval
    boundaries (0 and 1) as the HSR degeneracy limit, and hash-sigma=1/2 as
    the flat reference point — a deliberate reuse of the *shape* of the
    wiki/34 metric, not a claim that these are the same sigma. That
    reinterpretation is this engine's choice, not something wiki/34 states.
    """
    eps = 1e-6
    x = abs(2.0 * sigma - 1.0)          # 0 at sigma=1/2, -> 1 at sigma -> 0 or 1
    return 1.0 / max(1.0 - x, eps)

def geodesic_distance(sigma_a: float, sigma_b: float, steps: int = 200) -> float:
    """Numerical integral of g(sigma) ds along the straight path a -> b."""
    xs = np.linspace(sigma_a, sigma_b, steps)
    gs = np.array([sigma_face_metric(x) for x in xs])
    return float(abs(np.trapezoid(gs, xs)))

def method3_spectral_relativity(dim: int = 16) -> Dict[str, Any]:
    """
    Cody's method 3: Sedenion Spectral Relativity. Zero-divisors are
    metric singularities (wiki/34); the sigma-face table IS the metric.

    Test: is the geodesic distance (under g(sigma)) from e's hash-address
    to the TRUE d's hash-address a statistical outlier compared to the
    distance from e's address to random valid d' addresses? Given only
    (n, e).
    """
    per_key = []
    for key in TOY_KEYS:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']

        sigma_e = sigma_of_int(e)
        sigma_n = sigma_of_int(n)
        sigma_d_true = sigma_of_int(d)

        dist_true = geodesic_distance(sigma_e, sigma_d_true)

        controls = random_wrong_d_candidates(phi_n, d, e)
        dist_controls = [geodesic_distance(sigma_e, sigma_of_int(dp)) for dp in controls]
        rank = percentile_rank(dist_true, dist_controls)

        per_key.append({
            'n': n, 'e': e, 'd': d,
            'sigma_e': round(sigma_e, 6),
            'sigma_n': round(sigma_n, 6),
            'sigma_d_true': round(sigma_d_true, 6),
            'geodesic_dist_true_d': round(dist_true, 4),
            'geodesic_dist_control_mean': round(float(np.mean(dist_controls)), 4),
            'true_d_percentile_vs_controls': round(rank, 2),
        })

    ranks = [r['true_d_percentile_vs_controls'] for r in per_key]
    mean_rank = float(np.mean(ranks))
    signal_strength = abs(mean_rank - 50.0)
    if signal_strength > 30:
        verdict, confidence = 'POSSIBLE SIGNAL — worth a larger-scale follow-up', 'CONJECTURE'
    elif signal_strength > 15:
        verdict, confidence = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        verdict, confidence = 'AT CHANCE — no evidence this mechanism recovers d', 'OPEN'

    return {
        'claim': "Method 3 (Sedenion Spectral Relativity): is the sigma-metric geodesic to true d an outlier?",
        'per_key': per_key,
        'mean_percentile_rank': round(mean_rank, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'interpretation_caveat': (
            'g(sigma) here reuses the SHAPE of the wiki/34 sigma-face metric applied to the '
            'Horner-hash sigma address, not the same sigma variable wiki/34 defines. See '
            'sigma_face_metric() docstring for the exact reinterpretation made.'
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 4 — CONTENT + PUBLIC + PRIVATE = HASH  (Cody's equation, this session)
# ══════════════════════════════════════════════════════════════════════════

def method4_content_public_private_hash(dim: int = 16, search_pool: int = 500) -> Dict[str, Any]:
    """
    Cody's equation:  Content + Public + Private = Hash
                       Content + Public - Hash     = 1/Private   (his framing)

    Literal build, mapped onto RSA quantities:
        Public  = e   (public exponent)
        Private = d   (private exponent)
        Content = n   (the modulus — the only other per-key public quantity)
        Hash    = Content_s + Public_s + Private_s   (VECTOR SUM in S^16 —
                  see map_int_to_hypercomplex). Computing Hash REQUIRES d.
                  It is treated here as something the key-holder produces
                  once and reveals — the sedenion-embedding analogue of a
                  signature, not something a public-key-only attacker could
                  derive themselves.

    What Content_s + Public_s - Hash actually is: EXACTLY -Private_s, by
    plain vector-space algebra. That step needs no zero-divisor structure
    and is not a discovery — subtraction undoes addition in any vector
    space. Cody's framing calls the result '1/Private'; what's implemented
    and tested here is the vector-algebra reading ('-Private_s'), since
    that is what Content+Public-Hash is defined to equal. Whether that
    recovered vector can be turned back into the actual integer d is the
    real open question, tested below by search.

    The test: given (n, e, Hash) — NOT d — search a pool of candidate d'
    values, embed each, and see whether the TRUE d's embedding is the
    closest match to the recovered vector, and by how much, versus the
    random-guess control pool.
    """
    per_key = []
    for key in TOY_KEYS:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']

        content_s = map_int_to_hypercomplex(n, dim)
        public_s  = map_int_to_hypercomplex(e, dim)
        private_s = map_int_to_hypercomplex(d, dim)   # only used to BUILD Hash
        hash_s    = content_s + public_s + private_s  # the one-time published value

        recovered_neg_private_s = content_s + public_s - hash_s   # = -private_s, exactly

        # Distance from -recovered to each candidate's embedding (true d, then controls)
        true_dist = float(np.linalg.norm(-recovered_neg_private_s - private_s))

        controls = random_wrong_d_candidates(phi_n, d, e, count=search_pool)
        control_dists = [
            float(np.linalg.norm(-recovered_neg_private_s - map_int_to_hypercomplex(dp, dim)))
            for dp in controls
        ]
        all_dists = control_dists + [true_dist]
        true_is_closest_match = true_dist == min(all_dists)
        rank = percentile_rank(-true_dist, [-c for c in control_dists])  # smaller distance = better, so negate

        # Collision check: how many OTHER candidates embed to (near-)identical vectors as the true d?
        collisions = sum(1 for cd_ in control_dists if cd_ < 1e-9)

        per_key.append({
            'n': n, 'e': e, 'd': d,
            'true_d_distance_to_recovered_vector': round(true_dist, 10),
            'control_mean_distance': round(float(np.mean(control_dists)), 6),
            'true_d_is_closest_match_in_pool': true_is_closest_match,
            'exact_hash_collisions_with_true_d': collisions,
            'true_d_percentile_vs_controls': round(rank, 2),
        })

    all_exact = all(r['true_d_is_closest_match_in_pool'] for r in per_key)
    any_collisions = any(r['exact_hash_collisions_with_true_d'] > 0 for r in per_key)
    ranks = [r['true_d_percentile_vs_controls'] for r in per_key]
    mean_rank = float(np.mean(ranks))

    if all_exact and not any_collisions:
        verdict = 'EXACT — recovered vector uniquely and exactly matches the true d in every toy key'
        confidence = 'ESTABLISHED'
    elif all_exact and any_collisions:
        verdict = 'EXACT MATCH BUT NOT UNIQUE — other candidates embed to the same vector in at least one key'
        confidence = 'CONJECTURE'
    else:
        verdict = 'DOES NOT UNIQUELY RECOVER d — a wrong candidate matched at least as well in at least one key'
        confidence = 'OPEN'

    return {
        'claim': "Method 4 (Content+Public+Private=Hash): does subtracting Hash recover d by "
                 "search-matching against its embedding?",
        'per_key': per_key,
        'mean_percentile_rank': round(mean_rank, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'critical_caveat': (
            "This is NOT public-key-only key recovery. Hash = Content_s + Public_s + Private_s "
            "requires d to compute in the first place — it is only usable by someone who could "
            "already produce a value requiring the private key (e.g. a one-time revealed "
            "signature-like artifact), not by an attacker holding only (n, e). What this engine "
            "actually tests is narrower and still useful: IF such a Hash value is ever exposed, "
            "does the vector algebra exactly and uniquely identify d among a candidate pool, or "
            "does the lossy embedding (map_int_to_hypercomplex) blur multiple candidates together? "
            "'Exact and unique' here would validate the embedding's injectivity, not a factoring "
            "or key-recovery break."
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 5 — ZERO LATTICE PATHS  (Cody's method 5: RiemannHypothesisProof /
#            AbrikosovTree / POE pancake coil)
# ══════════════════════════════════════════════════════════════════════════
#
# Geometry ported from AbrikosovTree/engine/telperion_engine.py
# (cd_level_data / prime_tower_path), generalised from primes to any
# integer — the tower math (N-shape = x mod 16, quadrant, THE ANGLE) never
# actually required primality, only telperion_engine.py's docstrings and
# 'fermat_survives' framing are prime-specific. That framing is dropped
# here since Content/Public/Private/Hash aren't leaves being tested for
# survival, they're the four RSA quantities being routed through the same
# 9-level CD tower (k=0 real -> k=8 T_256) that primes are routed through
# there. The pancake coil (POE/hardware_primer.md) is the same L_(I|O)
# cardioid pathway geometry realised in copper instead of algebra — cited
# here as the origin of 'the path is the geometry', not re-derived.

N_LEVELS_TOWER = 9   # k = 0..8: ℝ, ℂ, ℍ, 𝕆, 𝕊, t_32, t_64, t_128, T_256
CD_TOWER_NAMES = {0: 'R', 1: 'C', 2: 'H', 3: 'O', 4: 'S',
                  5: 't_32', 6: 't_64', 7: 't_128', 8: 'T_256'}
TOWER_LEVEL_BASE_DEG = {0: 0.0, 1: 0.0, 2: 45.0, 3: 0.0, 4: 45.0,
                        5: 0.0, 6: 45.0, 7: 0.0, 8: 45.0}
THE_ANGLE_DEG = 22.5   # pi/8 — the angular quantum, from zero_lattice.py / telperion_engine.py

def tower_level_geometry(k: int) -> Dict[str, Any]:
    sigma = 1.0 - k / 4.0
    theta = k * math.pi / 8.0
    is_red = (k % 2 == 1) and k > 0
    is_blue = (k % 2 == 0) and k > 0
    return {
        'k': k, 'name': CD_TOWER_NAMES[k], 'sigma': sigma,
        'theta_rad': theta, 'is_zd': k >= 4,
        'j_type': 'J_red' if is_red else ('J_blue' if is_blue else 'real'),
        'base_deg': TOWER_LEVEL_BASE_DEG[k],
    }

def variable_tower_path(x: int, label: str) -> Dict[str, Any]:
    """
    Trace integer x through the 9-level CD tower (ℝ -> T_256), same
    geometry AbrikosovTree/telperion_engine.py uses for prime leaves,
    generalised to any integer standing in for an RSA quantity.
    """
    ns = x % 16
    q = ns % 4
    R = 3.0
    levels = []
    for k in range(N_LEVELS_TOWER):
        lv = tower_level_geometry(k)
        phi_base = lv['base_deg'] + q * 90.0
        if lv['j_type'] == 'J_red':
            phi = phi_base + THE_ANGLE_DEG
        elif lv['j_type'] == 'J_blue':
            phi = phi_base - THE_ANGLE_DEG
        else:
            phi = phi_base
        phi_r = math.radians(phi)
        theta = lv['theta_rad']
        levels.append({
            'k': k, 'name': lv['name'], 'sigma': round(lv['sigma'], 4),
            'is_zd': lv['is_zd'], 'phi_deg': round(phi, 3),
            'sph': (round(R*math.sin(theta)*math.cos(phi_r), 4),
                    round(R*math.sin(theta)*math.sin(phi_r), 4),
                    round(R*math.cos(theta), 4)),
        })
    return {'label': label, 'value': x, 'nshape': ns, 'quadrant': q, 'levels': levels}

def path_angular_distance(path_a: Dict, path_b: Dict) -> float:
    """Mean absolute angular difference (degrees) between two paths, level by level."""
    diffs = []
    for la, lb in zip(path_a['levels'], path_b['levels']):
        d = abs(la['phi_deg'] - lb['phi_deg']) % 360.0
        d = min(d, 360.0 - d)
        diffs.append(d)
    return float(np.mean(diffs))


def mod4_identity_theorem() -> Dict[str, Any]:
    """
    PROVEN, not conjectured: d = e (mod 4) for every RSA key with odd
    primes p, q.

    Proof: phi(n) = (p-1)(q-1) is a product of two even numbers, so
    4 | phi(n). e*d = 1 (mod phi(n)) therefore forces e*d = 1 (mod 4).
    The group (Z/4Z)* = {1, 3} has exponent 2 (1*1=1, 3*3=9=1 mod 4) --
    every element is its own inverse. So e*d = 1 (mod 4) forces
    d = e^{-1} = e (mod 4).

    This is why Method 5's path test showed e and d landing in the same
    tower quadrant on every toy key: the tower's angular coordinate only
    encodes x mod 4, and that coordinate was never hidden information to
    begin with -- it falls straight out of e via this identity, no
    sedenion or zero-divisor structure involved. Verified computationally
    on 2000 random toy RSA keys: 2000/2000 satisfy the identity, matching
    the proof exactly.

    Practical significance: reduces the private-key search space by
    exactly one bit (factor of 2). For any real key size this is
    cryptographically meaningless -- equivalent in weight to knowing d is
    odd. Real, exact, provable, and not a break.
    """
    rng = random.Random(20260709)
    def sieve(limit):
        s = bytearray([1]) * (limit + 1)
        s[0] = s[1] = 0
        for i in range(2, int(limit ** 0.5) + 1):
            if s[i]:
                s[i * i::i] = bytearray(len(s[i * i::i]))
        return [i for i in range(3, limit + 1) if s[i]]

    primes = sieve(20000)
    n_trials = 2000
    matches = 0
    for _ in range(n_trials):
        p, q = rng.sample(primes, 2)
        phi_n = (p - 1) * (q - 1)
        e_candidates = [x for x in range(3, 200) if math.gcd(x, phi_n) == 1]
        e = rng.choice(e_candidates)
        d = pow(e, -1, phi_n)
        assert phi_n % 4 == 0
        if (d - e) % 4 == 0:
            matches += 1

    return {
        'claim': 'd = e (mod 4) for every RSA key with odd primes p, q. Proven, not statistical.',
        'proof': (
            '4 | phi(n) since (p-1) and (q-1) are both even. e*d=1 (mod phi(n)) => e*d=1 (mod 4). '
            '(Z/4Z)*={1,3} has exponent 2, so every element is self-inverse, forcing d=e (mod 4).'
        ),
        'empirical_verification': f'{matches}/{n_trials} random RSA keys satisfy the identity',
        'matches_proof_exactly': matches == n_trials,
        'practical_significance': 'Reduces private-key search space by exactly 1 bit (factor of 2). '
                                   'Cryptographically meaningless at real key sizes.',
        'relation_to_sedenion_framework': 'None. This is classical number theory. It surfaced via the '
                                           "Zero Lattice path test only because that geometry's angle "
                                           'happens to encode x mod 4, not because of any zero-divisor '
                                           'or CD-tower mechanism.',
        'confidence': 'ESTABLISHED',
    }


def method5_zero_lattice_paths(search_pool: int = 200) -> Dict[str, Any]:
    """
    Cody's method 5: trace Content (n), Public (e), Private (d), and Hash
    (= n + e + d, the literal-integer reading of his equation this time,
    not the vector-sum reading used in Method 4) through the Zero Lattice
    tower, and show each variable's path.

    Content + Public - Hash = -d EXACTLY, same trivial algebra as Method 4
    (just in integers now instead of sedenion vectors) — so if Hash is
    exposed, d's N-shape/path is immediate arithmetic, not a discovery.
    The real test, same as every engine above: given ONLY (n, e) — Hash
    NOT exposed — does d's path show any structure a random valid d'
    wouldn't also show?
    """
    per_key = []
    for key in TOY_KEYS:
        n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']
        h = n + e + d

        content_path = variable_tower_path(n, 'Content (n)')
        public_path  = variable_tower_path(e, 'Public (e)')
        private_path = variable_tower_path(d, 'Private (d)')
        hash_path    = variable_tower_path(h, 'Hash (n+e+d)')

        recovered_d = n + e - h   # = -d, exact integer identity
        exact_recovery = (recovered_d == -d)

        # Public-key-only test: does true d's path structurally stand out
        # from random valid d' candidates, using only (n, e) -- no Hash?
        controls = random_wrong_d_candidates(phi_n, d, e, count=search_pool)
        true_dist_to_public = path_angular_distance(private_path, public_path)
        control_dists = [
            path_angular_distance(variable_tower_path(dp, 'control'), public_path)
            for dp in controls
        ]
        rank_pubkey_only = percentile_rank(true_dist_to_public, control_dists)

        per_key.append({
            'n': n, 'e': e, 'd': d, 'hash_n_plus_e_plus_d': h,
            'content_path': content_path, 'public_path': public_path,
            'private_path': private_path, 'hash_path': hash_path,
            'content_plus_public_minus_hash': recovered_d,
            'exact_recovery_if_hash_known': exact_recovery,
            'true_d_dist_to_public_path_deg': round(true_dist_to_public, 3),
            'control_mean_dist_deg': round(float(np.mean(control_dists)), 3),
            'true_d_percentile_vs_controls_pubkey_only': round(rank_pubkey_only, 2),
        })

    ranks = [r['true_d_percentile_vs_controls_pubkey_only'] for r in per_key]
    mean_rank = float(np.mean(ranks))
    signal_strength = abs(mean_rank - 50.0)
    if signal_strength > 30:
        pubkey_verdict, pubkey_conf = 'POSSIBLE SIGNAL — worth a larger-scale follow-up', 'CONJECTURE'
    elif signal_strength > 15:
        pubkey_verdict, pubkey_conf = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        pubkey_verdict, pubkey_conf = 'AT CHANCE — path alone (n,e only) does not single out d', 'OPEN'

    return {
        'claim': 'Method 5 (Zero Lattice paths): trace Content/Public/Private/Hash through the '
                 '9-level CD tower; test both the Hash-exposed and public-key-only scenarios.',
        'per_key': per_key,
        'hash_exposed_scenario': {
            'verdict': 'EXACT — Content+Public-Hash = -d exactly in every key (plain integer algebra)',
            'confidence': 'ESTABLISHED',
            'caveat': 'Same caveat as Method 4: requires Hash = n+e+d to be exposed somewhere, which '
                       'requires d to compute in the first place. Not a public-key-only attack.',
        },
        'public_key_only_scenario': {
            'mean_percentile_rank': round(mean_rank, 2),
            'chance_baseline': 50.0,
            'verdict': pubkey_verdict,
            'confidence': pubkey_conf,
        },
        'confidence': pubkey_conf,
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE 6 — EMERGENT ROTATION INFORMATION  (straightening the switchback path)
# ══════════════════════════════════════════════════════════════════════════
#
# Method 5's phi_deg was a function of quadrant (x mod 4) ONLY -- the polar
# angle theta was fixed per level (theta = k*pi/8), never a function of x at
# all. That is why Method 5's path visually looked "already straight": there
# was only ever one x-dependent degree of freedom (azimuth), not two. Cody's
# request here is to actually build the two-angle (inclination/declination)
# raw path, then compute what rotation at each shell straightens it -- that
# per-level rotation sequence is the candidate "emergent information."

def level_dim(k: int) -> int:
    return max(1, 2 ** k)

def raw_shell_angles(x: int, k: int) -> Tuple[float, float]:
    """
    Raw (unstraightened) inclination theta and azimuth phi for integer x at
    CD tower level k, using the REAL P1-hash embedding at that level's own
    native dimensionality (dim = 2^k). theta = arccos(v[0]) is the standard
    hyperspherical polar angle relative to the scalar axis. phi is the
    azimuth in the (e1, e2) plane. At k=0 (dim=1) the embedding is a single
    scalar -- degenerate, both angles defined as 0 (the tower's pole, same
    convention telperion_engine.py uses for k=0).
    """
    dim = level_dim(k)
    if dim == 1:
        return 0.0, 0.0
    v = map_int_to_hypercomplex(x, dim)
    theta = math.acos(max(-1.0, min(1.0, float(v[0]))))
    if dim >= 3:
        phi = math.atan2(float(v[2]), float(v[1]))
    else:
        phi = math.atan2(0.0, float(v[1]))
    return theta, phi

def _wrap_pi(a: float) -> float:
    """Wrap angle to (-pi, pi]."""
    return (a + math.pi) % (2 * math.pi) - math.pi

def emergent_rotation_information(x: int, label: str) -> Dict[str, Any]:
    """
    For integer x, compute the raw (theta_k, phi_k) at every level k=0..8,
    the straight-line (linearly interpolated between k=1 and k=8) target at
    each intermediate level, and the rotation (d_theta_k, d_phi_k) needed at
    each shell to correct the raw path onto that straight Lagrangian path.
    This per-level rotation sequence is the emergent-information signature.
    """
    raw = [raw_shell_angles(x, k) for k in range(N_LEVELS_TOWER)]
    theta_1, phi_1 = raw[1]
    theta_8, phi_8 = raw[8]
    d_phi_total = _wrap_pi(phi_8 - phi_1)

    corrections = []
    for k in range(1, N_LEVELS_TOWER):
        t = (k - 1) / 7.0
        target_theta = theta_1 + t * (theta_8 - theta_1)
        target_phi = phi_1 + t * d_phi_total
        raw_theta_k, raw_phi_k = raw[k]
        d_theta = raw_theta_k - target_theta
        d_phi = _wrap_pi(raw_phi_k - target_phi)
        corrections.append({
            'k': k, 'name': CD_TOWER_NAMES[k],
            'raw_theta': round(raw_theta_k, 6), 'raw_phi': round(raw_phi_k, 6),
            'target_theta': round(target_theta, 6), 'target_phi': round(target_phi, 6),
            'd_theta': round(d_theta, 6), 'd_phi': round(d_phi, 6),
        })

    signature = tuple(round(c['d_theta'], 4) for c in corrections) + \
                tuple(round(c['d_phi'], 4) for c in corrections)

    return {'label': label, 'value': x, 'corrections': corrections, 'signature': signature}

def signature_distance(sig_a: Tuple[float, ...], sig_b: Tuple[float, ...]) -> float:
    return float(np.linalg.norm(np.array(sig_a) - np.array(sig_b)))

def _random_toy_key(rng: random.Random, primes: List[int]) -> Dict[str, int]:
    p, q = rng.sample(primes, 2)
    phi_n = (p - 1) * (q - 1)
    e_candidates = [x for x in range(3, 200) if math.gcd(x, phi_n) == 1]
    e = rng.choice(e_candidates)
    d = pow(e, -1, phi_n)
    return {'p': p, 'q': q, 'n': p * q, 'phi_n': phi_n, 'e': e, 'd': d}

def method6_emergent_rotation_signature(search_pool: int = 200, n_verification_keys: int = 40) -> Dict[str, Any]:
    """
    Test: does Private's emergent-rotation signature (the per-shell
    inclination/declination corrections needed to straighten its raw path)
    align with Public's, Content's, or Hash's signature better than a
    random valid d' would -- given only (n, e)? Same honest scoring as
    every engine above.

    Runs on the standard 6 toy keys FIRST, then repeats on
    n_verification_keys independent random keys, because the 6-key result
    alone was misleading here: it showed mean percentile 31.19 (looked like
    a weak signal by this engine's own >15 threshold), but that did not
    survive a larger sample -- see verification_40_keys below. The 40-key
    result is treated as authoritative; the small-sample result is kept in
    the record, not deleted, per the standing 'failed predictions stay in
    the record' policy.
    """
    def run_on_keys(keys):
        per_key = []
        for key in keys:
            n, e, d, phi_n = key['n'], key['e'], key['d'], key['phi_n']
            public_sig  = emergent_rotation_information(e, 'Public (e)')['signature']
            private_sig = emergent_rotation_information(d, 'Private (d)')['signature']
            true_dist = signature_distance(private_sig, public_sig)
            controls = random_wrong_d_candidates(phi_n, d, e, count=search_pool)
            control_dists = [
                signature_distance(emergent_rotation_information(dp, 'control')['signature'], public_sig)
                for dp in controls
            ]
            rank = percentile_rank(true_dist, control_dists)
            per_key.append({
                'n': n, 'e': e, 'd': d,
                'true_d_sig_distance_to_public': round(true_dist, 6),
                'control_mean_sig_distance': round(float(np.mean(control_dists)), 6),
                'true_d_percentile_vs_controls': round(rank, 2),
            })
        return per_key

    per_key = run_on_keys(TOY_KEYS)
    ranks_6 = [r['true_d_percentile_vs_controls'] for r in per_key]
    mean_rank_6 = float(np.mean(ranks_6))

    def sieve(limit):
        s = bytearray([1]) * (limit + 1)
        s[0] = s[1] = 0
        for i in range(2, int(limit ** 0.5) + 1):
            if s[i]:
                s[i * i::i] = bytearray(len(s[i * i::i]))
        return [i for i in range(3, limit + 1) if s[i]]

    rng = random.Random(99)
    verify_primes = [p for p in sieve(5000) if p > 20]
    verify_keys = [_random_toy_key(rng, verify_primes) for _ in range(n_verification_keys)]
    verify_per_key = run_on_keys(verify_keys)
    ranks_40 = [r['true_d_percentile_vs_controls'] for r in verify_per_key]
    mean_rank_40 = float(np.mean(ranks_40))
    std_rank_40 = float(np.std(ranks_40))

    mean_rank = mean_rank_40
    signal_strength = abs(mean_rank - 50.0)
    if signal_strength > 30:
        verdict, confidence = 'POSSIBLE SIGNAL — worth a larger-scale follow-up', 'CONJECTURE'
    elif signal_strength > 15:
        verdict, confidence = 'WEAK, INCONSISTENT SIGNAL', 'CONJECTURE'
    else:
        verdict, confidence = (
            f'AT CHANCE on {n_verification_keys}-key verification (6-key sample showed '
            f'{mean_rank_6:.1f}, looked like a weak signal, did not survive scale-up)',
            'OPEN',
        )

    return {
        'claim': 'Method 6 (emergent rotation information): do per-shell straightening '
                 'corrections (inclination + declination) for d align with e more than chance?',
        'per_key': per_key,
        'six_key_mean_percentile': round(mean_rank_6, 2),
        f'verification_{n_verification_keys}_keys': {
            'mean_percentile_rank': round(mean_rank_40, 2),
            'std': round(std_rank_40, 2),
            'ranks': sorted(round(r, 1) for r in ranks_40),
        },
        'mean_percentile_rank': round(mean_rank, 2),
        'chance_baseline': 50.0,
        'verdict': verdict,
        'confidence': confidence,
        'method_note': (
            'This corrects a real gap in Method 5: its theta was fixed per level (k*pi/8), '
            'never a function of x, so it only ever carried one angular degree of freedom '
            '(azimuth via quadrant). This engine computes BOTH angles from the real P1-hash '
            "embedding at each level's own native dimensionality (dim=2^k), then measures the "
            'rotation needed at each shell to straighten the raw path onto the k=1-to-k=8 '
            'geodesic. That per-shell rotation sequence is the signature tested here.'
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# ENGINE — COMPARE ALL THREE
# ══════════════════════════════════════════════════════════════════════════

def compare_all_methods() -> Dict[str, Any]:
    """
    Runs the RSA control baseline and all three attack engines, and
    tabulates them side by side. This is the deliverable for deciding
    which (if any) of Cody's three methods is worth further investment.
    """
    baseline = rsa_control_baseline()
    mod4 = mod4_identity_theorem()
    m1 = method1_zero_divisor_shadow()
    m1b = method1b_ptolemy_null_operator()
    m2 = method2_j2_involution_t256()
    m3 = method3_spectral_relativity()
    m4 = method4_content_public_private_hash()
    m5 = method5_zero_lattice_paths()
    m6 = method6_emergent_rotation_signature()

    table = [
        {'method': '1 — Zero-divisor shadow (S^16)',
         'mean_percentile_vs_chance_50': m1['mean_percentile_rank'],
         'verdict': m1['verdict'], 'confidence': m1['confidence']},
        {'method': '1b — Ptolemy NULL operator (singularity_null)',
         'mean_percentile_vs_chance_50': m1b['mean_percentile_rank'],
         'verdict': m1b['verdict'], 'confidence': m1b['confidence']},
        {'method': '2 — J2 involution / T_256 eigenspectrum',
         'mean_percentile_vs_chance_50': m2['mean_percentile_rank'],
         'verdict': m2['verdict'], 'confidence': m2['confidence']},
        {'method': '3 — Sedenion Spectral Relativity geodesic',
         'mean_percentile_vs_chance_50': m3['mean_percentile_rank'],
         'verdict': m3['verdict'], 'confidence': m3['confidence']},
        {'method': '4 — Content+Public+Private=Hash (requires Hash to be exposed)',
         'mean_percentile_vs_chance_50': m4['mean_percentile_rank'],
         'verdict': m4['verdict'], 'confidence': m4['confidence']},
        {'method': '5 — Zero Lattice paths, public-key-only scenario',
         'mean_percentile_vs_chance_50': m5['public_key_only_scenario']['mean_percentile_rank'],
         'verdict': m5['public_key_only_scenario']['verdict'],
         'confidence': m5['public_key_only_scenario']['confidence']},
        {'method': '6 — Emergent rotation signature (inclination+declination)',
         'mean_percentile_vs_chance_50': m6['mean_percentile_rank'],
         'verdict': m6['verdict'], 'confidence': m6['confidence']},
    ]
    best = min(table, key=lambda r: abs(r['mean_percentile_vs_chance_50'] - 50.0) * -1) \
        if any(abs(r['mean_percentile_vs_chance_50'] - 50.0) > 15 for r in table) else None

    return {
        'claim': 'Side-by-side comparison of all five candidate RSA key-recovery mechanisms, '
                 'each scored against a random-guess control on the same 6 toy keys.',
        'baseline_reference': baseline,
        'mod4_theorem': mod4,
        'comparison_table': table,
        'strongest_signal': best['method'] if best else 'NONE — all five at chance',
        'confidence': 'OPEN' if best is None else 'CONJECTURE',
        'honest_summary': (
            'None of methods 1-6 takes only (n, e) and outputs d exactly. '
            'What each produces is a percentile rank: how unusual the true d looks under that '
            "method's geometry compared to 200-random-but-valid wrong guesses per key. "
            '50 == indistinguishable from chance, matching the prior finding that the RSA '
            'cross-check control stayed at chance across all 5 Translator test rounds. '
            'The one genuinely ESTABLISHED result of this session is the mod4_theorem: '
            'd = e (mod 4) always, proven by elementary number theory, unrelated to sedenions or '
            'zero-divisors, and cryptographically insignificant (1 bit of search-space reduction). '
            'Methods 1, 2, 3, 5(public-key-only), 6 are AT CHANCE (Method 6 initially looked like a '
            'weak signal on 6 toy keys, did not survive a 40-key verification). Method 1b (the '
            'actual Ptolemy NULL operator from singularity_null) initially looked like a strong '
            'signal on both the 6-key and 40-key tests, but a control test replacing e with an '
            'UNRELATED exponent produced the same bias -- proving it is a generic artifact of the '
            'hash construction, not information about the real (e,d) relationship. Method 4 and '
            'Method 5 (Hash-exposed scenario) are exact ONLY when a value requiring d to compute '
            '(Hash) is separately exposed -- neither is a public-key-only attack.'
        ),
    }


# ══════════════════════════════════════════════════════════════════════════
# MAIN — run everything, print a readable report
# ══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print()
    print("=" * 74)
    print("  UDEO RSA DEMO — five candidate key-recovery mechanisms, honestly scored")
    print("=" * 74)

    result = compare_all_methods()
    print()
    print("  Baseline (requires full known key — reference only):")
    for row in result['baseline_reference']['rows']:
        print(f"    n={row['n']:>6}  pq_norm_S16={row['pq_norm_in_S16']:.4f}  "
              f"ed_norm_S16={row['ed_norm_in_S16']:.4f}  near_ZD={row['near_zero_divisor']}")

    print()
    print("  ESTABLISHED result — d = e (mod 4), proven (not from the sedenion framework):")
    mod4 = result['mod4_theorem']
    print(f"    {mod4['empirical_verification']}  (matches proof exactly: {mod4['matches_proof_exactly']})")
    print(f"    Practical significance: {mod4['practical_significance']}")

    print()
    print("  Attack engines — given ONLY (n, e), scored vs 200 random-guess controls per key:")
    print(f"  {'Method':60s} {'mean %ile':>10s} {'confidence':>12s}  verdict")
    for row in result['comparison_table']:
        print(f"  {row['method']:60s} {row['mean_percentile_vs_chance_50']:>10.2f} "
              f"{row['confidence']:>12s}  {row['verdict']}")

    print()
    print(f"  Strongest signal: {result['strongest_signal']}")
    print()
    print("  " + result['honest_summary'])
    print("=" * 74)
