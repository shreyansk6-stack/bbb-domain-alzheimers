"""Manuscript figures 1 and 3.

Descriptive only - nothing here feeds an estimate. Every set is rebuilt with
the same code paths the analyses used (confirmatory.load_b3db, targetset,
and the definition constructions copied from secondary_domain_defs.py), so a
figure cannot drift from the numbers it illustrates. The script asserts its
recomputed counts against the recorded results and fails loudly if they differ.

Figure 1  (a) how far apart the two chemical spaces actually are, in both
              directions, with the registered cutoff drawn on;
          (b) the registered manipulation check - property matching closes the
              descriptor gap that random matching leaves open.

Figure 3  the four applicability-domain definitions select largely disjoint
          compounds, and two of them are the same statistic.

Usage: ./env/bin/python -I scripts/make_figures.py data
"""
import json
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Crippen, Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402
from targetset import aligned_b3db_mols, load_target_smiles  # noqa: E402

RDLogger.DisableLog("rdApp.*")

# categorical slots 1-3, validated for CVD separation against the light surface
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID = "#0b0b0b", "#52514e", "#d8d7d2"
SURFACE = "#fcfcfb"

DESCRIPTORS = [
    ("MW", Descriptors.MolWt), ("cLogP", Crippen.MolLogP),
    ("TPSA", Descriptors.TPSA), ("HBD", Descriptors.NumHDonors),
    ("HBA", Descriptors.NumHAcceptors), ("RotB", Descriptors.NumRotatableBonds),
    ("ArRings", Descriptors.NumAromaticRings), ("FracCSP3", Descriptors.FractionCSP3),
    ("HeavyAt", Descriptors.HeavyAtomCount), ("Rings", Descriptors.RingCount),
    ("MolMR", Crippen.MolMR),
]

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
plt.rcParams.update({
    "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
    "text.color": INK, "xtick.color": MUTED, "ytick.color": MUTED,
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
})

CACHE = "results/figure_data.npz"

# ------------------------------------------------------------------ data
fps, y, props, _ = C.load_b3db(data_dir)
ref_mols = aligned_b3db_mols(data_dir)
actives = load_target_smiles(data_dir, "AChE")
act_mols = [Chem.MolFromSmiles(s) for _, s in actives]
target_fps = C.load_target(data_dir, "AChE")
assert len(ref_mols) == len(fps)

# both directions: the asymmetry is the point
import os  # noqa: E402
if os.path.exists(CACHE):
    _c = np.load(CACHE)
    sims_ref, sims_act = _c["sims_ref"], _c["sims_act"]
    print(f"loaded similarities from {CACHE}")
else:
    sims_ref = np.array(
        [max(DataStructs.BulkTanimotoSimilarity(f, target_fps)) for f in fps])
    sims_act = np.array(
        [max(DataStructs.BulkTanimotoSimilarity(f, fps)) for f in target_fps])
    np.savez(CACHE, sims_ref=sims_ref, sims_act=sims_act)

A_idx = np.where(sims_ref >= C.CUTOFF)[0]
prim = json.load(open("results/confirmatory_real.json"))
assert len(A_idx) == prim["proximal"]["n"], (
    f"recomputed n={len(A_idx)} != recorded {prim['proximal']['n']}")
N_PRIM = len(A_idx)


def desc_matrix(mols):
    return np.array([[f(m) for _, f in DESCRIPTORS] for m in mols], dtype=float)


D_ref, D_act = desc_matrix(ref_mols), desc_matrix(act_mols)
mu, sd = D_act.mean(axis=0), D_act.std(axis=0) + 1e-9
Zr, Za = (D_ref - mu) / sd, (D_act - mu) / sd

defs = {"A nearest-neighbour": A_idx}

act_scaffolds = set()
for m in act_mols:
    try:
        act_scaffolds.add(MurckoScaffold.MurckoScaffoldSmiles(mol=m))
    except Exception:
        pass
B_mask = np.zeros(len(ref_mols), dtype=bool)
for i, m in enumerate(ref_mols):
    try:
        B_mask[i] = MurckoScaffold.MurckoScaffoldSmiles(mol=m) in act_scaffolds
    except Exception:
        pass
defs["B scaffold"] = np.where(B_mask)[0]

cov = np.cov(Za, rowvar=False)
inv = np.linalg.pinv(cov + 1e-6 * np.eye(cov.shape[0]))
defs["C mahalanobis"] = np.argsort(
    np.array([float(v @ inv @ v) for v in Zr]))[:N_PRIM]

hat = np.linalg.pinv(Za.T @ Za)
defs["D leverage"] = np.argsort(
    np.array([float(v @ hat @ v) for v in Zr]))[:N_PRIM]

rec = json.load(open("results/secondary_domain_defs.json"))["definitions"]
for k in ("B scaffold", "C mahalanobis", "D leverage"):
    assert len(defs[k]) == rec[k]["n"], f"{k}: {len(defs[k])} != {rec[k]['n']}"

# ============================================================== figure 2
fig = plt.figure(figsize=(10.0, 3.9))
gs = fig.add_gridspec(1, 2, width_ratios=[1.45, 1.0], wspace=0.28)

ax = fig.add_subplot(gs[0, 0])
bins = np.linspace(0, 1, 51)
ax.hist(sims_act, bins=bins, color=ORANGE, alpha=0.80,
        label="AChE actives → nearest B3DB compound")
ax.hist(sims_ref, bins=bins, color=BLUE, alpha=0.72,
        label="B3DB compounds → nearest AChE active")
ax.axvline(C.CUTOFF, color=INK, lw=1.4, ls="--")

pct_ref = 100 * (sims_ref >= C.CUTOFF).mean()
ymax = ax.get_ylim()[1]
ax.set_ylim(0, ymax * 1.18)          # headroom so the legend clears the bars
ax.annotate(f"registered cutoff {C.CUTOFF}", xy=(C.CUTOFF, ymax * 0.70),
            xytext=(C.CUTOFF + 0.06, ymax * 0.70), fontsize=8,
            color=INK, va="center",
            arrowprops=dict(arrowstyle="->", color=INK, lw=0.9))
ax.text(0.56, ymax * 0.50,
        f"only {pct_ref:.1f}% of the labelled\nBBB reference ({N_PRIM} compounds)\n"
        f"reaches the cutoff",
        fontsize=8, color=MUTED, va="top")
ax.set_xlabel("maximum Tanimoto similarity to the other set (ECFP4)")
ax.set_ylabel("compounds")
ax.set_xlim(0, 1)
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_title("a   The two chemical spaces barely overlap", fontsize=10,
             fontweight="bold", loc="left")
for sp in ("top", "right"):
    ax.spines[sp].set_visible(False)

ax = fig.add_subplot(gs[0, 1])
labels = ["MW", "cLogP", "TPSA"]
# the SMDs were written to the recorded text output, not the JSON, and
# confirmatory.py is hash-gated and must not be re-run: parse the artifact.
import re  # noqa: E402
_txt = open("results/confirmatory_real.txt").read()
_m = re.findall(r"match quality vs proximal.*?MW\s+([-+\d.]+)\s+cLogP\s+"
                r"([-+\d.]+)\s+TPSA\s+([-+\d.]+)", _txt)
assert len(_m) == 2, f"expected two match-quality lines, found {len(_m)}"
rand = [abs(float(v)) for v in _m[0]]   # ARM B, random
prop = [abs(float(v)) for v in _m[1]]   # ARM C, property-matched
assert max(prop) < 0.1 <= max(rand), "parsed SMDs contradict the recorded verdict"
yy = np.arange(len(labels))
ax.barh(yy + 0.19, rand, height=0.34, color=ORANGE, label="random matching")
ax.barh(yy - 0.19, prop, height=0.34, color=BLUE, label="property matching")
ax.axvline(0.1, color=INK, lw=1.2, ls="--")
ax.text(0.105, len(labels) + 0.02, "|SMD| = 0.1\nregistered threshold",
        fontsize=7.5, color=INK, va="top")
for i, (r, p) in enumerate(zip(rand, prop)):
    ax.text(r + 0.012, i + 0.19, f"{r:.2f}", va="center", fontsize=7.5, color=MUTED)
    ax.text(p + 0.012, i - 0.19, f"{p:.2f}", va="center", fontsize=7.5, color=MUTED)
ax.set_yticks(yy)
ax.set_yticklabels(labels)
ax.set_xlim(0, 0.46)
ax.set_ylim(-0.75, len(labels) + 0.08)
ax.set_xlabel("|standardised mean difference| vs the proximal set")
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.set_title("b   Property matching closes the gap", fontsize=10,
             fontweight="bold", loc="left")
for sp in ("top", "right", "left"):
    ax.spines[sp].set_visible(False)

fig.tight_layout()
fig.savefig("results/fig1_chemical_space.png", dpi=300)
print("wrote results/fig1_chemical_space.png")

# ============================================================== figure 3
names = list(defs)
n = len(names)
J = np.zeros((n, n))
for i, a in enumerate(names):
    for j, b in enumerate(names):
        sa, sb = set(defs[a].tolist()), set(defs[b].tolist())
        J[i, j] = len(sa & sb) / len(sa | sb) if (sa | sb) else 0.0

fig, ax = plt.subplots(figsize=(7.2, 4.8))
im = ax.imshow(J, cmap="Blues", vmin=0, vmax=1, aspect="auto")
for i in range(n):
    for j in range(n):
        v = J[i, j]
        ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=11,
                color=SURFACE if v > 0.55 else INK,
                fontweight="bold" if i != j and v > 0.9 else "normal")
ax.set_xticks(range(n))
ax.set_yticks(range(n))
ax.set_xticklabels([x.split(" ", 1)[0] for x in names])
ax.set_yticklabels(names, fontsize=9)
ax.set_xticks(np.arange(-0.5, n, 1), minor=True)
ax.set_yticks(np.arange(-0.5, n, 1), minor=True)
ax.grid(which="minor", color=SURFACE, lw=2.5)
ax.tick_params(which="minor", length=0)
cb = fig.colorbar(im, ax=ax, fraction=0.045, pad=0.03)
cb.set_label("Jaccard overlap", fontsize=9)
cb.outline.set_visible(False)
fig.text(0.015, 0.945, "Four standard domain definitions, four different answers",
         fontsize=12, fontweight="bold", color=INK, va="top")
fig.text(0.015, 0.045,
         "C and D are the same statistic: Mahalanobis distance is leverage once the "
         "descriptors are centred\non the target mean. No other pair agrees above 0.15 "
         "\u2014 the definitions select different compounds.",
         fontsize=8.5, color=MUTED, va="bottom")
fig.subplots_adjust(left=0.20, right=0.86, top=0.855, bottom=0.235)
fig.savefig("results/fig3_domain_definitions.png", dpi=300)
print("wrote results/fig3_domain_definitions.png")

print("\nJaccard matrix")
print("                      " + "  ".join(f"{x.split(' ')[0]:>6}" for x in names))
for i, a in enumerate(names):
    print(f"{a:<22}" + "  ".join(f"{J[i, j]:>6.3f}" for j in range(n)))
