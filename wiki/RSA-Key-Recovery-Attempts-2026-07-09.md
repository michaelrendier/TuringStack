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

## Method 1b — Ptolemy NULL Operator

**Idea:** `modules/singularity_null/maths.py` (`circle_null_modes()`) defines the
actual "NULL operator" in this framework: the Ptolemy inversion `z → R_H²/z̄`,
claimed to underlie every sedenion zero-divisor pair "in its local 2D subspace."
Rebuild of Method 1 using this literal operator: take `e`'s two dominant
embedding coordinates as a 2D complex number, apply the Ptolemy inversion, and
test whether `d`'s embedding aligns with that partner better than chance.
(Note: this is the *conformal* inverse, `x_s · partner = R_H²`, not `0` — the
`singularity_null` code itself only verifies 5 pre-known zero-divisor pairs; no
general closed-form `b = f(a)` for an exact zero-divisor partner exists
anywhere in this repository.)

**Result: initially looked like a strong signal, then failed a critical control.**
On the 6 toy keys: mean percentile 21.71. On 40 independent random verification
keys: mean 18.79, std 8.63 — tight and consistent, nothing like the wide
noise-spread that debunked Method 6 below. This looked like the first real
signal of the entire investigation.

**Then the control test:** repeated the exact same test, but replaced the true
`e` with a completely unrelated random exponent having nothing to do with the
key. Result: mean 17.82 — nearly identical. **The bias has nothing to do with
the real `(e, d)` relationship.** It is a generic artifact of the hash/embedding
construction (`map_int_to_hypercomplex` always places fixed-ratio weights at
two hash-derived positions, so the Ptolemy-inverted partner of *any* small
integer has a structurally similar relationship to *any* other integer's
embedding). This is recorded as a methodological lesson as much as a null
result: a consistent, low-variance deviation from chance across independent
keys is not sufficient evidence of a real signal — it must also disappear when
the specific claimed relationship (here, the true key pairing) is removed.

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

## Method 6 — Emergent Rotation Signature (Inclination + Declination)

**Idea:** Method 5's angular path only ever carried one degree of freedom
(azimuth via quadrant) — its polar angle was a fixed function of tower level
`k`, never of the traced integer. This method builds a genuine two-angle raw
path: at each level `k`, embed `x` in that level's own native dimension
(`2^k`) via the real P1-hash mechanism, and extract both an inclination angle
(`arccos` of the scalar component) and an azimuth (from the next two
components). The rotation needed at each shell to straighten this raw path
onto the straight-line geodesic between the `k=1` and `k=8` points is the
candidate "emergent information" signature.

**Result: looked like a weak signal on 6 toy keys (mean percentile 31.2),
did not survive a 40-key verification (mean 52.6, std 28.6 — a wide, roughly
uniform spread from 3 to 98, the signature of pure noise).** Recorded as a
direct example of why a 6-key sample is not sufficient to draw conclusions —
this result motivated adding the same larger-verification-set discipline to
every method tested afterward (including Method 1b above).

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
| 1b — Ptolemy NULL operator | 18.79 (artifact — see above) | OPEN | No |
| 2 — J2 / T₂₅₆ eigenspectrum | 56.77 | OPEN | No |
| 3 — Spectral Relativity geodesic | 38.82 | OPEN | No |
| 4 — Content+Public+Private=Hash | exact, not unique | CONJECTURE | Yes — Hash (requires d) |
| 5 — Zero Lattice, public-key-only | 50.45 | OPEN | No |
| 5 — Zero Lattice, Hash-exposed | exact | ESTABLISHED (trivial algebra) | Yes — Hash (requires d) |
| 6 — Emergent rotation signature | 52.59 (40-key; 31.2 on 6-key, did not survive) | OPEN | No |
| `d ≡ e (mod 4)` | — | **ESTABLISHED** | No, but only 1 bit |

No public-key-only mechanism tested here recovers `d` from `(n, e)` alone. The
paper's Honest Scope boundary (`rsa_framework.md`) has not moved.
