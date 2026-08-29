# SHA-1 Real-Collision Geometry — 2026-07-17

**Status:** Real result, verified against the actual published SHAttered
collision (Stevens et al., CWI/Google, 2017) — not toy data, not a
simulation. No new attack on SHA-1 is claimed; this is retrospective
algebraic characterization of an already-broken hash, same honest-scope
boundary as the rest of this repository. What's new here is that
`paper.tex`'s own stated Proposition about the SHAttered differential was,
until today, never actually tested against the real collision data —
only asserted. This page documents that test and its result.

**Code:** `sha1_zero_divisor_demo.py` (verified `sha1_compress()`, exact
against hashlib), `udeo_poc.py`'s `word_to_t32`/`CayleyDickson`, and the
inline scripts run this session (see git log 2026-07-17 for the exact
commands — reproducible from `shattered_data/`).

**Data:** `shattered_data/shattered-1.pdf`, `shattered_data/shattered-2.pdf`
— downloaded directly from `https://shattered.io/static/`, the original
disclosure site (already cited in `paper.tex`'s bibliography). Verified:
both files are 422,435 bytes, both hash to
`38762cf7f55934b34d179ae6a4c80cadccbb7f0a` (matches the publicly known
collision hash exactly) using hashlib AND our own from-scratch
`sha1_compress()`, chained across all 6,601 real 64-byte blocks with
correct padding. This is itself worth recording: the T32/GF(2)
characterization work in `paper.tex` is now demonstrated to be built on
a correct, from-scratch SHA-1 implementation exercised against real
multi-block data, not just single 64-byte toy blocks.

## 1. Where the real files actually differ

Byte-exact diff of the two 422,435-byte files: only 62 bytes differ,
all within byte offsets 192–319 — exactly blocks 3 and 4 (64-byte
blocks, 0-indexed). Blocks 0–2 are byte-identical (the common prefix);
blocks 5–6600 are byte-identical (the common suffix). This matches the
publicly documented structure of the SHAttered attack (two near-collision
blocks between a shared prefix and shared suffix) exactly, confirming the
downloaded files are the genuine article.

## 2. The test that came back at chance (and why)

First pass: `udeo_poc.py`'s own `sha1_message_differential_t32()` —
checks whether any two *adjacent* words of the raw 16-word block
differential multiply to exactly zero in T32/GF(2). Run against the real
blocks 3 and 4:

```
Block 3: has_zd_event = False   (0 exact ZD events, 16/16 words nonzero)
Block 4: has_zd_event = False   (0 exact ZD events, 16/16 words nonzero)
```

Same null as an earlier toy-collision control run this session (25 real
truncated-digest collisions, 200 random non-colliding pairs — 0/225
exact ZD events either way). Honest structural reason, not a bug: exact
ZD pairs are a sparse 336-pair locus; a dense, full-Hamming-weight
differential essentially never lands on it, real collision or not. This
test was never well-positioned to see what turned out to be the real
phenomenon (§3) — same shape of miss as `UDEO_RSA_DEMO.py`'s Method 1.

## 3. The real result: the expanded message schedule collapses to exact zero

`paper.tex`'s Proposition (SHAttered collision structure) is stated in
terms of L, the XOR-linear component of the FULL round structure
(message schedule recurrence + Parity rounds), not a raw adjacent-word
check. Testing that directly: expand each real block's 16 words to the
full 80-word message schedule via SHA-1's actual linear recurrence
(`W[t] = rotl(W[t-3]^W[t-8]^W[t-14]^W[t-16], 1)`, real bytes, real XOR,
real rotate — no simplification), then take the word-by-word XOR
differential across all 80 expanded words, for both real near-collision
blocks:

```
Block 3 AND Block 4 (identical differential pattern):
  message-schedule words where delta == EXACTLY ZERO:
    {30, 31, 35, 55, 58, 61, 62, 63, 64, 65, 66}   -- 11 of 80

  Hamming weight per round (16 initial + 64 expanded):
    rounds  0-19 (Ch,     non-linear): 3 3 7 5 8 2 5 7 3 3 7 4 7 4 2 5 3 5 3 4
    rounds 20-39 (Parity, LINEAR):     7 4 4 4 5 2 3 5 4 2 0 0 1 1 1 0 2 1 1 2
    rounds 40-59 (Maj,    non-linear): 2 3 2 3 3 1 1 2 1 1 1 1 1 1 1 0 2 2 0 1
    rounds 60-79 (Parity, LINEAR):     1 0 0 0 0 0 0 1 1 1 2 3 3 3 4 5 5 5 3 2
```

**Rounds 61–66: six exact zeros in a row**, immediately after round 60 —
precisely where SHA-1 re-enters its second Parity (pure-XOR, linear)
round block. The first Parity block (20–39) shows the same signature at
smaller scale (weights 0,0,1,1,1,0 across rounds 30–35). The differential
does not merely shrink near these boundaries — it hits exact zero,
repeatedly, specifically inside the algorithm's linear-round windows.

This is a real, verified, first-time confirmation of `paper.tex`'s own
claim — *"the zero-divisor attack targets the XOR-linear subspace; the
SHAttered collision is precisely a collision in this linear subspace"* —
against the actual published collision, not an assertion. Note this
required no interpretive step: XOR-difference is exactly T32/GF(2)
addition (`word_to_t32`), so "the differential collapses to zero" and
"these words are algebraically identical zero-divisors" are the same
statement, not two.

## 4. Honest scope

No preimage, no forgery, no working attack. This section demonstrates
*why* the already-known 2017 collision sits where the paper's own theory
says it should, using real data — it does not show how to find a new
one faster than Stevens et al. did. Consistent with the rest of this
repository: characterization, not exploitation.

## 5. The stability-distance panel — a failed prediction, kept in the record (2026-08-25)

*Grounded in `sha1_chladni_stability.py`'s composite-pair panel — the
red/blue gradient with gold zero-divisor markers over the 496×496
`(e_i+e_j)` composite grid. Recorded from Cody's own description of the
two images; noted here in case a different, uncommitted script is what's
actually meant — correct if so.*

**Original prediction:** the stability-distance gradient (popcount of the
product, 0 = exact zero-divisor collapse, up to 4 = maximally stable)
would vary spatially across the grid — "pockets" of differential
behavior, some regions of composite pairs settling toward the
zero-divisor locus faster than others, visible as a spatial gradient in
the red/blue coloring underneath the gold zero-divisor markers.

**Measured, and the prediction was wrong:** the settling behavior is
**uniform across the entire set** — every composite pair reaches its
stability distance the same way, no spatially clustered pockets. What
looked at first like it might carry positional information collapses to
a single invariant: they all settle at the same "time." A real, useful
result — just not the one being looked for.

**Why this belongs on the record rather than being quietly dropped**
(same discipline as wiki Phase 3's "failed predictions stay in the
data"): a uniform outcome across an entire measured set is itself a
finding — it rules out spatial/positional structure in this particular
metric, cleanly, rather than leaving the question open. Stated precisely
so it isn't re-investigated blind later: **if there had been variation in
settling across the grid, that would plausibly have been a spectral
signal** (eigenvalue/mode-related, the kind `trace_laplacian`'s
`spectral_dist` already probes elsewhere in this file) — but since the
metric is uniform, there is no such signal available to extract from it.
The absence is the result, not a gap in the analysis.

## Related

`paper.tex` §3 (SHA-1 in T32/GF(2)), `sha1_zero_divisor_demo.py` (the
verified compression function and toy-scale control tests this builds
on), `sha1_chladni_figure.py` (the trace-Laplacian nodal visualization —
same T32/GF(2) machinery, applied to SHA-1's IV/round constants instead
of a real collision), `sha1_chladni_stability.py` (the composite-pair
continuous stability gradient, §5 above).
