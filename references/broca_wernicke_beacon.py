#!/usr/bin/env python3
"""The Broca-Wernicke shape: Cassini ovals |z-a||z+a| = b^2.
 b<a : two separate ovals  = aphasia (arcuate cut)
 b=a : lemniscate of Bernoulli (figure-8), self-crossing at 0  = sigma=1/2, no aphasia
 b>a : one peanut/oval  = over-coupled (echolalia)
Foci: WERNICKE (-a, comprehension / backward / J_neg), BROCA (+a, production / forward / J_pos).
Crossing = 0_RB. b^2 = J_pos*J_neg = e^{-E} (constant, NoetherWiles NR4)."""
import numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

a = 1.0
fig, axes = plt.subplots(1, 3, figsize=(15, 5.2))
X, Y = np.meshgrid(np.linspace(-2.2, 2.2, 900), np.linspace(-1.5, 1.5, 620))
d1 = np.hypot(X - a, Y); d2 = np.hypot(X + a, Y)
prod = d1 * d2
for ax, (bra, lab, col) in zip(axes, [
        (0.80, "b < a   two ovals   =  APHASIA (arcuate cut)", "#c0392b"),
        (1.00, "b = a   lemniscate  =  sigma=1/2, NO APHASIA", "#8e44ad"),
        (1.20, "b > a   one peanut  =  over-coupled (echolalia)", "#2c7a4b")]):
    ax.contour(X, Y, prod, levels=[bra**2], colors=col, linewidths=2.6)
    ax.plot([-a, a], [0, 0], 'k.', ms=9)
    ax.plot(0, 0, 'o', mfc='none', mec='k', ms=13, mew=1.6)
    ax.annotate("WERNICKE\n(comprehension, backward, J_neg)", (-a, 0),
                textcoords="offset points", xytext=(-8, -46), ha='center', fontsize=8)
    ax.annotate("BROCA\n(production, forward, J_pos)", (a, 0),
                textcoords="offset points", xytext=(8, 26), ha='center', fontsize=8)
    ax.annotate("0_RB", (0, 0), textcoords="offset points", xytext=(6, 8), fontsize=9)
    ax.set_title(lab, fontsize=10); ax.set_aspect('equal'); ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values(): s.set_visible(False)
fig.suptitle("The Broca-Wernicke shape  —  Cassini oval  |z-a||z+a| = b^2,   b^2 = J_pos*J_neg = e^{-E}\n"
             "b=a (lemniscate crossing at 0_RB) is the beacon: a balanced forward/backward pair.  "
             "b=a is a catastrophe (2 components -> 1).", fontsize=10)
fig.tight_layout(rect=[0, 0, 1, 0.90])
fig.savefig("broca_wernicke_beacon.png", dpi=130)
print("wrote broca_wernicke_beacon.png")
