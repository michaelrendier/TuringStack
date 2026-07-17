#!/usr/bin/env python3
"""
hash_collision_demo.py — does the same content produce the same Hash_s
for different (e,d) key pairs? Cody's direct question, 2026-07-17.

v2: the first pass (see git history / session log) used
UDEO_RSA_DEMO.py's map_int_to_hypercomplex() unchanged, and found BOTH
the real (e,d) population AND an unrelated-random-integer control landing
on an EXACT 0.000000 minimum pairwise distance, every single control
trial. That's not a signal about keys — it's proof the embedding itself
is not injective: map_int_to_hypercomplex places weight at
(zidx % dim, hraw % dim) with dim=16, so it has at most ~256 distinct
possible outputs no matter the input range. ~97 draws into ~256 buckets
guarantees collisions by the birthday bound alone. Degeneracy that's
FREE (this) is noise; degeneracy that's EARNED (SHA-1's exact-ZD test,
built on the bit-exact T32/GF(2) embedding, found 0/225 real hits) is a
finding. This file fixes the measuring instrument before asking the
question again.

THE FIX: injective_embed() places x's own base-2^16 digits directly into
each of the 16 coordinates — no hashing, no folding mod a small dim.
Same philosophy as the T32 bit-exact embedding (word_to_t32: bit k -> e_k,
no aliasing), generalised to real-valued coefficients so it still works
inside S16's ordinary Euclidean/linear-algebra machinery (norms,
distances) that methods 1-6 in UDEO_RSA_DEMO.py depend on. Injective for
any x < (2^16)^16 = 2^256 -- covers every value used anywhere in this
codebase, toy-scale or real RSA-2048/4096, with room to spare.

Author:  Claude, at Cody's direction — 2026-07-17
White Hat.
"""

import math
import random
import hashlib
import numpy as np


def injective_embed(x: int, dim: int = 16) -> np.ndarray:
    """v3 fix: v1 (hash folded mod dim=16) had ~256 possible outputs --
    aliased. v2 (raw base-65536 digits) was injective but toy-scale
    values (~12 bits) never leave coordinate 0 -- no spread, not enough
    entropy to fill 16 real dimensions by position alone.

    This uses SHA-256's own avalanche property instead: even adjacent
    integers (x=7 vs x=8) hash to completely unrelated 256-bit outputs.
    Slicing that hash into 16 x 16-bit chunks, one per dimension, uses
    the FULL hash width directly as coordinates -- no mod-dim folding
    (v1's bug) and no low-entropy positional placement (v2's bug).
    Collision-resistant to SHA-256's own bound, not just injective in
    principle -- astronomically safe at a ~100-point sample."""
    h = hashlib.sha256(str(int(x)).encode()).digest()  # 32 bytes = 256 bits
    coords = np.zeros(dim)
    for i in range(dim):
        chunk = h[2 * i:2 * i + 2]
        coords[i] = float(int.from_bytes(chunk, 'big'))
    return coords


def enumerate_valid_e(phi_n: int, cap: int = 400):
    """All e in [3, cap] coprime to phi_n — many distinct valid key pairs
    for the SAME n."""
    return [e for e in range(3, min(cap, phi_n)) if math.gcd(e, phi_n) == 1]


def hash_vectors_for_n(p: int, q: int, dim: int = 16, cap: int = 400):
    n = p * q
    phi_n = (p - 1) * (q - 1)
    content_s = injective_embed(n, dim)
    es = enumerate_valid_e(phi_n, cap)
    pairs = []
    for e in es:
        d = pow(e, -1, phi_n)
        e_s = injective_embed(e, dim)
        d_s = injective_embed(d, dim)
        hash_s = content_s + e_s + d_s
        pairs.append((e, d, hash_s))
    return n, phi_n, content_s, pairs


def min_pairwise_distance(vectors, exclude_swaps=None):
    """Smallest Euclidean distance between any two DISTINCT vectors.
    If exclude_swaps is given (list of (e,d) tuples matching vectors by
    index), pairs that are just (e,d)/(d,e) role-swaps of the SAME
    relationship are skipped — they trivially collide because
    Content+e_s+d_s is symmetric under swapping e and d (addition
    commutes), which is not a genuine different-key-pair collision."""
    best = float('inf')
    best_idx = None
    n = len(vectors)
    for i in range(n):
        for j in range(i + 1, n):
            if exclude_swaps is not None:
                ei, di = exclude_swaps[i]
                ej, dj = exclude_swaps[j]
                if ei == dj and di == ej:
                    continue
            d = float(np.linalg.norm(vectors[i] - vectors[j]))
            if d < best:
                best = d
                best_idx = (i, j)
    return best, best_idx


def run_demo(dim: int = 16, cap: int = 400, n_control_trials: int = 20, seed: int = 20260717):
    rng = random.Random(seed)

    p, q = 61, 53
    print("=" * 74)
    print("  HASH COLLISION DEMO v2 — injective embedding, same content,")
    print("  many key pairs: does Hash_s ever genuinely collide?")
    print("=" * 74)
    print()
    n, phi_n, content_s, pairs = hash_vectors_for_n(p, q, dim, cap)
    print(f"  n = p*q = {p}*{q} = {n},  phi(n) = {phi_n}")
    print(f"  Valid (e,d) pairs found for e in [3,{cap}): {len(pairs)}")
    print()

    true_vectors = [hs for (_e, _d, hs) in pairs]
    ed_list = [(e, d) for (e, d, _hs) in pairs]

    true_min_all, idx_all = min_pairwise_distance(true_vectors)
    e1, d1 = ed_list[idx_all[0]]
    e2, d2 = ed_list[idx_all[1]]
    print(f"  Minimum pairwise Hash_s distance (INCLUDING e/d swaps): {true_min_all:.6f}")
    print(f"    between (e={e1},d={d1}) and (e={e2},d={d2})"
          + ("  <- trivial e/d swap, same relationship" if e1 == d2 and d1 == e2 else ""))
    print()

    true_min, idx = min_pairwise_distance(true_vectors, exclude_swaps=ed_list)
    e1, d1 = ed_list[idx[0]]
    e2, d2 = ed_list[idx[1]]
    print(f"  Minimum pairwise Hash_s distance (EXCLUDING trivial swaps): {true_min:.6f}")
    print(f"    between (e={e1},d={d1}) and (e={e2},d={d2})  <- genuinely different key relationships")
    print()

    n_points = len(pairs)
    control_mins = []
    for _trial in range(n_control_trials):
        rand_ints_e = [rng.randrange(3, 10 ** 6) for _ in range(n_points)]
        rand_ints_d = [rng.randrange(3, 10 ** 6) for _ in range(n_points)]
        rand_vecs = [content_s + injective_embed(e, dim) + injective_embed(d, dim)
                     for e, d in zip(rand_ints_e, rand_ints_d)]
        cmin, _ = min_pairwise_distance(rand_vecs)
        control_mins.append(cmin)

    control_mean = float(np.mean(control_mins))
    control_std = float(np.std(control_mins))
    print(f"  Control (unrelated random (e,d)-shaped points, same N={n_points}, {n_control_trials} trials):")
    print(f"    mean min-distance = {control_mean:.3f}   std = {control_std:.3f}")
    print(f"    range: [{min(control_mins):.3f}, {max(control_mins):.3f}]")
    print()

    z = (true_min - control_mean) / control_std if control_std > 0 else 0.0
    print(f"  Real (non-swap) min-distance vs control distribution: z = {z:.3f}")
    print()

    if control_std == 0 and true_min == control_mean:
        verdict = "STILL DEGENERATE — control std is 0, the embedding is still not resolving distinct points"
        confidence = "OPEN"
    elif abs(z) > 2.0 and true_min < control_mean:
        verdict = "SIGNAL — real distinct (e,d) pairs cluster measurably closer in Hash_s than random points do"
        confidence = "CONJECTURE"
    else:
        verdict = "AT CHANCE — with a properly injective embedding, real (e,d)-pair Hash_s vectors are no closer than random points; no genuine collision found"
        confidence = "OPEN"
    print(f"  VERDICT: {verdict}")
    print(f"  CONFIDENCE: {confidence}")
    print("=" * 74)

    return {
        'n': n, 'phi_n': phi_n, 'n_pairs': len(pairs),
        'true_min_distance_excl_swaps': true_min, 'control_mean': control_mean,
        'control_std': control_std, 'z_score': z, 'verdict': verdict, 'confidence': confidence,
    }


if __name__ == "__main__":
    run_demo()
