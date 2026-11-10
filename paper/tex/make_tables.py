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


# material names with chemical formulas, typeset with subscripts (other names print as written)
CHEM = {"Co2Cl2(BTDD)": r"Co\textsubscript{2}Cl\textsubscript{2}(BTDD)",
        "Zn2(bptc)": r"Zn\textsubscript{2}(bptc)",
        "COF-SO3H": r"COF-SO\textsubscript{3}H"}


def mat_name(key):
    """'Zn2(bptc) (Lin 2006) | lin2006_znbptc' -> typeset material name."""
    name = key.split("|")[0].strip().split(" (")[0]
    return CHEM.get(name, tex_escape(name))


def load_runs():
    rows = []
    for f in sorted((ROOT / "results").glob("confirmatory_runs.shard*.jsonl")):
        rows += [json.loads(x) for x in f.read_text(encoding="utf-8").splitlines() if x.strip()]
    return rows


def table_permaterial():
    """Per-material error ratios 10^d_m of P against each comparator (results/verdicts.json)."""
    vd = json.loads((ROOT / "results/verdicts.json").read_text(encoding="utf-8"))
    ds = json.loads((ROOT / "data/dataset_summary.json").read_text(encoding="utf-8"))
    cols = [("H1b", vd["H1"]["H1b"]), ("H1c", vd["H1"]["H1c"]), ("H1d", vd["H1"]["H1d"]),
            ("H1e", vd["H1"]["H1e"]), ("H1a", vd["descriptive"]["H1a"]),
            ("", vd["descriptive"]["D-Vnone"]), ("", vd["descriptive"]["D-Frel"])]
    runs = load_runs()
    ntrain = {}
    for r in runs:
        if r["cell"] == "P" and r["task"] in ("E-high", "E-low"):
            ntrain[r["material"]] = min(ntrain.get(r["material"], 99), len(r["train_T"]))
    mats = sorted(cols[0][1]["d_by_material"], key=lambda k: (ds[k]["class"], k.lower()))
    rows = []
    for m in mats:
        cells = [f"{10 ** c['d_by_material'][m]:.2f}" for _, c in cols]
        rows.append(" & ".join([mat_name(m), ds[m]["class"], str(ntrain[m])] + cells) + r" \\")
    hr = " & ".join([f"{c['R']:.2f}" for _, c in cols])
    head = (r"\begin{tabular}{llr" + "r" * len(cols) + "}\n" r"\toprule" "\n"
            r" & & & \multicolumn{" + str(len(cols)) + r"}{c}{$R_m = E_{\mathrm{P}}/E_X$} \\" "\n"
            r"\cmidrule(l){4-" + str(3 + len(cols)) + "}\n"
            r"Material & Class & $n_{\mathrm{train}}$ & " + " & ".join(
                (f"{h} " if h else "") + c["X"] for h, c in cols) + r" \\" "\n" r"\midrule")
    return ("% written by paper/tex/make_tables.py from results/verdicts.json and the run shards; do not edit\n"
            + r"{\footnotesize\setlength{\tabcolsep}{2pt}" + "\n" + head + "\n" + "\n".join(rows) + "\n" + r"\midrule" + "\n"
            + r"Hodges-Lehmann $R$ & & & " + hr + r" \\" + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}}" + "\n")


def table_h3():
    """Violating fits per model (results/verdicts.json, H3)."""
    vd = json.loads((ROOT / "results/verdicts.json").read_text(encoding="utf-8"))["H3"]
    order = ["P", "F-hard", "A-hard", "C1", "P-K", "V-pen", "V-none", "F-pen", "A-pen", "A-none", "F-rel", "F-none"]
    rows = []
    for c in order:
        v, a = vd["cells"][c], vd["cells_all_tasks"][c]
        lo, hi = v["wilson95"]
        rows.append(" & ".join([c, str(v["fits"]), str(v["violating_in_domain"]), f"{lo:.2f}--{hi:.2f}",
                                str(v["violating_extrapolated_band"]), str(v["violating_strict"]),
                                f"{a['violating_in_domain']}/{a['fits']}", v["class"]]) + r" \\")
    head = (r"\begin{tabular}{lrrlrrll}" "\n" r"\toprule" "\n"
            r"Model & Fits & In domain & Wilson 95\,\% & Band & Strict & All tasks & Class \\" "\n" r"\midrule")
    return ("% written by paper/tex/make_tables.py from results/verdicts.json; do not edit\n"
            + r"{\small" + "\n" + head + "\n" + "\n".join(rows) + "\n" + r"\bottomrule" + "\n"
            + r"\end{tabular}}" + "\n")


CLASS_WORD = {"P_better": "P better", "X_better": "X better", "equivalent": "equivalent",
              "differ_small": "differ by less than 25\\,\\%", "differ_uncertain": "differ, size uncertain",
              "inconclusive": "inconclusive"}


def table_h2():
    """The 15 isosteric-heat tests (results/verdicts.json, H2)."""
    h2 = json.loads((ROOT / "results/verdicts.json").read_text(encoding="utf-8"))["H2"]
    rows = []
    for fam in ("KS", "DA", "FG", "HS", "TC"):
        for X in ("V-pen", "A-hard", "F-none"):
            r = h2[f"H2-{fam}-{X}"]
            lo, hi = r["R_ci95"]
            word = f"{X} better" if r["class"] == "X_better" else CLASS_WORD[r["class"]]
            rows.append(" & ".join([fam if X == "V-pen" else "", X, f"{r['R']:.3g}", f"{lo:.3g}--{hi:.3g}",
                                    f"{r['p_adj']:.3f}", f"{r['failures']['P']}/{r['failures']['X']}", word]) + r" \\")
    head = (r"\begin{tabular}{llrlrll}" "\n" r"\toprule" "\n"
            r"Truth & Comparator $X$ & $R$ & 95\,\% interval & Holm $p$ & Failed P/$X$ & Verdict \\" "\n" r"\midrule")
    return ("% written by paper/tex/make_tables.py from results/verdicts.json; do not edit\n"
            + r"{\small" + "\n" + head + "\n" + "\n".join(rows) + "\n" + r"\bottomrule" + "\n"
            + r"\end{tabular}}" + "\n")


SENS = [("rule5_v1", "coverage rule, first version"), ("rule5_v2", "coverage rule, second version"),
        ("rule5_none", "no coverage rule"), ("minpoints7", "7 points per isotherm"),
        ("co2cl2_s8", "Co\\textsubscript{2}Cl\\textsubscript{2}(BTDD) from its characteristic curves"),
        ("perturb_s1", "digitisation shift, copy 1"), ("perturb_s2", "digitisation shift, copy 2")]


def table_sens():
    """H1 verdicts on the pre-registered dataset variants (results/sensitivity_<name>.json)."""
    vd = json.loads((ROOT / "results/verdicts.json").read_text(encoding="utf-8"))
    rows = []

    def cells(h1):
        out = []
        for h in ("H1b", "H1c", "H1d", "H1e"):
            r = h1[h]
            lo, hi = r["R_ci95"]
            c = r["class"]
            tag = {"P_better": "P", "X_better": "X", "equivalent": "eq", "differ_small": "d<25",
                   "differ_uncertain": "d", "inconclusive": "inc"}[c]
            out.append(f"{r['R']:.2f} [{lo:.2f}, {hi:.2f}] {tag}")
        return out
    rows.append(" & ".join(["confirmatory set", str(vd["H1"]["H1b"]["n_materials"])] + cells(vd["H1"])) + r" \\")
    for name, label in SENS:
        s = json.loads((ROOT / f"results/sensitivity_{name}.json").read_text(encoding="utf-8"))
        rows.append(" & ".join([label, str(s["n_materials"])] + cells(s["H1"])) + r" \\")
    head = (r"\begin{tabular}{lrllll}" "\n" r"\toprule" "\n"
            r"Dataset & $n$ & H1b V-pen & H1c A-hard & H1d F-none & H1e C1 \\" "\n" r"\midrule")
    return ("% written by paper/tex/make_tables.py from results/verdicts.json and results/sensitivity_*.json; "
            "do not edit\n" + r"{\footnotesize\setlength{\tabcolsep}{3pt}" + "\n" + head + "\n" + "\n".join(rows)
            + "\n" + r"\bottomrule" + "\n" + r"\end{tabular}}" + "\n")


def table_seeds():
    """Seed spread of the held-out error per model (results/descriptive_seeds.json)."""
    sd = json.loads((ROOT / "results/descriptive_seeds.json").read_text(encoding="utf-8"))["seed_spread_E_tasks"]
    order = ["P", "V-pen", "V-none", "A-hard", "A-pen", "A-none", "C1", "F-hard", "F-pen", "F-none", "F-rel", "P-K"]
    rows = [" & ".join([c, str(sd[c]["records"]), f"{sd[c]['median_range_decades']:.2f}",
                        f"{sd[c]['max_range_decades']:.2f}", str(sd[c]["records_range_over_1_decade"]),
                        str(sd[c]["selected_was_best_heldout"]), str(sd[c]["selected_was_worst_heldout"])]) + r" \\"
            for c in order]
    head = (r"\begin{tabular}{lrrrrrr}" "\n" r"\toprule" "\n"
            r"Model & Fits & Median range & Largest range & Range above 1 & Selected best & Selected worst \\" "\n"
            r"\midrule")
    return ("% written by paper/tex/make_tables.py from results/descriptive_seeds.json; do not edit\n"
            + r"{\small" + "\n" + head + "\n" + "\n".join(rows) + "\n" + r"\bottomrule" + "\n"
            + r"\end{tabular}}" + "\n")


def table_dataset():
    ds = json.loads((ROOT / "data/dataset_summary.json").read_text(encoding="utf-8"))
    rows = []
    for key in sorted(ds, key=lambda k: (ds[k]["set"] != "confirmatory", ds[k]["class"], k.lower())):
        v = ds[key]
        src = key.split("|")[1].strip()
        prefix = src.split("_")[0]
        doi = SRC_DOI[prefix]
        T = v["temperatures_K"]
        prov = PROV.get(v["provenance"], v["provenance"])
        rows.append(" & ".join([
            mat_name(key), v["class"], "conf." if v["set"] == "confirmatory" else "dev.", prov,
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


TABLES = {"tab_dataset.tex": table_dataset, "tab_permaterial.tex": table_permaterial,
          "tab_h3.tex": table_h3, "tab_seeds.tex": table_seeds,
          "tab_h2.tex": table_h2, "tab_sens.tex": table_sens}


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
