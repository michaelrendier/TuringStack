# RSA Key-Recovery Attempts — 2026-07-09

**Status:** Five candidate mechanisms tested against toy RSA keys. Four at chance.
One exact result requires a value that isn't public-key-only. One proven,
cryptographically-insignificant number-theory fact. No working attack on RSA is
claimed by this page — it documents what was tried and what the numbers showed,
per the repository's Scientific Integrity policy (failed predictions stay in the
record).

**Code:** `udeo_crypto/UDEO_RSA_DEMO.py` — run it directly, or see
`compare_all_methods()` for the full comparison.

**Method:** every mechanism below is given only the public key `(n, e)` at the
point it computes a candidate for `d`. The true `d` is used only afterward, to
score the candidate against a population of 200 random-but-valid wrong guesses
per key (a private exponent coprime to `φ(n)`, excluding the true `d`). The score
reported is a percentile rank: 50 means indistinguishable from chance; a number
consistently far from 50 across all keys would be a real signal.

**Toy keys used** (small enough to brute-force verify against):

| n | e | d | φ(n) |
|---|---|---|---|
| 143 | 7 | 103 | 120 |
| 253 | 7 | 63 | 220 |
| 77 | 7 | 43 | 60 |
| 3233 | 17 | 2753 | 3120 |
| 10403 | 7 | 8743 | 10200 |
| 8633 | 5 | 5069 | 8448 |

---

## Method 1 — Zero-Divisor Shadow (S¹⁶)

**Idea:** embed the public exponent `e` in the sedenion algebra. Left-multiplication
by `e_s` is a genuine linear operator; its smallest-singular-value direction is the
closest thing `e_s` has to an annihilator ("the shape of the hole it left behind"),
even when `e_s` isn't an exact zero-divisor. Test whether the true `d`'s embedding
aligns with that direction better than a random valid `d'` would.

**Result: mean percentile 46.91 — at chance.** None of the 6 toy keys landed `e`
on an exact zero-divisor (the 168 composite zero-divisor pairs in 𝕊 are a sparse,
rigid, discrete locus — verified separately across 303 real primes: minimum product
norm found was `0.9999999999999999`, i.e. essentially never near zero). The
"shadow" tested is the soft/near-singular direction, not a true kernel, and it
carries no detectable information about `d`.

## Method 2 — J2 Involution / T₂₅₆ Eigenspectrum

**Idea:** wiki/53 (T_256: Cryptographic Transparency) proposes `Ĥ_RB ↔ Ĥ_BR` as a
"whole coin" involution that becomes fully expressed at T_256. Read literally and
computationally: left- vs right-multiplication by `e_s` in the 256-dimensional
Cayley-Dickson algebra, `Δ = L_{e_s} - R_{e_s}`. Test whether `d`'s embedding
aligns with a dominant eigenvector of `Δ`.

**Result: mean percentile 56.77 — at chance.** Worth stating plainly: wiki/53's
own closing section is a formal-target checklist with every item unchecked
("prove or bound this claim," "state the complexity result"). There is no prior
code implementation of J2/T_256 anywhere in the repository. What was tested here
is a first, literal, necessarily provisional reading of an underspecified
theoretical note — not a validated mechanism, and it found nothing.

## Method 3 — Sedenion Spectral Relativity Geodesic

**Idea:** wiki/34 (Hypercomplex Spectral Relativity) frames zero-divisors as
metric singularities under a σ-face metric `g(σ)`. Map `e` and `d` to addresses
via the Horner prime hash (the same mechanism behind the one validated result in
this framework — see `tier8_sedenion.sedenion_self_organisation`), define
`g(σ)`, and test whether the geodesic distance from `e`'s address to `d`'s
address is a statistical outlier vs. random `d'`.

**Result: mean percentile 38.82 — at chance.** Caveat: `g(σ)` here reuses the
*shape* of wiki/34's metric applied to the hash-derived address, which lives in
`(0,1)` — not the same σ variable wiki/34 defines (`[½, ∞)`, a physical
mass/gravity scale). That reinterpretation is this test's choice, not something
wiki/34 states.

## Method 4 — Content + Public + Private = Hash

**Idea (Cody's equation):** `Content + Public + Private = Hash`, therefore
`Content + Public − Hash = 1/Private`. Built literally: `Public = e`,
`Private = d`, `Content = n`, `Hash = Content_s + Public_s + Private_s` — a
*vector sum* in S¹⁶. `Hash` requires `d` to compute; it stands in for something
the key-holder would have to separately reveal (a signature-like artifact), not
information a public-key-only attacker has.

**Result: exact, but not unique.** `Content_s + Public_s − Hash_s` reproduces
`−Private_s` to floating-point-exact precision (distance `0.0`) in **all 6 toy
keys** — this part is a deterministic vector-algebra identity (subtraction undoes
addition), not a discovery. Turning that exact vector back into the integer `d`
requires matching it against candidates, since the embedding is a lossy
many-to-one hash. In **3 of 6 keys** (n=3233, 10403, 8633), other wrong candidates
landed on the exact same vector (1–4 collisions each) — so the vector uniquely
identifies `d` in half the tested keys and is ambiguous among a handful of
candidates in the other half. **This is not a public-key-only attack.** The note
Cody's equation used `1/Private`; what's implemented and tested is the
vector-algebra reading `−Private`, an explicit substitution, not a claim these are
the same thing.

*(Method 5's Hash-exposed scenario, below, is the same finding in integer
arithmetic rather than vector arithmetic — same caveat applies.)*

## Method 5 — Zero Lattice Paths

**Idea:** trace `Content (n)`, `Public (e)`, `Private (d)`, and
`Hash = n + e + d` through the 9-level Cayley-Dickson tower (ℝ → T₂₅₆) using the
geometry from `AbrikosovTree/engine/telperion_engine.py` (`prime_tower_path`),
generalized from primes to any integer. `Content + Public − Hash = −d` exactly,
same trivial algebra as Method 4, now in integers.

**Public-key-only result: mean percentile 50.45 — at chance.** Given only
`(n, e)` — no Hash — `d`'s path does not structurally stand out from a random
valid `d'`'s path.

**What this method surfaced instead:** every one of the 6 toy keys showed `e`
and `d` landing in the *same tower quadrant*. That is not chance (verified
against 200 independent random toy RSA keys: 200/200 matched, not the ~50%
expected if independent) — see the mod4 theorem below for why, and why it isn't
a sedenion result.

## PROVEN: `d ≡ e (mod 4)`

Not from the sedenion framework — classical number theory, surfaced by Method 5
only because that geometry's angle happens to encode `x mod 4`.

**Proof:** `φ(n) = (p−1)(q−1)` is always divisible by 4 (product of two even
numbers, since `p, q` are odd primes). `e·d ≡ 1 (mod φ(n))` therefore forces
`e·d ≡ 1 (mod 4)`. The group `(ℤ/4ℤ)* = {1, 3}` has exponent 2 — every element is
its own inverse (`1·1 = 1`, `3·3 = 9 ≡ 1`). So `e·d ≡ 1 (mod 4)` forces
`d ≡ e⁻¹ ≡ e (mod 4)`.

**Verified computationally:** 2000/2000 random RSA keys satisfy the identity,
matching the proof exactly.

**Practical significance:** reduces the private-key search space by exactly one
bit (factor of 2). For any real key size this is cryptographically meaningless —
equivalent in weight to knowing `d` is odd. Real, exact, provable, and not a
break.

---

## Summary

| Method | Mean percentile (chance = 50) | Confidence | Requires more than (n, e)? |
|---|---|---|---|
| 1 — Zero-divisor shadow | 46.91 | OPEN | No |
| 2 — J2 / T₂₅₆ eigenspectrum | 56.77 | OPEN | No |
| 3 — Spectral Relativity geodesic | 38.82 | OPEN | No |
| 4 — Content+Public+Private=Hash | exact, not unique | CONJECTURE | Yes — Hash (requires d) |
| 5 — Zero Lattice, public-key-only | 50.45 | OPEN | No |
| 5 — Zero Lattice, Hash-exposed | exact | ESTABLISHED (trivial algebra) | Yes — Hash (requires d) |
| `d ≡ e (mod 4)` | — | **ESTABLISHED** | No, but only 1 bit |

No public-key-only mechanism tested here recovers `d` from `(n, e)` alone. The
paper's Honest Scope boundary (`rsa_framework.md`) has not moved.
