# The cost of the digit-by-digit factor search is the order of a unit group

**Researcher:** Cody Michael Allison — the.wandering.god@gmail.com
**ORCID:** https://orcid.org/0009-0007-7239-6760
**Date:** 2026-10-14
**Disclosure posture:** White hat. Nothing here breaks, weakens or speeds up the factoring of anything. It states, exactly, the cost of a search that is already known to be exponential, so that the cost can be read off instead of measured. No CVE is sought and no embargo applies.
**Nature of this document:** a white paper on one exact counting fact — not a research paper, and it keeps no history of superseded results.
**Tier:** `[ESTABLISHED:CALCULATED]` — elementary number theory; every statement below is checked by code over the stated range.
**Engine:** `ValaQuenta/modules/addition_matrix/` (v1.0) · **Explorer:** `MultiplicationMatrixExplorer` (`factor_reconstruction.py`, `toolsets/law.py`).

---

## The one fact

Write N = p·q with p, q of n decimal digits. Reconstruct p and q from N one column of the long-multiplication addition matrix at a time, from the units end: after column c a candidate pair (p′, q′) mod 10^(c+1) survives only if p′·q′ ≡ N (mod 10^(c+1)). The number of survivors is exactly

```
count(N, c)  =  f₂ · f₅,   f_p = (v+1)·φ(p^(c+1))            if v = v_p(N) < c+1
                           f_p = (c+1)·φ(p^(c+1)) + p^(c+1)    if N ≡ 0 mod p^(c+1)
```

For N coprime to 10 this is 4·10ᶜ — the order of the unit group (ℤ/10^(c+1))ˣ — for every column c < n. The survivors form one torsor of that group, acting by (p′, q′) → (u·p′, u⁻¹·q′); every survivor has exactly ten lifts to the next column. With a factor of 2 or 5 in N the set is (v₂+1)(v₅+1) such torsors. At column n the size of the factors enters and the count collapses (to 2 for the true pair and its swap).

**Machine-verified:** closed form against enumeration for every N in [0, 2·10ᵏ+50), k = 1, 2, 3; live-state counts of the Explorer's search equal the closed form in every column below n for N = 3233, 14351, 1022117, 420, 850, 5100; uniform 10-fold branching for N = 3233, 14351. (`ValaQuenta/tests/test_addition_matrix.py`, 11 tests.)

## What it says about security — and does not

- **Cost.** At column n−1 the search holds 4·10^(n−1) states. For a 2048-bit RSA modulus (about 308 digits per factor) that is about 4·10³⁰⁷. The law removes the need to run the search to know this; it does not lower it.
- **Partial knowledge.** Knowing p modulo 10ᵏ fixes q modulo 10ᵏ and leaves one survivor at column k−1, then ten at column k, a hundred at column k+1: measured on N = 1009·1013 (survivors by column, k known digits: k = 1: 1, 10, 100, 1000; k = 2: ·, 1, 10, 100; k = 3: ·, ·, 1, 10). Each known low-order digit divides the live set by 10; the first also removes the factor 4. This is the same lift used when part of a key is known (see the pointer below); it gives no advantage when nothing is known.
- **The address.** For a unit survivor mod 10ⁿ, K = (p′q′ − N)/10ⁿ is an integer, and the true factorisation is exactly K = 0. It is unique among zero-overflow survivors but **not isolated**: among 30 semiprimes of two 3-digit primes, every N had 400 survivors and exactly 2 with K = 0, while the smallest nonzero |K| among the others ranged from 1 to 15 over two seeded samples of 30 (1 to 14 and 1 to 15). To test K one needs the survivor set, which is the 4·10^(n−1)-element set above. The group's own coordinates give no signature that picks the true pair in advance; only the size constraint does.
- **Not a factoring method.** No claim is made of polynomial-time or sub-exponential factoring, and the code does not provide one.

## Pointer (Post-Hoc, not verified here)

Branch-and-prune lifting from the low-order bits is published for recovering RSA keys when some key bits are known: N. Heninger and H. Shacham, *Reconstructing RSA Private Keys from Random Key Bits*, CRYPTO 2009 (ePrint 2008/510). That file could not be downloaded (the host returned a bot-challenge page; not bypassed) and has not been read by the author of this note; it is listed in `ContextPlease/claude/references/INDEX.md` as not downloaded. This note claims only the decimal-column count above.

## Reproduce

```
python3 -c "from ValaQuenta.modules.addition_matrix import maths as M; print(M.live_state_counts(14351, 3), [M.solution_count_closed(14351, c+1) for c in range(3)])"
# [4, 40, 400, 48, 4, 2]  [4, 40, 400]
python3 MultiplicationMatrixExplorer/toolsets/law.py      # {'closed_form_mismatches': 0, 'pair_at_K0': True}
```

## What survives

This note concerns an elementary count and changes nothing about which schemes are sound. Post-quantum migration remains the correct response to the quantum threat to factoring-based schemes regardless of this note.
