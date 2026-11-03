"""Colour-separability gate for raster figures (PREREG_P3A.md section 3.5).

A raster figure is digitised only if every pair of its series colours differs by at least
twice the colour tolerance of the detector (2 x 0.18 = 0.36 in RGB units scaled to [0, 1]).
Below that, the anti-aliased edges of one series fall inside another series' tolerance and
points can be assigned to the wrong temperature (or material).

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
        ok = d >= GATE
        out[fig] = {"n_series": len(cols), "closest_pair": [a, b], "distance": round(d, 4), "passes": ok,
                    "colours": {k: [round(float(v), 3) for v in c] for k, c in cols.items()}}
        rows.append({"figure": fig, "n_series": len(cols), "min_colour_distance": round(d, 4),
                     "gate": GATE, "decision": "digitise" if ok else "exclude (colours not separable)"})
    (ROOT / "logs/colour_separability.json").write_text(json.dumps(out, indent=2))
    pd.DataFrame(rows).to_csv(ROOT / "data/digitisation_gate_log.csv", index=False)
    for r in rows:
        print(f"{r['decision']:34s} min distance {r['min_colour_distance']:.3f}  {r['figure']}")


if __name__ == "__main__":
    main()
