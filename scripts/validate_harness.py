"""Is the proximal arm's AUC unbiased under the null?

The proximal arm of the confirmatory design (scripts/confirmatory.py) has one
fixed evaluation set: the 492 labelled B3DB compounds within Tanimoto 0.35 of
AChE chemistry. A single label permutation therefore gives its AUC one
realisation, and a run of unlucky realisations can look exactly like harness
bias. Four permuted runs once returned a mean dAUC of +0.030 with two
descriptive tail probabilities of 0.010 and 0.005 on data containing no signal
at all, which prompted this check (docs/decisions.md IC-5).

Two independent tests, both on permuted labels only. Nothing here reads the real
labels; the real-label analysis stays gated inside confirmatory.py.

  1. Model frozen, evaluation labels permuted. Isolates the metric from
     everything else. Must centre on 0.500 with the Hanley-McNeil standard
     deviation for this class split.

  2. Joint permutation: labels permuted, model retrained, arm A rebuilt, across
     many seeds. This is what the validation runs actually do. Must centre on
     0.500 with the same spread.

Test 1 passing while test 2 failed would mean the training side leaks. Both
passing means an apparent effect in a permuted run is sampling noise in a single
evaluation set, not bias.

Hyperparameters are held at the modal selection from the tuning grid rather than
retuned per seed, to isolate the question being asked: whether the arm's AUC is
centred. Retuning per seed adds grid-selection noise to the thing being measured.

Usage: ./env/bin/python -I scripts/validate_harness.py data
"""
import sys

import numpy as np
from rdkit import DataStructs
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402

DATA = sys.argv[1] if len(sys.argv) > 1 else "data"
EVAL_PERM_REPS = 2000
SEEDS = [42, 7, 2024, 99, 1, 13, 256, 777, 31415, 8, 500, 64]
PARAMS = {"class_weight": "balanced", "max_features": "sqrt"}

print("=" * 74)
print("HARNESS VALIDATION - proximal arm, permuted labels only")
print("=" * 74)
print(f"pipeline under test: confirmatory.py  sha256 {C.script_sha256()[:16]}")
print()

fps, y_real, props, discordant = C.load_b3db(DATA)
tfps = C.load_target(DATA, "AChE")
sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, tfps)) for f in fps])
prox_idx = np.where(sims >= C.CUTOFF)[0]
X = C.fp_matrix(fps)
print(f"labelled reference {len(fps)}   proximal holdout n={len(prox_idx)} "
      f"at Tanimoto {C.CUTOFF}")
print()

# ---------------------------------------------- test 1: evaluation labels only
print("-" * 74)
print("TEST 1  model frozen, evaluation labels permuted")
print("-" * 74)
rng = np.random.default_rng(C.SEED)
y = np.random.default_rng(C.SEED).permutation(y_real)
model, _, _ = C.fit_arm(X, y, prox_idx, PARAMS, C.SEED)
raw, _ = model.predict_proba(X[prox_idx])
yp = y[prox_idx]
n1, n0 = int(yp.sum()), int(len(yp) - yp.sum())

perm = np.array([roc_auc_score(rng.permutation(yp), raw) for _ in range(EVAL_PERM_REPS)])
hm = np.sqrt((len(yp) + 1) / (12 * n1 * n0))
print(f"scores: {len(np.unique(raw))} distinct values, sd {raw.std():.4f}")
print(f"{EVAL_PERM_REPS} permutations: mean {perm.mean():.4f}  sd {perm.std():.4f}  "
      f"95% [{np.percentile(perm, 2.5):.4f}, {np.percentile(perm, 97.5):.4f}]")
print(f"Hanley-McNeil sd for {n1}/{n0}: {hm:.4f}")
t1_ok = abs(perm.mean() - 0.5) < 0.005 and abs(perm.std() - hm) < 0.005
print(f"verdict: {'PASS' if t1_ok else 'FAIL'} - the metric itself is centred")
print()

# ------------------------------------------------- test 2: joint permutation
print("-" * 74)
print("TEST 2  labels permuted and model retrained, across seeds")
print("-" * 74)
print(f"{'seed':>8} {'eval pos':>9} {'arm A AUC':>10}")
aucs = []
for s in SEEDS:
    ys = np.random.default_rng(s).permutation(y_real)
    mdl, _, _ = C.fit_arm(X, ys, prox_idx, PARAMS, C.SEED)
    r, _ = mdl.predict_proba(X[prox_idx])
    a = roc_auc_score(ys[prox_idx], r)
    aucs.append(a)
    print(f"{s:>8} {int(ys[prox_idx].sum()):>9} {a:>10.4f}", flush=True)
aucs = np.array(aucs)
se = aucs.std(ddof=1) / np.sqrt(len(aucs))
t = (aucs.mean() - 0.5) / se
print(f"\nmean {aucs.mean():.4f}  sd {aucs.std(ddof=1):.4f}  "
      f"range [{aucs.min():.4f}, {aucs.max():.4f}]  n={len(aucs)}")
print(f"t vs 0.5: {t:+.2f}")
t2_ok = abs(t) < 2.5
print(f"verdict: {'PASS' if t2_ok else 'FAIL'} - the arm is centred under the null")
print()

print("=" * 74)
print(f"OVERALL: {'PASS' if (t1_ok and t2_ok) else 'FAIL'}")
print("=" * 74)
print(f"""The proximal arm's AUC varies with sd ~{aucs.std(ddof=1):.3f} across
permutations because it is measured on one fixed set of {len(prox_idx)} compounds.
That spread is irreducible and is why the pre-registered minimum detectable
dAUC is ~0.061 rather than something smaller. It also means a single permuted
run cannot establish that the harness is unbiased: the gate in
confirmatory.py therefore requires {C.MIN_PERMUTATIONS} permuted runs and judges their
mean, not any one of them.""")
