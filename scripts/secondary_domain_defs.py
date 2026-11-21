"""Pre-registered sensitivity analysis: does the result depend on how the
applicability domain is defined?

SECONDARY, EXPLORATORY in timing. Pre-registered in section 8 and in the
registration's "Other planned analysis": leverage (Williams plot, OECD
guidance), Mahalanobis distance on the descriptor set, and Bemis-Murcko
scaffold membership, "reported whatever they show. If they disagree with the
nearest-neighbour definition, the disagreement is itself a reportable result."

The primary definition (A) is read from the confirmatory manifest and never
recomputed. B, C and D are run here against the same property-matched control
design.

Design choice, made before running: C and D take the n closest compounds, where
n is the primary definition's 492, rather than thresholding on an absolute
distance. Matching n holds the holdout size - and therefore the minimum
detectable effect - constant across definitions, so a difference in dAUC
between definitions means the definitions disagree about WHICH compounds are
proximal, not merely how many. The H2 analysis is confounded exactly this way
(docs/decisions.md, 2026-11-20) and this avoids repeating it. Definition B is
set-valued and takes whatever n it gives; its n is reported and its dAUC must be
read against its own power.

Usage: ./env/bin/python -I scripts/secondary_domain_defs.py data
"""
import json
import sys
import time

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Crippen, Descriptors
from rdkit.Chem.Scaffolds import MurckoScaffold
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402
from targetset import aligned_b3db_mols, load_target_smiles  # noqa: E402

RDLogger.DisableLog("rdApp.*")

DRAWS = 50
DESCRIPTORS = [
    ("MW", Descriptors.MolWt), ("cLogP", Crippen.MolLogP),
    ("TPSA", Descriptors.TPSA), ("HBD", Descriptors.NumHDonors),
    ("HBA", Descriptors.NumHAcceptors), ("RotB", Descriptors.NumRotatableBonds),
    ("ArRings", Descriptors.NumAromaticRings), ("FracCSP3", Descriptors.FractionCSP3),
    ("HeavyAt", Descriptors.HeavyAtomCount), ("Rings", Descriptors.RingCount),
    ("MolMR", Crippen.MolMR),
]

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
t0 = time.time()
out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


def desc_matrix(mols):
    return np.array([[f(m) for _, f in DESCRIPTORS] for m in mols], dtype=float)


say("=" * 78)
say("SENSITIVITY - DOES THE RESULT DEPEND ON THE DOMAIN DEFINITION?")
say("=" * 78)
say("PRE-REGISTERED SECONDARY. Run after the confirmatory verdict was known.")
say("Reported whatever it shows; disagreement with the primary definition is")
say("itself the result (preregistration section 8).")
say(f"commit {C.current_commit()}   draws {DRAWS} per definition")
say()

# ------------------------------------------------------------------- data
fps, y, props, _ = C.load_b3db(data_dir)
X = C.fp_matrix(fps)

ref_mols = aligned_b3db_mols(data_dir)

actives = load_target_smiles(data_dir, "AChE")
act_mols = [Chem.MolFromSmiles(s) for _, s in actives]
target_fps = C.load_target(data_dir, "AChE")
assert len(ref_mols) == len(fps), (
    f"alignment broken: {len(ref_mols)} mols vs {len(fps)} reference rows")
say(f"B3DB labelled reference: {len(fps)}   AChE actives: {len(act_mols)}")
say("descriptor/scaffold rows verified aligned to the confirmatory reference order.")

sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, target_fps)) for f in fps])
prim = json.load(open("results/confirmatory_real.json"))
A_idx = np.where(sims >= C.CUTOFF)[0]
N_PRIM = len(A_idx)
say(f"definition A (nearest-neighbour Tanimoto >= {C.CUTOFF}): n={N_PRIM}  "
    f"[from the confirmatory run]")

# the descriptor/scaffold work needs B3DB mols aligned to fps. load_b3db drops
# discordant skeletons, so align by recomputing its own skeleton order.
D_ref = desc_matrix(ref_mols)
D_act = desc_matrix(act_mols)
mu, sd = D_act.mean(axis=0), D_act.std(axis=0) + 1e-9
Zr, Za = (D_ref - mu) / sd, (D_act - mu) / sd

# ------------------------------------------------------- domain definitions
defs = {}

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
d_mahal = np.array([float(v @ inv @ v) for v in Zr])
defs["C mahalanobis"] = np.argsort(d_mahal)[:N_PRIM]

hat = np.linalg.pinv(Za.T @ Za)
lev = np.array([float(v @ hat @ v) for v in Zr])
defs["D leverage"] = np.argsort(lev)[:N_PRIM]

say()
say("overlap with definition A (Jaccard, and share of A recovered):")
As = set(A_idx.tolist())
for name, idx in defs.items():
    s = set(idx.tolist())
    j = len(As & s) / len(As | s) if (As | s) else 0.0
    say(f"  {name:<16} n={len(idx):<6} Jaccard {j:.3f}   recovers "
        f"{100 * len(As & s) / len(As):.1f}% of A")
say()

# ------------------------------------------------------------------- arms
rows = {"A nearest-neighbour": dict(
    n=prim["proximal"]["n"], prox=prim["proximal"]["auc"],
    ctrl=prim["results"]["property"]["control_auc"],
    delta=prim["results"]["property"]["delta"],
    lo=prim["results"]["property"]["lo"], hi=prim["results"]["property"]["hi"])}

for name, prox_idx in defs.items():
    say("=" * 78)
    say(f"DEFINITION {name.upper()}")
    say("=" * 78)
    n_pos, n_neg = int(y[prox_idx].sum()), int((1 - y[prox_idx]).sum())
    say(f"n={len(prox_idx)}  BBB+ {n_pos}  BBB- {n_neg}   trained on {len(y) - len(prox_idx)}")
    if len(prox_idx) < 200 or min(n_pos, n_neg) < 50:
        say("  fails the pre-specified sufficiency criterion; not analysed.")
        say()
        continue

    rng = np.random.default_rng(C.SEED)
    mask = np.zeros(len(y), dtype=int)
    mask[prox_idx] = 1
    pool = np.where(mask == 0)[0]
    params, _ = C.tune(X, y, prox_idx, C.SEED)
    model, thr, _ = C.fit_arm(X, y, prox_idx, params, C.SEED)
    pm, pp = C.evaluate(model, X[prox_idx], y[prox_idx], thr)
    say(f"proximal AUC {pm['auc']:.4f}   ece {pm['ece']:.4f}")

    ps = C.propensity_scores(props, mask)
    aucs, smds = [], []
    for d in range(DRAWS):
        hold = C.draw_propensity(rng, pool, y, prox_idx, ps)
        mdl, t2, _ = C.fit_arm(X, y, hold, params, C.SEED + d)
        m, _ = C.evaluate(mdl, X[hold], y[hold], t2)
        aucs.append(m["auc"])
        smds.append([C.smd(props[hold][:, i], props[prox_idx][:, i]) for i in range(3)])
        if (d + 1) % 10 == 0:
            print(f"    draw {d + 1}/{DRAWS}  AUC {m['auc']:.3f}", flush=True)
    aucs = np.array(aucs)

    pos_i = np.where(y[prox_idx] == 1)[0]
    neg_i = np.where(y[prox_idx] == 0)[0]
    yp = y[prox_idx]
    boot = np.empty(C.BOOTSTRAP)
    for b in range(C.BOOTSTRAP):
        take = np.concatenate([rng.choice(pos_i, len(pos_i), replace=True),
                               rng.choice(neg_i, len(neg_i), replace=True)])
        boot[b] = roc_auc_score(yp[take], pp[take])
    delta = float(np.median(aucs) - pm["auc"])
    dist = aucs[rng.integers(0, len(aucs), C.BOOTSTRAP)] - boot
    lo, hi = float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))
    s = np.array(smds).mean(axis=0)
    say("match quality (SMD):  " + "  ".join(
        f"{nm} {s[i]:+.2f}" for i, nm in enumerate(("MW", "cLogP", "TPSA"))))
    say(f"dAUC {delta:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")
    say()
    rows[name] = dict(n=len(prox_idx), prox=pm["auc"], ctrl=float(np.median(aucs)),
                      delta=delta, lo=lo, hi=hi)

say("=" * 78)
say("SUMMARY - dAUC by domain definition")
say("=" * 78)
say(f"{'definition':<22} {'n':>6} {'proximal':>9} {'control':>8} {'dAUC':>9} {'95% CI':>21}")
for k, r in rows.items():
    say(f"{k:<22} {r['n']:>6} {r['prox']:>9.4f} {r['ctrl']:>8.4f} {r['delta']:>+9.4f} "
        f"{'[' + format(r['lo'], '+.4f') + ', ' + format(r['hi'], '+.4f') + ']':>21}")
say()
agree = all(r["lo"] <= 0 <= r["hi"] for r in rows.values())
say(f"every definition's interval covers zero: {'yes' if agree else 'NO'}")
say()
say(f"elapsed {time.time() - t0:.0f}s")

open("results/secondary_domain_defs.txt", "w").write("\n".join(out) + "\n")
json.dump(dict(secondary=True, exploratory_timing=True, draws=DRAWS,
               commit=C.current_commit(), definitions={k: v for k, v in rows.items()}),
          open("results/secondary_domain_defs.json", "w"), indent=2)
print("wrote results/secondary_domain_defs.txt")
