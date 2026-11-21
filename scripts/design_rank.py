"""Rank the A1.2 survivors under Amendment A2 and produce the reportable set.

EXPLORATORY, post-registration. The ranking rule is the one introduced in
Amendment A2 (2026-11-21), which replaced the registered rule after that rule
was found to select against novelty. Output under BOTH rules is written, so the
effect of the amendment is visible rather than asserted.

Amendment A2 ranking, applied to the novelty-filtered survivors:
  1. one representative per Bemis-Murcko scaffold - lowest Ertl SA, ties broken
     by higher p(BBB+), then canonical SMILES, so selection is deterministic
  2. representatives ranked by Ertl SA ascending
  3. capped at 20
  4. Tanimoto and p(BBB+) reported as columns, not ranked on

Outputs:
  results/design_proposals.txt   the reportable table, both rankings
  results/design_proposals.csv   all 793, for the supplementary information
  results/design_proposals.png   figure: top pairs, parent beside product

Usage: ./env/bin/python -I scripts/design_rank.py
"""
import csv
import json
import sys

from rdkit import Chem, RDLogger
from rdkit.Chem import Draw, rdFMCS
from rdkit.Chem.Draw import rdMolDraw2D
from rdkit.Chem.Scaffolds import MurckoScaffold

sys.path.insert(0, "scripts")

RDLogger.DisableLog("rdApp.*")

CAP = 20
N_FIGURE = 6

nov = json.load(open("results/novelty.json"))
novel = nov["novel"]
checked = nov["checked"]
out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


for p in novel:
    p["scaffold"] = MurckoScaffold.MurckoScaffoldSmiles(
        mol=Chem.MolFromSmiles(p["smiles"]))

# ---------------------------------------------------- Amendment A2 ranking
by_scaffold = {}
for p in sorted(novel, key=lambda d: (d["sa"], -d["p_bbb"], d["smiles"])):
    by_scaffold.setdefault(p["scaffold"], p)
reps = sorted(by_scaffold.values(), key=lambda d: (d["sa"], -d["p_bbb"], d["smiles"]))
a2 = reps[:CAP]

# ------------------------------------------------- original registered rule
orig = sorted(novel, key=lambda d: (-d["max_tanimoto"], d["sa"]))[:CAP]

say("=" * 78)
say("A1.2 DESIGN PROPOSALS")
say("=" * 78)
say("EXPLORATORY. Post-dates registration 10.17605/OSF.IO/UQR62.")
say("Ranking per Amendment A2 (2026-11-21), which replaced the registered rule")
say("after that rule was found to select against novelty. Both are shown.")
say()
say("These are compounds on which a BBB prediction can be defended. They are NOT")
say("predicted to be active, and no activity model was applied. No claim of")
say("permeability, activity or therapeutic potential is made or implied.")
say()
say(f"novelty-filtered survivors : {len(novel)}  (no exact ChEMBL/PubChem match "
    f"as of {checked})")
say(f"distinct scaffolds         : {len(by_scaffold)}")
say(f"distinct parents           : {len({p['parent_chembl'] for p in novel})}")
say()

say("=" * 78)
say(f"TOP {CAP} UNDER AMENDMENT A2 - one per scaffold, ranked by synthetic accessibility")
say("=" * 78)
say(f"{'#':>3} {'tx':>4} {'SA':>5} {'Tani':>6} {'p(BBB+)':>8} {'MW':>6} {'cLogP':>6} "
    f"{'TPSA':>6}  parent")
for i, p in enumerate(a2, 1):
    say(f"{i:>3} {p['transformation']:>4} {p['sa']:>5.2f} {p['max_tanimoto']:>6.3f} "
        f"{p['p_bbb']:>8.3f} {p['mw']:>6.1f} {p['clogp']:>6.2f} {p['tpsa']:>6.1f}  "
        f"{p['parent_chembl']}")
say()
for i, p in enumerate(a2, 1):
    say(f"{i:>3}  {p['smiles']}")
say()

say("=" * 78)
say(f"TOP {CAP} UNDER THE ORIGINAL REGISTERED RULE, for comparison")
say("=" * 78)
say("Retained so the effect of Amendment A2 is visible. Not the reported set.")
say(f"{'#':>3} {'tx':>4} {'Tani':>6} {'SA':>5}  parent")
for i, p in enumerate(orig, 1):
    say(f"{i:>3} {p['transformation']:>4} {p['max_tanimoto']:>6.3f} {p['sa']:>5.2f}  "
        f"{p['parent_chembl']}")
say()
say(f"distinct parents in the A2 top {CAP}       : "
    f"{len({p['parent_chembl'] for p in a2})}")
say(f"distinct parents in the original top {CAP} : "
    f"{len({p['parent_chembl'] for p in orig})}")
say(f"distinct scaffolds, A2 / original       : "
    f"{len({p['scaffold'] for p in a2})} / {len({p['scaffold'] for p in orig})}")
say()
say("CAVEATS that must accompany any use of this table:")
say("  - Novelty is an exact full-InChIKey match check as of " + checked + ".")
say("    A stereoisomer, tautomer or salt of a known compound reads as unmatched.")
say("  - Close analogues exist by construction: each is a single edit of a known")
say("    active. No literature or patent search was performed.")
say("  - p(BBB+) comes from the model this paper audits. It is reported because")
say("    the compound is inside that model's domain, not because the model is")
say("    known to be correct out of it.")

# --------------------------------------------------------------- SI table
with open("results/design_proposals.csv", "w", newline="") as fh:
    w = csv.writer(fh)
    w.writerow(["rank_a2", "smiles", "parent_smiles", "parent_chembl",
                "transformation", "transformation_name", "scaffold",
                "max_tanimoto", "p_bbb", "sa", "mw", "clogp", "tpsa",
                "novelty_checked"])
    order = {p["smiles"]: i + 1 for i, p in enumerate(a2)}
    for p in sorted(novel, key=lambda d: (order.get(d["smiles"], 10**6), d["sa"])):
        w.writerow([order.get(p["smiles"], ""), p["smiles"], p["parent"],
                    p["parent_chembl"], p["transformation"], p["tname"],
                    p["scaffold"], p["max_tanimoto"], p["p_bbb"], p["sa"],
                    p["mw"], p["clogp"], p["tpsa"], checked])

# ----------------------------------------------------------------- figure
pairs, legends, highlights = [], [], []
for p in a2[:N_FIGURE]:
    par = Chem.MolFromSmiles(p["parent"])
    pro = Chem.MolFromSmiles(p["smiles"])
    try:
        mcs = rdFMCS.FindMCS([par, pro], timeout=10,
                             ringMatchesRingOnly=True, completeRingsOnly=False)
        patt = Chem.MolFromSmarts(mcs.smartsString)
        keep = set(pro.GetSubstructMatch(patt)) if patt else set()
        changed = [a.GetIdx() for a in pro.GetAtoms() if a.GetIdx() not in keep]
    except Exception:
        changed = []
    pairs += [par, pro]
    legends += [f"parent {p['parent_chembl']}",
                f"{p['transformation']}  SA {p['sa']:.2f}  "
                f"Tani {p['max_tanimoto']:.2f}  p(BBB+) {p['p_bbb']:.2f}"]
    highlights += [[], changed]

img = Draw.MolsToGridImage(pairs, molsPerRow=2, subImgSize=(420, 320),
                           legends=legends, highlightAtomLists=highlights,
                           useSVG=False, returnPNG=False)
img.save("results/design_proposals.png")

open("results/design_proposals.txt", "w").write("\n".join(out) + "\n")
json.dump(dict(exploratory=True, amendment="A2", novelty_checked=checked,
               n_novel=len(novel), n_scaffolds=len(by_scaffold),
               top_a2=a2, top_original_rule=orig),
          open("results/design_proposals.json", "w"), indent=2)
print("wrote results/design_proposals.{txt,csv,json,png}")
