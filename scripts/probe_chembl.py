"""Tabulate the ChEMBL assay metadata behind our target sets, so curation filters
are chosen against the actual distribution rather than guessed.

Pulls activities at a deliberately loose threshold (pChEMBL >= 5, IC50/Ki/Kd) and
reports what is really there: assay types, confidence scores, censored relations,
validity flags, organisms, and replicate spread per compound.

Writes a JSON cache so later scripts can re-filter without refetching.

Usage: ./env/bin/python -I scripts/probe_chembl.py data/chembl_probe.json
"""
import json, sys, time, urllib.parse, urllib.request
from collections import Counter, defaultdict

ACT = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
ASSAY = "https://www.ebi.ac.uk/chembl/api/data/assay.json"
TARGETS = {"BACE1": "CHEMBL4822", "AChE": "CHEMBL220"}
OUT = sys.argv[1] if len(sys.argv) > 1 else "data/chembl_probe.json"

FIELDS = ",".join([
    "molecule_chembl_id", "canonical_smiles", "pchembl_value", "standard_type",
    "standard_relation", "standard_value", "standard_units", "data_validity_comment",
    "assay_chembl_id", "assay_type", "target_organism", "activity_comment",
])


def get(url, params, timeout=180):
    q = urllib.parse.urlencode(params)
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"{url}?{q}", timeout=timeout) as r:
                return json.load(r)
        except Exception as e:
            if attempt == 3:
                raise
            sys.stderr.write(f"    retry {attempt + 1} after {type(e).__name__}\n")
            time.sleep(2 * (attempt + 1))


def fetch_activities(target_id):
    rows, offset = [], 0
    while True:
        d = get(ACT, {
            "target_chembl_id": target_id,
            "pchembl_value__gte": 5,
            "standard_type__in": "IC50,Ki,Kd",
            "limit": 1000, "offset": offset, "only": FIELDS,
        })
        acts = d.get("activities", [])
        rows.extend(acts)
        meta = d.get("page_meta", {})
        sys.stderr.write(f"  {target_id}: {len(rows)}/{meta.get('total_count')}\n")
        if not meta.get("next") or not acts:
            return rows
        offset += 1000
        time.sleep(0.15)


def fetch_confidence(assay_ids):
    """confidence_score lives on the assay resource, not the activity resource."""
    conf, ids = {}, sorted(assay_ids)
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        d = get(ASSAY, {
            "assay_chembl_id__in": ",".join(chunk),
            "limit": 1000,
            "only": "assay_chembl_id,confidence_score,assay_type,relationship_type",
        })
        for a in d.get("assays", []):
            conf[a["assay_chembl_id"]] = a
        sys.stderr.write(f"  assays: {len(conf)}/{len(ids)}\n")
        time.sleep(0.15)
    return conf


def show(title, counter, total, limit=None):
    print(f"\n{title}")
    items = counter.most_common(limit)
    for k, v in items:
        print(f"    {str(k):<46} {v:>7}  {100 * v / total:5.1f}%")
    if limit and len(counter) > limit:
        print(f"    ... {len(counter) - limit} more")


data = {}
for name, tid in TARGETS.items():
    sys.stderr.write(f"{name} ({tid})\n")
    acts = fetch_activities(tid)
    assay_ids = {a["assay_chembl_id"] for a in acts if a.get("assay_chembl_id")}
    sys.stderr.write(f"  fetching confidence for {len(assay_ids)} assays\n")
    conf = fetch_confidence(assay_ids)
    for a in acts:
        meta = conf.get(a.get("assay_chembl_id"), {})
        a["confidence_score"] = meta.get("confidence_score")
        a["relationship_type"] = meta.get("relationship_type")
    data[name] = acts

with open(OUT, "w") as f:
    json.dump(data, f)
sys.stderr.write(f"\ncached -> {OUT}\n")

for name, acts in data.items():
    n = len(acts)
    print("=" * 78)
    print(f"{name}: {n} activity records (pChEMBL >= 5, IC50/Ki/Kd)")
    print("=" * 78)
    show("standard_type", Counter(a.get("standard_type") for a in acts), n)
    show("standard_relation", Counter(a.get("standard_relation") for a in acts), n)
    show("assay_type", Counter(a.get("assay_type") for a in acts), n)
    show("confidence_score", Counter(a.get("confidence_score") for a in acts), n)
    show("relationship_type", Counter(a.get("relationship_type") for a in acts), n)
    show("target_organism", Counter(a.get("target_organism") for a in acts), n, limit=6)
    show("data_validity_comment", Counter(a.get("data_validity_comment") for a in acts), n, limit=6)
    show("standard_units", Counter(a.get("standard_units") for a in acts), n, limit=5)

    # replicate spread: how inconsistent are repeated measurements per compound?
    per = defaultdict(list)
    for a in acts:
        try:
            per[a["molecule_chembl_id"]].append(float(a["pchembl_value"]))
        except (TypeError, ValueError, KeyError):
            pass
    multi = {k: v for k, v in per.items() if len(v) > 1}
    spreads = sorted(max(v) - min(v) for v in multi.values())
    print(f"\n  compounds: {len(per)} total, {len(multi)} with >1 measurement")
    if spreads:
        import statistics
        over = lambda t: 100 * sum(s > t for s in spreads) / len(spreads)
        print(f"  replicate spread (log units): median {statistics.median(spreads):.2f}  "
              f"p90 {spreads[int(0.9 * len(spreads))]:.2f}  max {spreads[-1]:.2f}")
        print(f"  share of replicated compounds spanning >0.3 log: {over(0.3):.1f}%   "
              f">1.0 log: {over(1.0):.1f}%")
    print()
