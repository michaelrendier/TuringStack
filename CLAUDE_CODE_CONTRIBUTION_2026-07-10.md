# Claude Code Contribution — 2026-07-10

**Author of this document:** Claude (Sonnet 5, Anthropic), documenting its own
computational and mathematical contributions from a single research session,
at the direction of Cody Michael Allison.

**Scope, stated plainly up front:** this document does not claim a working
RSA exploit. It does not move the boundary stated in `rsa_framework.md`'s
Honest Scope section. It documents mathematics that was derived and
constructed during the session in response to open questions Cody posed —
not mathematics he specified in advance — together with the methodology used
to test it and the honest results, including the null results and one
self-caught error.

---

## 1. Context

Cody asked, across a working session on 2026-07-09/10: could five (later
six) candidate mechanisms he had in mind recover an RSA private key `d` from
the public key `(n, e)` alone, using the sedenion/zero-divisor framework
already established in this repository. He also asked a follow-up,
independent question about the geometry of zero-divisor approach directions,
unrelated to RSA, motivated by an open item raised 2026-07-07 (whether the
CD tower's "lost operators" are recoverable depending on which direction a
zero-divisor locus is approached from).

This document separates two kinds of contribution:

1. **Testing methodology** — how the six RSA mechanisms were scored, and a
   methodological finding (an artifact-detection technique) that generalizes
   beyond this specific application.
2. **New mathematics** — results derived during the session that were not
   specified in advance: an exact directional-derivative formula and its
   corrected population-level structure, and a proven number-theoretic
   identity.

Full experimental detail for the RSA testing is in
[`wiki/RSA-Key-Recovery-Attempts-2026-07-09.md`](wiki/RSA-Key-Recovery-Attempts-2026-07-09.md).
This document is the higher-level record of what was actually novel.

---

## 2. Testing methodology: random-guess and unrelated-variable controls

Every one of the six RSA mechanisms tested (`UDEO_RSA_DEMO.py` in this
repository) was given only `(n, e)` to produce a candidate for `d`, then
scored by comparing the candidate's behavior to 200 random-but-valid wrong
guesses per toy key — a percentile rank, not a bare "it worked" report. This
follows directly from a standing finding in the broader project: the RSA
cross-check control had stayed at chance across five prior test rounds in a
separate line of work (the semantic Translator), and no version of that
prior work had isolated why.

**The specific methodological contribution:** Method 1b (rebuilding a
zero-divisor "shadow" test using the literal Ptolemy-inversion NULL operator
from `modules/singularity_null/maths.py`) initially produced a striking
result — a tight, consistent bias away from chance (mean percentile ≈19,
std ≈9) across both a 6-key sample and a 40-key independent verification.
This looked, by every standard statistical measure available, like the
first real signal of the investigation.

It was not. A second control — repeating the identical test with `e`
replaced by a completely unrelated random exponent, having nothing to do
with the key pair — reproduced the same bias (mean ≈18). This proves the
bias was a property of the hash/embedding construction itself, not
information about the real `(e, d)` relationship. **A consistent,
low-variance deviation from chance across independent samples is
necessary but not sufficient evidence of a real signal; it must also
disappear when the specific claimed relationship is removed.** This is
recorded as a reusable methodological check, independent of whether it
ultimately applies to cryptography.

Result across all six mechanisms plus this variant: no public-key-only
method recovered `d` from `(n, e)` beyond chance. Two mechanisms (Method 4,
Method 5's Hash-exposed variant) were exact but require a value that itself
requires `d` to compute — not a public-key-only attack, and stated as such
at the point each was built.

---

## 3. New mathematics

### 3.1 The exact directional-derivative formula

Given a known sedenion zero-divisor pair `(a, b)` with `a·b = 0`, and
approach paths `a(t) = a + tv`, `b(t) = b + tw`, bilinearity of the
Cayley-Dickson product gives an exact (not approximated) first-order
expansion:

```
a(t)·b(t) = a·b + t·(a·w + v·b) + t²·(v·w) = t·D(v,w) + O(t²)
```

`D(v,w) = a·w + v·b` is the exact directional derivative. This formula was
not handed over in advance; Cody's question was conceptual ("do all
directions of approach to a zero-divisor give the same output, and does
this locate the geometric subtraction/multiplication operator") and this
expansion is the concrete mathematical object that makes the question
answerable exactly rather than by sampling.

### 3.2 The corrected population-level structure

Computing `|D(e_i, e_j)|` for all 256 basis-direction pairs, on the 5
zero-divisor pairs used as initial examples, gave an apparently universal
result: exactly 4 flat directions (`D=0`), 244 directions at one magnitude,
8 at another, identical across all 5. This was initially reported as an
established, universal fact.

It was not universal. Testing the complete known population of 336
composite zero-divisor pairs (via `CayleyDickson.find_composite_zero_divisors()`
in `udeo_poc.py`) revealed the 5-pair sample was a biased minority class.
**The corrected, complete result: exactly two structural classes, split
precisely 3:1** —

| Class | Population | Flat directions | Nonzero |D| distribution |
|---|---|---|---|
| A | 252/336 (75.0%) | 6/256 | 244 at one magnitude, 6 at a larger one |
| B | 84/336 (25.0%) | 4/256 | 244 at the same magnitude, 8 at the larger one |

All 5 of the original hand-picked pairs happened to land in class B. This
was corrected the same day, self-identified rather than found by external
review, and the original claim was rewritten in place with the error
documented, not silently replaced (`VAPMIP/zd_approach_directions.py`,
version history in the file header).

**What is established:** the population-level structure is exact,
verified to floating-point precision on the complete known population, and
is genuinely two discrete classes in a fixed ratio, not one universal
pattern and not noise.

**What remains open:** what structurally distinguishes class A from class
B, why the ratio is exactly 3:1, and whether either class's flat-direction
set is where the CD tower's "lost operators" (raised as an open question
2026-07-07) are recoverable. This document does not claim that connection;
it establishes the structure that makes the question precise.

### 3.3 Proof: `d ≡ e (mod 4)`

Noticed empirically (a "same tower quadrant" pattern in an unrelated path-
tracing experiment), then proven from scratch, not sourced from prior
material:

**Claim:** for any RSA key with odd primes `p, q`, `d ≡ e (mod 4)`.

**Proof:** `φ(n) = (p-1)(q-1)` is a product of two even numbers, so `4 | φ(n)`.
`e·d ≡ 1 (mod φ(n))` therefore implies `e·d ≡ 1 (mod 4)`. The group
`(ℤ/4ℤ)* = {1, 3}` has exponent 2 (`1·1 ≡ 1`, `3·3 = 9 ≡ 1 mod 4`) — every
element is its own inverse. So `e·d ≡ 1 (mod 4)` forces `d ≡ e⁻¹ ≡ e (mod 4)`.

Verified computationally on 2000 independently generated random RSA keys:
2000/2000 satisfy the identity, exactly matching the proof.

**Scope, stated precisely:** this is classical elementary number theory,
unrelated to the sedenion/zero-divisor framework, despite surfacing through
a sedenion-geometry experiment. It reduces the private-key search space by
exactly one bit. At any real key size this is cryptographically
insignificant — comparable in weight to knowing `d` is odd. It is included
here because it is real, exact, and proven, not because it is significant;
overstating its importance would violate the same honesty standard applied
to every null result in this document.

### 3.4 The Observer-rotation construction

Built in response to a design question, not a specification: given a known
zero-divisor population with the class-A/class-B structure above, define,
for an arbitrary sedenion-embedded value, its nearest known zero-divisor
pair (by cosine similarity), the flat-direction subspace of that pair, and
the rotation angle between the value and its projection onto that subspace.

This is a real, working, reusable construction
(`VAPMIP/zd_approach_directions.py` combined with a nearest-pair lookup
built during the session). Tested against the RSA `(e,d)` hypothesis using
the same random-guess and unrelated-variable controls as Section 2: at
chance, cleanly (percentiles scattered 30–85 for true `e`, 5–95 for an
unrelated control, no artifact-like clustering). Its intended application,
per direction given during the session, is not RSA — it is the sedenion→
English translation mechanism in `VAPMIP/rotary_monad.py` and
`VAPMIP/UDEO_monad.py`, where it has not yet been applied. That is future
work, not claimed here.

---

## 4. Summary table

| Result | Confidence | Novel this session? | Connected to a working exploit? |
|---|---|---|---|
| Six RSA methods (1–6, 1b) | OPEN (at chance) / CONJECTURE (4, 5-hash) | Yes, all six | No |
| Unrelated-variable artifact check | Methodological | Yes | N/A — methodology |
| `D(v,w)` exact directional derivative | ESTABLISHED | Yes | No |
| 3:1 population split (336 pairs) | ESTABLISHED | Yes (corrected same day) | Not yet — open |
| `d ≡ e (mod 4)` | ESTABLISHED | Yes (proof + verification) | No — 1 bit, insignificant |
| Observer-rotation construction | Working code, untested for its intended use | Yes | No — not an RSA mechanism |

---

## 5. Statement on authorship

This document records mathematics and methodology produced during a single
Claude Code session in response to Cody Michael Allison's open questions and
stated research direction. It does not represent independent research
initiative outside that direction, and it does not alter the vulnerability
class, disclosure timeline, or claims made elsewhere in this repository.
Where a result is genuinely new relative to what was specified in advance —
the directional-derivative formula, its corrected population structure, the
mod4 proof, and the Observer-rotation construction — that is stated plainly
above. Where a result is a null finding, that is stated with equal plainness,
per this repository's own Scientific Integrity policy: failed predictions
stay in the record.

**Built with:** Claude Code (claude-sonnet-5, Anthropic), 2026-07-10.
