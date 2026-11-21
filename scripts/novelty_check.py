"""A1.2 filter F5: novelty of the enumerated survivors against ChEMBL and PubChem.

EXPLORATORY. Post-dates the registration.

A novelty claim is only true on the day it is made - both databases are live -
so the query date is recorded in the output and must appear in the manuscript.

Method: exact structure lookup by full InChIKey in PubChem (PUG-REST) and
ChEMBL (web services). A structure with no hit in either is "no exact match as
of <date>", which is the defensible claim. It is NOT a claim that no close
analogue exists, and because the key is the full InChIKey a stereoisomer,
tautomer or salt of a known compound would be reported as unmatched. Both
limitations are printed with the result.

Results are cached to results/novelty_cache.json so a rerun costs nothing and
an interrupted run resumes.

Requests are throttled below PubChem's published limits (5 requests/second,
400 per minute) and carry a generic User-Agent. No project or personal
information is sent; only structures.

Usage: ./env/bin/python -I scripts/novelty_check.py
"""
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date

from rdkit import Chem, RDLogger

RDLogger.DisableLog("rdApp.*")

UA = "bbb-domain-study/1.0 (academic research; structure novelty check)"
PAUSE = 0.26           # ~3.8 req/s, under PubChem's 5/s
CACHE = "results/novelty_cache.json"
PUBCHEM = ("https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/inchikey/"
           "{key}/cids/JSON")
CHEMBL = ("https://www.ebi.ac.uk/chembl/api/data/molecule.json"
          "?molecule_structures__standard_inchi_key={key}&limit=1")


def get(url, tries=3):
    """Return (status, body). 404 is a valid answer meaning 'not present'."""
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.status, r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return 404, ""
            if e.code in (429, 503) and attempt < tries - 1:
                time.sleep(2 ** attempt * 2)
                continue
            return e.code, ""
        except Exception:
            if attempt < tries - 1:
                time.sleep(2 ** attempt)
                continue
            return -1, ""
    return -1, ""


def in_pubchem(key):
    st, body = get(PUBCHEM.format(key=key))
    if st == 404:
        return False
    if st == 200:
        try:
            return bool(json.loads(body).get("IdentifierList", {}).get("CID"))
        except Exception:
            return None
    return None


def in_chembl(key):
    st, body = get(CHEMBL.format(key=urllib.parse.quote(key)))
    if st == 404:
        return False
    if st == 200:
        try:
            return json.loads(body)["page_meta"]["total_count"] > 0
        except Exception:
            return None
    return None


ranked = json.load(open("results/design_enumeration.json"))["ranked"]
cache = json.load(open(CACHE)) if os.path.exists(CACHE) else {}
today = date.today().isoformat()

keys = {}
for p in ranked:
    m = Chem.MolFromSmiles(p["smiles"])
    if m is not None:
        keys[p["smiles"]] = Chem.MolToInchiKey(m)

todo = [s for s in keys if s not in cache]
print(f"{len(ranked)} survivors, {len(todo)} to query "
      f"({len(cache)} already cached)", flush=True)

for i, smi in enumerate(todo, 1):
    k = keys[smi]
    pc = in_pubchem(k)
    time.sleep(PAUSE)
    cb = in_chembl(k)
    time.sleep(PAUSE)
    cache[smi] = dict(inchikey=k, pubchem=pc, chembl=cb, checked=today)
    if i % 50 == 0 or i == len(todo):
        json.dump(cache, open(CACHE, "w"))
        print(f"  {i}/{len(todo)}", flush=True)
json.dump(cache, open(CACHE, "w"))

out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


say("=" * 78)
say("A1.2 FILTER F5 - NOVELTY AGAINST CHEMBL AND PUBCHEM")
say("=" * 78)
say("EXPLORATORY. Query date " + today + ". Both databases are live, so this")
say("result is only true as of that date and the date must be reported.")
say()

novel, known, unknown = [], [], []
for p in ranked:
    c = cache.get(p["smiles"])
    if not c or c["pubchem"] is None or c["chembl"] is None:
        unknown.append(p)
    elif c["pubchem"] or c["chembl"]:
        known.append(p)
    else:
        novel.append(p)

say(f"survivors checked        : {len(ranked)}")
say(f"  exact match found      : {len(known)}  (not novel)")
say(f"  no exact match         : {len(novel)}")
say(f"  lookup failed          : {len(unknown)}")
say()
pc_only = sum(1 for p in known if cache[p["smiles"]]["pubchem"]
              and not cache[p["smiles"]]["chembl"])
cb_only = sum(1 for p in known if cache[p["smiles"]]["chembl"]
              and not cache[p["smiles"]]["pubchem"])
both = len(known) - pc_only - cb_only
say(f"  of the matched: PubChem only {pc_only}, ChEMBL only {cb_only}, both {both}")
say()

from collections import Counter  # noqa: E402

say("novel survivors by transformation:")
for t, n in sorted(Counter(p["transformation"] for p in novel).items()):
    say(f"  {t}  {n}")
say(f"distinct parents among novel: "
    f"{len({p['parent_chembl'] for p in novel})}")
say()
say("CAVEATS, to be reported with any novelty claim:")
say("  - Exact-structure lookup on the full InChIKey. A stereoisomer, tautomer")
say("    or salt of a known compound is reported here as unmatched.")
say("  - 'No exact match' is not 'no close analogue'. These are single edits of")
say("    known actives, so close analogues exist by construction.")
say("  - Absence from ChEMBL and PubChem is not absence from the literature or")
say("    from patents, which were not searched.")
say()

json.dump(dict(exploratory=True, checked=today, n_checked=len(ranked),
               n_novel=len(novel), n_known=len(known), n_failed=len(unknown),
               novel=novel), open("results/novelty.json", "w"), indent=2)
open("results/novelty.txt", "w").write("\n".join(out) + "\n")
print("wrote results/novelty.txt")
