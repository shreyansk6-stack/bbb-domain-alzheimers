"""Does the headline out-of-domain result survive every curation choice we had to make?

Builds the primary compound set plus one variant per contested decision, and
recomputes the out-of-domain fraction for each. If the variants agree, the
decisions are not load-bearing and the controversy in the curation literature
(Kalliokoski 2013 vs Landrum & Riniker 2024 on pooling IC50 with Ki) does not
affect this study's conclusion.

Reads the metadata cache written by scripts/probe_chembl.py.
Self-contained by design: run under -I, so it does not import from scripts/.

Usage: ./env/bin/python -I scripts/sensitivity.py data
"""
import json, statistics, sys
from collections import defaultdict

import numpy as np
import pandas as pd
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import inchi, rdFingerprintGenerator

RDLogger.DisableLog("rdApp.*")

DATA = sys.argv[1] if len(sys.argv) > 1 else "data"
CUTOFFS = [0.3, 0.35, 0.4]
gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


def skeleton(mol):
    try:
        key = inchi.MolToInchiKey(mol)
    except Exception:
        return None
    return key.split("-")[0] if key else None


def fp_and_skel(smiles):
    m = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) else None
    if m is None:
        return None, None
    return gen.GetFingerprint(m), skeleton(m)


# ---------------------------------------------------------------- B3DB reference
b3 = pd.read_csv(f"{DATA}/B3DB_classification.tsv", sep="\t").dropna(subset=["SMILES"])
groups = defaultdict(list)
unkeyed = []
for smi, lab in zip(b3["SMILES"], b3["BBB+/BBB-"].astype(str)):
    fp, sk = fp_and_skel(smi)
    if fp is None:
        continue
    (groups[sk] if sk else unkeyed).append((fp, lab))

ref_fps, ref_labels = [], []
discordant = 0
for members in groups.values():
    if len({lab for _, lab in members}) > 1:
        discordant += 1
        continue  # contradictory ground truth: excluded from the labelled reference
    ref_fps.append(members[0][0])
    ref_labels.append(members[0][1])
for fp, lab in unkeyed:
    ref_fps.append(fp)
    ref_labels.append(lab)
ref_labels = np.array(ref_labels)
print(f"B3DB labelled reference set: {len(ref_fps)} skeletons "
      f"({discordant} discordant skeletons excluded)")
print(f"  BBB+: {(ref_labels == 'BBB+').sum()}   BBB-: {(ref_labels == 'BBB-').sum()}\n")

# ---------------------------------------------------------- activity record cache
probe = json.load(open(f"{DATA}/chembl_probe.json"))


def build(acts, types, min_pchembl, conf, assay_types=("B",), dedup=True):
    """Apply one curation recipe and return deduplicated fingerprints."""
    per = defaultdict(list)
    for a in acts:
        if a.get("standard_type") not in types:
            continue
        if a.get("confidence_score") not in conf:
            continue
        if a.get("assay_type") not in assay_types:
            continue
        if a.get("standard_relation") != "=":
            continue
        if a.get("data_validity_comment") is not None:
            continue
        if a.get("standard_units") != "nM":
            continue
        try:
            val = float(a["pchembl_value"])
        except (TypeError, ValueError, KeyError):
            continue
        per[a["molecule_chembl_id"]].append((val, a.get("canonical_smiles")))

    out, skels = [], set()
    for records in per.values():
        # aggregate replicates by median potency, then apply the threshold once
        if statistics.median([v for v, _ in records]) < min_pchembl:
            continue
        smi = next((s for _, s in records if s), None)
        fp, sk = fp_and_skel(smi)
        if fp is None:
            continue
        if dedup:
            if sk and sk in skels:
                continue
            if sk:
                skels.add(sk)
        out.append(fp)
    return out


def ood(fps):
    """Share of compounds whose nearest B3DB neighbour falls below each cutoff."""
    sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, ref_fps)) for f in fps])
    return sims, [100 * (sims < c).mean() for c in CUTOFFS]


PRIMARY = dict(types={"IC50", "Ki"}, min_pchembl=6.0, conf={9}, assay_types=("B",), dedup=True)

VARIANTS = [
    ("PRIMARY  IC50+Ki, p>=6, conf9, B, dedup", {}),
    ("pool      + confidence 8 (homologous)", dict(conf={8, 9})),
    ("types     IC50 only",                   dict(types={"IC50"})),
    ("types     Ki only",                     dict(types={"Ki"})),
    ("types     + Kd",                        dict(types={"IC50", "Ki", "Kd"})),
    ("thresh    pChEMBL >= 5",                dict(min_pchembl=5.0)),
    ("thresh    pChEMBL >= 7",                dict(min_pchembl=7.0)),
    ("thresh    pChEMBL >= 8",                dict(min_pchembl=8.0)),
    ("assay     B + F + A",                   dict(assay_types=("B", "F", "A"))),
    ("dedup     no skeleton dedup",           dict(dedup=False)),
]

hdr = f"{'variant':<42} {'n':>6} " + " ".join(f"{'<' + str(c):>8}" for c in CUTOFFS) + f" {'median':>7}"
for target in ("BACE1", "AChE"):
    print("=" * len(hdr))
    print(f"{target}: out-of-domain % of target actives (no B3DB neighbour above cutoff)")
    print("=" * len(hdr))
    print(hdr)
    base = None
    for label, override in VARIANTS:
        recipe = {**PRIMARY, **override}
        fps = build(probe[target], **recipe)
        if not fps:
            print(f"{label:<42} {'0':>6}   (empty set)")
            continue
        sims, fracs = ood(fps)
        row = f"{label:<42} {len(fps):>6} " + " ".join(f"{f:>7.1f}%" for f in fracs)
        row += f" {np.median(sims):>7.3f}"
        if base is None:
            base = fracs
        else:
            drift = max(abs(a - b) for a, b in zip(fracs, base))
            row += f"   drift {drift:>4.1f}pp"
        print(row)
    print()

print("""Interpretation: the primary recipe is the first row; "drift" is the largest
change in any out-of-domain percentage relative to it. Small drift means the
curation decision is not load-bearing for this study's conclusion.""")

# ------------------------------------------------- feasibility gate, primary recipe
print()
print("=" * 78)
print("FEASIBILITY GATE under the primary recipe")
print("=" * 78)
print("Labelled B3DB compounds within each cutoff of target chemistry. This is the")
print("sample available for measuring prediction error, and it sets the power.\n")

primary_fps = {t: build(probe[t], **PRIMARY) for t in ("BACE1", "AChE")}
GATE_CUTOFFS = [0.3, 0.35, 0.4, 0.5]
for target, fps in primary_fps.items():
    print(f"--- {target} (n={len(fps)} actives) ---")
    sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, fps)) for f in ref_fps])
    print(f"{'cutoff':>7} {'n':>6} {'BBB+':>6} {'BBB-':>6} {'ratio':>7}   {'sufficient?':>12}")
    for c in GATE_CUTOFFS:
        m = sims >= c
        npos = int((ref_labels[m] == "BBB+").sum())
        nneg = int((ref_labels[m] == "BBB-").sum())
        # pre-registered criterion: >=200 compounds with >=50 in each class
        ok = "PASS" if (npos + nneg) >= 200 and min(npos, nneg) >= 50 else "fail"
        ratio = f"{npos / nneg:.1f}:1" if nneg else "-"
        print(f"{c:>7} {int(m.sum()):>6} {npos:>6} {nneg:>6} {ratio:>7}   {ok:>12}")
    print()

print("""Pre-registered sufficiency criterion (docs/preregistration.md section 10):
>=200 labelled compounds with >=50 in each class at the primary 0.35 cutoff.
Rerun scripts/power.py with the class counts above after any recipe change.""")
