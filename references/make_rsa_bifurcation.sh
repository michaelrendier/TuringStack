#!/usr/bin/env bash
# make_rsa_bifurcation.sh -- annotate the logistic bifurcation diagram to show
# where RSA and adjacent factoring maths sit.  Non-destructive: reads the clean
# source, writes a new file.  ImageMagick 6.x.
#
# Calibration (verified against logistic_bifurcation_ANNOTATED.png):
#   x_px = 583*r - 442                 (ORIGINAL 2021x935 frame)
#   y_px = 896 - 856*x_star
# Canvas extended +70 top, +370 bottom  ->  y_out = 966 - 856*x_star
#
# r anchors:  r=3 -> 1307   r_inf=3.5699 -> 1639   period-3 3.8284 -> 1790   r=4 -> 1890
set -e
cd "$(dirname "$0")"
SRC=logistic_bifurcation_windows_of_order.png
OUT=logistic_bifurcation_RSA.png
T="$(mktemp -u /tmp/rsa_bif_XXXXXX).png"

# --- pass 0 : extend canvas on white ---
convert "$SRC" -background white -gravity South -extent 2021x1005 \
               -background white -gravity North -extent 2021x1375 "$T"

# --- pass 1 : region tints ---
convert "$T" \
  -fill 'rgba(70,130,180,0.10)' -draw "rectangle 1307,118 1639,952" \
  -fill 'rgba(210,140,0,0.13)'  -draw "rectangle 1639,118 1890,952" \
  "$T"

# --- pass 2 : vertical reference lines + tick labels ---
convert "$T" -strokewidth 3 -fill none \
  -stroke '#1a7a3a' -draw "line 1307,118 1307,952" \
  -stroke '#c0161d' -draw "line 1639,118 1639,952" \
  -stroke '#7b1fa2' -draw "line 1790,118 1790,952" \
  "$T"
convert "$T" -font DejaVu-Sans -gravity NorthWest -pointsize 16 \
  -fill '#1a7a3a' -annotate +1258+96 "r=3  p=q" \
  -fill '#c0161d' -annotate +1600+96 "r-inf  chaos" \
  -fill '#7b1fa2' -annotate +1748+96 "period-3" \
  "$T"

# --- pass 3 : callout leader lines + target dots ---
convert "$T" -strokewidth 2 -fill '#111' -stroke '#111' \
  -draw "line 1150,470 1712,527" -draw "circle 1712,527 1717,527" \
  -draw "line 1188,392 1305,401" \
  -draw "line 1352,905 1742,932" -draw "circle 1742,932 1747,932" \
  "$T"

# --- pass 4 : band tags inside the plot ---
convert "$T" -font DejaVu-Sans -gravity NorthWest -pointsize 18 \
  -undercolor 'rgba(255,255,255,0.85)' \
  -fill '#33475b' -annotate +300+128 "period-1 : one determinant  (prime / prime power)" \
  -fill '#2c5378' -annotate +1312+128 "P2->chaos band = the Fermat regime" \
  -fill '#2c5378' -annotate +1312+152 "(p ~ q, branches near merge)" \
  -fill '#7a5100' -annotate +1648+128 "TELPERION bulk" \
  -fill '#7a5100' -annotate +1648+152 "GNFS sieves here" \
  "$T"

# --- pass 4c : NOT-A-BIFURCATION correction box (v2) ---
convert "$T" -strokewidth 3 -fill 'rgba(255,255,255,0.93)' -stroke '#c0161d' \
  -draw "rectangle 360,150 942,322" "$T"
convert "$T" -font DejaVu-Sans -gravity NorthWest \
  -fill '#c0161d' -pointsize 22 -annotate +380+168 "THE MODULUS IS NOT A BIFURCATION" \
  -fill '#111' -pointsize 18 \
  -annotate +380+202 "N = p*q is depth-1 : one split, two primes." \
  -annotate +380+228 "N = a^2 - b^2  (Fermat).  No cascade, no 2^k." \
  -annotate +380+262 "This maps WHERE THE METHODS LIVE, by regime --" \
  -annotate +380+288 "nothing about the modulus's own structure." \
  "$T"

# --- pass 5 : title + callouts over the plot ---
convert "$T" -font DejaVu-Sans -gravity NorthWest -fill '#111' \
  -pointsize 29 \
  -annotate +40+34 "WHERE THE FACTORING METHODS LIVE  --  the modulus itself is NOT a bifurcation" \
  -pointsize 21 -undercolor 'rgba(255,255,255,0.88)' \
  -annotate +430+446 "RSA-2048 : a  p:q  mode-lock window, width ~ 1/N" \
  -annotate +430+476 "the order is real; no scan reaches it" \
  -annotate +430+506 "its entry tangency = the structure RSA omits" \
  -annotate +820+372 "Fermat : p ~ q  (branches merge)" \
  -annotate +1030+890 "trial division / ECM : one factor near 0" \
  -annotate +1120+690 "period-3 = LAURELIN : order in chaos, opens at a tangent  -->" \
  -annotate +1050+606 "windows of order = where TELPERION hugs LAURELIN" \
  -annotate +1000+238 "Shor : reads the  p:q  rotation number directly" \
  "$T"

# --- pass 6 : caption block ---
convert "$T" -font DejaVu-Sans -gravity NorthWest -fill '#111' -pointsize 21 \
  -annotate +40+1030 "A composite IS a walk from 0 to N through exactly two primes :  N = a^2 - b^2.  Depth-1, NOT a bifurcation -- the cascade below only sorts the methods." \
  -annotate +40+1064 "the cascade is a MAP OF METHODS BY REGIME, not a model of the modulus.   pitchfork r=3 : p=q, the Fermat limit RSA forbids." \
  -annotate +40+1098 "chaotic bulk (r > 3.5699) = TELPERION : structure present, unreadable.  GNFS sieves it statistically (sub-exponential); never enters a window." \
  -annotate +40+1132 "windows of order = LAURELIN : genuine periodic structure inside the chaos, each opening at a tangent (saddle-node) = the entry point." \
  -annotate +40+1166 "RSA-2048 = a  p:q  mode-lock window of width ~ 1/N, exponentially narrow.  The order is real; you cannot scan to it." \
  -annotate +40+1200 "Shor reads the rotation number  p:q  directly -- a DTMF-style filter.  The diagram explains the hardness; it does not remove it." \
  -pointsize 15 -fill '#888' \
  -annotate +40+1248 "v2 (2026-09-01) -- corrected: the modulus is not a bifurcation construction.   logistic map x_{n+1}=r x_n(1-x_n),  x=583r-442, y=966-856x*.   build: make_rsa_bifurcation.sh" \
  "$OUT"

rm -f "$T"
identify -format '%f  %wx%h  %[colorspace]\n' "$OUT"
