"""Verify candidate primary papers: Crossref metadata, Unpaywall OA status, ISODB presence.

Input : data/primary_candidates.csv (manually curated list: shortkey, doi, materials, ...)
        data/isodb_water_records.csv (from isodb_water_inventory.py), optional
Output: data/primary_doi_check.csv
Usage : python -I primary_doi_check.py
"""
import csv
import os
import sys
import time

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.dirname(HERE)
EMAIL = "unpaywall_00@example.com"  # neutral placeholder; never a personal address
UA = {"User-Agent": f"ai-isotherm-thermo inventory (mailto:{EMAIL})"}


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    cands = list(csv.DictReader(open(os.path.join(DATA, "primary_candidates.csv"), encoding="utf-8")))
    isodb = {}
    p = os.path.join(DATA, "isodb_water_records.csv")
    if os.path.exists(p):
        for r in csv.DictReader(open(p, encoding="utf-8")):
            d = (r["DOI"] or "").strip().lower()
            isodb.setdefault(d, []).append(r)
    out = []
    for c in cands:
        doi = c["doi"].strip()
        row = dict(c)
        cr = requests.get("https://api.crossref.org/works/" + doi, headers=UA, timeout=60)
        if cr.status_code == 200:
            m = cr.json()["message"]
            row["crossref_status"] = "ok"
            row["cr_title"] = " ".join((m.get("title") or [""])[0].split())
            row["cr_journal"] = (m.get("container-title") or [""])[0]
            row["cr_year"] = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
            au = m.get("author") or []
            row["cr_first_author"] = (au[0].get("family", "") if au else "")
            row["cr_last_author"] = (au[-1].get("family", "") if au else "")
            row["cr_licenses"] = ";".join(sorted({l.get("URL", "") for l in m.get("license", [])}))
        else:
            row["crossref_status"] = f"HTTP {cr.status_code}"
        time.sleep(0.3)
        up = requests.get(f"https://api.unpaywall.org/v2/{doi}", params={"email": EMAIL}, timeout=60)
        if up.status_code == 200:
            u = up.json()
            b = u.get("best_oa_location") or {}
            row["up_is_oa"] = u.get("is_oa")
            row["up_oa_status"] = u.get("oa_status")
            row["up_best_license"] = b.get("license")
            row["up_best_version"] = b.get("version")
            row["up_best_host"] = b.get("host_type")
            row["up_best_url"] = b.get("url_for_pdf") or b.get("url")
            row["up_all_licenses"] = ";".join(sorted({str(l.get("license")) for l in u.get("oa_locations") or []}))
        else:
            row["up_is_oa"] = f"HTTP {up.status_code}"
        time.sleep(0.3)
        hits = isodb.get(doi.lower(), [])
        row["isodb_n_water_isotherms"] = len(hits)
        row["isodb_temperatures_K"] = ";".join(sorted({f"{float(h['temperature_K']):g}" for h in hits if h.get("temperature_K")}, key=float))
        row["isodb_materials"] = " | ".join(sorted({h["material_name"] for h in hits}))[:300]
        out.append(row)
        print(doi, row.get("crossref_status"), row.get("up_oa_status"), row.get("up_best_license"), row["isodb_n_water_isotherms"], flush=True)
    cols = list(cands[0].keys()) + ["crossref_status", "cr_title", "cr_journal", "cr_year", "cr_first_author", "cr_last_author",
                                    "cr_licenses", "up_is_oa", "up_oa_status", "up_best_license", "up_best_version",
                                    "up_best_host", "up_best_url", "up_all_licenses", "isodb_n_water_isotherms",
                                    "isodb_temperatures_K", "isodb_materials"]
    with open(os.path.join(DATA, "primary_doi_check.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(out)


if __name__ == "__main__":
    main()
