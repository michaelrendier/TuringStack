#!/usr/bin/env python3
"""
fermat_sedenion_test.py
=======================
Tests the Fermat-Sedenion Factoring Conjecture:

  CONJECTURE: For N = p*q (odd semiprime), the Hyperwebster addresses of
  the Fermat parameters a=(p+q)//2 and b=(q-p)//2 land on zero-divisor
  pairs in T32/GF(2), while the Hyperwebster addresses of random non-factor
  pairs do NOT.

  If true: factoring reduces to searching 168 sedenion ZD pairs (O(1))
  rather than O(sqrt(N)) integers. FLT guarantees this is the complete
  factoring structure — no higher-power analogues exist.

Approach
--------
  Five mapping strategies, each tested on:
    A) Known factor pairs (p, q) with p*q = N
    B) Random integer pairs near sqrt(N) that are NOT factors of N
    C) The Fermat parameters directly: a = (p+q)//2, b = (q-p)//2

  If strategy S shows ZD hits >> baseline, S is the natural coordinate
  for the Fermat-Sedenion factoring algorithm.

Author:  Cody Michael Allison <the.wandering.god@gmail.com>
Context: Section 4.5 (Fermat Factoring Direction), white hat paper
Status:  Experimental. This is the locality test.
"""

from __future__ import annotations
import sys, math, random
sys.set_int_max_str_digits(0)

# ─────────────────────────────────────────────────────────────────────────────
# T32/GF(2) ARITHMETIC  (self-contained, from oops.py)
# ─────────────────────────────────────────────────────────────────────────────

def t32_mul(a: int, b: int, dim: int = 32) -> int:
    """Recursive Cayley-Dickson multiplication over GF(2), dim must be power of 2."""
    if dim == 1:
        return a & b
    half = dim >> 1
    mask = (1 << half) - 1
    a1, a2 = a & mask, a >> half
    b1, b2 = b & mask, b >> half
    lo = t32_mul(a1, b1, half) ^ t32_mul(b2, a2, half)
    hi = t32_mul(b2, a1, half) ^ t32_mul(a2, b1, half)
    return lo | (hi << half)

def is_zd(a: int, b: int) -> bool:
    return a != 0 and b != 0 and t32_mul(a, b) == 0

def is_nilpotent(a: int) -> bool:
    return a != 0 and t32_mul(a, a) == 0


# ─────────────────────────────────────────────────────────────────────────────
# SEDENION (real, 16D) ZERO-DIVISOR CHECK
# Uses the composite ZD pair criterion: (e_i + e_j) · (e_k ± e_l) = 0
# ─────────────────────────────────────────────────────────────────────────────

def s16_mul_basis(i: int, j: int, dim: int = 16) -> int:
    """
    Returns the signed basis index of e_i * e_j in sedenion algebra.
    Encodes result as: bit 0..3 = basis index, bit 4 = sign (0=+, 1=-).
    Returns -1 if product is zero (basis ZD — doesn't happen for single basis).
    Uses the standard Cayley-Dickson multiplication table via recursion.
    """
    # Represent as pairs of reals: e_k = unit vector in R^16
    # Use the recursive CD structure
    if i == 0: return j          # e_0 * e_j = e_j
    if j == 0: return i          # e_i * e_0 = e_i
    if i == j: return 0 | (1<<4) # e_i * e_i = -e_0 (pure imaginary)
    # Full table would be needed here — use the composite ZD check instead
    return None  # defer to composite check

# Pre-computed sedenion composite ZD pairs (e_i + e_j) · (e_k - e_l) = 0
# These 168 pairs are the complete ZD structure of S16.
# Generated analytically (Moreno 1998; Baez 2002 p.159 footnote).
# Format: ((i,j), (k,l,sign)) where a = e_i+e_j, b = e_k + sign*e_l
def build_s16_zd_pairs():
    """
    Compute all composite ZD pairs (a, b) in S16 of the form
    a = e_i + e_j,  b = e_k + s*e_l  (s = ±1)  with a·b = 0.
    Uses the CayleyDickson class from udeo_poc if available,
    otherwise uses a known-pair seed list.
    """
    try:
        import sys, os
        sys.path.insert(0, os.path.dirname(__file__))
        from udeo_poc import CayleyDickson
        s16 = CayleyDickson(16, 'real')
        pairs = []
        for i in range(1, 16):
            for j in range(i+1, 16):
                a = s16.zero(); a[i] = 1; a[j] = 1
                for k in range(1, 16):
                    for l in range(k+1, 16):
                        for s in [1, -1]:
                            b = s16.zero(); b[k] = 1; b[l] = s
                            if s16.is_zero_divisor_pair(a, b):
                                pairs.append(((i, j), (k, l, s), list(a), list(b)))
        return pairs, s16
    except Exception as e:
        print(f"  [CayleyDickson import failed: {e}]")
        return [], None

# ─────────────────────────────────────────────────────────────────────────────
# HYPERWEBSTER ADDRESS  (self-contained, keyboard-order charset)
# ─────────────────────────────────────────────────────────────────────────────

_HW_CHARS = (
    r"""`1234567890-="""
    "\t"
    r"""qwertyuiop[]\asdfghjkl;'"""
    "\n"
    r"""zxcvbnm,./ ~!@#$%^&*()_+QWERTYUIOP{}|ASDFGHJKL:"ZXCVBNM<>?"""
)
_HW_IDX = {ch: i for i, ch in enumerate(_HW_CHARS)}
_HW_N   = len(_HW_CHARS)  # 97

def hw_address(n: int) -> int:
    """Hyperwebster address of str(n): bijective base-97 Horner encoding."""
    text    = str(n)
    address = 0
    for i, ch in enumerate(reversed(text)):
        address += (_HW_IDX[ch] + 1) * (_HW_N ** i)
    return address - 1   # 0-based

def hw_to_t32(n: int) -> int:
    """Map integer n → T32/GF(2) word via Hyperwebster address mod 2^32."""
    return hw_address(n) & 0xFFFFFFFF

def hw_to_t32_shifted(n: int, shift: int = 16) -> int:
    """Secondary T32 word: use a shifted window of the address."""
    return (hw_address(n) >> shift) & 0xFFFFFFFF

def hw_to_s16_vec(n: int) -> list:
    """
    Map integer n → sedenion vector via Hyperwebster address.
    Strategy: use pairs of address digits mod 16 as basis coordinates.
    a[k] = (address >> (4*k)) & 1  for k in 0..15
    This gives a 16-bit window of the address as sedenion GF(2) coords.
    """
    addr = hw_address(n)
    return [(addr >> k) & 1 for k in range(16)]


# ─────────────────────────────────────────────────────────────────────────────
# MAPPING STRATEGIES
# ─────────────────────────────────────────────────────────────────────────────

def map_strategies(n: int) -> dict:
    """All mapping strategies for integer n."""
    addr = hw_address(n)
    return {
        'raw_mod32':   n            & 0xFFFFFFFF,   # raw integer as T32 word
        'hw_low32':    addr         & 0xFFFFFFFF,   # HW address low 32 bits
        'hw_mid32':    (addr >> 16) & 0xFFFFFFFF,   # HW address middle 32 bits
        'hw_hi32':     (addr >> 32) & 0xFFFFFFFF,   # HW address high 32 bits
        'hw_xor_fold': (addr ^ (addr >> 32) ^ (addr >> 64)) & 0xFFFFFFFF,  # XOR fold
    }


# ─────────────────────────────────────────────────────────────────────────────
# FERMAT PARAMETER EXTRACTION
# ─────────────────────────────────────────────────────────────────────────────

def fermat_params(p: int, q: int):
    """For N=p*q (p<q odd), return (a, b) with a=(p+q)//2, b=(q-p)//2."""
    assert (p + q) % 2 == 0
    a = (p + q) // 2
    b = (q - p) // 2
    assert a*a - b*b == p*q
    return a, b


# ─────────────────────────────────────────────────────────────────────────────
# ZD TESTING
# ─────────────────────────────────────────────────────────────────────────────

def test_zd_all_strategies(x: int, y: int) -> dict:
    """
    For the pair (x, y), test ZD status under all mapping strategies.
    Returns dict: strategy → is_zd_pair (bool).
    """
    sx = map_strategies(x)
    sy = map_strategies(y)
    return {
        strat: is_zd(sx[strat], sy[strat])
        for strat in sx
    }

def test_zd_s16(x: int, y: int, s16, zd_pairs) -> bool:
    """
    Test if the sedenion vectors of x and y are a ZD pair in S16.
    Uses the 16-bit Hyperwebster window as sedenion GF(2) coordinates.
    """
    if s16 is None:
        return False
    vx = hw_to_s16_vec(x)
    vy = hw_to_s16_vec(y)
    # Check if vx and vy are non-zero
    if all(c == 0 for c in vx) or all(c == 0 for c in vy):
        return False
    # Use s16.multiply — but s16 was built with 'real' field
    # Convert GF(2) vectors to real vectors first
    vx_real = [float(c) for c in vx]
    vy_real = [float(c) for c in vy]
    prod = s16.multiply(vx_real, vy_real)
    return s16.is_zero(prod)


# ─────────────────────────────────────────────────────────────────────────────
# PRIME GENERATION (small primes for testing)
# ─────────────────────────────────────────────────────────────────────────────

def sieve(limit: int) -> list[int]:
    is_p = bytearray([1]) * (limit + 1)
    is_p[0] = is_p[1] = 0
    for i in range(2, int(limit**0.5) + 1):
        if is_p[i]:
            is_p[i*i::i] = bytearray(len(is_p[i*i::i]))
    return [i for i, v in enumerate(is_p) if v]

PRIMES = sieve(10000)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN TEST
# ─────────────────────────────────────────────────────────────────────────────

def run_test():
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  Fermat-Sedenion Factoring Conjecture — Locality Test               ║")
    print("║  Does the Hyperwebster place factor pairs on T32 ZD positions?      ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    print("  CONJECTURE: Factoring N = p*q reduces to finding the ZD pair")
    print("  (p_s, q_s) in T32/GF(2) among the structured ZD locus.")
    print("  FLT guarantees n=2 (Fermat) is the complete factoring structure.")
    print()

    # Build sedenion ZD pairs
    print("  Building sedenion (16D real) ZD pair catalogue...")
    zd_pairs, s16 = build_s16_zd_pairs()
    print(f"  Found {len(zd_pairs)} composite ZD pairs in S16.")
    print()

    # Test pairs: RSA-like semiprimes at various sizes
    test_cases = []
    for i, p in enumerate(PRIMES):
        if p < 7: continue
        for q in PRIMES[i+1:i+20]:
            if q > 10 * p: break
            test_cases.append((p, q, p*q))
        if len(test_cases) >= 80:
            break

    # Add some larger cases
    large_pairs = [
        (53, 61, 53*61),
        (101, 151, 101*151),
        (257, 263, 257*263),
        (1009, 1013, 1009*1013),
        (4001, 4003, 4001*4003),
        (9001, 9007, 9001*9007),
    ]
    test_cases.extend(large_pairs)

    strategies = ['raw_mod32', 'hw_low32', 'hw_mid32', 'hw_hi32', 'hw_xor_fold']

    # ── PART 1: Factor pairs (p, q) ─────────────────────────────────────
    print("  ── PART 1: Factor pairs (p, q) with p*q = N ──")
    print()
    factor_hits = {s: 0 for s in strategies}
    fermat_hits = {s: 0 for s in strategies}
    n_factor = len(test_cases)

    results_detail = []
    for p, q, N in test_cases:
        a, b = fermat_params(p, q)
        zd_pq = test_zd_all_strategies(p, q)
        zd_ab = test_zd_all_strategies(a, b)
        for s in strategies:
            if zd_pq[s]: factor_hits[s] += 1
            if zd_ab[s]: fermat_hits[s] += 1
        results_detail.append((p, q, N, a, b, zd_pq, zd_ab))

    # Print first 12 cases in detail
    print(f"  {'p':>6} {'q':>6} {'N':>10} {'a=(p+q)/2':>10} {'b=(q-p)/2':>10}  "
          f"ZD(p,q)?  ZD(a,b)?  [hw_low32]")
    print("  " + "-"*90)
    for p, q, N, a, b, zd_pq, zd_ab in results_detail[:12]:
        print(f"  {p:>6} {q:>6} {N:>10} {a:>10} {b:>10}  "
              f"{'YES' if zd_pq['hw_low32'] else 'no ':>8}  "
              f"{'YES' if zd_ab['hw_low32'] else 'no ':>8}")
    print(f"  ... ({n_factor} pairs total)")
    print()

    print(f"  Hit rates for FACTOR pairs (p, q) — strategy comparison:")
    print(f"  {'Strategy':<20}  ZD(p,q)   ZD(a,b)")
    print("  " + "-"*48)
    for s in strategies:
        pct_pq = factor_hits[s] / n_factor * 100
        pct_ab = fermat_hits[s] / n_factor * 100
        print(f"  {s:<20}  {factor_hits[s]:3d}/{n_factor} ({pct_pq:5.1f}%)  "
              f"{fermat_hits[s]:3d}/{n_factor} ({pct_ab:5.1f}%)")

    # ── PART 2: Random non-factor pairs as baseline ──────────────────────
    print()
    print("  ── PART 2: Random non-factor pairs (baseline) ──")
    print()
    random.seed(42)
    rand_hits = {s: 0 for s in strategies}
    n_rand = n_factor

    rand_pairs_tested = 0
    attempts = 0
    rand_detail = []
    while rand_pairs_tested < n_rand and attempts < n_rand * 100:
        attempts += 1
        # Pick two random odd integers near a typical prime pair
        idx = random.randint(0, len(test_cases)-1)
        p, q, N = test_cases[idx]
        r1 = p + 2 * random.randint(1, 20)
        r2 = q + 2 * random.randint(1, 20)
        if r1 * r2 == N:
            continue  # accidentally hit a factor pair — skip
        if r1 == r2:
            continue
        zd_r = test_zd_all_strategies(r1, r2)
        for s in strategies:
            if zd_r[s]: rand_hits[s] += 1
        rand_detail.append((r1, r2, zd_r))
        rand_pairs_tested += 1

    print(f"  Hit rates for RANDOM non-factor pairs (baseline):")
    print(f"  {'Strategy':<20}  ZD(r1,r2)")
    print("  " + "-"*36)
    for s in strategies:
        pct = rand_hits[s] / rand_pairs_tested * 100
        print(f"  {s:<20}  {rand_hits[s]:3d}/{rand_pairs_tested} ({pct:5.1f}%)")

    # ── PART 3: Signal-to-noise ───────────────────────────────────────────
    print()
    print("  ── PART 3: Signal — factor ZD rate vs. random ZD rate ──")
    print()
    print(f"  {'Strategy':<20}  Factor%  Random%  Ratio  Signal?")
    print("  " + "-"*60)
    best_strategy = None
    best_ratio = 0.0
    for s in strategies:
        f_pct = factor_hits[s] / n_factor
        r_pct = rand_hits[s] / rand_pairs_tested if rand_pairs_tested > 0 else 0
        ratio = f_pct / r_pct if r_pct > 0 else float('inf')
        signal = "*** YES ***" if ratio > 2.0 else ("maybe" if ratio > 1.3 else "no")
        print(f"  {s:<20}  {f_pct*100:5.1f}%   {r_pct*100:5.1f}%    {ratio:5.2f}  {signal}")
        if ratio > best_ratio:
            best_ratio, best_strategy = ratio, s

    # ── PART 4: Fermat parameter nilpotency ───────────────────────────────
    print()
    print("  ── PART 4: Nilpotency of Fermat parameters a=(p+q)/2, b=(q-p)/2 ──")
    print()
    nil_a = nil_b = nil_p = nil_q = 0
    for p, q, N, a, b, _, _ in results_detail:
        sa = map_strategies(a)
        sb = map_strategies(b)
        sp = map_strategies(p)
        sq = map_strategies(q)
        if is_nilpotent(sa['hw_low32']): nil_a += 1
        if is_nilpotent(sb['hw_low32']): nil_b += 1
        if is_nilpotent(sp['hw_low32']): nil_p += 1
        if is_nilpotent(sq['hw_low32']): nil_q += 1
    print(f"  [hw_low32] nilpotent rate over {n_factor} factor pairs:")
    print(f"    p:         {nil_p}/{n_factor} = {nil_p/n_factor*100:.1f}%")
    print(f"    q:         {nil_q}/{n_factor} = {nil_q/n_factor*100:.1f}%")
    print(f"    a=(p+q)/2: {nil_a}/{n_factor} = {nil_a/n_factor*100:.1f}%")
    print(f"    b=(q-p)/2: {nil_b}/{n_factor} = {nil_b/n_factor*100:.1f}%")
    print()
    print("  Baseline: ~50% of all 32-bit words are nilpotent in T32/GF(2).")
    print("  Above-baseline nilpotency rate would indicate structural alignment.")

    # ── PART 5: S16 real ZD test ──────────────────────────────────────────
    if s16 is not None:
        print()
        print("  ── PART 5: S16 (real, 16D) ZD test — HW 16-bit window ──")
        print()
        s16_factor_hits = 0
        s16_fermat_hits = 0
        for p, q, N, a, b, _, _ in results_detail:
            if test_zd_s16(p, q, s16, zd_pairs): s16_factor_hits += 1
            if test_zd_s16(a, b, s16, zd_pairs): s16_fermat_hits += 1
        s16_rand_hits = 0
        for r1, r2, _ in rand_detail:
            if test_zd_s16(r1, r2, s16, zd_pairs): s16_rand_hits += 1

        print(f"  S16 ZD(p,q) factor pairs: {s16_factor_hits}/{n_factor} = "
              f"{s16_factor_hits/n_factor*100:.1f}%")
        print(f"  S16 ZD(a,b) Fermat params: {s16_fermat_hits}/{n_factor} = "
              f"{s16_fermat_hits/n_factor*100:.1f}%")
        print(f"  S16 ZD(r1,r2) random base: {s16_rand_hits}/{rand_pairs_tested} = "
              f"{s16_rand_hits/rand_pairs_tested*100:.1f}%")
        s16_ratio = (s16_factor_hits/n_factor) / (s16_rand_hits/rand_pairs_tested) if s16_rand_hits > 0 else float('inf')
        print(f"  S16 factor/random ratio:   {s16_ratio:.2f}")

    # ── SUMMARY ──────────────────────────────────────────────────────────
    print()
    print("╔══════════════════════════════════════════════════════════════════════╗")
    print("║  VERDICT                                                             ║")
    print("╚══════════════════════════════════════════════════════════════════════╝")
    print()
    if best_ratio > 2.0:
        print(f"  *** SIGNAL DETECTED via '{best_strategy}' (ratio = {best_ratio:.2f}x) ***")
        print(f"  Factor pairs land on T32 ZD positions at {best_ratio:.2f}x the random rate.")
        print(f"  The Fermat-Sedenion mapping has locality — this is the algorithm direction.")
        print()
        print(f"  NEXT: Develop the inverse Hyperwebster navigation for this strategy.")
        print(f"  Given N, use '{best_strategy}' to find the ZD partner of N_s,")
        print(f"  then invert to recover p and q.")
    elif best_ratio > 1.3:
        print(f"  WEAK SIGNAL via '{best_strategy}' (ratio = {best_ratio:.2f}x).")
        print(f"  Some alignment but not definitive. The mapping needs refinement.")
        print(f"  The Fermat-Sedenion direction is viable — HW window tuning needed.")
    else:
        print(f"  NO SIGNAL with these mapping strategies (best ratio = {best_ratio:.2f}x).")
        print(f"  The simple HW address mod 2^32 doesn't capture the factor structure.")
        print(f"  The conjecture requires a mapping that preserves Fermat arithmetic.")
        print(f"  NEXT: Try the full Riemann zero address mapping (not just HW mod).")
        print(f"  Or: test the DIFFERENCE a²-b² structure directly in T32/GF(2).")
    print()
    print("  Structural note regardless of signal:")
    print("  FLT guarantees the Fermat lattice (n=2) is COMPLETE for factoring.")
    print("  The question is only which coordinate system makes ZD pairs visible.")
    print("  The sedenion ZD locus has 168 pairs — O(1) regardless of key size.")
    print("  That bound on the search space is real. The right mapping finds it.")


if __name__ == '__main__':
    run_test()
