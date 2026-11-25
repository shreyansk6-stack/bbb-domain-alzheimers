"""Redraw Figure 4 (design proposals, parent beside product) at print resolution.

`design_rank.py` emits this figure as a side effect of ranking, at a size that
prints under 300 dpi. Re-running that script to get a bigger PNG would also
rewrite `design_proposals.csv` — Additional file 2 — and re-touch the novelty
check, so the drawing is replayed here instead from the recorded
`results/design_proposals.json`.

The pairs, the MCS-based changed-atom highlighting and the legends are
identical to design_rank.py; only the canvas size and the saved dpi differ.
Nothing in this script ranks, filters or selects anything.

Usage: ./env/bin/python -I scripts/make_fig4.py
"""
import json

from rdkit import Chem
from rdkit.Chem import Draw, rdFMCS

N_FIGURE = 6
SUB = (604, 460)       # 1.44x design_rank.py's (420, 320); fits a page at 300 dpi
DPI = 300

a2 = json.load(open("results/design_proposals.json"))["top_a2"]

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

img = Draw.MolsToGridImage(pairs, molsPerRow=2, subImgSize=SUB,
                           legends=legends, highlightAtomLists=highlights,
                           useSVG=False, returnPNG=False)
img.save("results/design_proposals.png", dpi=(DPI, DPI))

w, h = img.size
print(f"wrote results/design_proposals.png")
print(f"  {w}x{h} px at {DPI} dpi = {w / DPI:.1f} x {h / DPI:.1f} in, "
      f"{len(pairs) // 2} pairs")
