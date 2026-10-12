"""Summarise the water data in CoRE MOF 2024 (Zenodo 10.5281/zenodo.15055758, v1.1).

Reads data/raw/coremof2024/water.zip (downloaded from
https://zenodo.org/records/15055758/files/water.zip) without extracting it and
writes data/coremof2024_water_summary.json: number of AIF files per subset,
temperatures, pressure grids, number of points, force fields, loading units,
and the sheet names / headers / row counts of water_data.xlsx and widom.xlsx.
Usage: python -I coremof2024_water_check.py
"""
import io
import json
import os
import re
import sys
import zipfile
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
ZP = os.path.join(DATA, "raw", "coremof2024", "water.zip")


def field(t, k):
    m = re.search(r"^" + re.escape(k) + r"\s+(.+)$", t, re.M)
    return m.group(1).strip() if m else None


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    z = zipfile.ZipFile(ZP)
    names = z.namelist()
    aif = [n for n in names if n.endswith(".aif")]
    out = {"zip": "water.zip", "n_entries": len(names), "n_aif": len(aif),
           "aif_by_subset": dict(Counter(n.split("/")[1] for n in aif))}
    c = {k: Counter() for k in ("temperature", "forcefield_adsorbent", "forcefield_adsorptive",
                                 "units_loading", "units_pressure", "n_points", "pressure_grid", "p0",
                                 "header_comment")}
    for n in aif:
        t = z.read(n).decode("utf-8", "replace")
        c["temperature"][field(t, "_exptl_temperature")] += 1
        c["forcefield_adsorbent"][field(t, "_simltn_forcefield_adsorbent")] += 1
        c["forcefield_adsorptive"][field(t, "_simltn_forcefield_adsorptive")] += 1
        c["units_loading"][field(t, "_units_loading")] += 1
        c["units_pressure"][field(t, "_units_pressure")] += 1
        c["header_comment"][" | ".join(l for l in t.splitlines() if l.startswith("#"))] += 1
        rows = t.split("_adsorp_amount", 1)[1].split()
        nums = [float(x) for x in rows if re.match(r"^-?[0-9.eE+-]+$", x)]
        ps = nums[0::3]
        p0 = nums[1::3]
        c["n_points"][len(ps)] += 1
        c["pressure_grid"][";".join(f"{p:g}" for p in ps)] += 1
        c["p0"][";".join(sorted({f"{p:g}" for p in p0}))] += 1
    for k, v in c.items():
        out[k] = dict(v.most_common(10))
    out["readme"] = z.read("README.txt").decode("utf-8", "replace")
    try:
        import openpyxl
        for x in ("water_data.xlsx", "widom.xlsx"):
            xn = [n for n in names if n.endswith(x)][0]
            wb = openpyxl.load_workbook(io.BytesIO(z.read(xn)), read_only=True, data_only=True)
            out[x] = {}
            for ws in wb.worksheets:
                it = ws.iter_rows(values_only=True)
                hdr = next(it, None)
                first = next(it, None)
                nrow = 2 + sum(1 for _ in it)
                out[x][ws.title] = {"header": [str(h) for h in (hdr or [])], "first_row": [str(v) for v in (first or [])], "n_rows_incl_header": nrow}
    except ImportError:
        out["xlsx"] = "openpyxl not installed"
    with open(os.path.join(DATA, "coremof2024_water_summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
