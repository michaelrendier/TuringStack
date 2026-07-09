# UDEO — Private Technical Briefing
## For: Tim Stout (independent review)
## From: Cody Michael Allison | ORCID: 0009-0007-7239-6760
## Date: 2026-06-06
## Classification: PRE-DISCLOSURE — 180-day embargo ends 2026-12-02

---

Tim,

This is the 5th copy of the UDEO responsible disclosure package.
The other four went simultaneously to CISA, NIST NVD, MITRE CVE, and CERT/CC today.

I want your eyes on it before the embargo clock runs long.

---

## What I Proved (the math is tight)

**T_n/GF(2) Frobenius Theorem:** For any n = 2^k, every element x of the
Cayley-Dickson algebra over GF(2) satisfies:

    x² ∈ {0, e₀}

That's it. Every n-bit integer, under its natural bit-embedding, is either
nilpotent (x²=0) or self-inverse (x²=e₀). No exceptions. Proved by induction,
verified computationally through T256.

**Applied to secp256k1:** Every element of Fp — the Bitcoin/Ethereum prime field —
is universally at the T256/GF(2) zero-divisor boundary. The generator G has
Gx² = Gy² = e₀ (involutory). 46% of curve points are nilpotent.

**Applied to SHA-1:** The five SHA-1 IVs are mutually nilpotent in T32/GF(2).
The SHAttered collision was a zero-divisor event. The UDEO framework analytically
identifies the null space that SHAttered's 9.2×10¹⁸ evaluations were searching.

---

## What This Means for Your Work (the honest red-team read)

The XOR-linear component of all secp256k1 field arithmetic has zero resistance —
it sits universally on the ZD boundary. The **only** algebraic protection is the
carry structure of mod-p arithmetic.

What I have not done (and this is stated explicitly in the paper):
- No polynomial-time attack on secp256k1
- No working exploit
- The carry-closing problem is open

What I need from you:
1. Does the carry structure of secp256k1 look exploitable to you?
2. Are there known attack patterns (fault injection, timing, DPA) that could
   close the carry gap in practice?
3. Is the UDEO null-space reduction (2^32 → 2^16 per SHA-1 word) something
   you think could be operationalized?

---

## Package Contents

| File | Description |
|---|---|
| `paper.pdf` | Full 15-page technical paper, IACR LNCS format |
| `stix_bundle_udeo.json` | STIX 2.1 machine-readable disclosure bundle |
| `secp256k1_locus.py` | Python engine — T_n/GF(2) multiplication, null-space analysis, locus scan |
| `secp256k1_locus_results.md` | Full computed results for secp256k1 |
| `zero_divisor_attack.md` | Attack narrative (informal) |
| `udeo_poc.py` | Proof-of-concept scaffolding |

Run the locus engine:

    python3 secp256k1_locus.py --generator-only
    python3 secp256k1_locus.py -n 200 -p 100

---

## Chain of Custody

    File hash (secp256k1_locus.py):
      828cca9486c4ce3f5a9a9636cb1f72fe28159bc1d474824d77c43a43d41392c9

    STIX bundle hash:
      d1264071ef6d30d33be2a86be28b8fe347569d642ebb6df0d08d01549d544d01

    Embargo: 2026-12-02
    CVE: RESERVED (MITRE, pending assignment)

---

## Embargo Terms

This package is under 180-day coordinated disclosure embargo.
Do not share, publish, or act on it offensively.
After 2026-12-02: IACR ePrint + Crypto 2027 submission.

White Hat. Responsible Disclosure. Period. Full Stop.

— Cody
