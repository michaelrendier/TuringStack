#!/usr/bin/env python3
"""
The Chladni figure hypercomplex_laplacian.py names but never renders.

Main panel: 32x32 grid, cell(i,j) = popcount(e_i . e_j) in T32/GF(2) --
the actual nodal-line structure of the algebra itself. Black = exact
zero-divisor pair (on the nodal line). Brighter = farther from it.
This is the whole T32 Laplacian's nodal pattern in one view, dimension-
and message-independent -- the fixed background SHA-1's constants sit in.

Side strip: SHA-1's 9 real constants (5 IVs + 4 round constants K),
each as its 32-bit pattern, colour-coded by whether it's nilpotent
(on the nodal line -- the "composite" reading) using the exact same
trace_laplacian() theorem already proven in hypercomplex_laplacian.py.
"""

import sys
sys.path.insert(0, '/storage/emulated/0/ThePlace/TuringStack')
from hypercomplex_laplacian import t32_mul, is_nilpotent, trace_laplacian
from PIL import Image, ImageDraw

DIM = 32
CELL = 18
MARGIN = 40
STRIP_H = 40

SHA1_CONSTANTS = [
    ('H0', 0x67452301), ('H1', 0xEFCDAB89), ('H2', 0x98BADCFE),
    ('H3', 0x10325476), ('H4', 0xC3D2E1F0),
    ('K0', 0x5A827999), ('K1', 0x6ED9EBA1), ('K2', 0x8F1BBCDC), ('K3', 0xCA62C1D6),
]

# ── Main panel: COMPOSITE-pair product grid -- this is where real ZD
# pairs actually live (single basis pairs are always popcount=1, never
# zero -- confirmed empirically, corrected from a first pass at this
# image). Composites = e_i+e_j (i<j), C(32,2)=496 of them. In GF(2),
# subtraction=addition, so no sign ambiguity to track here. ─────────────

composites = [((1 << i) | (1 << j), f"{i}+{j}")
              for i in range(DIM) for j in range(i + 1, DIM)]
N = len(composites)
CELL2 = 2

grid = [[0] * N for _ in range(N)]
n_zd = 0
for a in range(N):
    ca, _ = composites[a]
    for b in range(N):
        cb, _ = composites[b]
        prod = t32_mul(ca, cb, DIM)
        pop = bin(prod).count('1')
        grid[a][b] = pop
        if pop == 0 and a != b:
            n_zd += 1

W = MARGIN + N * CELL2 + 20
H = MARGIN + N * CELL2 + STRIP_H * len(SHA1_CONSTANTS) + 80
img = Image.new('RGB', (W, H), (250, 250, 252))
draw = ImageDraw.Draw(img)

for a in range(N):
    for b in range(N):
        pop = grid[a][b]
        if pop == 0:
            color = (255, 210, 20) if a != b else (10, 10, 15)  # ZD pair = gold; self = black
        else:
            t = pop / DIM
            color = (int(15 + 20 * t), int(15 + 20 * t), int(40 + 60 * t))
        x0 = MARGIN + b * CELL2
        y0 = MARGIN + a * CELL2
        draw.rectangle([x0, y0, x0 + CELL2 - 1, y0 + CELL2 - 1], fill=color)

draw.text((MARGIN, 10),
          f"T32/GF(2) COMPOSITE-pair Laplacian: (e_i+e_j).(e_k+e_l), {N}x{N} = {N*N:,} pairs, "
          f"gold = exact ZD ({n_zd} found)", fill=(0, 0, 0))

# ── Side strip: SHA-1's real constants, bit pattern + nilpotency ──────────

strip_y = MARGIN + N * CELL2 + 30
draw.text((MARGIN, strip_y - 15), "SHA-1's real constants, bit pattern + trace-Laplacian nodal test:",
          fill=(0, 0, 0))
bit_w = (N * CELL2) / 32.0
for k, (name, w) in enumerate(SHA1_CONSTANTS):
    y0 = strip_y + k * STRIP_H
    t = trace_laplacian(w, DIM)
    nodal = t['on_nodal_line']
    for b in range(32):
        bit = (w >> (31 - b)) & 1
        x0 = MARGIN + int(b * bit_w)
        x1 = MARGIN + int((b + 1) * bit_w)
        if bit:
            color = (200, 30, 30) if nodal else (30, 120, 200)
        else:
            color = (235, 235, 238)
        draw.rectangle([x0, y0, x1 - 1, y0 + STRIP_H - 12], fill=color)
    label = f"{name}=0x{w:08X}  nilpotent={nodal}  spectral_dist={t['spectral_dist']}"
    draw.text((MARGIN, y0 + STRIP_H - 12), label, fill=(0, 0, 0))

out_path = "/storage/emulated/0/ThePlace/TuringStack/sha1_chladni_figure.png"
img.save(out_path)
print(f"Saved {out_path}")
print(f"Grid: {n_zd} / {N*N:,} composite pairs are exact zero-divisor pairs (nodal line)")
for name, w in SHA1_CONSTANTS:
    t = trace_laplacian(w, DIM)
    print(f"  {name}: nilpotent={t['on_nodal_line']}  spectral_dist={t['spectral_dist']}")
