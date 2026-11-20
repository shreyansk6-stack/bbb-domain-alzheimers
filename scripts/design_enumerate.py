"""Amendment A1.2 - domain-constrained design proposals.

EXPLORATORY. Post-dates the registration. No p-value, no claim of activity,
brain penetration or therapeutic potential. Nothing here is confirmatory and
nothing here can change the primary verdict.

What this does: applies the fixed catalogue in config/transformations.json to
the curated AChE actives, one single edit per product, then filters the products
on the pre-declared criteria. No generative model. No activity prediction -
predicting activity on novel chemistry without auditing that model's own
applicability domain is the exact error this paper documents.

Filters, applied cheapest first so the expensive ones see few molecules:
  F1 validity            parses, sanitises, differs from the parent
  F6 scaffold retention  Bemis-Murcko scaffold identical to the parent's
  F7 property window     MW <= 450, cLogP 1-4, TPSA <= 90
  F8 no PAINS            RDKit PAINS catalogue (480 entries)
  F4 synthetic access.   Ertl SA score <= 4.0
  F2 in domain           max Tanimoto to the labelled B3DB reference >= 0.35
  F3 predicted BBB+      the audited ECFP4 random forest, registered hyperparameters
  F5 novelty             NOT APPLIED HERE - see the note it prints

Usage: ./env/bin/python -I scripts/design_enumerate.py data
"""
import json
import os
import statistics
import sys
import time
from collections import defaultdict

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import AllChem, Crippen, Descriptors, FilterCatalog
from rdkit.Chem import RDConfig
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import matthews_corrcoef

sys.path.insert(0, "scripts")
sys.path.append(os.path.join(RDConfig.RDContribDir, "SA_Score"))
import confirmatory as C  # noqa: E402
import sascorer  # noqa: E402

RDLogger.DisableLog("rdApp.*")

MAX_MW, LOGP_LO, LOGP_HI, MAX_TPSA = 450.0, 1.0, 4.0, 90.0
MAX_SA = 4.0
DOMAIN_CUTOFF = C.CUTOFF

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
t0 = time.time()
out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


say("=" * 78)
say("AMENDMENT A1.2 - DOMAIN-CONSTRAINED DESIGN PROPOSALS")
say("=" * 78)
say("EXPLORATORY. Post-dates registration 10.17605/OSF.IO/UQR62.")
say("No activity prediction. No claim of activity, permeability or therapeutic use.")
say(f"commit {C.current_commit()}   catalogue config/transformations.json")
say()

# ------------------------------------------------------------------ parents
probe = json.load(open(f"{data_dir}/chembl_probe.json"))
per = defaultdict(list)
for a in probe["AChE"]:
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

parents, seen = [], set()
for cid, recs in per.items():
    if statistics.median([v for v, _ in recs]) < C.RECIPE["min_pchembl"]:
        continue
    smi = next((s for _, s in recs if s), None)
    if not smi:
        continue
    m = Chem.MolFromSmiles(smi)
    if m is None:
        continue
    sk = Chem.MolToInchiKey(m).split("-")[0]
    if sk in seen:
        continue
    seen.add(sk)
    parents.append((cid, Chem.MolToSmiles(m)))
say(f"curated AChE actives (identical recipe to the confirmatory run): {len(parents)}")

# ------------------------------------------------- reference set and the model
fps_ref, y_ref, props_ref, _ = C.load_b3db(data_dir)
X_ref = C.fp_matrix(fps_ref)
say(f"labelled B3DB reference: {len(fps_ref)} skeletons")

def _coerce(v):
    """The manifest stores hyperparameters as strings; restore their types so the
    registered values stay the source rather than being retyped by hand."""
    if v == "None":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return v


params = json.load(open("results/confirmatory_real.json")).get("hyperparameters") or {
    "class_weight": "None", "max_features": "0.03"}
params = {k: _coerce(v) for k, v in params.items()}
say(f"BBB model: ECFP4 random forest, registered hyperparameters {params}")
model = C.ArmModel(params, C.SEED).fit(X_ref, y_ref)
ths = np.linspace(0.05, 0.95, 91)
thr = float(max(ths, key=lambda t: matthews_corrcoef(y_ref, (model.oof >= t).astype(int))))
say(f"trained on all {len(y_ref)} labelled compounds; threshold {thr:.2f} from "
    f"out-of-fold predictions. This is a NEW fit for design triage, not the "
    f"confirmatory model.")
say()

# --------------------------------------------------------------- enumerate
catalogue = json.load(open("config/transformations.json"))["transformations"]
approved = [t for t in catalogue if t["status"] != "rejected"]
say(f"transformations in catalogue: {len(catalogue)}   not rejected: {len(approved)}")
if any(t["status"] == "proposed" for t in approved):
    say("NOTE: entries are still 'proposed'. The chemistry co-author has not yet")
    say("signed off on the catalogue; treat the output as provisional.")
say()

pains_params = FilterCatalog.FilterCatalogParams()
pains_params.AddCatalog(FilterCatalog.FilterCatalogParams.FilterCatalogs.PAINS)
pains = FilterCatalog.FilterCatalog(pains_params)

counts = defaultdict(int)
products = {}

for t in approved:
    rxn = AllChem.ReactionFromSmarts(t["smarts"])
    for cid, psmi in parents:
        pm = Chem.MolFromSmiles(psmi)
        if pm is None:
            continue
        try:
            outs = rxn.RunReactants((pm,))
        except Exception:
            continue
        p_scaf = MurckoScaffold.MurckoScaffoldSmiles(mol=pm)
        for o in outs:
            prod = o[0]
            counts["raw"] += 1
            try:
                Chem.SanitizeMol(prod)
                # reaction SMARTS that set an explicit [H] leave it in the output
                # SMILES; strip it so products are written in the same form as
                # their parents rather than in a reaction-specific dialect
                prod = Chem.RemoveHs(prod)
                smi = Chem.MolToSmiles(prod)
            except Exception:
                continue
            if smi == psmi or Chem.MolFromSmiles(smi) is None:
                continue
            counts["F1_valid"] += 1
            mol = Chem.MolFromSmiles(smi)
            if MurckoScaffold.MurckoScaffoldSmiles(mol=mol) != p_scaf:
                continue
            counts["F6_scaffold"] += 1
            mw, logp = Descriptors.MolWt(mol), Crippen.MolLogP(mol)
            tpsa = Descriptors.TPSA(mol)
            if not (mw <= MAX_MW and LOGP_LO <= logp <= LOGP_HI and tpsa <= MAX_TPSA):
                continue
            counts["F7_properties"] += 1
            if pains.HasMatch(mol):
                continue
            counts["F8_pains"] += 1
            sa = sascorer.calculateScore(mol)
            if sa > MAX_SA:
                continue
            counts["F4_sa"] += 1
            if smi in products:
                continue
            products[smi] = dict(smiles=smi, parent=psmi, parent_chembl=cid,
                                 transformation=t["id"], tname=t["name"],
                                 mw=round(mw, 1), clogp=round(logp, 2),
                                 tpsa=round(tpsa, 1), sa=round(sa, 2))

say(f"raw products generated          : {counts['raw']}")
say(f"F1 valid and different          : {counts['F1_valid']}")
say(f"F6 scaffold retained            : {counts['F6_scaffold']}")
say(f"F7 inside property window       : {counts['F7_properties']}")
say(f"F8 PAINS-free                   : {counts['F8_pains']}")
say(f"F4 SA <= {MAX_SA}                    : {counts['F4_sa']}")
say(f"unique structures               : {len(products)}")
say()

# ------------------------------------------------------- domain + prediction
if products:
    smis = list(products)
    mols = [Chem.MolFromSmiles(s) for s in smis]
    gen = AllChem.GetMorganGenerator(radius=2, fpSize=2048)
    pfps = [gen.GetFingerprint(m) for m in mols]
    sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, fps_ref)) for f in pfps])
    Xp = C.fp_matrix(pfps)
    raw, cal = model.predict_proba(Xp)

    for i, s in enumerate(smis):
        products[s]["max_tanimoto"] = round(float(sims[i]), 3)
        products[s]["p_bbb"] = round(float(cal[i]), 3)

    in_dom = [s for s in smis if products[s]["max_tanimoto"] >= DOMAIN_CUTOFF]
    say(f"F2 in domain (max Tanimoto >= {DOMAIN_CUTOFF}) : {len(in_dom)}")
    survivors = [s for s in in_dom if products[s]["p_bbb"] >= thr]
    say(f"F3 predicted BBB+ (p >= {thr:.2f})        : {len(survivors)}")
else:
    survivors = []
say()

say("=" * 78)
say("F5 NOVELTY - NOT APPLIED, AND WHY")
say("=" * 78)
say("A1.2 specifies novelty against ChEMBL and PubChem. Neither can be checked")
say("offline: the local snapshot holds only AChE actives, not either database in")
say("full, and there is no bulk structure-lookup that avoids one network call per")
say("structure. Applying it to every enumerated product was never feasible. It is")
say("feasible on the survivors, which is why it is ordered last here. Run it as a")
say("separate, rate-limited step and record the date, because both databases are")
say("live and a novelty claim is only true as of a given day.")
say()

ranked = sorted(survivors,
                key=lambda s: (-products[s]["max_tanimoto"], products[s]["sa"]))
by_tx = defaultdict(int)
for s in ranked:
    by_tx[products[s]["transformation"]] += 1

say("=" * 78)
say("SURVIVORS BY TRANSFORMATION")
say("=" * 78)
for t in approved:
    say(f"  {t['id']}  {by_tx.get(t['id'], 0):6d}   {t['name']}")
say()

say("=" * 78)
say("TOP 20 BY THE PRE-REGISTERED RANKING (Tanimoto desc, then SA asc)")
say("=" * 78)
say(f"{'#':>3} {'tx':>4} {'Tani':>6} {'p(BBB+)':>8} {'SA':>5} {'MW':>6} "
    f"{'cLogP':>6} {'TPSA':>6}  parent")
for i, s in enumerate(ranked[:20], 1):
    p = products[s]
    say(f"{i:>3} {p['transformation']:>4} {p['max_tanimoto']:>6.3f} {p['p_bbb']:>8.3f} "
        f"{p['sa']:>5.2f} {p['mw']:>6.1f} {p['clogp']:>6.2f} {p['tpsa']:>6.1f}  "
        f"{p['parent_chembl']}")
say()
for i, s in enumerate(ranked[:20], 1):
    say(f"{i:>3}  {s}")
say()
say(f"elapsed {time.time() - t0:.0f}s")

os.makedirs("results", exist_ok=True)
open("results/design_enumeration.txt", "w").write("\n".join(out) + "\n")
json.dump(dict(exploratory=True, registration="10.17605/OSF.IO/UQR62",
               commit=C.current_commit(), threshold=thr, counts=dict(counts),
               n_survivors=len(survivors),
               novelty_checked=False,
               ranked=[products[s] for s in ranked]),
          open("results/design_enumeration.json", "w"), indent=2)
print("wrote results/design_enumeration.txt")
