"""Look up the Paper 3A priority materials in the ISODB pure-water records.

Input : data/isodb_water_records.csv (from isodb_water_inventory.py)
Output: data/isodb_priority_materials.csv (one row per priority material x DOI)
Matching is by case-insensitive regular expression on the ISODB adsorbent name;
the patterns are listed in PRIORITY below and every match is written out so that
false positives can be checked by eye.
Usage : python -I isodb_priority_materials.py
"""
import csv
import os
import re
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)

PRIORITY = {
    "COF-432": r"COF-?432",
    "COF (any)": r"COF",
    "MOF-303": r"MOF-?303",
    "MOF-801": r"MOF-?801",
    "MOF-841": r"MOF-?841",
    "CAU-10": r"CAU-?10",
    "CAU-23": r"CAU-?23",
    "Al-fumarate (A520)": r"fumarate|A520|Al-?Fum|Basolite A",
    "MIL-160": r"MIL-?160",
    "M2Cl2(BTDD)": r"BTDD",
    "MIL-100": r"MIL-?100",
    "MIL-101": r"MIL-?101",
    "UiO-66": r"UiO-?66",
    "KMF-1": r"KMF",
    "MOF-LA2-1": r"LA2-\d",
    "CPO-27 / MOF-74": r"CPO-?27|MOF-?74|dobdc",
    "HKUST-1": r"HKUST|Cu-?BTC|Cu3\(BTC\)",
    "MIL-53": r"MIL-?53",
    "ZIF-8": r"ZIF-?8\b",
}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    rows = [r for r in csv.DictReader(open(os.path.join(DATA, "isodb_water_records.csv"), encoding="utf-8"))
            if r["fetch_status"] == "ok"]
    out = []
    for label, pat in PRIORITY.items():
        rx = re.compile(pat, re.I)
        grp = defaultdict(list)
        for r in rows:
            if rx.search(r["material_name"]):
                grp[(r["DOI"], r["material_name"])].append(r)
        for (doi, name), rs in sorted(grp.items()):
            ts = sorted({round(float(r["temperature_K"]), 1) for r in rs})
            out.append({
                "priority_label": label, "pattern": pat, "DOI": doi, "material_name": name,
                "n_isotherms": len(rs), "n_distinct_T": len(ts), "temperatures_K": ";".join(f"{t:g}" for t in ts),
                "n_points_each": ";".join(r["n_points"] for r in rs),
                "categories": ";".join(sorted({r["category"] for r in rs})),
                "tabular_data": ";".join(sorted({r["tabular_data"] for r in rs})),
                "pressure_units": ";".join(sorted({r["pressure_units"] for r in rs})),
                "adsorption_units": ";".join(sorted({r["adsorption_units"] for r in rs})),
                "pressure_trends": ";".join(sorted({r["pressure_trend_heuristic"] for r in rs})),
            })
        n_mat = len({k[1] for k in grp})
        tset = sorted({round(float(r["temperature_K"]), 1) for v in grp.values() for r in v})
        print(f"{label:22s} isotherms={sum(len(v) for v in grp.values()):4d} material_names={n_mat:3d} DOIs={len({k[0] for k in grp}):3d} T={tset[:12]}")
    with open(os.path.join(DATA, "isodb_priority_materials.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
