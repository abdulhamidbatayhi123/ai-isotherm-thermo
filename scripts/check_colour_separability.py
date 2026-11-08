"""Colour-separability gate for raster figures (PREREG_P3A.md section 3.5).

A series of a raster figure is digitised only if its colour differs from EVERY other series
colour present in the figure (used or not) by at least twice the colour tolerance of the
detector (2 x 0.18 = 0.36 in RGB units scaled to [0, 1]). Below that, the anti-aliased edges
of one series fall inside another series' tolerance and points can be assigned to the wrong
temperature (or material). A figure passes if at least 3 temperature series of one material
pass (rule 1).

Revised 2026-11-08 before any fit (review E3; CORRECTIONS P3A-17): the first version required
EVERY pair of series to be separable, so one close pair excluded a whole figure. The decisions
are unchanged: every figure that passed still passes; the two Fathieh 2018 figures now have 6
of 9 separable series but are excluded by the overlay gate (section 3.5), because the
adsorption steps of all nine temperatures coincide and are drawn over each other. The CIE76
colour difference (Delta E in L*a*b*, D65) is reported beside the RGB distance.

Colours: for digitised figures, the series colours recorded in data/digitised_provenance;
figures that share one image (Tan 2021 panels) are grouped. For the Fathieh et al. 2018 SI
figures, the legend markers are sampled here (median of a 5 x 5 patch at each legend marker).
Output: logs/colour_separability.json and data/digitisation_gate_log.csv.
"""
import collections
import itertools
import json
import sys
from pathlib import Path

import fitz
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import digitise  # noqa: E402

TOL = 0.18
GATE = 2 * TOL


def min_pair(cols):
    pairs = [(a, b, float(np.linalg.norm(np.asarray(cols[a]) - np.asarray(cols[b]))))
             for a, b in itertools.combinations(cols, 2)]
    return min(pairs, key=lambda t: t[2]) if pairs else (None, None, float("inf"))


def srgb_to_lab(c):
    c = np.asarray(c, float)
    lin = np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)
    M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750],
                  [0.0193339, 0.1191920, 0.9503041]])
    xyz = M @ lin / np.array([0.95047, 1.0, 1.08883])
    f = np.where(xyz > (6 / 29) ** 3, np.cbrt(xyz), xyz / (3 * (6 / 29) ** 2) + 4 / 29)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


def per_series(cols):
    """For each series: the smallest RGB distance and CIE76 Delta E to any other series."""
    out = {}
    for a in cols:
        others = [b for b in cols if b != a]
        if not others:
            out[a] = (float("inf"), float("inf"))
            continue
        out[a] = (min(float(np.linalg.norm(np.asarray(cols[a]) - np.asarray(cols[b]))) for b in others),
                  min(float(np.linalg.norm(srgb_to_lab(cols[a]) - srgb_to_lab(cols[b]))) for b in others))
    return out


OVERLAY_EXCLUDED = {
    "fathieh2018 SI fig. S6 (MOF-801)": "adsorption steps of all nine temperatures coincide in p/psat and "
                                        "are drawn over each other (the 45 and 50 C markers hide the others)",
    "fathieh2018 SI fig. S23 (MOF-303)": "adsorption steps of all nine temperatures coincide in p/psat and "
                                         "are drawn over each other (the 45 and 50 C markers hide the others)",
}


def main():
    groups = collections.defaultdict(dict)
    for f in sorted((ROOT / "data/digitised_provenance").glob("*.json")):
        d = json.loads(f.read_text())
        if "raster" not in d.get("method", ""):
            continue
        fig = f"{d['key'].split('_fig')[0]}:{d['figure']}" if d["key"].startswith("tan2021") else d["key"]
        for label, s in d["series"].items():
            groups[fig][f"{d['key']}:{label}"] = s["colour"]
    # Fathieh et al. 2018 (10.1126/sciadv.aat3198) SI figs. S6 (MOF-801) and S23 (MOF-303):
    # legend markers at the same image positions in both figures (1320 x 1064 px)
    pdf = fitz.open(ROOT / "data/raw/primary/fathieh2018_sciadv/aat3198_SM.pdf")
    for page_no, xref, name in ((16, 54, "fathieh2018 SI fig. S6 (MOF-801)"),
                                (45, 181, "fathieh2018 SI fig. S23 (MOF-303)")):
        img = digitise.load_page_image(pdf[page_no - 1], xref=xref)
        for tc, yd in zip(range(10, 55, 5), range(238, 600, 40)):
            r, c = int(yd * 1.5), int(652 * 1.5)
            groups[name][f"{tc} C"] = np.median(img[r - 2: r + 3, c - 2: c + 3].reshape(-1, 3), axis=0).tolist()
    out, rows = {}, []
    for fig, cols in groups.items():
        a, b, d = min_pair(cols)
        ps = per_series(cols)
        sep = [k for k, (dist, _) in ps.items() if dist >= GATE]
        colour_ok = len(sep) >= 3
        if not colour_ok:
            decision = "exclude (fewer than 3 separable series)"
        elif fig in OVERLAY_EXCLUDED:
            decision = "exclude (overlay gate: " + OVERLAY_EXCLUDED[fig] + ")"
        else:
            decision = "digitise"
        out[fig] = {"n_series": len(cols), "closest_pair": [a, b], "distance": round(d, 4),
                    "separable_series": sep, "passes_colour_gate": colour_ok, "decision": decision,
                    "per_series_min_rgb": {k: round(v[0], 4) for k, v in ps.items()},
                    "per_series_min_deltaE76": {k: round(v[1], 2) for k, v in ps.items()},
                    "colours": {k: [round(float(v), 3) for v in c] for k, c in cols.items()}}
        rows.append({"figure": fig, "n_series": len(cols), "min_colour_distance": round(d, 4),
                     "separable_series": len(sep),
                     "min_deltaE76": round(min(v[1] for v in ps.values()), 2),
                     "gate": GATE, "decision": decision})
    (ROOT / "logs/colour_separability.json").write_text(json.dumps(out, indent=2))
    pd.DataFrame(rows).to_csv(ROOT / "data/digitisation_gate_log.csv", index=False)
    for r in rows:
        print(f"{r['decision']:34s} min distance {r['min_colour_distance']:.3f}  {r['figure']}")


if __name__ == "__main__":
    main()
