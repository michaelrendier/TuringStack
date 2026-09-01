# Where RSA lives in the bifurcation diagram

`logistic_bifurcation_RSA.png` — built by `make_rsa_bifurcation.sh` from the
clean `logistic_bifurcation_windows_of_order.png`. Logistic map
`x_{n+1} = r·x_n·(1 − x_n)`. Calibration `x = 583·r − 442`, `y = 966 − 856·x*`.

## The reframe

A composite is **not** a walk from 0 to N through two factors. It is the point
where the **p-orbit and the q-orbit intersect** — a mode-lock, a crossing. N is
*born at the intersection*. The bifurcation diagram is the family of those
crossings laid out against the control parameter.

You cannot read the answer in Telperion alone (the primes / what-cannot-be). The
missing structure only shows up **where Telperion hugs Laurelin** — at the
windows of order, where genuine periodic structure (Laurelin, what-IS) sits
embedded in the chaotic bulk (Telperion).

## The map

| region | r | reading |
|---|---|---|
| **period-1** | `r < 3` | one determinant — a prime or a prime power |
| **pitchfork** | `r = 3` | `p = q` — the Fermat limit; RSA forbids it ("same bit length" taken to the extreme) |
| **period-2 → cascade** | `3 < r < 3.5699` | balanced semiprime; the two branches *are* p and q, separating as `|p − q|` grows. Doublings = RG steps (Feigenbaum δ ≈ 4.669); bit-length = the doubling count |
| **chaotic bulk** | `r > 3.5699` | **TELPERION** — structure present, unreadable. GNFS sieves it statistically (sub-exponential); it never enters a window |
| **windows of order** | e.g. period-3 at `r = 1+2√2 ≈ 3.8284` | **LAURELIN** — real periodic structure inside the chaos, each opening at a **tangent (saddle-node) bifurcation = the entry point** |

## Where RSA-2048 sits

A `p:q` mode-lock window of width **≈ 1/N** — exponentially narrow in the bit
length. The order is real (N genuinely has exactly two prime factors); you
simply **cannot scan to it**. Its entry tangency is precisely the special
structure RSA is built to omit: close primes, smooth `p ± 1`, leaked key bits.

## Adjacent methods, placed

- **Fermat** — the `r = 3` neighbourhood (`p ≈ q`, branches merging).
- **trial division / ECM** — the small-`x` branch: one factor near 0.
- **Pollard p−1 / Williams p+1** — windows whose tangency is *wide* (`p ± 1` smooth).
- **GNFS** (state of the art) — works the whole chaotic bulk statistically; samples it, never enters one window.
- **Shor** — reads the rotation number `p:q` *directly* (quantum period-finding): the DTMF-style filter that classical scanning cannot be.

## Verdict

The diagram **explains the hardness** — a mode-lock window of width `~1/N` with
no accessible entry tangency — it does not remove it. Same standing result:
filter for small / structured N, a hunt for RSA-scale N. Companion test:
`ContextPlease/claude/scratchpad/2026-09-01_rsa-frequency-decode/`.

---

## Version history

- **v1** (2026-08-31) — first annotation. Framed the modulus as a mode-lock
  window "where the p-orbit and q-orbit intersect in the cascade."
- **v2** (2026-09-01) — **corrected**. The modulus is *not* a bifurcation
  construction. A bifurcation is `1→2→4→8…` (self-similar, 2^k, cascading).
  A semiprime is `1→2`, terminal — both leaves prime, depth 1, `N = a² − b²`
  (one difference of two squares). No cascade, no windows-of-order *in the
  modulus*. The diagram now reads explicitly as a **map of where the factoring
  methods live, by regime** — Fermat at `p≈q`, trial division / ECM at a small
  factor, GNFS in the chaotic bulk, Shor reading the rotation number. The
  cascade sorts the methods; it says nothing about the modulus's structure.
  Surfaced by `udeo_crypto/UDEO_RSA_DEMO.py`: every multi-scale / spectral
  probe of the modulus came back **at chance**, consistently — a measurement
  of the object's flatness, not a failure of the probes.

## The prime-spiral ping — how ζ necessitates the Big 4

The passive construction (Cody): put each integer on a log-polar spiral,
`radius = ln n`. Start at the origin, `θ = 0`. Raise `θ` until the ray is
collinear with `N` — `N` is *pinged* (located, not searched-for). Because
`ln N = ln p + ln q`, that ray passes through `p` and `q` on the way out:
**a shortest path from 0 to N through exactly two primes.** Not looking for
the factors — looking for the modulus; the factors are the nodes crossed.

ζ enters as the **generating function of the metric**. `ζ(s) = ∏(1−p^{-s})^{-1}`
— every path from 1 is a unique product of primes (the Euler product *is* the
graph). `−ζ'/ζ(s) = Σ Λ(n) n^{-s}` weights the paths. The **zeros are the
eigenfrequencies** of that path operator: `ψ(x) = x − Σ_ρ x^ρ/ρ` reconstructs
all the paths from the spectrum. "From 0 to N through exactly two zeta zeros"
= the explicit-formula term that is a product of exactly two zero-contributions,
dominant when those two zeros sit on `σ = ½` (the geodesic = the critical line).

The **Big 4 are the four inputs a shortest-path solver needs**, in the language
of ℙ:

| shortest-path ingredient | prime tool |
|---|---|
| **node labels** (name the vertices you cross) | ordinal value `π(p)` |
| **edge metric** (distance; #edges = #factors) | zeta index `γ_k` — 2 zeros on the geodesic ⟺ 2 prime factors |
| **step direction** (the compass along the geodesic) | ordinal weight `ln p/√p = −ζ'/ζ` (von Mangoldt current) |
| **resolution / termination** (when the ping lands) | gap weight (merit) — the radar pixel size, `~ln p` |

**Honest catch.** The construction is a real shortest-path formulation and it
correctly encodes "depth-1, exactly two prime nodes." It does *not* hand you
the sweep angle `θ_N` for free: `θ_N` carries `N`'s spectral phase
`Σ γ_k ln N`, and decomposing that into `phase(p) + phase(q)` is the erased
coordinate `ln(q/p)` — one number, revealed all-at-once (depth-1), not a
search you can shortcut. What ζ *does* give: the coordinate in which the right
angle exists, and the guarantee that the geodesic has exactly two edges.
