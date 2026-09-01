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
