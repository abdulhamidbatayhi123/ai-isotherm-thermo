"""Fetch Crossref metadata for every DOI in refs_master.json into crossref_cache.json (once; re-run only for misses).

The ACS reference formatter (refs_acs.py) takes author lists, issue and page ranges from this cache and keeps the
audited title, journal abbreviation, volume and year strings of refs_master.json. No contact address is sent.
"""
import json
import os
import re
import time
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "crossref_cache.json")
UA = "ai-isotherm-thermo-refcheck/1.0 (https://github.com/abdulhamidbatayhi123/ai-isotherm-thermo)"


def dois():
    m = json.load(open(os.path.join(HERE, "refs_master.json"), encoding="utf-8"))["entries"]
    out = {}
    for k, v in m.items():
        d = re.search(r"doi:(10\.\S+?)(?:\s|$)", v)
        if d:
            out[k] = d.group(1).rstrip(".")
    return out


def main():
    cache = json.load(open(CACHE, encoding="utf-8")) if os.path.exists(CACHE) else {}
    for k, doi in dois().items():
        if k in cache and cache[k].get("DOI", "").lower() == doi.lower():
            continue
        for attempt in range(5):
            try:
                req = urllib.request.Request("https://api.crossref.org/works/" + urllib.request.quote(doi),
                                             headers={"User-Agent": UA})
                msg = json.load(urllib.request.urlopen(req, timeout=30))["message"]
                keep = {f: msg.get(f) for f in ("DOI", "author", "editor", "title", "container-title",
                                                 "short-container-title", "volume", "issue", "page",
                                                 "article-number", "issued", "published-print",
                                                 "published-online", "type")}
                cache[k] = keep
                print("ok", k, doi)
                break
            except Exception as e:  # 429 / transient
                print("retry", k, doi, e)
                time.sleep(5 * (attempt + 1))
        time.sleep(1.0)
        json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(len(cache), "cached")


if __name__ == "__main__":
    main()
