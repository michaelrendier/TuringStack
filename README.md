# UDEO — Zero-Divisor Structure of Cayley-Dickson Algebras over GF(2)

## A white-hat research framework, and a retrospective structural account of the SHA-1 break

**Discovery / Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
**ORCID:** https://orcid.org/0009-0007-7239-6760
**Disclosure posture:** White hat. Responsible, coordinated.
**Status:** Research framework + one exact theorem + a retrospective result on the
already-public SHA-1 collision. **No working key-recovery or preimage exploit is
claimed or provided.**

> **Scientific-integrity note (Ainulindale protocol — failed predictions stay in the record).**
> This README was corrected on 2026-07-28 after every script in the repository
> was re-run. A prior version claimed Critical severity, private-key recovery
> from public keys, ECDSA signature forgery, and breaks of SHA-2/SHA-3. **None
> of those are supported by the code in this repository** — each script's own
> summary says so. The corrected scope is below. The overclaims are not deleted;
> they are recorded here as what was retracted, and why.

---

## 1. What is actually established (reproduced 2026-07-28)

Each claim carries its evidence tier. Run the named script to reproduce.

### ESTABLISHED — the T_n/GF(2) trace-Laplacian theorem
`hypercomplex_laplacian.py`

For any n = 2^k, in the Cayley-Dickson algebra T_n over GF(2), every element x
satisfies **x² ∈ {0, e₀}**. Equivalently, the trace-Laplacian
Δ(w) = w · (0xFF…F) is zero **iff** w is nilpotent, iff w lies on the nodal
line (the zero-divisor locus). This is an exact algebraic theorem, not a
statistical claim — it either holds for an element or it does not, and it is
checked directly.

### ESTABLISHED — the named SHA-1 constants land on the nodal line
`hypercomplex_laplacian.py`

The five SHA-1 initialization-vector constants are **all nilpotent in T32** —
every one lies exactly on the zero-divisor nodal line:

| Name | w | Δ(w) | Distance | Nilpotent |
|---|---|---|---|---|
| H0 | 0x67452301 | 0x00000000 | 0 | ✓ |
| H1 | 0xEFCDAB89 | 0x00000000 | 0 | ✓ |
| H2 | 0x98BADCFE | 0x00000000 | 0 | ✓ |
| H3 | 0x10325476 | 0x00000000 | 0 | ✓ |
| H4 | 0xC3D2E1F0 | 0x00000000 | 0 | ✓ |

The four round constants (K0–K3), by contrast, sit at the **maximum** spectral
distance (32) — a clean bimodal split: the IVs are on the locus, the round
constants are as far from it as the space allows. This is the "name collision"
result: the *named* constants of SHA-1 collide onto the nodal line while the
round constants do not. It is exact and reproducible.

### ESTABLISHED — secp256k1's generator has involutory coordinates in T256
`secp256k1_locus.py`, `secp256k1_locus_results.md`

Both generator coordinates Gx, Gy are **involutory** (x² = e₀) in T256/GF(2) —
neither is nilpotent, and Gx · Gy ≠ 0. This is a structural fact about how the
curve's fixed constants sit in the algebra. It is **not** an attack; see §3.

---

## 2. The SHA-1 account (the solid, defensible core)

SHA-1 is genuinely, publicly broken — the SHAttered collision (Stevens et al.,
2017) is real and required ≈ 2⁶³ (~9.2 × 10¹⁸) compressions to find. This
repository does **not** re-break SHA-1 and claims no new SHA-1 attack. What it
offers is a **retrospective structural reading** of the known break:

- SHA-1's IV constants sit exactly on the T32 zero-divisor nodal line (§1).
- A collision is, in these coordinates, a zero-divisor event in T32 — two
  distinct messages whose differential lands on the locus.
- Framed this way, the 2⁶³ search of SHAttered was a *search* for a locus that
  is describable analytically.

This is a lens on an already-known result, offered as mathematical
context — **not** a claim to have navigated to that locus in polynomial time.
That step is open (§3).

---

## 3. What is OPEN or NULL — do not cite these as results

### OPEN — polynomial-time navigation to the locus
The whole framework's value as an *attack* would rest on reaching the
zero-divisor locus analytically rather than by search. `udeo_poc.py` states it
directly: *"Current gap: 'navigate to' is not yet polynomial-time."* No script
in this repository closes it.

### OPEN — ECC / secp256k1 key recovery
`secp256k1_locus.py`'s own conclusion: modular reduction (carries mod p) is the
sole algebraic barrier, and *"Whether carry-closing is polynomial: OPEN
PROBLEM. Not a working exploit."* There is no public-key → private-key recovery
here, demonstrated or implied.

### NULL — the sedenion factoring "signal" does not exist
`fermat_sedenion_test.py` prints *"SIGNAL DETECTED via 'hw_hi32'
(ratio = inf)."* **This is a divide-by-zero artifact, not a signal.** The
ratio code is `f_pct / r_pct if r_pct > 0 else float('inf')`, so a strategy
that scores 0/97 for *both* factor and random pairs (0/0) is reported as
infinite signal. The actual per-strategy hit rates:

| Strategy | factor pairs | random pairs |
|---|---|---|
| raw_mod32 | 0/97 (0.0%) | 4/97 (4.1%) |
| hw_low32 | 1/97 (1.0%) | 3/97 (3.1%) |
| hw_mid32 | 2/97 (2.1%) | 2/97 (2.1%) |
| hw_hi32 | 0/97 (0.0%) | 0/97 (0.0%) ← the "inf" |
| hw_xor_fold | 1/97 (1.0%) | 1/97 (1.0%) |

Random pairs land on the ZD locus **at least as often** as factor pairs.
There is no factoring locality here. The S16 (real 16-D) test is likewise
0/97 across all groups. The `ratio = inf` verdict should be read as *no
result*, and the reporting bug should be fixed to print "n/a (0/0)".

### NULL / at-chance — RSA and ECDSA recovery
Consistent with the broader project record: every RSA/ECDSA private-key
recovery attempt in this framework has measured at chance, with one apparent
positive elsewhere traced to a contaminated control. No recovery is
demonstrated here.

### NOT demonstrated — SHA-2, SHA-3
No preimage, second-preimage, or collision result against SHA-2 or SHA-3
exists in this repository. The prior README's "under investigation" was, in
practice, "not started."

---

## 4. Corrected scope — what this is, and what it is not

**It IS:**
- an exact algebraic theorem about Cayley-Dickson algebras over GF(2);
- an exact, reproducible observation that SHA-1's IV constants are nilpotent
  in T32 while its round constants are maximally far from the locus;
- a retrospective structural framing of the *known* SHA-1 collision;
- a threat-model / research direction for ECC, with the exploit step open.

**It is NOT:**
- a working recovery of any ECC or RSA private key;
- a signature-forgery capability;
- any attack on SHA-2 or SHA-3;
- "Critical" severity — there is no demonstrated exploit to rate.

**No currently deployed cryptographic system is shown to be broken by anything
in this repository.** Anyone relying on secp256k1, P-256/384/521, ECDSA, ECDH,
SHA-2, or SHA-3 should not treat this repository as evidence of a break in
those primitives. (Post-quantum migration remains good practice on its own
merits and is unrelated to any result here.)

---

## 5. Repository contents

| File | What it actually contains |
|---|---|
| `hypercomplex_laplacian.py` | The T_n/GF(2) theorem + SHA-1 IV nodal-line result (§1). **Solid.** |
| `secp256k1_locus.py` | secp256k1 generator structure in T256; states carries as OPEN. |
| `secp256k1_locus_results.md` | Computed structural facts about Gx, Gy. |
| `fermat_sedenion_test.py` | Factoring-locality test — **NULL result**; contains the `0/0 → inf` reporting bug (§3). |
| `udeo_poc.py` | Framework demo. States its own honest scope; no working exploit. |
| `sha1_demonstration.md` | SHA-1 worked example / T32 correspondence. |
| `rsa_framework.md` | RSA in RedBlue coordinates — framework, not a recovery. |
| `zero_divisor_attack.md` | Attack-model prose. Read against §3/§4 before citing. |
| `paper.pdf`, `paper.tex` | Research paper — must be reconciled with this corrected scope. |
| `stix_bundle_udeo.json` | STIX 2.1 bundle — already framed as OPEN/no-exploit; see §6. |
| `DISCLOSURE_CHECKLIST.md` | Disclosure process record. |

---

## 6. On the CVE / STIX framing

**A CVE in the "Critical, private-key recovery" sense cannot be substantiated
by this repository, and must not be filed as such.** A vulnerability report to
MITRE/NIST/CISA/OpenSSL claiming a working break of ECC or SHA-2/3, addressed
to real organizations, would be a false report — regardless of intent — and
would not survive their triage against the code here.

What *is* honestly disclosable, and what the STIX bundle in this repo already
describes, is narrower and defensible:
- a proved algebraic theorem;
- a retrospective structural result on the already-broken SHA-1;
- an ECC threat *model* with the exploit explicitly OPEN and **"no working
  exploit provided."**

The existing `stix_bundle_udeo.json` is written correctly at that scope
(it labels the ECC step an OPEN PROBLEM and states no exploit is provided).
Any CVE-style specification prepared from this work must inherit that scope,
not the retracted README's. The correct disclosure vehicle for the solid
content is **academic publication** (the framework theorem + the SHA-1
retrospective), not a CVE against unbroken primitives.

---

## 7. Cover art

`Gemini_Generated_Image_Breaking_Enigma.png` is thematic cover art (Enigma /
Turing, R. Crumb style) — decorative, not evidence. Noting it so it is not
mistaken for a figure.

---

## License

White-hat research, provided for defensive and scholarly purposes. See
`LICENSE`.

**Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
**README corrected:** 2026-07-28, after re-running every script in the repo.
