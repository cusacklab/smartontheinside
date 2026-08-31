"""Colour-vision-deficiency check for categorical palettes.

Simulates dichromacy (Vienot et al. 1999) and reports OKLab Delta-E between every
pair of palette colours. Thresholds follow the project's visualisation guidance:
Delta-E >= 8 target for CVD separation, >= 15 for normal vision.
"""
from __future__ import annotations
import itertools, sys
import numpy as np

_RGB2LMS = np.array([[17.8824, 43.5161, 4.11935],
                     [3.45565, 27.1554, 3.86714],
                     [0.0299566, 0.184309, 1.46709]])
_LMS2RGB = np.linalg.inv(_RGB2LMS)
_SIM = {
    "protanopia": np.array([[0, 2.02344, -2.52581], [0, 1, 0], [0, 0, 1]]),
    "deuteranopia": np.array([[1, 0, 0], [0.494207, 0, 1.24827], [0, 0, 1]]),
    "tritanopia": np.array([[1, 0, 0], [0, 1, 0], [-0.395913, 0.801109, 0]]),
}

def hex_to_linear(h):
    h = h.lstrip("#")
    c = np.array([int(h[i:i+2], 16) / 255 for i in (0, 2, 4)])
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)

def simulate(lin, kind):
    lms = _RGB2LMS @ lin
    return np.clip(_LMS2RGB @ (_SIM[kind] @ lms), 0, 1)

def oklab(lin):
    m = np.array([[0.4122214708, 0.5363325363, 0.0514459929],
                  [0.2119034982, 0.6806995451, 0.1073969566],
                  [0.0883024619, 0.2817188376, 0.6299787005]])
    c = np.cbrt(m @ lin)
    n = np.array([[0.2104542553, 0.7936177850, -0.0040720468],
                  [1.9779984951, -2.4285922050, 0.4505937099],
                  [0.0259040371, 0.7827717662, -0.8086757660]])
    return n @ c

def delta_e(a, b):
    return float(np.linalg.norm(oklab(a) - oklab(b)) * 100)

def validate(colors, *, cvd_min=8.0, normal_min=15.0):
    lins = [hex_to_linear(c) for c in colors]
    ok = True
    print(f"palette: {' '.join(colors)}  (n={len(colors)})\n")
    worst_n = min((delta_e(lins[i], lins[j]), colors[i], colors[j])
                  for i, j in itertools.combinations(range(len(colors)), 2))
    status = "PASS" if worst_n[0] >= normal_min else "FAIL"
    ok &= worst_n[0] >= normal_min
    print(f"normal vision : min dE = {worst_n[0]:5.1f}  ({worst_n[1]} vs {worst_n[2]})  "
          f"[>= {normal_min}] {status}")
    for kind in _SIM:
        sims = [simulate(l, kind) for l in lins]
        worst = min((delta_e(sims[i], sims[j]), colors[i], colors[j])
                    for i, j in itertools.combinations(range(len(colors)), 2))
        status = "PASS" if worst[0] >= cvd_min else "FAIL"
        ok &= worst[0] >= cvd_min
        print(f"{kind:14s}: min dE = {worst[0]:5.1f}  ({worst[1]} vs {worst[2]})  "
              f"[>= {cvd_min}] {status}")
    print(f"\noverall: {'PASS' if ok else 'FAIL'}")
    return ok

if __name__ == "__main__":
    cols = sys.argv[1].split(",") if len(sys.argv) > 1 else []
    sys.exit(0 if validate([c.strip() for c in cols]) else 1)
