import json, sys, time, urllib.parse, urllib.request

BASE = "https://www.ebi.ac.uk/chembl/api/data/activity.json"
OUT = sys.argv[1]
TARGETS = {"BACE1": "CHEMBL4822", "AChE": "CHEMBL220"}

def fetch(target_id):
    rows, offset = [], 0
    while True:
        q = urllib.parse.urlencode({
            "target_chembl_id": target_id,
            "pchembl_value__gte": 6,
            "standard_type__in": "IC50,Ki",
            "limit": 1000, "offset": offset,
            "only": "molecule_chembl_id,canonical_smiles,pchembl_value,standard_type",
        })
        with urllib.request.urlopen(BASE + "?" + q, timeout=120) as r:
            d = json.load(r)
        acts = d.get("activities", [])
        rows.extend(acts)
        tc = d.get("page_meta", {}).get("total_count")
        sys.stderr.write(f"  {target_id}: {len(rows)}/{tc}\n")
        if not d.get("page_meta", {}).get("next") or not acts:
            break
        offset += 1000
        time.sleep(0.2)
    return rows

out = {}
for name, tid in TARGETS.items():
    sys.stderr.write(f"{name} ({tid})\n")
    rows = fetch(tid)
    seen = {}
    for a in rows:
        smi, mid = a.get("canonical_smiles"), a.get("molecule_chembl_id")
        if smi and mid and mid not in seen:
            seen[mid] = smi
    out[name] = seen
    sys.stderr.write(f"{name}: {len(rows)} activities -> {len(seen)} unique compounds\n")

with open(OUT, "w") as f:
    json.dump(out, f)
print(json.dumps({k: len(v) for k, v in out.items()}))
