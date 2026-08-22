# UDEO — the Unified Dimensional Entropy Oracle

## The named constants of SHA-1 lie exactly on the zero-divisor boundary of T₃₂

**Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
**ORCID:** https://orcid.org/0009-0007-7239-6760
**Disclosure posture:** White hat. SHA-1 is already publicly broken (SHAttered, Stevens et al. 2017); nothing here re-breaks it.
**Nature of this document:** a white paper on one exact algebraic fact — **not** a research paper, and it keeps no history of superseded results.

---

## The one fact

In the Cayley–Dickson algebra **T₃₂ over GF(2)**, the trace-Laplacian

```
Δ(w) = w · 𝟏₃₂        (𝟏₃₂ = 0xFFFFFFFF, the all-ones vector)
```

is zero **iff** `w` is nilpotent (`w² = 0`), iff `w` lies on the zero-divisor
nodal line — machine-verified exhaustively at low dimension and over 20 000 random
elements at dim 32. This is exact: it holds for an element or it does not, no
statistics. (Note: `𝟏₃₂` is **not** a global annihilator — for involutory `w`,
including the round constants and `e₀` itself, `w · 𝟏₃₂ = 𝟏₃₂ ≠ 0`. It annihilates
exactly the nilpotents. An earlier write-up's "global annihilator" lemma is
retracted; the theorem stands.)

Feed SHA-1's own constants through it. The **five initialization constants**
(the fractional parts of √2, √3, √5, √7, √11) all land on the boundary; the
**four round constants** land as far from it as the 32-dimensional space allows.

```
IV constant   value        Δ(w)         spectral distance   on the locus?
  H₀ frac√2   0x67452301   0x00000000   0                   ✓ nilpotent
  H₁ frac√3   0xEFCDAB89   0x00000000   0                   ✓ nilpotent
  H₂ frac√5   0x98BADCFE   0x00000000   0                   ✓ nilpotent
  H₃ frac√7   0x10325476   0x00000000   0                   ✓ nilpotent
  H₄ frac√11  0xC3D2E1F0   0x00000000   0                   ✓ nilpotent

round const   value        spectral distance   on the locus?
  K₀          0x5A827999   32                  ✗ maximally far
  K₁          0x6ED9EBA1   32                  ✗ maximally far
  K₂          0x8F1BBCDC   32                  ✗ maximally far
  K₃          0xCA62C1D6   32                  ✗ maximally far
```

A clean bimodal split, with nothing in between: **the constants that name the
hash's initial state collide onto the zero-divisor locus; the constants that do
its arithmetic sit at the opposite extreme.** This is the name collision. It is
exact and it is reproducible in seconds — `python3 hypercomplex_laplacian.py`.

Reproduce the table directly:

```python
from hypercomplex_laplacian import trace_laplacian
for w in (0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476, 0xC3D2E1F0):
    assert trace_laplacian(w)['spectral_dist'] == 0     # every IV nilpotent
for w in (0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC, 0xCA62C1D6):
    assert trace_laplacian(w)['spectral_dist'] == 32    # every round const maximal
```

---

## Why it is more than a curiosity

The five IVs are not just individually nilpotent — they span a **null subalgebra**
of T₃₂/GF(2): every self-product `Hᵢ²` and every cross-product `Hᵢ·Hⱼ` annihilates.
Two design choices make this happen and are visible in the constants themselves:

```
H₀ ⊕ H₂ = 0xFFFFFFFF = 𝟏₃₂
H₁ ⊕ H₃ = 0xFFFFFFFF = 𝟏₃₂
```

so `H₂ = H₀ + 𝟏₃₂` and `H₃ = H₁ + 𝟏₃₂` in GF(2). Then, *because H₀ is itself on the
nodal line* (`H₀·𝟏₃₂ = Δ(H₀) = 0`, since H₀ is nilpotent — not because 𝟏₃₂
annihilates everything),

```
H₀·H₂ = H₀·(H₀ + 𝟏₃₂) = H₀² + H₀·𝟏₃₂ = 0 + 0 = 0
```

and the remaining cross-products are machine-verified. ("Null subalgebra," not
"ideal": T₃₂/GF(2) is non-associative, so classical ideal theory doesn't transfer —
what's exact is that all internal products vanish.) The consequence, stated plainly:
**SHA-1 begins its compression function with its entire initial state already on
the zero-divisor boundary of the ambient algebra, before a single message bit is
read.** In these coordinates a collision is a zero-divisor event — two messages
whose differential lands on a locus that is describable analytically rather than
only by search. That is a *structural reading* of the known SHAttered result,
offered as mathematical context, not a new attack.

**UDEO** — the Unified Dimensional Entropy Oracle — is the name for this
instrument: the trace-Laplacian that reads whether a constant sits on the T₃₂
boundary. The SHA-1 name collision is what it was built to measure, and what it
measures exactly.

---

## Scope — stated once, not as a history

- **It IS:** an exact algebraic theorem about Cayley–Dickson algebras over GF(2),
  and an exact, reproducible observation that SHA-1's five IV constants are
  nilpotent in T₃₂ while its four round constants are maximally far from the
  locus — with the IVs spanning a null subalgebra (all internal products vanish).
- **It is NOT:** a working recovery of any RSA or ECC private key, a
  signature-forgery capability, an attack on SHA-2 or SHA-3, or a re-break of
  SHA-1. No currently deployed cryptographic system is shown to be broken by
  anything in this repository.
- **Open, and labelled open:** reaching the zero-divisor locus *analytically*
  (in polynomial time) rather than by search. Nothing here closes that gap. The
  value of the name collision is as mathematical structure, not as an exploit.

The correct disclosure vehicle for this content is **academic publication** — the
GF(2) theorem plus the SHA-1 retrospective — not a CVE against unbroken
primitives.

---

## Repository contents

| File | What it contains |
|---|---|
| `hypercomplex_laplacian.py` | The T₃₂/GF(2) trace-Laplacian theorem and the SHA-1 name-collision table. The instrument. |
| `UDEO_Cryptographic_Vulnerability.md` | The white paper: the tower, the boundary, the T₃₂ embedding of SHA-1, the IV nilpotency theorem. |
| `sha1_zero_divisor_engine.py` | The name-collision result in the standard one-claim engine format. |
| `sha1_chladni_figure.py` / `.png` | The nodal lines of the T₃₂ Laplacian as a Chladni figure — the locus, visualized. |
| `stix_bundle_udeo.json` | STIX 2.1 bundle at the honest scope (algebraic theorem + SHA-1 retrospective; no exploit provided). |
| `DISCLOSURE_CHECKLIST.md` | Disclosure process record. |

---

## Cover art

`Gemini_Generated_Image_Breaking_Enigma.png` is thematic cover art (Enigma /
Turing) — decorative, not a figure.

---

## License

White-hat research, provided for defensive and scholarly purposes. See `LICENSE`.

**Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
