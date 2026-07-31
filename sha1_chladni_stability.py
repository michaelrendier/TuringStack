#!/usr/bin/env python3
"""
sha1_chladni_stability.py -- research-quality version of the composite-pair
Chladni figure (sha1_chladni_figure.py), with the Mandelbrot render's
continuous stability metric applied instead of a binary ZD/not-ZD split.

"Periodic table one layer below the elements" (Cody, 2026-07-17): single
basis elements (e_i) are always units, never zero-divisors -- confirmed
empirically earlier this session. The real structure lives one layer
down, at COMPOSITE pairs (e_i+e_j, i<j -- two "atoms" bonded), the same
way H2's stability is a question about a bond, not about hydrogen alone.
This renders every one of the C(32,2)=496 composite elements against
every other as a continuous stability gradient (popcount of the product
= distance from the zero-divisor locus, the same role escape/convergence
speed played in the 4000x4000 Mandelbrot render), not a yes/no.

Panel 2 keeps the SHA-1 real-constants strip from the first pass --
independently useful, kept unchanged in substance, restyled to match.
"""

import sys
sys.path.insert(0, '/storage/emulated/0/ThePlace/TuringStack')
from hypercomplex_laplacian import t32_mul, trace_laplacian

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.colors import ListedColormap, LinearSegmentedColormap
from matplotlib.patches import Patch

DIM = 32

SHA1_CONSTANTS = [
    ('H0', 0x67452301), ('H1', 0xEFCDAB89), ('H2', 0x98BADCFE),
    ('H3', 0x10325476), ('H4', 0xC3D2E1F0),
    ('K0', 0x5A827999), ('K1', 0x6ED9EBA1), ('K2', 0x8F1BBCDC), ('K3', 0xCA62C1D6),
]

# ── Build the composite-pair stability grid ────────────────────────────────

composites = [((1 << i) | (1 << j), i, j) for i in range(DIM) for j in range(i + 1, DIM)]
N = len(composites)
print(f"Composite elements (e_i+e_j, i<j): {N}")

grid = np.zeros((N, N), dtype=np.int32)
for a in range(N):
    ca = composites[a][0]
    for b in range(N):
        cb = composites[b][0]
        grid[a, b] = bin(t32_mul(ca, cb, DIM)).count('1')

n_zd = int(np.sum((grid == 0) & ~np.eye(N, dtype=bool)))
print(f"Exact zero-divisor pairs found: {n_zd} / {N*N - N:,} off-diagonal cells")
print(f"Stability distance range: {grid.min()} (exact ZD) to {grid.max()} (maximally stable)")

# ── Figure ──────────────────────────────────────────────────────────────

fig = plt.figure(figsize=(13, 15), dpi=160, facecolor='#0a0a12')
gs = GridSpec(2, 1, height_ratios=[4.6, 1.0], hspace=0.16, figure=fig,
              top=0.91, bottom=0.055, left=0.085, right=0.965)

ax1 = fig.add_subplot(gs[0])
ax1.set_facecolor('#0a0a12')

VMAX = int(grid.max())  # real data range is 0-4, not 0-32 -- a 2-term
                         # composite times a 2-term composite expands to
                         # at most 4 basis terms, so popcount cannot
                         # exceed 4. Fixing the colour scale to the real
                         # range instead of the algebra's full dimension
                         # is what makes the gradient visible at all.
# Bifurcation gradient: 0 = the zero-divisor locus, the collapse/branch
# point a composite pair sits on or falls away from -- red. Farther away
# (popcount rising toward VMAX) is the stable branch -- blue. Not viridis:
# the two ends are the two sides of the bifurcation, not an arbitrary scale.
cmap = LinearSegmentedColormap.from_list('bifurcation_r2b', ['#FF0000', '#0000FF'])
im = ax1.imshow(grid, cmap=cmap, vmin=0, vmax=VMAX, origin='upper',
                interpolation='nearest', aspect='equal')

# Mark exact zero-divisor cells (the "black hole" / bond-collapse cells)
# with a distinct gold contour-style overlay so they stay identifiable
# even though they're now the dark end of a continuous scale, not a
# separate binary colour.
zd_mask = (grid == 0) & ~np.eye(N, dtype=bool)
ys, xs = np.where(zd_mask)
ax1.scatter(xs, ys, s=1.1, c='#ffd014', marker='s', linewidths=0, alpha=0.85,
            label=f'exact zero-divisor bond ({n_zd:,})')

ax1.set_xlabel("Composite index b  (e_i+e_j, i<j — 496 pairwise \"bonds\")",
               color='#aaaaaa', fontsize=10)
ax1.set_ylabel("Composite index a  (e_i+e_j, i<j — 496 pairwise \"bonds\")",
               color='#aaaaaa', fontsize=10)
ax1.tick_params(colors='#888888', labelsize=8)

# Sparse, readable tick labels showing the actual (i,j) basis pair at
# regular intervals, not every one of the 496 (unreadable at that density)
tick_idx = list(range(0, N, 40)) + [N - 1]
tick_labels = [f"{composites[k][1]},{composites[k][2]}" for k in tick_idx]
ax1.set_xticks(tick_idx); ax1.set_xticklabels(tick_labels, rotation=90, fontsize=7)
ax1.set_yticks(tick_idx); ax1.set_yticklabels(tick_labels, fontsize=7)

cbar = fig.colorbar(im, ax=ax1, fraction=0.0455, pad=0.02, ticks=range(VMAX + 1))
cbar.set_label("Stability distance\n(popcount of product)", color='#cccccc', fontsize=9)
cbar.ax.tick_params(colors='#888888', labelsize=9)
cbar.outline.set_edgecolor('#555555')

fig.text(0.085, 0.008,
         "Stability distance: 0 = exact zero-divisor (the bond collapses, gold-marked) — "
         "higher popcount = farther from the locus, i.e. a more stable bond. "
         "Real range for 2-term composites is 0-4, not the algebra's full 32.",
         color='#888888', fontsize=8, ha='left')

legend = ax1.legend(loc='upper right', facecolor='#161620', edgecolor='#444444',
                     labelcolor='#dddddd', fontsize=8, markerscale=6, framealpha=0.9)

for spine in ax1.spines.values():
    spine.set_edgecolor('#444444')

# ── Panel 2: SHA-1's real constants ────────────────────────────────────────

ax2 = fig.add_subplot(gs[1])
ax2.set_facecolor('#0a0a12')
ax2.set_xlim(0, 32)
ax2.set_ylim(0, len(SHA1_CONSTANTS))
ax2.invert_yaxis()

for k, (name, w) in enumerate(SHA1_CONSTANTS):
    t = trace_laplacian(w, DIM)
    nodal = t['on_nodal_line']
    row_color_bit1 = '#e04030' if nodal else '#3070c0'
    for b in range(32):
        bit = (w >> (31 - b)) & 1
        color = row_color_bit1 if bit else '#20202a'
        ax2.add_patch(plt.Rectangle((b, k + 0.06), 1, 0.82, facecolor=color,
                                     edgecolor='none'))
    label = f"{name} = 0x{w:08X}   nilpotent={nodal}   spectral_dist={t['spectral_dist']}"
    ax2.text(32.4, k + 0.5, label, color='#cccccc', fontsize=8.3,
              va='center', ha='left', family='monospace')

ax2.set_xlim(0, 60)
ax2.set_xticks([])
ax2.set_yticks([])
for spine in ax2.spines.values():
    spine.set_visible(False)
ax2.set_title("SHA-1's real constants: bit pattern + trace-Laplacian nodal-line test",
              color='#dddddd', fontsize=10.5, loc='left', pad=8)

legend_elems = [
    Patch(facecolor='#e04030', label='bit=1, nilpotent (IVs — on the nodal line)'),
    Patch(facecolor='#3070c0', label='bit=1, not nilpotent (round constants K)'),
    Patch(facecolor='#20202a', label='bit=0'),
]
ax2.legend(handles=legend_elems, loc='lower left', bbox_to_anchor=(0.0, -0.32),
           ncol=3, facecolor='#161620', edgecolor='#444444', labelcolor='#cccccc',
           fontsize=7.5, framealpha=0.9)

fig.suptitle(
    "T32/GF(2) Composite-Pair Stability Map — the periodic table one layer below\n"
    "single basis elements: 496 pairwise \"bonds\" (e_i+e_j), each tested against\n"
    "every other for continuous distance from the zero-divisor locus",
    color='#ffffff', fontsize=13, y=0.985, weight='bold', linespacing=1.6)

out = "/storage/emulated/0/ThePlace/TuringStack/sha1_chladni_stability.png"
fig.savefig(out, facecolor=fig.get_facecolor())
print(f"Saved {out}")
