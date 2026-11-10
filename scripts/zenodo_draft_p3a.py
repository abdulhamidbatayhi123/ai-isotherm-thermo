"""Create the Zenodo draft for the Paper 3A code-and-results archive and reserve its DOI (adapted from
pinn-machining/zenodo_upload_paperA_api.py, which was verified against the live API on 2026-11-09/10).

It NEVER publishes: the token (ZENODO_TOKEN, process env or Windows user env; never printed) has the scope
deposit:write only, which cannot publish. The author publishes the draft in the Zenodo web interface at submission,
after the final snapshot is uploaded with --upload.

    python scripts/zenodo_draft_p3a.py                 # create the draft (once) and reserve the DOI
    python scripts/zenodo_draft_p3a.py --upload FILE   # upload FILE (e.g. the git archive of the submitted commit)

State (no token): paper/submission/ZENODO_DRAFT_STATE.json
"""
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.request

API = "https://zenodo.org/api"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATE = os.path.join(ROOT, "paper", "submission", "ZENODO_DRAFT_STATE.json")
UA = "ai-isotherm-thermo-deposit/1.0"
OTHER_PROJECT_DRAFTS = {"23661737", "24087443"}   # Paper 1 and pinn-machining Paper A: never touch

TITLE = ("Code, results and pre-registration for: Hard Shape Constraints versus Penalties for Temperature "
         "Extrapolation of MOF and COF Water Isotherms")
DESC = ("<p>Archive of the repository github.com/abdulhamidbatayhi123/ai-isotherm-thermo for the manuscript "
        "\"Hard Shape Constraints versus Penalties for Temperature Extrapolation of MOF and COF Water Isotherms\" "
        "(submitted to the Journal of Chemical Information and Modeling). It contains the frozen pre-registration and "
        "its manifest (SHA-256 of every frozen file), the public corrections ledger, the models, fitting, scoring "
        "and thermodynamic code, the separately written second scorer, every confirmatory, synthetic-heat, "
        "sensitivity and diagnostic run record and result file, the figure scripts with provenance, and the "
        "manuscript build that checks every number in the text against its source file. The digitised and "
        "database point lists are not redistributed (third-party figures and records); the digitisation scripts "
        "regenerate them and their hashes are in the freeze manifest.</p>")


class FileBody:
    def __init__(self, p):
        self.f = open(p, "rb")
        self.n = os.path.getsize(p)

    def read(self, k=-1):
        return self.f.read(k)

    def __len__(self):
        return self.n


def req(method, url, token, body=None, data=None, ctype="application/json", ok=(200, 201, 202, 204)):
    h = {"Authorization": f"Bearer {token}", "User-Agent": UA, "Accept": "application/vnd.inveniordm.v1+json"}
    if body is not None:
        data = json.dumps(body).encode()
    if data is not None:
        h["Content-Type"] = ctype
        if isinstance(data, FileBody):
            h["Content-Length"] = str(data.n)
    for attempt in range(5):
        if isinstance(data, FileBody):
            data.f.seek(0)
        r = urllib.request.Request(url, data=data, method=method, headers=h)
        try:
            with urllib.request.urlopen(r, timeout=3600) as resp:
                txt = resp.read().decode() or "{}"
                return json.loads(txt) if txt.strip().startswith(("{", "[")) else {}
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="replace")[:600]
            if e.code in (429, 502, 503, 504) and attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise SystemExit(f"HTTP {e.code} on {method} {url.split('?')[0]}: {msg}")
        except (urllib.error.URLError, TimeoutError):
            if attempt < 4:
                time.sleep(10 * (attempt + 1))
                continue
            raise


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def token():
    t = (os.environ.get("ZENODO_TOKEN") or "").strip().strip('"')
    if not t:
        import winreg
        k = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment")
        t = winreg.QueryValueEx(k, "ZENODO_TOKEN")[0].strip().strip('"')
    return t


def save(st):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8", newline="\n") as f:
        json.dump(st, f, indent=1)


def main():
    tk = token()
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    rid = st.get("id")
    if rid in OTHER_PROJECT_DRAFTS:
        raise SystemExit(f"refusing: {rid} belongs to another project")
    if not rid:
        meta = {"metadata": {
            "resource_type": {"id": "software"},
            "title": TITLE,
            "publication_date": time.strftime("%Y-%m-%d"),
            "creators": [{"person_or_org": {"type": "personal", "given_name": "Abdulhamid", "family_name": "Batayhi",
                                            "identifiers": [{"scheme": "orcid",
                                                             "identifier": "0009-0007-0374-6755"}]},
                          "affiliations": [{"name": "Yildiz Technical University"}]}],
            "description": DESC,
            "rights": [{"id": "mit"}],
            "publisher": "Zenodo",
        }, "access": {"record": "public", "files": "public"}, "files": {"enabled": True}}
        d = req("POST", f"{API}/records", tk, meta)
        rid = d["id"]
        st = {"id": rid, "created": time.strftime("%Y-%m-%d %H:%M:%S")}
        save(st)
        print("draft created:", rid)
    if not st.get("doi"):
        d = req("POST", f"{API}/records/{rid}/draft/pids/doi", tk, {})
        st["doi"] = d["pids"]["doi"]["identifier"]
        save(st)
    print("reserved DOI:", st["doi"])
    if "--upload" in sys.argv:
        p = sys.argv[sys.argv.index("--upload") + 1]
        n = os.path.basename(p)
        local = md5(p)
        have = {e["key"]: e for e in req("GET", f"{API}/records/{rid}/draft/files", tk).get("entries", [])}
        for k in have:                       # one snapshot only: replace any earlier upload
            req("DELETE", f"{API}/records/{rid}/draft/files/{k}", tk)
        req("POST", f"{API}/records/{rid}/draft/files", tk, [{"key": n}])
        req("PUT", f"{API}/records/{rid}/draft/files/{n}/content", tk, data=FileBody(p),
            ctype="application/octet-stream")
        c = req("POST", f"{API}/records/{rid}/draft/files/{n}/commit", tk)
        if c.get("checksum") != f"md5:{local}":
            raise SystemExit(f"CHECKSUM MISMATCH {n}: zenodo {c.get('checksum')} local md5:{local}")
        st["file"] = {"name": n, "md5": local, "bytes": os.path.getsize(p)}
        save(st)
        print(f"uploaded {n}, md5 verified")
    print("NOT PUBLISHED. Draft:", f"https://zenodo.org/uploads/{rid}")


if __name__ == "__main__":
    main()
