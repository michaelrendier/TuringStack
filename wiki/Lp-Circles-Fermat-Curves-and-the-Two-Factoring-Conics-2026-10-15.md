# The seventh circle (ℓ_p), the Fermat curves, and the two factoring conics

**Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
**ORCID:** https://orcid.org/0009-0007-7239-6760
**Date:** 2026-10-15
**Disclosure posture:** White hat. Scope: classical number theory and classical norm geometry (Euler, Fermat, Gołąb) — it records which conic each classical method lives on and what changes when the norm changes.
**Nature of this document:** a white paper on one organising fact, with every statement checked by code.
**Tier:** `[ESTABLISHED:CALCULATED]` for the number theory and norm geometry; the application to word-factoring is `[OPEN]` and stated as a test plan.
**Engine:** `GenerationalLineage/engine/toolsets/circle.py` (`lp_circle`, `pi_p`, `classify_sl2`) · scratch: `p10_seventh_circle_factoring.py`.

---

## The one fact

A factorisation N = p·q is a statement about a **conic**, and which conic decides which classical method applies:

| conic (Cayley–Klein type) | equation | method | applies to N = p·q when |
|---|---|---|---|
| circle (elliptic, ε = +1) | x² + y² = N | Euler: two representations N = a² + b² = c² + d² give the factor gcd(N, ad − bc) | both p, q ≡ 1 (mod 4) |
| hyperbola (hyperbolic, ε = −1) | a² − b² = N | Fermat: p = a − b, q = a + b | always (odd N) |
| lines (parabolic, ε = 0) | x² = N | a perfect square | p = q |

Checked: for every product of two distinct odd primes below 200 (990 products), Euler's method has two sum-of-squares representations **exactly when both primes are ≡ 1 mod 4** (210 of 210 pairs) and **never otherwise** (0 of 780). N = 65, 221, 1073, 3233, 11413 factor by Euler to (5,13), (13,17), (29,37), (53,61), (101,113) and by Fermat to the same pairs. Products with a prime ≡ 3 (mod 4), including every Blum integer, are invisible to the circle and visible to the hyperbola.

The imaginary circle x² + y² = −N and the hyperbola are one object: replacing y by iy turns a² + (ib)² into a² − b². The circle of radius √N has area πN; its imaginary-second-axis section is the hyperbola with sector area (N/2)φ and no π.

## The seventh circle

The ℓ_p unit circle |x|^p + |y|^p = 1 changes the **norm** instead of the drawing. Its own π_p = C/d: π₂ = π (the minimum), π₁ = π_∞ = 4, and **π_p = π_q whenever 1/p + 1/q = 1** (Gołąb 1932; Adler–Tanton 2000), verified to 1e-13 and tabulated:

| p | q | π_p | area_p | area_q |
|---|---|---|---|---|
| 1.25 | 5 | 3.498457 | 2.42714 | 3.80060 |
| 1.5 | 3 | 3.259768 | 2.73785 | 3.53328 |
| 4 | 4/3 | 3.396935 | 3.70815 | 2.54164 |

Duality preserves circumference ÷ diameter and not area.

**For integer p the ℓ_p circle is the Fermat curve x^p + y^p = z^p.** Integer points with z ≤ 300: p = 2 → 209 (the Pythagorean triples); p = 3, 4, 5 → 0 (Fermat's Last Theorem, Wiles 1995). The circle is the only integer-exponent norm circle with a lattice of rational points — which is why the two-conic table above is the whole story for N = pq, and why the "forbidden Fermat zone" 0 < σ < ½ in the Σ_RB coupling and the p > 2 norm circles are the same kind of emptiness.

## The first-line test

`classify_sl2(a, b, c, d)` returns elliptic / parabolic / hyperbolic from |trace| below / equal to / above 2 for a unit-determinant 2×2; it is the cheap test of which conic a rotation-like operator lives on.

## The English-word side — OPEN, as a test plan

The word-factoring work reads a word through a vector and a distance. The norm fixes the shape of the unit ball and therefore which neighbours are nearest: ℓ₁ (taxicab), ℓ₂, ℓ_∞ (Chebyshev) and the dual pairs (p, q) are exactly the choices. The testable proposals, none yet run: (1) for the WordNet box-kite vectors, measure how the nearest-neighbour sets of a word change across p ∈ {1, 4/3, 2, 4, ∞}; (2) test whether the dual pair (p, q) gives the same circumference-to-diameter ratio but a different neighbour set; (3) check whether the elliptic/hyperbolic split above has an analogue in how a word's two factors (its context and its content) sit as a sum or a difference of squares. No result is claimed.

## Citations

Gołąb, S. (1932), *Trav. Acad. Mines Cracovie* 6, 1–79. · Adler, C. L., Tanton, J. (2000), *College Math. J.* 31(2), 102–106. · Euler's method for factoring by two sums of squares (Euler, 1745–47, letters to Goldbach; see any text on classical factoring) · Fermat's difference-of-squares method (Fermat, 1643 letter to Mersenne) · Wiles, A. (1995), *Ann. Math.* 141, 443–551. · Klein, F. (1871) and Yaglom, I. M. (1979) for the Cayley–Klein triple. None was downloaded for this page; check against the sources before a paper.
