#!/usr/bin/env python3
"""
sha1_zero_divisor_demo.py — the RSA demo's methodology, reframed onto SHA-1.

UDEO_RSA_DEMO.py's discipline: given only public information, does a
zero-divisor/geometric mechanism single out the true hidden value against
a control population of equally-plausible wrong ones, scored by percentile
rank, verified on an independent sample, checked for artifact-ness? Every
RSA method that got this treatment came back at chance except one identity
unrelated to sedenions (see udeo_crypto/UDEO_RSA_DEMO.py).

This file applies the SAME discipline to SHA-1 instead of RSA, per Cody's
direction: "reframe the goal to SHA-1 not RSA."

THE MECHANISM UNDER TEST (already coded in udeo_poc.py, reused unchanged
here — not reinvented): sha1_message_differential_t32() computes whether
a message-block differential delta_m = m1 XOR m2 has a "zero-divisor
event" (two consecutive T32/GF(2) differential words whose product is
zero). paper.tex's Proposition (SHAttered collision structure) frames a
real collision's differential as living in the T32 ZD locus. This file
asks the honest, scored question that neither udeo_poc.py nor paper.tex
actually ran: does having a ZD event PREDICT that two message blocks
truncated-SHA1-collide, at a rate better than a random non-colliding
pair of blocks also showing one?

TOY SCALE, SAME PHILOSOPHY AS THE RSA DEMO'S TOY KEYS:
Full SHA-1 (160-bit output) collisions are computationally out of reach
here (that's the whole reason SHAttered took 9.2e18 evaluations). Toy RSA
used small real primes instead of RSA-2048; this uses the REAL, FULL
80-round SHA-1 compression function (single block, no shortcuts) but
truncates its output to a small bit count so genuine collisions are
findable by brute-force birthday search on a phone in seconds. The
compression math is exactly SHA-1's; only the output length is toy-scale,
same spirit as small p,q instead of 1024-bit primes.

Author:  Claude, at Cody's direction — 2026-07-17
White Hat. Same responsible-disclosure discipline as the rest of TuringStack.
"""

import struct
import random
from typing import List, Tuple

from udeo_poc import CayleyDickson, sha1_message_differential_t32

SHA1_IV = (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0)


def _rotl(x: int, n: int) -> int:
    return ((x << n) | (x >> (32 - n))) & 0xFFFFFFFF


def sha1_compress(block: bytes, H: Tuple[int, int, int, int, int] = SHA1_IV) -> List[int]:
    """
    Real, unabridged single-block SHA-1 compression function (all 80
    rounds, real round constants). Not a simplification — this is the
    actual algorithm, applied to exactly one 64-byte block with no
    padding logic (the block IS the input, matching sha1_message_differential_t32's
    own raw-block interface and paper.tex's 'message blocks M, M'' framing).
    """
    assert len(block) == 64
    w = list(struct.unpack('>16I', block))
    for t in range(16, 80):
        w.append(_rotl(w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16], 1))

    a, b, c, d, e = H
    for t in range(80):
        if t < 20:
            f = (b & c) | ((~b & 0xFFFFFFFF) & d)
            k = 0x5A827999
        elif t < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif t < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (_rotl(a, 5) + f + e + k + w[t]) & 0xFFFFFFFF
        e, d, c, b, a = d, c, _rotl(b, 30), a, temp

    return [(H[0]+a) & 0xFFFFFFFF, (H[1]+b) & 0xFFFFFFFF, (H[2]+c) & 0xFFFFFFFF,
            (H[3]+d) & 0xFFFFFFFF, (H[4]+e) & 0xFFFFFFFF]


def sha1_compress_trace(block: bytes, H: Tuple[int, int, int, int, int] = SHA1_IV) -> List[int]:
    """
    Same computation as sha1_compress(), but returns the 'a' register's
    value after EVERY round (80 values) instead of only the final state.
    'a' is the only register that receives genuinely new information each
    round (b,c,d,e just shift/rotate the previous round's a,b,c) so it is
    the natural single trace to diff between two messages.

    THE REAL ROADMAP, per Cody's direction: SHA-1's own round function
    already alternates between non-linear and linear rounds — Ch (t<20,
    AND-based, non-linear), Parity (20<=t<40, XOR-only, linear), Maj
    (40<=t<60, AND-based, non-linear), Parity (60<=t<80, linear) — see
    udeo_poc.py's own round_xors comments ('non-linear (AND)' / 'fully
    linear in T32'). Reading non-linear=red, linear=blue gives a red/blue
    alternation that is SHA-1's actual mechanism, not an imported tower
    parity. This is the signpost sequence tested below.
    """
    assert len(block) == 64
    w = list(struct.unpack('>16I', block))
    for t in range(16, 80):
        w.append(_rotl(w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16], 1))

    a, b, c, d, e = H
    a_trace = []
    for t in range(80):
        if t < 20:
            f = (b & c) | ((~b & 0xFFFFFFFF) & d)
            k = 0x5A827999
        elif t < 40:
            f = b ^ c ^ d
            k = 0x6ED9EBA1
        elif t < 60:
            f = (b & c) | (b & d) | (c & d)
            k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d
            k = 0xCA62C1D6
        temp = (_rotl(a, 5) + f + e + k + w[t]) & 0xFFFFFFFF
        e, d, c, b, a = d, c, _rotl(b, 30), a, temp
        a_trace.append(a)
    return a_trace


def sha1_round_inverse(t: int, a2: int, b2: int, c2: int, d2: int, e2: int, w_t: int) -> Tuple[int, int, int, int, int]:
    """
    Exact inverse of one SHA-1 round: given the state AFTER round t
    (a2,b2,c2,d2,e2) and the message word w_t that round t used, recover
    the state BEFORE round t. 'Moving backward on the clock' — mod 2^32
    is a 2^32-hour clock, and the one non-trivial step here (recovering
    e) is genuine subtraction, not XOR/GF(2) negation.

    Forward round t was:
        temp = (rotl(a,5) + f(b,c,d) + e + k[t] + w[t]) mod 2^32
        (a',b',c',d',e') = (temp, a, rotl(b,30), c, d)

    So, given (a',b',c',d',e') = (a2,b2,c2,d2,e2):
        a = b2
        b = rotr(c2, 30)
        c = d2
        d = e2
        e = (a2 - rotl(a,5) - f(b,c,d) - k[t] - w_t) mod 2^32   <- the clock runs backward here
    """
    a = b2
    b = ((c2 >> 30) | (c2 << 2)) & 0xFFFFFFFF   # rotr(c2, 30)
    c = d2
    d = e2

    if t < 20:
        f = (b & c) | ((~b & 0xFFFFFFFF) & d)
        k = 0x5A827999
    elif t < 40:
        f = b ^ c ^ d
        k = 0x6ED9EBA1
    elif t < 60:
        f = (b & c) | (b & d) | (c & d)
        k = 0x8F1BBCDC
    else:
        f = b ^ c ^ d
        k = 0xCA62C1D6

    e = (a2 - _rotl(a, 5) - f - k - w_t) & 0xFFFFFFFF   # <-- the actual backward-clock step
    return (a, b, c, d, e)


def sha1_decompress_verify(block: bytes, H: Tuple[int, int, int, int, int] = SHA1_IV) -> bool:
    """
    Round-trip proof that the backward clock is exact: compress a REAL
    block forward to get the final state, then walk backward through all
    80 rounds using sha1_round_inverse() with the SAME real message
    words, and check we land exactly back on the starting IV. Same role
    as _verify_against_hashlib() — this must be exact, not toy-scale.
    """
    assert len(block) == 64
    w = list(struct.unpack('>16I', block))
    for t in range(16, 80):
        w.append(_rotl(w[t-3] ^ w[t-8] ^ w[t-14] ^ w[t-16], 1))

    # forward pass, keep every intermediate state
    a, b, c, d, e = H
    states = [(a, b, c, d, e)]
    for t in range(80):
        if t < 20:
            f = (b & c) | ((~b & 0xFFFFFFFF) & d); k = 0x5A827999
        elif t < 40:
            f = b ^ c ^ d; k = 0x6ED9EBA1
        elif t < 60:
            f = (b & c) | (b & d) | (c & d); k = 0x8F1BBCDC
        else:
            f = b ^ c ^ d; k = 0xCA62C1D6
        temp = (_rotl(a, 5) + f + e + k + w[t]) & 0xFFFFFFFF
        a, b, c, d, e = temp, a, _rotl(b, 30), c, d
        states.append((a, b, c, d, e))

    # backward pass from the final state, using the real w[t] at each step
    ba, bb, bc, bd, be = states[80]
    for t in range(79, -1, -1):
        ba, bb, bc, bd, be = sha1_round_inverse(t, ba, bb, bc, bd, be, w[t])

    return (ba, bb, bc, bd, be) == H


def round_type(t: int) -> str:
    """SHA-1's real function alternation, read as red (non-linear) / blue (linear)."""
    if t < 20:
        return 'red'    # Ch — AND-based, non-linear
    elif t < 40:
        return 'blue'   # Parity — XOR-only, linear
    elif t < 60:
        return 'red'    # Maj — AND-based, non-linear
    else:
        return 'blue'   # Parity — XOR-only, linear


def altitude_roadmap(m1: bytes, m2: bytes) -> List[int]:
    """
    Hamming weight of the 'a'-register differential at every round —
    distance from the fixed point (0 = registers agree exactly, the
    singularity; higher = farther uphill, more escape velocity) traced
    round by round through SHA-1's OWN real alternation, not a synthetic
    tower.
    """
    t1 = sha1_compress_trace(m1)
    t2 = sha1_compress_trace(m2)
    return [bin(a ^ b).count('1') for a, b in zip(t1, t2)]


def run_roadmap_demo(bits: int = 20, n_collisions: int = 25, n_controls: int = 200,
                      seed: int = 20260717):
    rng = random.Random(seed + 1)  # distinct stream from the exact-ZD demo

    print("=" * 74)
    print("  SHA-1 ROADMAP DEMO — altitude (Hamming weight of the 'a'-register")
    print("  differential) traced round-by-round through SHA-1's real red/blue")
    print("  (non-linear/linear) alternation, true collisions vs random pairs")
    print("=" * 74)
    print()

    print(f"  Finding {n_collisions} independent real collisions ({bits}-bit truncated digest)...")
    collision_pairs = []
    for _ in range(n_collisions):
        m1, m2, _tries = find_real_collision(bits, rng)
        collision_pairs.append((m1, m2))

    print(f"  Building {n_controls} random NON-colliding control pairs...")
    control_pairs = []
    while len(control_pairs) < n_controls:
        m1, m2 = random_block(rng), random_block(rng)
        if truncated_digest(m1, bits) == truncated_digest(m2, bits):
            continue
        control_pairs.append((m1, m2))

    def block_means(pairs):
        """Mean altitude within each of the 4 real SHA-1 function blocks
        (Ch/Parity/Maj/Parity = rounds 0-19/20-39/40-59/60-79), averaged
        over all pairs in the group."""
        sums = [0.0, 0.0, 0.0, 0.0]
        for m1, m2 in pairs:
            road = altitude_roadmap(m1, m2)
            sums[0] += sum(road[0:20]) / 20
            sums[1] += sum(road[20:40]) / 20
            sums[2] += sum(road[40:60]) / 20
            sums[3] += sum(road[60:80]) / 20
        n = len(pairs)
        return [s / n for s in sums]

    true_means = block_means(collision_pairs)
    ctrl_means = block_means(control_pairs)

    labels = ['Ch  (red, rounds  0-19)', 'Parity (blue, rounds 20-39)',
              'Maj (red, rounds 40-59)', 'Parity (blue, rounds 60-79)']

    print()
    print("  RESULTS (raw mean altitude per block, out of 32 max):")
    print(f"  {'Block':30s} {'true collisions':>16s} {'random pairs':>16s} {'diff':>8s}")
    for lbl, tm, cm in zip(labels, true_means, ctrl_means):
        print(f"  {lbl:30s} {tm:16.3f} {cm:16.3f} {tm-cm:8.3f}")
    print()

    max_gap = max(abs(t - c) for t, c in zip(true_means, ctrl_means))
    print(f"  Largest block-mean gap (true vs random): {max_gap:.3f} altitude-bits (out of 32)")
    if max_gap > 3.0:
        verdict = "POSSIBLE SIGNAL — a real block shows a meaningful gap, worth verification-scaling"
        confidence = "CONJECTURE"
    else:
        verdict = "AT CHANCE — no block shows a gap beyond sampling noise; the real red/blue alternation does not distinguish true collisions from random pairs at this sample size"
        confidence = "OPEN"
    print(f"  VERDICT: {verdict}")
    print(f"  CONFIDENCE: {confidence}")
    print("=" * 74)

    return {'true_means': true_means, 'ctrl_means': ctrl_means, 'max_gap': max_gap,
            'verdict': verdict, 'confidence': confidence}


def _verify_against_hashlib():
    """Sanity check: our compression function matches hashlib.sha1 on a
    properly padded single-block message. Not toy-scale — this must be exact."""
    import hashlib
    msg = b"UDEO"
    padded = msg + b'\x80' + b'\x00' * (64 - len(msg) - 1 - 8) + struct.pack('>Q', len(msg) * 8)
    assert len(padded) == 64
    ours = b''.join(struct.pack('>I', w) for w in sha1_compress(padded))
    theirs = hashlib.sha1(msg).digest()
    assert ours == theirs, f"MISMATCH: {ours.hex()} vs {theirs.hex()}"
    return True


def truncated_digest(block: bytes, bits: int) -> int:
    full = sha1_compress(block)
    full_int = 0
    for w in full:
        full_int = (full_int << 32) | w
    return full_int >> (160 - bits)


def random_block(rng: random.Random) -> bytes:
    return bytes(rng.getrandbits(8) for _ in range(64))


def find_real_collision(bits: int, rng: random.Random, max_tries: int = 2_000_000):
    """Birthday-search for a genuine truncated-SHA1 collision between two
    single-block messages, using the REAL compression function. Returns
    (m1, m2) with m1 != m2 and truncated_digest(m1)==truncated_digest(m2)."""
    seen = {}
    for i in range(max_tries):
        m = random_block(rng)
        d = truncated_digest(m, bits)
        if d in seen and seen[d] != m:
            return seen[d], m, i + 1
        seen[d] = m
    raise RuntimeError(f"no collision found in {max_tries} tries at {bits} bits")


def run_demo(bits: int = 20, n_collisions: int = 25, n_controls: int = 200, seed: int = 20260717):
    rng = random.Random(seed)
    cd = CayleyDickson(32, 'gf2')

    print("=" * 74)
    print("  SHA-1 ZERO-DIVISOR DEMO — RSA demo's control-scoring methodology,")
    print("  reframed onto SHA-1 (Cody's direction, 2026-07-17)")
    print("=" * 74)
    print()
    print("  Sanity check: our sha1_compress() vs hashlib.sha1 on a real padded message...")
    _verify_against_hashlib()
    print("  MATCH — compression function is exact, not approximated.")
    print()
    print(f"  Truncated digest width: {bits} bits (full SHA-1 is 160 — toy-scale for")
    print(f"  brute-force tractability, same role as small p,q in the RSA demo's toy keys)")
    print()

    # ---- Find n_collisions REAL, independently-found collisions ----
    print(f"  Finding {n_collisions} independent real collisions by birthday search...")
    collisions = []
    total_tries = 0
    for i in range(n_collisions):
        m1, m2, tries = find_real_collision(bits, rng)
        total_tries += tries
        result = sha1_message_differential_t32(m1, m2, cd)
        collisions.append(result)
    print(f"  Done. Mean tries per collision: {total_tries / n_collisions:.0f} "
          f"(birthday expectation ~{int(1.25 * (2 ** (bits/2)))})")
    print()

    hit_rate_true = sum(1 for r in collisions if r['has_zd_event']) / n_collisions
    mean_events_true = sum(len(r['zero_div_events']) for r in collisions) / n_collisions

    # ---- Control population: random NON-colliding block pairs ----
    print(f"  Building control population: {n_controls} random NON-colliding block pairs...")
    controls = []
    while len(controls) < n_controls:
        m1 = random_block(rng)
        m2 = random_block(rng)
        if truncated_digest(m1, bits) == truncated_digest(m2, bits):
            continue  # accidental collision, exclude — controls must be genuine non-collisions
        controls.append(sha1_message_differential_t32(m1, m2, cd))

    hit_rate_control = sum(1 for r in controls if r['has_zd_event']) / n_controls
    mean_events_control = sum(len(r['zero_div_events']) for r in controls) / n_controls

    print()
    print("  RESULTS (raw, before interpretation):")
    print(f"    True collisions   (n={n_collisions:3d}): ZD-event rate = {hit_rate_true:.3f}   "
          f"mean events/pair = {mean_events_true:.3f}")
    print(f"    Random non-collisions (n={n_controls:3d}): ZD-event rate = {hit_rate_control:.3f}   "
          f"mean events/pair = {mean_events_control:.3f}")
    print()

    ratio = (hit_rate_true / hit_rate_control) if hit_rate_control > 0 else \
            (float('inf') if hit_rate_true > 0 else 1.0)
    print(f"  Enrichment ratio (true-collision rate / random-pair rate): {ratio:.3f}")
    print()

    if hit_rate_control > 0.9 or hit_rate_true - hit_rate_control < 0.05:
        verdict = ("AT CHANCE — has_zd_event fires on almost every random pair too; "
                   "it carries no information distinguishing real collisions from noise")
        confidence = "OPEN"
    elif ratio > 2.0 and hit_rate_true > hit_rate_control:
        verdict = "SIGNAL — real collisions show ZD events at a meaningfully higher rate than random pairs"
        confidence = "CONJECTURE"
    else:
        verdict = "WEAK/INCONCLUSIVE at this sample size"
        confidence = "OPEN"

    print(f"  VERDICT: {verdict}")
    print(f"  CONFIDENCE: {confidence}")
    print("=" * 74)

    return {
        'bits': bits, 'n_collisions': n_collisions, 'n_controls': n_controls,
        'hit_rate_true': hit_rate_true, 'hit_rate_control': hit_rate_control,
        'mean_events_true': mean_events_true, 'mean_events_control': mean_events_control,
        'ratio': ratio, 'verdict': verdict, 'confidence': confidence,
    }


if __name__ == "__main__":
    run_demo()
    print()
    run_roadmap_demo()
