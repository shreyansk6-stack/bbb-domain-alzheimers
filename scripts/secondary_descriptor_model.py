"""Secondary model: gradient boosting on curated 2D descriptors.

PRE-REGISTERED SECONDARY (section 8, model 2 of 3), with one declared
deviation.

DEVIATION. The registration specifies "curated 2D Mordred descriptors".
Mordred is not a dependency of this project and is unmaintained against current
Python and numpy; adding it would mean pinning an unmaintained package into the
environment that produced the registered results. The substantive requirement
is a descriptor-based baseline standing against the fingerprint-based primary
model, not Mordred specifically, so RDKit's own 2D descriptor set is used
instead and the substitution is declared here, in docs/decisions.md and in the
manuscript. It is a deviation decided with knowledge of the confirmatory result
but with no knowledge of this model's result, since this is its first run.

Curation is unsupervised and label-free: non-finite columns, zero-variance
columns, then one of each pair correlated above |r| = 0.95, dropped in a fixed
column order so the result does not depend on iteration order. No label is
consulted, so the curation cannot leak outcome information.

Everything else follows the confirmatory design unchanged: the same proximal
holdout at Tanimoto 0.35, the same property-matched and random control arms,
the same per-fold Platt calibration, the same decision-threshold rule, AUC on
the uncalibrated score, and the same paired-bootstrap interval.

50 control draws rather than 200, for the reason given in
scripts/secondary_cutoffs.py: the control mean is estimated to ~0.002 at 50
draws while the proximal arm is one fixed evaluation set with sd ~0.027.

Usage: ./env/bin/python -I scripts/secondary_descriptor_model.py data
"""
import json
import sys
import time

import numpy as np
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import matthews_corrcoef, roc_auc_score

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402
from targetset import aligned_b3db_mols  # noqa: E402

RDLogger.DisableLog("rdApp.*")

DRAWS = 50
CORR_MAX = 0.95
GRID = [dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=31),
        dict(max_iter=300, learning_rate=0.05, max_leaf_nodes=15),
        dict(max_iter=500, learning_rate=0.03, max_leaf_nodes=31)]

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
t0 = time.time()
out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


class DescModel:
    """Mirrors confirmatory.ArmModel: 3-fold CV, Platt per fold, folds averaged.

    Kept structurally identical so the two models differ only in features and
    learner, not in how they are fitted, calibrated or thresholded.
    """

    def __init__(self, params, seed):
        self.params, self.seed = params, seed

    def fit(self, X, y):
        self.folds = []
        oof = np.zeros(len(y))
        skf = StratifiedKFold(3, shuffle=True, random_state=self.seed)
        for tr, te in skf.split(X, y):
            gb = HistGradientBoostingClassifier(random_state=self.seed,
                                                **self.params).fit(X[tr], y[tr])
            held = gb.predict_proba(X[te])[:, 1]
            cal = LogisticRegression(C=1e6, max_iter=1000).fit(
                held.reshape(-1, 1), y[te])
            oof[te] = cal.predict_proba(held.reshape(-1, 1))[:, 1]
            self.folds.append((gb, cal))
        self.oof = oof
        return self

    def predict_proba(self, X):
        raws = np.column_stack([gb.predict_proba(X)[:, 1] for gb, _ in self.folds])
        cals = np.column_stack([cal.predict_proba(raws[:, [i]])[:, 1]
                                for i, (_, cal) in enumerate(self.folds)])
        return raws.mean(axis=1), cals.mean(axis=1)


def fit_desc_arm(X, y, holdout, params, seed):
    train = np.setdiff1d(np.arange(len(y)), holdout)
    model = DescModel(params, seed).fit(X[train], y[train])
    ths = np.linspace(0.05, 0.95, 91)
    thr = float(max(ths, key=lambda t: matthews_corrcoef(
        y[train], (model.oof >= t).astype(int))))
    return model, thr, len(train)


def evaluate(model, X_eval, y_eval, thr):
    raw, cal = model.predict_proba(X_eval)
    pred = (cal >= thr).astype(int)
    return dict(auc=roc_auc_score(y_eval, raw),
                mcc=matthews_corrcoef(y_eval, pred),
                bacc=float(((pred[y_eval == 1] == 1).mean()
                            + (pred[y_eval == 0] == 0).mean()) / 2),
                brier=float(np.mean((cal - y_eval) ** 2)),
                ece=C.ece(y_eval, cal)), raw


say("=" * 78)
say("SECONDARY MODEL - gradient boosting on curated 2D descriptors")
say("=" * 78)
say("PRE-REGISTERED SECONDARY. The primary model and verdict are unchanged.")
say("DEVIATION: RDKit 2D descriptors substituted for Mordred (see header).")
say(f"commit {C.current_commit()}   draws {DRAWS}")
say()

fps, y, props, _ = C.load_b3db(data_dir)
mols = aligned_b3db_mols(data_dir)
assert len(mols) == len(fps), f"alignment broken: {len(mols)} vs {len(fps)}"
say(f"B3DB labelled reference: {len(fps)}   rows verified aligned")

names = [n for n, _ in Descriptors._descList]
funcs = [f for _, f in Descriptors._descList]
raw = np.full((len(mols), len(funcs)), np.nan)
for i, m in enumerate(mols):
    for j, f in enumerate(funcs):
        try:
            raw[i, j] = f(m)
        except Exception:
            pass
say(f"RDKit 2D descriptors computed: {raw.shape[1]}")

keep = np.isfinite(raw).all(axis=0)
say(f"  after dropping non-finite columns: {keep.sum()}")
keep &= np.concatenate([[raw[:, j].std() > 1e-9] if keep[j] else [False]
                        for j in range(raw.shape[1])])
say(f"  after dropping zero-variance columns: {keep.sum()}")

idx = np.where(keep)[0]
sub = raw[:, idx]
corr = np.corrcoef(sub, rowvar=False)
drop = set()
for a in range(len(idx)):
    if a in drop:
        continue
    for b in range(a + 1, len(idx)):
        if b not in drop and abs(corr[a, b]) > CORR_MAX:
            drop.add(b)
final = [idx[a] for a in range(len(idx)) if a not in drop]
D = raw[:, final]
say(f"  after pruning |r| > {CORR_MAX}: {D.shape[1]} descriptors retained")
say()

target_fps = C.load_target(data_dir, "AChE")
sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, target_fps)) for f in fps])
prox_idx = np.where(sims >= C.CUTOFF)[0]
distal_pool = np.where(sims < C.CUTOFF)[0]
full_pool = np.arange(len(y))
n_pos, n_neg = int(y[prox_idx].sum()), int((1 - y[prox_idx]).sum())
say(f"proximal holdout at Tanimoto {C.CUTOFF}: n={len(prox_idx)}  "
    f"BBB+ {n_pos}  BBB- {n_neg}")

best, best_auc = None, -1
train0 = np.setdiff1d(np.arange(len(y)), prox_idx)
for g in GRID:
    m = DescModel(g, C.SEED).fit(D[train0], y[train0])
    a = roc_auc_score(y[train0], m.oof)
    if a > best_auc:
        best, best_auc = g, a
say(f"hyperparameters (inside the proximal arm's training partition): {best}   "
    f"inner CV AUC {best_auc:.3f}")
say("Shared across arms by construction.")
say()

say("=" * 78)
say("ARM A - proximal holdout")
say("=" * 78)
model, thr, n_train = fit_desc_arm(D, y, prox_idx, best, C.SEED)
pm, pp = evaluate(model, D[prox_idx], y[prox_idx], thr)
say(f"trained on {n_train}   threshold {thr:.2f}")
say("  " + "  ".join(f"{k}={v:.4f}" for k, v in pm.items()))
say()

ps = C.propensity_scores(props, (sims >= C.CUTOFF).astype(int))
rng = np.random.default_rng(C.SEED)
arms = {}
for arm, label in (("random", "ARM B - size/class-matched random holdout"),
                   ("property", "ARM C - property-matched holdout (GOVERNS)")):
    say("=" * 78)
    say(label)
    say("=" * 78)
    aucs, smds = [], []
    for d in range(DRAWS):
        hold = (C.draw_random(rng, full_pool, y, n_pos, n_neg) if arm == "random"
                else C.draw_propensity(rng, distal_pool, y, prox_idx, ps))
        mdl, t2, _ = fit_desc_arm(D, y, hold, best, C.SEED + d)
        m, _ = evaluate(mdl, D[hold], y[hold], t2)
        aucs.append(m["auc"])
        smds.append([C.smd(props[hold][:, i], props[prox_idx][:, i]) for i in range(3)])
        if (d + 1) % 10 == 0:
            print(f"    draw {d + 1}/{DRAWS}  AUC {m['auc']:.3f}", flush=True)
    aucs = np.array(aucs)
    arms[arm] = aucs
    s = np.array(smds).mean(axis=0)
    say(f"{DRAWS} draws   AUC mean {aucs.mean():.4f}  median {np.median(aucs):.4f}  "
        f"sd {aucs.std(ddof=1):.4f}")
    say("  match quality (SMD):  " + "  ".join(
        f"{nm} {s[i]:+.2f}" for i, nm in enumerate(("MW", "cLogP", "TPSA"))))
    say()

pos_i = np.where(y[prox_idx] == 1)[0]
neg_i = np.where(y[prox_idx] == 0)[0]
yp = y[prox_idx]
boot = np.empty(C.BOOTSTRAP)
for b in range(C.BOOTSTRAP):
    take = np.concatenate([rng.choice(pos_i, len(pos_i), replace=True),
                           rng.choice(neg_i, len(neg_i), replace=True)])
    boot[b] = roc_auc_score(yp[take], pp[take])

say("=" * 78)
say("SECONDARY ENDPOINT - dAUC, descriptor model")
say("=" * 78)
results = {}
for arm in ("property", "random"):
    c = arms[arm]
    delta = float(np.median(c) - pm["auc"])
    dist = c[rng.integers(0, len(c), C.BOOTSTRAP)] - boot
    lo, hi = float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))
    results[arm] = dict(delta=delta, lo=lo, hi=hi, control_auc=float(np.median(c)))
    say(f"{arm:>9}: dAUC {delta:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]"
        + ("  <- comparable to the primary endpoint" if arm == "property" else ""))
say(f"  proximal AUC {pm['auc']:.4f}")
say()

prim = json.load(open("results/confirmatory_real.json"))
say("=" * 78)
say("SIDE BY SIDE WITH THE PRIMARY (FINGERPRINT) MODEL")
say("=" * 78)
say(f"{'model':<34} {'proximal':>9} {'control':>8} {'dAUC':>9} {'95% CI':>21}")
say(f"{'ECFP4 random forest (primary)':<34} {prim['proximal']['auc']:>9.4f} "
    f"{prim['results']['property']['control_auc']:>8.4f} "
    f"{prim['results']['property']['delta']:>+9.4f} "
    f"{'[' + format(prim['results']['property']['lo'], '+.4f') + ', ' + format(prim['results']['property']['hi'], '+.4f') + ']':>21}")
say(f"{'Descriptor gradient boosting':<34} {pm['auc']:>9.4f} "
    f"{results['property']['control_auc']:>8.4f} {results['property']['delta']:>+9.4f} "
    f"{'[' + format(results['property']['lo'], '+.4f') + ', ' + format(results['property']['hi'], '+.4f') + ']':>21}")
say()
say("The primary verdict is unchanged whatever this shows. A secondary model that")
say("agreed would corroborate; one that disagreed would be a reportable limitation.")
say()
say(f"elapsed {time.time() - t0:.0f}s")

open("results/secondary_descriptor_model.txt", "w").write("\n".join(out) + "\n")
json.dump(dict(secondary=True, deviation="RDKit 2D descriptors substituted for Mordred",
               commit=C.current_commit(), draws=DRAWS, n_descriptors=int(D.shape[1]),
               hyperparameters=best, proximal=pm, results=results),
          open("results/secondary_descriptor_model.json", "w"), indent=2, default=float)
print("wrote results/secondary_descriptor_model.txt")
