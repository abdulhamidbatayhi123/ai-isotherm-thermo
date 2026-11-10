"""ACS reference style for J. Chem. Inf. Model. (ACS Style Quick Guide, journal article form):

    Author, A. B.; Author, C. D. Title. J. Abbrev. Year, Volume (Issue), first-last. DOI: 10.xxxx/yyyy.

Typeset as achemso does: journal italic, year bold, volume italic. Sources, in order of trust:
  * refs_master.json (audited live, hub task T8): author initials of entries that list every author, the title,
    the journal abbreviation, the volume and the year;
  * crossref_cache.json (crossref_fetch.py): the full author list of entries the master cut to "et al.", the issue
    and the page range;
  * OVERRIDES below for the entries without a Crossref record (conference papers, a preprint, a database).
check() verifies, for every DOI entry, that the master and Crossref agree on volume, year, first page, first author
and (when the master lists every author) the number of authors; build_ms.py fails if it reports anything.
"""
import json
import os
import re
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
BS = chr(92)
AMP = BS + "&"

# Verified live 2026-11-11: proceedings.neurips.cc citation metadata (NeurIPS 33: pp 15427-15438; NeurIPS 32: no
# pages given) and proceedings.mlr.press/v70/amos17b (PMLR 70, pp 146-155).
OVERRIDES = {
    "liu2020cert": "Liu, X.; Han, X.; Zhang, N.; Liu, Q. Certified monotonic neural networks. In " + BS +
                   "textit{Advances in Neural Information Processing Systems 33}, " + BS + "textbf{2020}; "
                   "pp 15427--15438. arXiv:2011.10219.",
    "amos2017": "Amos, B.; Xu, L.; Kolter, J. Z. Input convex neural networks. In " + BS + "textit{Proceedings of the "
                "34th International Conference on Machine Learning}; PMLR, " + BS + "textbf{2017}; Vol. 70, "
                "pp 146--155. arXiv:1609.07152.",
    "wehenkel2019": "Wehenkel, A.; Louppe, G. Unconstrained monotonic neural networks. In " + BS + "textit{Advances "
                    "in Neural Information Processing Systems 32}, " + BS + "textbf{2019}. arXiv:1908.05164.",
    "cheng2026": "Cheng, B. Equivariant learning of a transferable three-dimensional classical density functional. "
                 + BS + "textit{arXiv} " + BS + "textbf{2026}, arXiv:2608.13506. https://arxiv.org/abs/2608.13506.",
    "isodb": "Siderius, D. W.; Shen, V. K.; Johnson, R. D., III; van Zee, R. D., Eds. " + BS + "textit{NIST/ARPA-E "
             "Database of Novel and Emerging Adsorbent Materials}; National Institute of Standards and Technology: "
             "Gaithersburg, MD. DOI: 10.18434/T43882 (records retrieved October 13, 2026).",
}

# LaTeX accent commands for the non-ASCII letters that occur in Crossref author names
ACCENTS = {"́": "'", "̀": "`", "̈": '"', "̂": "^", "̃": "~", "̆": "u", "̌": "v",
           "̧": "c", "̊": "r"}


def latex_name(s):
    s = s.replace("‐", "-").replace("‑", "-").replace("’", "'")
    out = []
    for ch in unicodedata.normalize("NFD", s):
        if unicodedata.combining(ch):
            if ch not in ACCENTS or not out:
                raise ValueError(f"no accent mapping for {ch!r} in {s!r}")
            base = out.pop()
            out.append(BS + ACCENTS[ch] + "{" + base + "}")
        else:
            out.append(ch)
    r = "".join(out)
    if not r.isascii():
        raise ValueError(f"non-ASCII left in author name {s!r}")
    return r


def initials(given):
    parts = []
    for word in given.replace(".", ". ").split():
        sub = [w for w in word.split("-") if w]
        parts.append("-".join(w[0] + "." for w in sub))
    return " ".join(parts)


# Crossref splits this name wrongly: the article (doi:10.1038/s41467-019-10960-0) prints "A. Ken Inge", family Inge
NAME_FIX = {("A.", "Ken Inge"): ("A. Ken", "Inge")}
HYPHENS = {"‐": "-", "‑": "-", "‒": "-", "–": "-"}


def crossref_authors(rec):
    out = []
    for a in rec["author"]:
        given, family = NAME_FIX.get((a.get("given", ""), a["family"]), (a.get("given", ""), a["family"]))
        given = "".join(HYPHENS.get(ch, ch) for ch in given)
        out.append(latex_name(family) + ", " + latex_name(initials(given)))
    return out


def master_authors(entry):
    """Author list of a master entry that lists every author ('A, B. C., D, E. \\& F, G.' or one author)."""
    if AMP in entry:
        head, tail = entry.split(AMP, 1)
        m = re.match(r"\s*([^,]+, (?:[A-Z][a-z]?\.[ -]?)+?)(?= [A-Z0-9\\])", tail)
        if not m:
            raise ValueError("cannot find the last author in: " + entry[:80])
        last = m.group(1).strip()
        rest = entry[len(head) + len(AMP) + m.end():]
        names = re.split(r"(?<=\.), (?=[^,]+, (?:[A-Z][a-z]?\.))", head.strip().rstrip(","))
        names = [n.strip() for n in names] + [last]
    else:
        m = re.match(r"([^,]+, (?:[A-Z][a-z]?\.[ -]?)+?)(?= [A-Z0-9\\])", entry)
        names, rest = [m.group(1).strip()], entry[m.end():]
    return names, rest.strip()


def parse_tail(rest):
    """'Title. \\textit{J.} \\textbf{V}, P (Y). doi:D' -> title, journal, volume, year, doi."""
    m = re.match(r"(.*?)\.\s+" + re.escape(BS) + r"textit\{([^}]*)\}\s*(?:" + re.escape(BS) +
                 r"textbf\{([^}]*)\},\s*([^ ]+)\s*)?\((\d{4})\)\.\s*doi:(\S+)$", rest)
    if not m:
        raise ValueError("cannot parse: " + rest[:100])
    title, journal, vol, page, year, doi = m.groups()
    return title, journal, vol, year, doi.rstrip(".")


def pages(rec):
    p = rec.get("page") or rec.get("article-number") or ""
    return p.replace("-", "--")


def format_acs(key, entry, cache):
    if key in OVERRIDES:
        return OVERRIDES[key]
    rec = cache[key]
    if " et al." in entry:
        authors = crossref_authors(rec)
        rest = entry.split(" et al.", 1)[1].strip()
    else:
        authors, rest = master_authors(entry)
    title, journal, vol, year, doi = parse_tail(rest)
    s = "; ".join(authors) + " " + title + ". " + BS + "textit{" + journal + "} " + BS + "textbf{" + year + "}"
    if vol:
        s += ", " + BS + "textit{" + vol + "}"
        if rec.get("issue"):
            s += " (" + rec["issue"].replace("-", "--") + ")"
        if pages(rec):
            s += ", " + pages(rec)
    return s + ". DOI: " + doi + "."


def load_cache():
    return json.load(open(os.path.join(HERE, "crossref_cache.json"), encoding="utf-8"))


def _fold(s):
    s = re.sub(re.escape(BS) + r".\{(\w)\}", r"\1", s)
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower().strip()


def check(master, cache):
    """Master vs Crossref agreement for every DOI entry; returns a list of problems."""
    probs = []
    for k, v in master.items():
        if k in OVERRIDES:
            continue
        if k not in cache:
            probs.append(f"{k}: no Crossref record (run crossref_fetch.py)")
            continue
        rec = cache[k]
        rest = v.split(" et al.", 1)[1].strip() if " et al." in v else master_authors(v)[1]
        title, journal, vol, year, doi = parse_tail(rest)
        if doi.lower() != rec["DOI"].lower():
            probs.append(f"{k}: DOI {doi} vs Crossref {rec['DOI']}")
        if vol and str(rec.get("volume")) != vol:
            probs.append(f"{k}: volume {vol} vs Crossref {rec.get('volume')}")
        years = {(rec.get(f) or {}).get("date-parts", [[None]])[0][0] for f in ("issued", "published-print")}
        if int(year) not in years:
            probs.append(f"{k}: year {year} vs Crossref {sorted(y for y in years if y)}")
        mp = re.search(r"\}, ([^ ]+) \(", v)
        if mp and mp.group(1) != pages(rec).split("--")[0]:
            probs.append(f"{k}: first page {mp.group(1)} vs Crossref {pages(rec)}")
        fam = [_fold(a.get("family", "")) for a in rec.get("author") or []]
        first = _fold(v.split(",")[0])
        if not fam or fam[0] != first:
            probs.append(f"{k}: first author {first} vs Crossref {fam[:1]}")
        if " et al." not in v and len(master_authors(v)[0]) != len(fam):
            probs.append(f"{k}: {len(master_authors(v)[0])} authors vs Crossref {len(fam)}")
    return probs


if __name__ == "__main__":
    master = json.load(open(os.path.join(HERE, "refs_master.json"), encoding="utf-8"))["entries"]
    cache = load_cache()
    print("check:", check(master, cache) or "all agree")
    for k, v in master.items():
        print(k, "|", format_acs(k, v, cache))
