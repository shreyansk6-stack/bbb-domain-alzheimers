"""Shared dataset loaders: the curated target actives, and B3DB molecules.

scripts/confirmatory.py builds this set internally and returns only
fingerprints, which is all the confirmatory analysis needs. The exploratory
work needs the structures themselves. Rather than restate the recipe in each
script - where it could drift away from the registered one without anyone
noticing - it is written once here and imported.

The filters are read from confirmatory.RECIPE, so they cannot drift at all:
changing the recipe would change the hash of the confirmatory pipeline and
re-lock it.
"""
import json
import statistics
import sys
from collections import defaultdict

from rdkit import Chem, RDLogger

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402

RDLogger.DisableLog("rdApp.*")


def load_target_smiles(data_dir, target):
    """[(chembl_id, canonical_smiles)] for actives under the registered recipe.

    Identical filtering and median-pChEMBL aggregation to
    confirmatory.load_target, and the same InChIKey-skeleton deduplication, so
    the returned set is the one the confirmatory run analysed.
    """
    probe = json.load(open(f"{data_dir}/chembl_probe.json"))
    per = defaultdict(list)
    for a in probe[target]:
        if (a.get("standard_type") not in C.RECIPE["types"]
                or a.get("confidence_score") not in C.RECIPE["conf"]
                or a.get("assay_type") not in C.RECIPE["assay_types"]
                or a.get("standard_relation") != "="
                or a.get("data_validity_comment") is not None
                or a.get("standard_units") != "nM"):
            continue
        try:
            val = float(a["pchembl_value"])
        except (TypeError, ValueError, KeyError):
            continue
        per[a["molecule_chembl_id"]].append((val, a.get("canonical_smiles")))

    actives, seen = [], set()
    for cid, recs in per.items():
        if statistics.median([v for v, _ in recs]) < C.RECIPE["min_pchembl"]:
            continue
        smi = next((s for _, s in recs if s), None)
        if not smi:
            continue
        mol = Chem.MolFromSmiles(smi)
        if mol is None:
            continue
        sk = Chem.MolToInchiKey(mol).split("-")[0]
        if sk in seen:
            continue
        seen.add(sk)
        actives.append((cid, Chem.MolToSmiles(mol)))
    return actives


def aligned_b3db_mols(data_dir):
    """B3DB molecules in the exact order confirmatory.load_b3db returns rows.

    load_b3db deduplicates to InChIKey skeletons, drops discordant skeletons and
    appends unkeyed records last. Indices into its fps/y/props arrays are only
    meaningful against that same order, so the grouping is replicated here
    rather than approximated: a misalignment would silently pair each
    compound's descriptors with a different compound's label and still produce
    entirely plausible output.

    Callers should assert len(result) == len(fps).
    """
    import pandas as pd
    from collections import defaultdict as _dd

    df = pd.read_csv(f"{data_dir}/B3DB_classification.tsv",
                     sep="\t").dropna(subset=["SMILES"])
    groups, unkeyed = _dd(list), []
    for smi, lab in zip(df["SMILES"], df["BBB+/BBB-"].astype(str)):
        fp, sk, _ = C.featurise(smi)
        if fp is None:
            continue
        (groups[sk] if sk else unkeyed).append((smi, lab))

    mols = []
    for members in groups.values():
        if len({lab for _, lab in members}) > 1:
            continue
        mols.append(Chem.MolFromSmiles(members[0][0]))
    for smi, _ in unkeyed:
        mols.append(Chem.MolFromSmiles(smi))
    return mols
