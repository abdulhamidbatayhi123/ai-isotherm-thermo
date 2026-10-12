"""Summarise the numeric (spreadsheet) files found among the primary-literature downloads.

Reads, read-only, the small xlsx files under data/raw/primary/ (files > 5 MB are
listed but not opened, to stay within the RAM budget) and writes
data/primary_numeric_files_summary.json: per sheet, the header rows and, for each
column pair, the number of numeric rows. For Mg-SU-102 (Figure4 sheet) it also
records per-temperature point counts and RH ranges.
Usage: python -I primary_numeric_check.py
"""
import json
import os
import sys

import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
PRIM = os.path.join(DATA, "raw", "primary")


def isnum(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    out = {}
    for d in sorted(os.listdir(PRIM)):
        for fn in sorted(os.listdir(os.path.join(PRIM, d))):
            if not fn.lower().endswith(".xlsx"):
                continue
            p = os.path.join(PRIM, d, fn)
            key = f"{d}/{fn}"
            size = os.path.getsize(p)
            if size > 5_000_000:
                out[key] = {"bytes": size, "opened": False}
                continue
            wb = openpyxl.load_workbook(p, read_only=True, data_only=True)
            sheets = {}
            for ws in wb.worksheets:
                rows = list(ws.iter_rows(values_only=True))
                head = [[str(v) if v is not None else "" for v in r[:24]] for r in rows[:4]]
                ncol = max((len(r) for r in rows), default=0)
                numeric_per_col = [sum(1 for r in rows if c < len(r) and isnum(r[c])) for c in range(min(ncol, 40))]
                sheets[ws.title] = {"n_rows": len(rows), "n_cols": ncol, "head": head,
                                    "numeric_rows_per_col": numeric_per_col}
                if d.startswith("mgsu102") and ws.title == "Figure4":
                    per_t = {}
                    for c in range(0, ncol - 1, 2):
                        label = rows[0][c]
                        if label is None:
                            continue
                        xs = [r[c] for r in rows[3:] if c + 1 < len(r) and isnum(r[c]) and isnum(r[c + 1])]
                        if xs:
                            per_t[str(label)] = {"n_points": len(xs), "rh_min": min(xs), "rh_max": max(xs)}
                    sheets[ws.title]["per_temperature"] = per_t
            wb.close()
            out[key] = {"bytes": size, "opened": True, "sheets": sheets}
    with open(os.path.join(DATA, "primary_numeric_files_summary.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, ensure_ascii=False)
    for k, v in out.items():
        print(k, v.get("bytes"), list(v.get("sheets", {}).keys()))
        if "sheets" in v and "Figure4" in v["sheets"]:
            print(json.dumps(v["sheets"]["Figure4"].get("per_temperature"), ensure_ascii=False))


if __name__ == "__main__":
    main()
