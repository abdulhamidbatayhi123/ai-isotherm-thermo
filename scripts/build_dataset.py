"""Build the Paper 3A isotherm table from all sources (PREREG_P3A.md sections 3.3 and 3.4).

Every source is converted to SI (p in Pa, q in mol/kg, T in K), the preprocessing of
section 3.4 is applied identically, and the inclusion rules of section 3.3 are checked.
Outputs:
  data/raw/dataset/isotherms.csv    all included points (local: source licences)
  data/inclusion_log.csv            every material-source pair with its decision and reason
  data/dataset_summary.json         per material: set, class, temperatures, counts, ranges

Conversions:
  g/g -> mol/kg: / 0.01801528 kg/mol;  mmol/g = mol/kg;  cm3(STP)/g -> mol/kg: / 22.414
  mL/g (adsorbed liquid volume, characteristic curves) -> g/g: x RHO_LIQ_ASSUMED
  p/psat -> p: x psat_IAPWS(T);  A (kJ/mol) -> p/psat = exp(-1000 A / (R T));  bar -> Pa: x 1e5
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from p3a import water  # noqa: E402
from p3a.constants import R  # noqa: E402

M_W = 0.01801528  # kg/mol
V_STP = 22.414  # L/mol (0 C, 1 atm), the cm3(STP) convention
# Adsorbed-liquid density for W in mL/g. The source does not state its value; 1 g/mL is the
# common Dubinin convention. Using the IAPWS liquid density at 20-40 C instead changes q by
# 0.2 to 0.8 % (reported as a sensitivity, not used).
RHO_LIQ_ASSUMED = 1.0  # g/mL
RH_MAX = 0.90
MIN_POINTS = 8
MIN_POINTS_DEV = 5    # development set only (tuning, never scored): rule 2 relaxed, so that
                      # TFPPy-PDA-COF (7 points at 288 K) gives the set a COF (review I1)
MIN_TEMPS = 3
# Descriptive sensitivity variants (PREREG 3.3, review E2). "main" is the confirmatory rule set;
# the others write to data/raw/dataset/variants/<name>/ and data/variants/ and never replace it.
VARIANTS = ("main", "rule5_v1", "rule5_v2", "rule5_none", "minpoints7")
# coverage rule (PREREG_P3A.md section 3.3, rule 5; added 2026-11-03 before any fit, after
# the digitiser showed that covered markers can leave an isotherm with only its step):
# a gap in uptake is NOT a criterion: steep steps are physical (CORRECTIONS P3A-8)
MAX_GAP_RH = 0.25     # largest gap in p/psat between consecutive points (hidden plateau)
MAX_START_RH = 0.10   # the curve's start is present if the first point is at p/psat <= 0.10
MAX_START_Q = 0.10    # ... or at uptake <= 0.10 q_ref (a flat, empty pre-step region carries
                      # no information; COF-432 at 25 C is measured from p/psat 0.21 at 1 %)

ISODB = ROOT / "data/raw/isodb/records"
DIG = ROOT / "data/raw/digitised"
RAW = ROOT / "data/raw/primary"


def psat(T_K):
    return water.p_sat(torch.as_tensor(np.asarray(T_K, float))).numpy()


def isodb_adsorption(filename):
    """Adsorption branch of an ISODB record: the points up to the maximum pressure (a record
    may store a loop); pressure in Pa, q in the record's units."""
    r = json.loads((ISODB / f"{filename}.json").read_text())
    p = np.array([x["pressure"] for x in r["isotherm_data"]], float) * 1e5
    q = np.array([x["species_data"][0]["adsorption"] for x in r["isotherm_data"]], float)
    k = int(np.argmax(p))
    return float(r["temperature"]), p[: k + 1], q[: k + 1], r["adsorptionUnits"]


def to_molkg(q, unit):
    """q in mol/kg. (kg water per kg sorbent) / (kg/mol) = mol/kg, so g/g -> q / M_W."""
    unit = unit.strip()
    if unit == "g/g":
        return q / M_W
    if unit in ("mmol/g", "mol/kg"):
        return q
    if unit in ("cm3(STP)/g", "cm3STP/g"):
        return q / V_STP
    if unit == "mL/g":
        return q * RHO_LIQ_ASSUMED / M_W
    if unit == "wt%":
        # read as g water per 100 g sorbent (ISODB does not define it; the per-total-mass
        # reading w/(1+w) differs by up to 3 % at 25 wt% and is a stated ambiguity)
        return q / 100.0 / M_W
    raise ValueError(unit)


# ---------------------------------------------------------------- source registry

DEV = "development"
CONF = "confirmatory"


def src_isodb(material, cls, setname, key, files):
    rows = []
    for f in files:
        T, p, q, unit = isodb_adsorption(f)
        for pi, qi in zip(p, q):
            rows.append((material, cls, setname, key, T, pi, to_molkg(np.array(qi), unit).item(), "isodb-digitised"))
    return rows


def src_mgsu102():
    s = pd.read_excel(RAW / "mgsu102_2025_natcommun/41467_2025_59551_MOESM3_ESM.xlsx",
                      sheet_name="Figure4", header=None)
    rows = []
    for i, tc in enumerate([15, 20, 25, 30, 35, 40, 45, 50, 55]):
        rh = pd.to_numeric(s.iloc[3:, 2 * i], errors="coerce").to_numpy()
        q = pd.to_numeric(s.iloc[3:, 2 * i + 1], errors="coerce").to_numpy()
        ok = np.isfinite(rh) & np.isfinite(q)
        T = tc + 273.15
        for a, b in zip(rh[ok], q[ok]):
            rows.append(("Mg-SU-102", "MOF", CONF, "mgsu102_2025_natcommun", T, a * psat(T),
                         to_molkg(np.array(b), "g/g").item(), "numeric"))
    return rows


def src_digitised(key, material, cls, setname, source=None):
    """One digitised table; several keys (e.g. one panel per temperature) are grouped into
    one source by passing a list of keys and a common source name."""
    if isinstance(key, (list, tuple)):
        return [row for k in key for row in src_digitised(k, material, cls, setname, source)]
    d = pd.read_csv(DIG / f"{key}.csv")
    rows = []
    for _, r in d.iterrows():
        T = r["T_C"] + 273.15
        if r["x_quantity"] == "p/psat":
            rh = r["x"]
        elif r["x_quantity"] == "RH_percent":
            rh = r["x"] / 100.0
        elif r["x_quantity"] == "A_kJ_per_mol":
            rh = np.exp(-1000.0 * r["x"] / (R * T))
        elif r["x_quantity"] == "p_mmHg":  # absolute pressure, used as reported (PREREG 3.4)
            rh = r["x"] * 133.322368 / psat(T)
        else:
            raise ValueError(r["x_quantity"])
        rows.append((material, cls, setname, source or key, T, rh * psat(T),
                     to_molkg(np.array(r["q"]), r["q_unit"]).item(),
                     "vector-digitised" if "vector" in json.loads(
                         (ROOT / "data/digitised_provenance" / f"{key}.json").read_text())["method"]
                     else "raster-digitised"))
    return rows


def rezk(material, first, last):
    return [f"10.1016j.ijheatmasstransfer.2012.07.068.Isotherm{i}" for i in range(first, last + 1)]


SOURCES = [
    # development set (tuning only). Rezk 2012: the 9-temperature series (records 26 to 43,
    # one figure, common pressure grid); the second, 5-temperature series is not used.
    lambda: src_isodb("CuBTC", "MOF", DEV, "rezk2012", rezk("CuBTC", 26, 34)),
    lambda: src_isodb("MIL-100", "MOF", DEV, "rezk2012", rezk("MIL-100", 35, 43)),
    lambda: src_isodb("CAU-10-H", "MOF", DEV, "frohlich2014",
                      [f"10.1039C4dt02264e.Isotherm{i}" for i in (1, 2, 3)]),
    lambda: src_isodb("MIL-160", "MOF", DEV, "cadiau2015",
                      [f"10.1002adma.201502418.Isotherm{i}" for i in (6, 7, 8)]),
    # confirmatory set
    src_mgsu102,
    lambda: src_isodb("MIL-160(Al)", "MOF", CONF, "silva2021",
                      [f"10.1007s10450020002865.Isotherm{i}" for i in (12, 13, 14)]),
    lambda: src_digitised("nguyen2020_cof432", "COF-432", "COF", CONF),
    # measured isotherms (SI Fig. S9), not the characteristic curves derived from them (S8);
    # changed 2026-11-09 before any fit (CORRECTIONS P3A-20)
    lambda: src_digitised("rieth2017_co2cl2btdd_s9", "Co2Cl2(BTDD)", "MOF", CONF),
    lambda: src_digitised("cho2020_kmf1", "KMF-1", "MOF", CONF),
    lambda: src_digitised("kim2018_natcommun", "MOF-801", "MOF", CONF),
    lambda: src_digitised("hanikel2019_mof303", "MOF-303", "MOF", CONF),
    lambda: src_digitised("hanikel2019_alfum", "Al-fumarate", "MOF", CONF),
    lambda: src_digitised("abdulhalim2025_ketoenamine", "COF-TP-43", "COF", CONF),
    # ISODB multi-temperature rigid MOFs added 2026-11-03 before any fit (INVENTORY 1.2);
    # flexible/breathing frameworks (MIL-53 variants, Cu(C10H6O6)) stay out of scope
    lambda: src_isodb("CALF-25", "MOF", CONF, "taylor2012_calf25",
                      [f"10.1021Ja306812r.Isotherm{i}" for i in (3, 4, 5, 6)]),
    lambda: src_isodb("Zn2(bptc) (Lin 2006)", "MOF", CONF, "lin2006_znbptc",
                      [f"10.1021Ja060946u.Isotherm{i}" for i in (11, 14, 15, 16)]),
    lambda: src_digitised("nguyen2022_hcof_S43", "AB-COF", "COF", CONF),
    lambda: src_digitised("nguyen2022_hcof_S44", "COF-480-hydrazide", "COF", CONF),
    lambda: src_digitised("nguyen2022_hcof_S45", "Py-COF-2D", "COF", CONF),
    lambda: src_digitised("nguyen2022_hcof_S46", "COF-482-hydrazide", "COF", CONF),
    lambda: src_digitised("nguyen2025_hcof2", "HCOF-2", "COF", CONF),
    lambda: src_digitised("grunenberg2023_PI-3-COF", "PI-3-COF", "COF", CONF),
    lambda: src_digitised("grunenberg2023_NO-PI-3-COF", "NO-PI-3-COF", "COF", CONF),
    lambda: src_digitised("schweng2024_sulfoCOF", "COF-SO3H", "COF", CONF),
    *[(lambda m=m: src_digitised([f"tan2021_fig3{p}_{m}" for p in "abc"], m, "COF", CONF, "tan2021_fig3"))
      for m in ("HFPTP-PDA-COF", "HFPTP-DMePDA-COF", "HFPTP-BPDA-COF")],
    *[(lambda m=m: src_digitised([f"tan2021_fig4{p}_{m}" for p in "ijk"], m, "COF", CONF, "tan2021_fig4"))
      for m in ("TFBCz-PDA-COF", "TTA-TFB-COF", "TPB-DMTP-COF")],
    # moved to the development set on 2026-11-08, before any fit (review I1): excluded from the
    # confirmatory set by rule 2 alone, it gives the development set a COF
    lambda: src_digitised([f"tan2021_fig4{p}_TFPPy-PDA-COF" for p in "ijk"], "TFPPy-PDA-COF", "COF", DEV,
                          "tan2021_fig4"),
    lambda: src_digitised("nguyen2025_cof309", "COF-309", "COF", CONF),
]


# Rule 4 decisions that need the source itself, each with its evidence (PREREG 3.3)
RULE4_EXCLUDE = {
    ("KMF-1", "cho2020_kmf1"): (
        "excluded: rule 4. SI Fig. 18 (the characteristic curves digitised here) plots the 20 C "
        "isotherm a second time as '30 C': the two series coincide point by point in p/psat "
        "(A rescaled by 303.15/293.15), while the measured isotherms of main-text Fig. 2a step at "
        "about 0.11 (20 C) and 0.14 (30 C). Fig. 2a cannot replace it: its 20 and 30 C pre-step "
        "markers are covered by the open 40 C desorption markers (rule 5 / overlay gate). Decided "
        "2026-11-09 before any fit (CORRECTIONS P3A-20)."),
}


def coverage_failure(variant, h, hf, q_ref):
    """Rule 5 per isotherm; h is the isotherm after the 0.90 cut, hf the curve as published.
    Returns a reason string, or None if covered. Earlier versions kept for sensitivity
    (CORRECTIONS P3A-8): v1 adds an uptake-gap and an uptake-start test; v2 starts only at
    p/psat <= 0.10 and tests the gap after the cut."""
    if variant == "rule5_none":
        return None
    curve = h if variant == "rule5_v2" else hf
    gap_rh = float(np.diff(curve.rh).max()) if len(curve) > 1 else 1.0
    first = h.iloc[0]
    if variant == "rule5_v2":
        start_ok = first.rh <= MAX_START_RH
    elif variant == "rule5_v1":
        q = h.q_molkg.to_numpy()
        start_ok = first.q_molkg <= 0.25 * q_ref and (len(q) < 2 or np.diff(q).max() <= 0.25 * q_ref)
    else:
        start_ok = first.rh <= MAX_START_RH or first.q_molkg <= MAX_START_Q * q_ref
    if gap_rh > MAX_GAP_RH or not start_ok:
        return f"gap_rh={gap_rh:.3f} first_rh={first.rh:.3f} first_q/q_ref={first.q_molkg / q_ref:.3f}"
    return None


def main():
    variant = sys.argv[sys.argv.index("--variant") + 1] if "--variant" in sys.argv else "main"
    if variant not in VARIANTS:
        sys.exit(f"unknown variant {variant}; one of {VARIANTS}")
    min_conf = 7 if variant == "minpoints7" else MIN_POINTS
    cols = ["material", "class", "set", "source", "T_K", "p_Pa", "q_molkg", "provenance"]
    raw = pd.DataFrame([r for f in SOURCES for r in f()], columns=cols)
    raw["rh"] = raw["p_Pa"] / psat(raw["T_K"].to_numpy())
    log, keep = [], []
    for (mat, src), g in raw.groupby(["material", "source"], sort=False):
        full = g[g.p_Pa > 0]  # the curve as published: coverage is judged before the cut
        g = full[full.rh <= RH_MAX]
        per_T = g.groupby("T_K").size()
        q_ref = g.q_molkg.max()
        min_pts = MIN_POINTS_DEV if g["set"].iloc[0] == DEV else min_conf
        uncovered = {}
        for T, h in g.groupby("T_K"):
            h = h.sort_values("p_Pa")
            hf = full[full.T_K == T].sort_values("p_Pa")
            why = coverage_failure(variant, h, hf, q_ref)
            if why:
                uncovered[float(T)] = why
        good_T = [T for T in per_T[per_T >= min_pts].index if float(T) not in uncovered]
        short = {float(t): int(n) for t, n in per_T.items() if n < min_pts}
        ok = len(good_T) >= MIN_TEMPS and (mat, src) not in RULE4_EXCLUDE
        reason = (f"included: {len(good_T)} usable temperatures"
                  if ok else RULE4_EXCLUDE.get((mat, src),
                                               f"excluded: rules 1/2/5, {len(good_T)} usable temperatures"))
        if short:
            reason += f"; temperatures below {min_pts} points: {short}"
        if uncovered:
            reason += f"; temperatures failing coverage (rule 5): {uncovered}"
        log.append({"material": mat, "source": src, "set": g["set"].iloc[0], "class": g["class"].iloc[0],
                    "decision": "include" if ok else "exclude", "reason": reason,
                    "temperatures_K": ";".join(f"{t:.2f}" for t in sorted(per_T.index)),
                    "points_by_T": ";".join(str(int(per_T[t])) for t in sorted(per_T.index))})
        if ok:
            keep.append(g[g.T_K.isin(good_T)])
    out = pd.concat(keep).sort_values(["set", "material", "T_K", "p_Pa"])
    if variant == "main":
        ds_dir, log_path, summ_path = (ROOT / "data/raw/dataset", ROOT / "data/inclusion_log.csv",
                                       ROOT / "data/dataset_summary.json")
    else:
        ds_dir = ROOT / f"data/raw/dataset/variants/{variant}"
        (ROOT / "data/variants").mkdir(exist_ok=True)
        log_path = ROOT / f"data/variants/{variant}_inclusion_log.csv"
        summ_path = ROOT / f"data/variants/{variant}_dataset_summary.json"
    ds_dir.mkdir(parents=True, exist_ok=True)
    out.to_csv(ds_dir / "isotherms.csv", index=False)
    pd.DataFrame(log).to_csv(log_path, index=False)
    summ = {}
    for (mat, src), g in out.groupby(["material", "source"]):
        summ[f"{mat} | {src}"] = {
            "set": g["set"].iloc[0], "class": g["class"].iloc[0], "provenance": g["provenance"].iloc[0],
            "temperatures_K": sorted(round(t, 2) for t in g.T_K.unique()),
            "points_by_T": [int(n) for _, n in g.groupby("T_K").size().items()],
            "rh_range": [round(float(g.rh.min()), 4), round(float(g.rh.max()), 4)],
            "q_ref_molkg": round(float(g.q_molkg.max()), 4)}
    summ_path.write_text(json.dumps(summ, indent=2))
    for r in log:
        print(f"{r['decision']:8s} {r['set'][:4]} {r['material']:14s} {r['source']:24s} {r['reason']}")


if __name__ == "__main__":
    main()
