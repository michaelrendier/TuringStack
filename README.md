# Navigability of Modular Form Spaces via RedBlue Geometries
## Implications for Elliptic Curve Cryptography and Hash Function Security

**Status:** Pre-disclosure draft. DO NOT PUBLISH before coordinated disclosure is complete.  
**Disclosure path:** NIST → CISA → implementers → 180-day embargo → arXiv + IACR ePrint  
**Framework:** SMMIP / H_hat_RB — Wiles Conjugate (R̂† = B̂)  
**Author:** Cody Michael Allison <the.wandering.god@gmail.com>  
**Built with:** Claude Code (claude-sonnet-4-6)  
**Ethics:** White Hat. Responsible disclosure. Failed predictions stay in the record.

---

## Disclosure Contacts (in order)

1. `pqc-forum@nist.gov` + `crypto@nist.gov` — NIST Computer Security Division
2. `report@cisa.gov` — CISA critical infrastructure coordination
3. `openssl-security@openssl.org` — OpenSSL
4. `security@mozilla.org` — Mozilla NSS
5. `security@letsencrypt.org` — Let's Encrypt
6. Google VRP `g.co/vulnz` — BoringSSL / Chrome
7. `security@signal.org` — Signal Protocol

**Embargo:** 180 days from first NIST contact before any public disclosure.

---

## Paper Outline

See `paper_outline.md` for full structure.  
See `zero_divisor_attack.md` for the attack vector section (Section 5 — core contribution).  
See `sha1_demonstration.md` for the SHA-1 worked example.  
See `rsa_framework.md` for RSA in RedBlue coordinates.

---

## What Survives

CRYSTALS-Kyber, CRYSTALS-Dilithium, FALCON, SPHINCS+ (lattice and hash-based).
These do not rely on modular form hardness or prime distribution.
Post-quantum migration is the correct response regardless of this paper's outcome.

---

## Failed Predictions Stay in the Record

P3 (NFW concentration) failed in the SPARC analysis. It is documented.
Any negative results from cryptographic testing go in the paper.
Period. Full stop.
