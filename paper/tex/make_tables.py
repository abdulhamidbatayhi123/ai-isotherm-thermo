"""Write the generated LaTeX tables of the Paper 3A manuscript from the result and data files.

    python paper/tex/make_tables.py           # (re)write every table file
    python paper/tex/make_tables.py --check   # exit 1 if a table file differs from what the sources give

build_ms.py gate G8 runs the check, so a table cannot go stale. Every number in a table comes from the
file named in its generator; the tables are \\input into si.tex and main.tex (G1 does not scan them, G8 does).
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

# Source key prefix of data/dataset_summary.json -> DOI. Each DOI is checked against the repository's own
# Crossref check (data/primary_doi_check.csv, crossref_status ok) or, for ISODB sets, data/INVENTORY.md.
SRC_DOI = {
    "hanikel2019": "10.1021/acscentsci.9b00745",
    "taylor2012": "10.1021/ja306812r",
    "nguyen2020": "10.1021/jacs.9b13094",
    "nguyen2022": "10.1021/acscentsci.2c00398",
    "schweng2024": "10.1002/cssc.202301906",
    "rieth2017": "10.1021/acscentsci.7b00186",
    "rezk2012": "10.1016/j.ijheatmasstransfer.2012.07.068",
    "tan2021": "10.1038/s41467-021-27128-4",
    "cadiau2015": "10.1002/adma.201502418",
    "mgsu102": "10.1038/s41467-025-59551-2",
    "grunenberg2023": "10.1021/jacs.3c02572",
    "lin2006": "10.1021/ja060946u",
}
PROV = {"raster-digitised": "raster", "vector-digitised": "vector", "numeric": "numeric", "isodb-digitised": "ISODB"}


def check_dois():
    ok = {r["doi"].lower() for r in csv.DictReader(open(ROOT / "data/primary_doi_check.csv", encoding="utf-8"))
          if r["crossref_status"] == "ok"}
    inv = (ROOT / "data/INVENTORY.md").read_text(encoding="utf-8").lower()
    # ISODB file ids are the DOI without its slash (scripts/build_dataset.py src_isodb calls)
    isodb = (ROOT / "scripts/build_dataset.py").read_text(encoding="utf-8").lower()
    bad = [d for d in SRC_DOI.values()
           if d.lower() not in ok and d.lower() not in inv and d.lower().replace("/", "") + ".isotherm" not in isodb]
    if bad:
        raise SystemExit(f"DOIs not found in the repository's DOI checks: {bad}")


def tex_escape(s):
    return s.replace("_", r"\_").replace("&", r"\&")


def table_dataset():
    ds = json.loads((ROOT / "data/dataset_summary.json").read_text(encoding="utf-8"))
    rows = []
    for key in sorted(ds, key=lambda k: (ds[k]["set"] != "confirmatory", ds[k]["class"], k.lower())):
        v = ds[key]
        name, src = [x.strip() for x in key.split("|")]
        name = name.split(" (")[0]          # "Zn2(bptc) (Lin 2006)": the source is in its own column
        prefix = src.split("_")[0]
        doi = SRC_DOI[prefix]
        T = v["temperatures_K"]
        prov = PROV.get(v["provenance"], v["provenance"])
        rows.append(" & ".join([
            tex_escape(name), v["class"], "conf." if v["set"] == "confirmatory" else "dev.", prov,
            r"\ID{" + tex_escape(doi) + "}",
            f"{min(T):.2f}--{max(T):.2f}", str(len(T)),
            f"{min(v['points_by_T'])}--{max(v['points_by_T'])}",
            f"{v['rh_range'][0]:.2g}--{v['rh_range'][1]:.3f}", f"{v['q_ref_molkg']:.2f}"]) + r" \\")
    head = (r"\begin{tabular}{llllllrlll}" "\n" r"\toprule" "\n"
            r"Material & Class & Set & Data & Source DOI & $T$ range (K) & $n_T$ & Points per $T$ & $\pss$ range"
            r" & $\qref$ (mol\,kg$^{-1}$) \\" "\n" r"\midrule")
    return ("% written by paper/tex/make_tables.py from data/dataset_summary.json; do not edit\n"
            + r"{\scriptsize\setlength{\tabcolsep}{3pt}" + "\n" + head + "\n" + "\n".join(rows) + "\n"
            + r"\bottomrule" + "\n" + r"\end{tabular}}" + "\n")


TABLES = {"tab_dataset.tex": table_dataset}


def main():
    check_dois()
    check = "--check" in sys.argv
    stale = []
    for name, fn in TABLES.items():
        text = fn()
        p = HERE / name
        if check:
            if not p.exists() or p.read_text(encoding="utf-8").replace("\r\n", "\n") != text:
                stale.append(name)
        else:
            p.write_text(text, encoding="utf-8", newline="\n")
            print("wrote", p)
    if stale:
        print("STALE tables (rerun paper/tex/make_tables.py):", stale)
        sys.exit(1)


if __name__ == "__main__":
    main()
