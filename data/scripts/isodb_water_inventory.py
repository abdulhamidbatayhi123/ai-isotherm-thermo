"""Inventory of pure-water isotherms in the NIST/ARPA-E ISODB.

Steps
1. Fetch the gas list and find water by name (InChIKey taken from the API, not hard coded).
2. Fetch the isotherm index and keep records whose only adsorbate is water.
3. Fetch every pure-water record (cached as raw JSON under data/raw/isodb/records/,
   one file per record, 0.2 s pause between requests; cached files are reused).
4. Write data/isodb_water_records.csv (one row per isotherm).
5. Write data/isodb_water_multiT.csv (per material x DOI) and
   data/isodb_water_multiT_by_material.csv (per material across DOIs),
   plus data/isodb_water_summary.json with all counts quoted in INVENTORY.md.

Material class heuristic (ISODB matdb has no class field; materials.json only has
hashkey, name, synonyms): regular expressions on the adsorbent name, applied in
the order COF, zeolite/zeotype, MOF (names, linker abbreviations, metal-bracket
formulas, and Hill-type formulas containing C plus a framework metal), carbon or
polymer, silica/oxide/salt, other. See classify(). It is a heuristic: inspect
material_name in the CSVs before relying on a class label for a given material.

Branch: ISODB records carry no adsorption/desorption field. We report
`pressure_trend` from the order of the pressure points: 'increasing'
(adsorption-like), 'decreasing' (desorption-like), 'up_then_down' (loop stored in
one record), 'mixed'. This is a heuristic and is labelled as such.

Usage: python -I isodb_water_inventory.py [--no-fetch]
"""
import csv
import json
import os
import re
import sys
import time
from collections import defaultdict

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
RAW = os.path.join(DATA, "raw", "isodb")
REC_DIR = os.path.join(RAW, "records")
BASE = "https://adsorption.nist.gov"
UA = {"User-Agent": "ai-isotherm-thermo data inventory (academic research script)"}


def get_json(url, timeout=120):
    for attempt in range(4):
        try:
            r = requests.get(url, headers=UA, timeout=timeout)
            if r.status_code == 200:
                return r.json()
            print(f"HTTP {r.status_code} {url}", flush=True)
        except Exception as e:  # network hiccup
            print(f"error {e!r} {url}", flush=True)
        time.sleep(2 + 3 * attempt)
    return None


def safe_name(fn):
    return re.sub(r"[^A-Za-z0-9._-]", "_", fn) + ".json"


COF_RE = re.compile(r"COF|covalent organic framework|\bTp[A-Z]|\bTAPB|\bTAPT|\bTFP|\bDAAQ|\bBTD-TAPB|\bPy-|imine[- ]linked|triazine framework|\bCTF-", re.I)
ZEO_RE = re.compile(r"zeolite|zeotype|\b13X\b|\bNaX\b|\bNaY\b|\b[345]A\b|\bZSM|\bSAPO|\bAlPO|AlPO4|chabazite|\bCHA\b|\bFAU\b|\bLTA\b|\bMFI\b|silicalite|mordenite|clinoptilolite|\bSSZ-|\bBEA\b|beta zeolite|faujasite|\bH-?Y\b|\bUSY\b|\bAFI\b|\bLTL\b|ferrierite|\bKFI\b|\bRHO\b|\bSOD\b|sodalite|\bFER\b|analcime|\bAEI\b|\bERI\b|\bMOR\b|\bMWW\b|\bNa-?A\b|\bK-?A\b|\bCa-?A\b|\bLi-?X|\bCa-?X", re.I)
MOF_RE = re.compile(r"MOF|\bZIF|\bUiO|\bMIL-|\bHKUST|\bCAU-|IRMOF|\bCu-?BTC|Cu3\(BTC\)|Basolite|\bPCN-|\bNU-\d|\bDUT-|\bMAF-|\bSIFSIX|\bZJU-|\bUTSA-|\bBUT-|\bKMF|\bA520|fumarate|\bMOP\b|\bbtdd|BTDD|\bbdc|BDC|\bbtc|\bbpy|bipy|\bdobdc|dobpdc|\bdhtp|\bCPO-27|\bted\b|\bdabco|pyrazine|imidazol|\bLa?-?BTB|\bBTB\b|\bbtb\b|\bTCPP|\bPCP|coordination polymer|metal[- ]organic|\bSNU-|\bJUC-|\bFJI-|\bSBMOF|\bMFM-|\bSTA-\d|\bCUK-|\bMIP-|\bNOTT-|\bFMOF|\bAl-?fum|\bMg-?MOF|\bZn\(|\bCu\(|\bCo\(|\bNi\(|\bFe\(|\bZr\(|\bAl\(|\bCr\(|\bMn\(|\bCd\(|\bMg\(|\[Zn|\[Cu|\[Co|\[Ni|\[Fe|\[Zr|\[Al|\[Cr|\[Mn|\[Cd|\[Mg|\[Ln|\[Eu|\[Tb|\[La|\[Ca|\[Sr|\[Ba", re.I)
CARBON_RE = re.compile(r"carbon|graphen|graphit|charcoal|\bCNT|nanotube|\bAC\b|activated|\bPOC\b|\bPAF|polymer|resin|\bPIM|porous organic|Maxsorb|Norit|Kureha|BPL", re.I)
SILICA_RE = re.compile(r"silica|\bMCM-|\bSBA-|alumina|titania|\bclay|bentonite|montmorillonite|\bSiO2|Al2O3|\boxide\b|aerogel|silicagel|silica gel|cellulose|\bsalt\b|CaCl2|LiCl|LiBr", re.I)


EXTRA_MOF_RE = re.compile(r"\bCALF-|\bSU-\d|\bMOF\b|\bbnn-", re.I)
# Hill-type formula containing carbon and a framework metal, e.g. "Zn2C14N2O8H4", "C12H12O4Zn"
FORMULA_MOF_RE = re.compile(r"^(?=.*C\d)(?=.*(Zn|Cu|Co|Ni|Fe|Al|Zr|Cr|Mg|Mn|Cd|Ti|Ga|In|Sc|La|Ce|Eu|Tb|Ca|Sr|Ba|Hf|V)\d*)[A-Za-z0-9().·*\s]+$")


def classify(name):
    n = name or ""
    if COF_RE.search(n):
        return "COF"
    if ZEO_RE.search(n):
        return "zeolite"
    if MOF_RE.search(n) or EXTRA_MOF_RE.search(n):
        return "MOF"
    if FORMULA_MOF_RE.match(n.strip()):
        return "MOF"
    if CARBON_RE.search(n):
        return "carbon_or_polymer"
    if SILICA_RE.search(n):
        return "silica_oxide_salt"
    return "other_unclassified"


def trend(ps):
    if len(ps) < 2:
        return "single_point"
    d = [b - a for a, b in zip(ps, ps[1:])]
    up = sum(x > 0 for x in d)
    dn = sum(x < 0 for x in d)
    if dn == 0:
        return "increasing"
    if up == 0:
        return "decreasing"
    k = max(range(len(ps)), key=lambda i: ps[i])
    if all(x >= 0 for x in d[:k]) and all(x <= 0 for x in d[k:]):
        return "up_then_down"
    return "mixed"


def main():
    fetch = "--no-fetch" not in sys.argv
    os.makedirs(REC_DIR, exist_ok=True)

    gases = get_json(BASE + "/isodb/api/gases.json")
    water = [g for g in gases if (g.get("name") or "").strip().lower() == "water"]
    assert len(water) == 1, water
    WKEY = water[0]["InChIKey"]
    print("water InChIKey", WKEY, flush=True)

    index = get_json(BASE + "/isodb/api/isotherms.json", timeout=300)
    n_index = len(index)
    any_water = [x for x in index if any(a.get("InChIKey") == WKEY for a in x["adsorbates"])]
    pure = [x for x in any_water if len(x["adsorbates"]) == 1]
    del index
    print(f"index {n_index} isotherms; water-containing {len(any_water)}; pure water {len(pure)}", flush=True)
    with open(os.path.join(RAW, "index_pure_water.json"), "w", encoding="utf-8") as f:
        json.dump({"retrieved": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "water_InChIKey": WKEY,
                   "n_index_total": n_index, "n_water_containing": len(any_water),
                   "records": pure}, f, indent=0)

    rows = []
    key_union = set()
    for i, x in enumerate(pure):
        fn = x["filename"]
        path = os.path.join(REC_DIR, safe_name(fn))
        rec = None
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                rec = json.load(f)
        elif fetch:
            rec = get_json(BASE + "/isodb/api/isotherm/" + requests.utils.quote(fn, safe="") + ".json", timeout=60)
            time.sleep(0.2)
            if rec is not None:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(rec, f)
        if i % 100 == 0:
            print(f"{i}/{len(pure)}", flush=True)
        if rec is None:
            rows.append({"filename": fn, "DOI": x["DOI"], "fetch_status": "failed"})
            continue
        key_union.update(rec.keys())
        pts = rec.get("isotherm_data") or []
        ps = [p.get("pressure") for p in pts if p.get("pressure") is not None]
        qs = [p.get("total_adsorption") for p in pts if p.get("total_adsorption") is not None]
        ads = rec.get("adsorbent") or {}
        rows.append({
            "filename": fn,
            "DOI": rec.get("DOI", x["DOI"]),
            "material_name": (ads.get("name") or "").strip(),
            "material_id": ads.get("hashkey", x["adsorbent"].get("hashkey")),
            "material_class_heuristic": classify(ads.get("name")),
            "temperature_K": rec.get("temperature"),
            "n_points": len(pts),
            "pressure_units": rec.get("pressureUnits"),
            "p_min": min(ps) if ps else "",
            "p_max": max(ps) if ps else "",
            "adsorption_units": rec.get("adsorptionUnits"),
            "q_max": max(qs) if qs else "",
            "category": rec.get("category"),
            "tabular_data": rec.get("tabular_data"),
            "digitizer": rec.get("digitizer"),
            "articleSource": rec.get("articleSource"),
            "date": rec.get("date"),
            "isotherm_type": rec.get("isotherm_type"),
            "pressure_trend_heuristic": trend(ps),
            "fetch_status": "ok",
        })

    cols = ["filename", "DOI", "material_name", "material_id", "material_class_heuristic", "temperature_K",
            "n_points", "pressure_units", "p_min", "p_max", "adsorption_units", "q_max", "category",
            "tabular_data", "digitizer", "articleSource", "date", "isotherm_type",
            "pressure_trend_heuristic", "fetch_status"]
    with open(os.path.join(DATA, "isodb_water_records.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow(r)

    ok = [r for r in rows if r.get("fetch_status") == "ok"]

    def tkey(t):
        return round(float(t), 1)

    # per material x DOI
    by_md = defaultdict(list)
    for r in ok:
        by_md[(r["material_id"], r["DOI"])].append(r)
    md_rows = []
    for (mid, doi), rs in by_md.items():
        ts = sorted({tkey(r["temperature_K"]) for r in rs})
        ts_ads = sorted({tkey(r["temperature_K"]) for r in rs if r["pressure_trend_heuristic"] in ("increasing", "up_then_down")})
        md_rows.append({
            "material_id": mid, "material_name": rs[0]["material_name"],
            "material_class_heuristic": rs[0]["material_class_heuristic"], "DOI": doi,
            "n_isotherms": len(rs), "n_distinct_T": len(ts), "temperatures_K": ";".join(f"{t:g}" for t in ts),
            "n_distinct_T_adsorption_like": len(ts_ads),
            "categories": ";".join(sorted({str(r["category"]) for r in rs})),
            "tabular_data_values": ";".join(sorted({str(r["tabular_data"]) for r in rs})),
            "pressure_units": ";".join(sorted({str(r["pressure_units"]) for r in rs})),
            "adsorption_units": ";".join(sorted({str(r["adsorption_units"]) for r in rs})),
            "total_points": sum(int(r["n_points"]) for r in rs),
        })
    md_rows.sort(key=lambda r: (-r["n_distinct_T"], r["material_class_heuristic"], r["material_name"]))
    with open(os.path.join(DATA, "isodb_water_multiT.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(md_rows[0].keys()))
        w.writeheader()
        w.writerows(md_rows)

    # per material across DOIs
    by_m = defaultdict(list)
    for r in ok:
        by_m[r["material_id"]].append(r)
    m_rows = []
    for mid, rs in by_m.items():
        ts = sorted({tkey(r["temperature_K"]) for r in rs})
        m_rows.append({
            "material_id": mid, "material_name": rs[0]["material_name"],
            "material_class_heuristic": rs[0]["material_class_heuristic"],
            "n_DOIs": len({r["DOI"] for r in rs}), "DOIs": ";".join(sorted({r["DOI"] for r in rs})),
            "n_isotherms": len(rs), "n_distinct_T": len(ts), "temperatures_K": ";".join(f"{t:g}" for t in ts),
            "categories": ";".join(sorted({str(r["category"]) for r in rs})),
        })
    m_rows.sort(key=lambda r: (-r["n_distinct_T"], r["material_class_heuristic"], r["material_name"]))
    with open(os.path.join(DATA, "isodb_water_multiT_by_material.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(m_rows[0].keys()))
        w.writeheader()
        w.writerows(m_rows)

    # counts
    def cnt(rs, field):
        c = defaultdict(int)
        for r in rs:
            c[str(r[field])] += 1
        return dict(sorted(c.items()))

    def thresholds(rs, filt=None):
        out = {}
        for k in (2, 3, 4):
            sel = [r for r in rs if r["n_distinct_T"] >= k and (filt is None or filt(r))]
            byc = defaultdict(int)
            for r in sel:
                byc[r["material_class_heuristic"]] += 1
            out[f">={k}"] = {"total": len(sel), "by_class": dict(sorted(byc.items()))}
        return out

    exp_only = lambda r: set(r["categories"].split(";")) <= {"exp", ""}
    summary = {
        "retrieved": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "water_InChIKey": WKEY,
        "n_index_total": n_index,
        "n_water_containing_isotherms": len(any_water),
        "n_pure_water_isotherms": len(pure),
        "n_fetched_ok": len(ok),
        "n_fetch_failed": len(rows) - len(ok),
        "record_field_union": sorted(key_union),
        "isotherms_by_category": cnt(ok, "category"),
        "isotherms_by_tabular_data": cnt(ok, "tabular_data"),
        "isotherms_by_digitizer": cnt(ok, "digitizer"),
        "isotherms_by_articleSource": cnt(ok, "articleSource"),
        "isotherms_by_isotherm_type": cnt(ok, "isotherm_type"),
        "isotherms_by_pressure_units": cnt(ok, "pressure_units"),
        "isotherms_by_adsorption_units": cnt(ok, "adsorption_units"),
        "isotherms_by_pressure_trend_heuristic": cnt(ok, "pressure_trend_heuristic"),
        "isotherms_by_class_heuristic": cnt(ok, "material_class_heuristic"),
        "n_materials": len(by_m),
        "materials_by_class_heuristic": cnt(m_rows, "material_class_heuristic"),
        "n_DOIs": len({r["DOI"] for r in ok}),
        "n_material_DOI_pairs": len(md_rows),
        "multiT_material_DOI_pairs_all_categories": thresholds(md_rows),
        "multiT_material_DOI_pairs_category_exp_or_blank": thresholds(md_rows, exp_only),
        "multiT_material_DOI_pairs_adsorption_like_T": {
            f">={k}": sum(1 for r in md_rows if r["n_distinct_T_adsorption_like"] >= k) for k in (2, 3, 4)},
        "multiT_materials_across_DOIs_all_categories": thresholds(m_rows),
        "multiT_materials_across_DOIs_exp_or_blank": thresholds(m_rows, exp_only),
    }
    with open(os.path.join(DATA, "isodb_water_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
