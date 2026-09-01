# The zero-divisor locus is the equatorial geodesic of the sedenion

**Date:** 2026-09-01
**Tier:** `[THEORETICAL — geometric picture]` + `[ESTABLISHED — exact topology, Moreno 1998]`
**Engine:** `ValaQuenta/modules/emerger/` -- the `{8:8}` bracket's
`on_zd_equator` test is this locus; `emerge()` reports it in firing order.
**Companion:** `hypercomplex_laplacian.py` ("ZD pairs are the NODAL LINES of L_w — the
Chladni figures of the T32 algebra"). This note gives the locus those nodal lines fill.

## Statement

**Spin Telperion** — the prime axis / the "what-cannot-be" direction, one imaginary
meridian of 𝕊 — about `e₀` (the real axis, 0_RB). It sweeps the **imaginary unit
sphere `S¹⁴`**.

The **equator** of that sweep — the locus where the forward octonion half and the
backward octonion half carry equal norm, `|a| = |b|` — is the **fixed set of the
`J_red ↔ J_blue` involution** (Telperion ↔ Laurelin, forward ↔ backward, the ⊕8
hemisphere-swap `x ↦ e₈ x̄ e₈⁻¹`). Multiplication degenerates exactly there.

**That balance equator is the zero-divisor locus.**

## Why

- Every zero divisor of 𝕊 has `Re(x) = 0` (standard) → the ZD locus lies on `S¹⁴`,
  never at the poles `±e₀`.
- The basis ZD pairs `(eᵢ ± eⱼ)`, `i ∈ 1..7`, `j ∈ 9..15`, organised by the Fano /
  box-kite / `PSL(2,7)` structure, are norm-balanced: `|first half| = |second half|`.
- Norm-balance + purely-imaginary = the fixed set of the involution that exchanges the
  two octonion halves. That involution is the algebraic form of the Two-Trees mirror.

## Same object, four names

| name | context |
|---|---|
| ZD locus / L_w nodal lines | sedenion algebra (`hypercomplex_laplacian.py`) |
| **σ = ½** — the critical line | `\|ξ(s)\| = \|ξ(1−s)\|`, amplitude-balanced reflection (RHP §6.3.1) |
| the **Mingling** — equal tree brightness | `n ~ e²` (generational-lineage) |
| the **Cymatic Nodal Line** | Chladni node: zero displacement AND zero net power flux |

All are the fixed set of the forward↔backward mirror.

## Consequence for factoring

- **primes** sit near the spin axis (the poles) — irreducible = on the axis, never
  swept into the equatorial collapse.
- **composites** are swept off-axis toward the equator.
- a semiprime `N = pq` is where a spun-`p` meridian crosses a spun-`q` meridian. If
  the crossing lands **on** the equator, `pq` hits a zero divisor. **RSA keeps its
  crossing off the equator** — generic merit-~1 primes, no ZD-locus alignment
  (`fermat_sedenion_test.py`'s locality test is asking exactly whether the Fermat
  coordinates `a = (p+q)/2`, `b = (q−p)/2` land on the equator).

## Honest tiering

"Equatorial **geodesic**" is the picture, not a literal great subsphere. A round
`S¹³` (the naive equator `{Re a = 0, Re b = 0, |a| = |b|}` inside `S¹⁵`) is
12-dimensional; the true ZD locus is larger.

**Moreno (1998), "The zero divisors of the Cayley–Dickson algebras over the real
numbers," Bol. Soc. Mat. Mexicana (3) 4:** the unit zero-divisor set of 𝕊 is
homeomorphic to the compact exceptional Lie group **G₂** (dimension 14).

So the defensible statement is: the ZD locus is the **balance equator** — the
totally-degenerate fixed set of the hemisphere-swap involution — and it carries
**G₂'s shape**, not a sphere's. "Geodesic" is right in spirit (multiplication's
acceleration vanishes there, the way a geodesic is where curvature-driven
acceleration vanishes); "great circle" is not literal.
