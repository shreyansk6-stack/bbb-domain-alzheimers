"""Aggregate the label-permuted validation runs into one table.

Each run of scripts/confirmatory.py --mode permuted writes its own manifest.
This collects them, checks they all belong to the same pipeline, and reports
the distribution of the primary endpoint under the null. That distribution is
what the real-label gate judges: a single permuted run characterises one
realisation of a single fixed evaluation set, not the harness.

Usage: ./env/bin/python -I scripts/summarise_permuted.py
"""
import glob
import json
import sys

import numpy as np

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402

runs = []
for f in sorted(glob.glob("results/confirmatory_permuted*.json")):
    try:
        runs.append(json.load(open(f)))
    except Exception as e:
        print(f"skipped {f}: {e}")

if not runs:
    sys.exit("no permuted manifests found")

cur = C.script_sha256()
hashes = {r.get("script_sha256") for r in runs}

print("=" * 74)
print("LABEL-PERMUTED VALIDATION - summary across runs")
print("=" * 74)
print(f"pipeline under test : confirmatory.py sha256 {cur[:16]}")
print(f"manifests found     : {len(runs)}")
print(f"all same pipeline   : {'yes' if hashes == {cur} else 'NO - ' + str(len(hashes))}")
print(f"gate requires       : {C.MIN_PERMUTATIONS} runs, >={C.MIN_PERMUTED_DRAWS} draws, "
      f"mean |dAUC| <= {C.MAX_MEAN_NULL_DELTA}")
print()

print(f"{'seed':>8} {'draws':>6} {'proximal':>9} {'control':>8} {'dAUC':>9} "
      f"{'95% CI':>20} {'covers 0':>9}")
rows = []
for r in sorted(runs, key=lambda r: r.get("permute_seed", 0)):
    p = r["results"]["property"]
    prox = r["proximal"]["auc"]
    covers = p["lo"] <= 0 <= p["hi"]
    rows.append((p["delta"], covers))
    print(f"{r.get('permute_seed'):>8} {r.get('draws'):>6} {prox:>9.4f} "
          f"{p['control_auc']:>8.4f} {p['delta']:>+9.4f} "
          f"{'[' + format(p['lo'], '+.4f') + ', ' + format(p['hi'], '+.4f') + ']':>20} "
          f"{'yes' if covers else 'NO':>9}")

d = np.array([r[0] for r in rows])
se = d.std(ddof=1) / np.sqrt(len(d))
print()
print(f"mean dAUC {d.mean():+.4f}   sd {d.std(ddof=1):.4f}   "
      f"SE {se:.4f}   t vs 0: {d.mean() / se:+.2f}")
print(f"signs: {(d > 0).sum()} positive, {(d < 0).sum()} negative")
print(f"intervals covering zero: {sum(c for _, c in rows)}/{len(rows)}")
print()

ok = (hashes == {cur} and len(runs) >= C.MIN_PERMUTATIONS
      and abs(d.mean()) <= C.MAX_MEAN_NULL_DELTA
      and all(c for _, c in rows))
print("=" * 74)
print(f"VERDICT: {'PASS' if ok else 'FAIL'} - harness shows no effect on data containing none")
print("=" * 74)
print(f"""The per-run spread (sd {d.std(ddof=1):.4f}) is dominated by the proximal arm, which is
measured on one fixed set of compounds and so varies with sd ~0.027 between
permutations. Individual runs therefore reach {np.abs(d).max():+.4f} by chance alone; the
first four seeds run during development were all positive, averaging +0.030,
which looked like bias and was not (docs/decisions.md IC-5). The mean over
{len(d)} runs is the quantity that carries information, and it is {d.mean():+.4f}.""")
