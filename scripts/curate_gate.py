"""Skeleton-level curation, then recompute the domain-overlap scoping numbers.

Motivation: deduplicating B3DB on canonical SMILES finds almost no duplicates,
because 2D SMILES distinguish stereoisomers that 2D fingerprints cannot. Collapsing
to the InChIKey skeleton (first 14-character block, which drops the stereochemical
and protonation layers) is the curation that matters for a fingerprint-based model.
See docs/literature-search.md.

Reports raw and skeleton-deduplicated numbers side by side so the effect of the
curation decision is visible rather than silently applied.

Usage: ./env/bin/python -I scripts/curate_gate.py data
"""
import json, sys
from collections import defaultdict

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, inchi, rdFingerprintGenerator
from rdkit.Chem.Scaffolds import MurckoScaffold

RDLogger.DisableLog("rdApp.*")

DATA = sys.argv[1]
THRESHOLDS = [0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8]
gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


def skeleton(mol):
    """First block of the InChIKey: connectivity only, no stereo/protonation."""
    try:
        key = inchi.MolToInchiKey(mol)
    except Exception:
        return None
    return key.split("-")[0] if key else None


def parse(smiles, ids):
    """SMILES -> per-molecule records, silently dropping unparseable structures."""
    out = []
    for smi, i in zip(smiles, ids):
        m = Chem.MolFromSmiles(smi) if isinstance(smi, str) else None
        if m is None:
            continue
        try:
            scaff = MurckoScaffold.MurckoScaffoldSmiles(mol=m)
        except Exception:
            scaff = None
        out.append(
            dict(
                id=i,
                fp=gen.GetFingerprint(m),
                skel=skeleton(m),
                scaffold=scaff,
                props=(Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m)),
            )
        )
    return out


def dedup(records, labels=None):
    """Keep one representative per InChIKey skeleton.

    Records with no computable skeleton are kept as-is (they cannot be grouped).
    With labels, also returns the label agreement status of each group.
    """
    groups = defaultdict(list)
    unkeyed = []
    for idx, r in enumerate(records):
        (groups[r["skel"]] if r["skel"] else unkeyed).append(idx)

    reps, status, sizes = [], [], []
    for skel, members in groups.items():
        reps.append(records[members[0]])
        sizes.append(len(members))
        if labels is None:
            status.append(None)
        else:
            vals = {labels[i] for i in members}
            status.append(next(iter(vals)) if len(vals) == 1 else "DISCORDANT")
    for idx in unkeyed:
        reps.append(records[idx])
        sizes.append(1)
        status.append(None if labels is None else labels[idx])
    return reps, status, np.array(sizes)


def max_sim(query_fps, ref_fps):
    return np.array([max(DataStructs.BulkTanimotoSimilarity(f, ref_fps)) for f in query_fps])


def ood_table(name, sims):
    frac = "  ".join(f"<{t}: {100 * (sims < t).mean():5.1f}%" for t in [0.3, 0.35, 0.4, 0.5])
    print(f"{name:>22}: n={len(sims):>5}  median={np.median(sims):.3f}  mean={sims.mean():.3f}")
    print(f"{'':>22}  {frac}")


print("=" * 78)
print("B3DB CURATION")
print("=" * 78)

b3 = pd.read_csv(f"{DATA}/B3DB_classification.tsv", sep="\t").dropna(subset=["SMILES"])
b_raw = parse(b3["SMILES"].tolist(), b3.index.tolist())
raw_labels = b3.loc[[r["id"] for r in b_raw], "BBB+/BBB-"].astype(str).tolist()
print(f"parsed from file:        {len(b_raw)}")

n_smiles_dupes = len(b_raw) - b3.loc[[r['id'] for r in b_raw], "SMILES"].nunique()
print(f"canonical-SMILES dupes:  {n_smiles_dupes}")

b_reps, b_status, b_sizes = dedup(b_raw, raw_labels)
n_discordant = sum(1 for s in b_status if s == "DISCORDANT")
print(f"InChIKey skeletons:      {len(b_reps)}   (collapsed {len(b_raw) - len(b_reps)} records)")
print(f"multi-member skeletons:  {(b_sizes > 1).sum()}   largest group: {b_sizes.max()}")
print(f"DISCORDANT skeletons:    {n_discordant}   (both BBB+ and BBB- labels on one skeleton)")

# Discordant skeletons carry contradictory ground truth and are excluded from the
# labelled reference set. They are retained for domain-coverage geometry, where only
# structure matters, and reported separately.
keep = [i for i, s in enumerate(b_status) if s != "DISCORDANT"]
b_clean = [b_reps[i] for i in keep]
b_clean_labels = np.array([b_status[i] for i in keep])
print(f"labelled reference set:  {len(b_clean)}   "
      f"(BBB+: {(b_clean_labels == 'BBB+').sum()}, BBB-: {(b_clean_labels == 'BBB-').sum()})")

print()
print("=" * 78)
print("TARGET CURATION")
print("=" * 78)

acts = json.load(open(f"{DATA}/chembl_actives.json"))
T = {}
for name, d in acts.items():
    ids = list(d.keys())
    raw = parse([d[i] for i in ids], ids)
    reps, _, sizes = dedup(raw)
    T[name] = dict(raw=raw, reps=reps)
    print(f"{name:>8}: parsed {len(raw):>5} -> {len(reps):>5} skeletons "
          f"(collapsed {len(raw) - len(reps)}, largest group {sizes.max()})")

print()
print("=" * 78)
print("1. OUT-OF-DOMAIN FRACTION OF TARGET ACTIVES  (the paper's premise)")
print("=" * 78)
print("Share of target actives whose nearest B3DB neighbour falls below each cutoff.\n")

b_raw_fps = [r["fp"] for r in b_raw]
b_clean_fps = [r["fp"] for r in b_clean]
ood = {}
for name in T:
    print(f"--- {name} ---")
    ood_table(f"{name} raw vs B3DB raw", max_sim([r["fp"] for r in T[name]["raw"]], b_raw_fps))
    s = max_sim([r["fp"] for r in T[name]["reps"]], b_clean_fps)
    ood[name] = s
    ood_table(f"{name} dedup vs clean", s)
    print()

print("=" * 78)
print("2. LABELLED GROUND TRUTH NEAR TARGET CHEMISTRY  (the feasibility gate)")
print("=" * 78)
print("B3DB compounds within each cutoff of target chemistry, after curation.\n")

per = {name: max_sim(b_clean_fps, [r["fp"] for r in T[name]["reps"]]) for name in T}
overall = np.maximum.reduce(list(per.values()))
print(f"median max-sim: {np.median(overall):.3f}   mean: {overall.mean():.3f}   "
      f"p90: {np.percentile(overall, 90):.3f}")
hdr = f"{'cutoff':>7} {'n':>6} {'BBB+':>6} {'BBB-':>6}" + "".join(f"{n + '-like':>13}" for n in T)
print(hdr)
for t in THRESHOLDS:
    m = overall >= t
    row = f"{t:>7} {m.sum():>6} {(b_clean_labels[m] == 'BBB+').sum():>6} {(b_clean_labels[m] == 'BBB-').sum():>6}"
    row += "".join(f"{(per[n] >= t).sum():>13}" for n in T)
    print(row)

print()
print("=" * 78)
print("3. SCAFFOLD AND IDENTITY OVERLAP")
print("=" * 78)
b_scaffs = {r["scaffold"] for r in b_clean if r["scaffold"]}
b_skels = {r["skel"] for r in b_clean if r["skel"]}
for name in T:
    t_scaffs = {r["scaffold"] for r in T[name]["reps"] if r["scaffold"]}
    t_skels = {r["skel"] for r in T[name]["reps"] if r["skel"]}
    print(f"{name:>8}: scaffolds {len(t_scaffs):>5}  shared with B3DB {len(b_scaffs & t_scaffs):>4}"
          f"   |  identical skeletons in B3DB: {len(b_skels & t_skels)}")
print(f"{'B3DB':>8}: scaffolds {len(b_scaffs)}")

print()
print("=" * 78)
print("4. PHYSICOCHEMICAL SPACE")
print("=" * 78)


def fmt(name, props):
    p = np.array(props)
    return (f"{name:>10}  n={len(p):>5}  MW {p[:, 0].mean():6.1f}±{p[:, 0].std():5.1f}   "
            f"cLogP {p[:, 1].mean():5.2f}±{p[:, 1].std():4.2f}   TPSA {p[:, 2].mean():6.1f}±{p[:, 2].std():5.1f}")


print(fmt("BBB+", [r["props"] for r, l in zip(b_clean, b_clean_labels) if l == "BBB+"]))
print(fmt("BBB-", [r["props"] for r, l in zip(b_clean, b_clean_labels) if l == "BBB-"]))
for name in T:
    print(fmt(name, [r["props"] for r in T[name]["reps"]]))
