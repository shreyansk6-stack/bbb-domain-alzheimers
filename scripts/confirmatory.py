"""Confirmatory analysis: proximal holdout vs matched random holdouts.

Implements docs/preregistration.md sections 6-9 for the primary endpoint only:
dROC-AUC of an ECFP4 random forest on the AChE-proximal holdout versus a
property-matched random holdout of identical size and class balance.

    arm A  proximal        labelled B3DB compounds within Tanimoto 0.35 of AChE
                           chemistry, removed from training and used as eval
    arm B  random          size- and class-matched random holdouts, N draws
    arm C  property        as B, but propensity-matched on MW, cLogP, TPSA

Arm C governs the conclusion (preregistration section 8): proximal compounds are
larger and more lipophilic than B3DB's average, so a drop against arm B alone
could be molecular complexity rather than domain novelty.

Sign convention: dAUC = AUC(control) - AUC(proximal). Positive means the model
is WORSE on target-proximal chemistry, which is the hypothesis.

---------------------------------------------------------------------------
TWO MODES. The pre-registration commits to validating this code on
label-permuted data before it is ever run on real labels, as a substitute for
analyst blinding (docs/osf-submission.md, blinding section).

    --mode permuted   labels shuffled before modelling. Expected result:
                      AUC ~ 0.5 in every arm and dAUC ~ 0 with a CI covering
                      zero. Any systematic dAUC here is a harness bug, not a
                      finding. Run freely, as often as needed.

    --mode real       the one confirmatory run. REFUSES to start unless a
                      permuted run has already been recorded and the
                      registration identifier is supplied with --registered.

Usage:
    ./env/bin/python -I scripts/confirmatory.py data --mode permuted --draws 20
    ./env/bin/python -I scripts/confirmatory.py data --mode real \
        --draws 200 --registered <OSF registration DOI>
"""
import argparse
import hashlib
import json
import os
import platform
import statistics
import subprocess
import sys
import time
import warnings
from collections import defaultdict

import numpy as np
import pandas as pd
import sklearn
from rdkit import Chem, DataStructs, RDLogger
from rdkit.Chem import Descriptors, inchi, rdFingerprintGenerator
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (balanced_accuracy_score, brier_score_loss,
                             matthews_corrcoef, roc_auc_score)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler

RDLogger.DisableLog("rdApp.*")
# sklearn's sigmoid calibrator overflows in its Newton step when predicted
# probabilities are tightly clustered, which happens under permuted labels.
# Verified benign: the fitted calibrator is finite and Brier/ECE are sane.
warnings.filterwarnings("ignore", message=".*encountered in matmul",
                        category=RuntimeWarning)

# ----------------------------------------------------------------- pre-registered
SEED = 42
CUTOFF = 0.35                      # primary domain cutoff, preregistration section 6
SUPPORT_DELTA = 0.06               # decision rules, preregistration section 9
REFUTE_BAND = 0.03
BOOTSTRAP = 2000
ECE_BINS = 10
# primary ChEMBL recipe, docs/curation-decisions.md
RECIPE = dict(types={"IC50", "Ki"}, min_pchembl=6.0, conf={9}, assay_types=("B",))

gen = rdFingerprintGenerator.GetMorganGenerator(radius=2, fpSize=2048)


# =============================================================== chemistry helpers
def skeleton(mol):
    """First block of the InChIKey: connectivity only, no stereo or protonation."""
    try:
        key = inchi.MolToInchiKey(mol)
    except Exception:
        return None
    return key.split("-")[0] if key else None


def featurise(smiles):
    """SMILES -> (fingerprint, skeleton, (MW, cLogP, TPSA)) or (None, None, None)."""
    m = Chem.MolFromSmiles(smiles) if isinstance(smiles, str) else None
    if m is None:
        return None, None, None
    props = (Descriptors.MolWt(m), Descriptors.MolLogP(m), Descriptors.TPSA(m))
    return gen.GetFingerprint(m), skeleton(m), props


def fp_matrix(fps):
    """RDKit bit vectors -> dense uint8 array for sklearn."""
    X = np.zeros((len(fps), 2048), dtype=np.uint8)
    for i, f in enumerate(fps):
        DataStructs.ConvertToNumpyArray(f, X[i])
    return X


# ==================================================================== data loading
def load_b3db(data_dir):
    """Labelled reference set, deduplicated to InChIKey skeletons.

    Discordant skeletons (both BBB+ and BBB- on one connectivity) are excluded:
    contradictory ground truth. Matches scripts/curate_gate.py exactly.
    """
    df = pd.read_csv(f"{data_dir}/B3DB_classification.tsv", sep="\t").dropna(subset=["SMILES"])
    groups, unkeyed = defaultdict(list), []
    for smi, lab in zip(df["SMILES"], df["BBB+/BBB-"].astype(str)):
        fp, sk, props = featurise(smi)
        if fp is None:
            continue
        rec = (fp, lab, props)
        (groups[sk] if sk else unkeyed).append(rec)

    fps, labels, props, discordant = [], [], [], 0
    for members in groups.values():
        if len({lab for _, lab, _ in members}) > 1:
            discordant += 1
            continue
        fp, lab, pr = members[0]
        fps.append(fp); labels.append(lab); props.append(pr)
    for fp, lab, pr in unkeyed:
        fps.append(fp); labels.append(lab); props.append(pr)

    y = (np.array(labels) == "BBB+").astype(int)
    return fps, y, np.array(props), discordant


def load_target(data_dir, target):
    """Target actives under the primary curation recipe, skeleton-deduplicated."""
    probe = json.load(open(f"{data_dir}/chembl_probe.json"))
    per = defaultdict(list)
    for a in probe[target]:
        if a.get("standard_type") not in RECIPE["types"]:
            continue
        if a.get("confidence_score") not in RECIPE["conf"]:
            continue
        if a.get("assay_type") not in RECIPE["assay_types"]:
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

    fps, seen = [], set()
    for records in per.values():
        # replicates aggregated by median, threshold applied once (decision D5)
        if statistics.median([v for v, _ in records]) < RECIPE["min_pchembl"]:
            continue
        smi = next((s for _, s in records if s), None)
        fp, sk, _ = featurise(smi)
        if fp is None:
            continue
        if sk:
            if sk in seen:
                continue
            seen.add(sk)
        fps.append(fp)
    return fps


# ======================================================================== matching
def propensity_scores(props, is_proximal):
    """P(proximal | MW, cLogP, TPSA). The confound arm C is built to remove."""
    Z = StandardScaler().fit_transform(props)
    lr = LogisticRegression(max_iter=2000, random_state=SEED).fit(Z, is_proximal)
    return lr.predict_proba(Z)[:, 1]


def smd(a, b):
    """Standardised mean difference, for reporting match quality."""
    pooled = np.sqrt((a.var(ddof=1) + b.var(ddof=1)) / 2)
    return 0.0 if pooled == 0 else (a.mean() - b.mean()) / pooled


def draw_random(rng, pool, y, n_pos, n_neg):
    """Class-matched random holdout drawn from `pool` (indices into the full set)."""
    pos = pool[y[pool] == 1]
    neg = pool[y[pool] == 0]
    return np.concatenate([rng.choice(pos, n_pos, replace=False),
                           rng.choice(neg, n_neg, replace=False)])


def draw_propensity(rng, pool, y, prox_idx, ps, k=5):
    """Propensity-matched holdout: per proximal compound, one of its k nearest
    unmatched same-class neighbours in propensity. Sampling among k (rather than
    taking the single nearest) is what makes repeated draws a distribution
    instead of one deterministic set."""
    chosen = []
    taken = set()
    order = rng.permutation(len(prox_idx))
    by_class = {c: pool[y[pool] == c] for c in (0, 1)}
    for j in order:
        i = prox_idx[j]
        cands = by_class[y[i]]
        cands = np.array([c for c in cands if c not in taken])
        if len(cands) == 0:
            continue
        near = cands[np.argsort(np.abs(ps[cands] - ps[i]))[:k]]
        pick = int(rng.choice(near))
        taken.add(pick)
        chosen.append(pick)
    return np.array(chosen)


# ========================================================================= metrics
def ece(y, p, bins=ECE_BINS):
    """Expected calibration error, equal-width bins."""
    edges = np.linspace(0, 1, bins + 1)
    total = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (p > lo) & (p <= hi) if lo > 0 else (p >= lo) & (p <= hi)
        if m.sum() == 0:
            continue
        total += m.sum() / len(p) * abs(y[m].mean() - p[m].mean())
    return total


def evaluate(model, X_eval, y_eval, threshold):
    p = model.predict_proba(X_eval)[:, 1]
    hard = (p >= threshold).astype(int)
    return dict(
        auc=roc_auc_score(y_eval, p),
        mcc=matthews_corrcoef(y_eval, hard),
        bacc=balanced_accuracy_score(y_eval, hard),
        brier=brier_score_loss(y_eval, p),
        ece=ece(y_eval, p),
        n=len(y_eval),
        n_pos=int(y_eval.sum()),
    ), p


def fit_arm(X, y, holdout, params, seed):
    """Train on everything except `holdout`; return fitted model and the decision
    threshold, which is chosen from training-fold predictions only."""
    mask = np.ones(len(y), dtype=bool)
    mask[holdout] = False
    X_tr, y_tr = X[mask], y[mask]

    base = RandomForestClassifier(n_estimators=500, random_state=seed, n_jobs=-1, **params)
    # sigmoid calibration: monotonic, so it cannot alter AUC, only Brier/ECE
    model = CalibratedClassifierCV(base, method="sigmoid", cv=3).fit(X_tr, y_tr)

    # threshold from out-of-fold predictions on the training partition only
    oof = cross_val_predict(
        CalibratedClassifierCV(
            RandomForestClassifier(n_estimators=500, random_state=seed, n_jobs=-1, **params),
            method="sigmoid", cv=3),
        X_tr, y_tr, cv=StratifiedKFold(3, shuffle=True, random_state=seed),
        method="predict_proba")[:, 1]
    grid = np.linspace(0.05, 0.95, 91)
    threshold = float(grid[np.argmax([matthews_corrcoef(y_tr, (oof >= t).astype(int))
                                      for t in grid])])
    return model, threshold, int(mask.sum())


def tune(X, y, holdout, seed):
    """Hyperparameters by CV inside the primary arm's training partition.

    The chosen configuration is then shared by every arm. Shared rather than
    per-arm because an identical configuration cannot create a between-arm
    difference; see docs/decisions.md IC-2.
    """
    mask = np.ones(len(y), dtype=bool)
    mask[holdout] = False
    search = GridSearchCV(
        RandomForestClassifier(n_estimators=500, random_state=seed, n_jobs=-1),
        {"max_features": ["sqrt", 0.03], "class_weight": [None, "balanced"]},
        scoring="roc_auc", cv=StratifiedKFold(3, shuffle=True, random_state=seed),
    ).fit(X[mask], y[mask])
    return search.best_params_, float(search.best_score_)


# =========================================================================== gate
MIN_PERMUTED_DRAWS = 100


def check_unlocked(args):
    """Refuse the real-label run unless the registered preconditions are met.

    Not ceremony: a permuted run with a handful of draws proves nothing, so the
    recorded permuted run must be large enough to have detected a biased harness
    and must actually have come back null.
    """
    manifest = "results/confirmatory_permuted.json"
    if not args.registered:
        sys.exit("REFUSED: --mode real requires --registered <OSF registration DOI>.\n"
                 "The pre-registration is timestamped before the confirmatory run, "
                 "not after it.")
    if not os.path.exists(manifest):
        sys.exit(f"REFUSED: {manifest} not found.\n"
                 "The pre-registration commits to validating this pipeline on "
                 "label-permuted data first. Run --mode permuted.")
    m = json.load(open(manifest))
    if m.get("draws", 0) < MIN_PERMUTED_DRAWS:
        sys.exit(f"REFUSED: the recorded permuted run used {m.get('draws')} draws; "
                 f"{MIN_PERMUTED_DRAWS} are required.\nA permuted run too small to "
                 "detect a biased harness does not validate it.")
    # pinned to the script's own content, not to HEAD: editing this pipeline
    # re-locks the gate, while committing documentation does not
    if m.get("script_sha256") != script_sha256():
        sys.exit(f"REFUSED: the permuted run validated pipeline "
                 f"{str(m.get('script_sha256'))[:12]}, but this file hashes to "
                 f"{script_sha256()[:12]}.\nThe analysis code has changed since it "
                 "was validated. Re-run --mode permuted.")
    r = m.get("results", {}).get("property", {})
    if not (r.get("lo", -1) <= 0 <= r.get("hi", 1)):
        sys.exit(f"REFUSED: the permuted run returned dAUC {r.get('delta'):+.4f} with "
                 f"CI [{r.get('lo'):+.4f}, {r.get('hi'):+.4f}], which excludes zero.\n"
                 "The harness finds an effect where none exists. Fix it before "
                 "running on real labels.")
    print(f"gate passed: permuted run on pipeline {m['script_sha256'][:12]} "
          f"(commit {str(m.get('commit'))[:12]}), {m['draws']} draws, "
          f"dAUC {r['delta']:+.4f} CI [{r['lo']:+.4f}, {r['hi']:+.4f}]\n")


def current_commit():
    try:
        return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                              text=True, check=True).stdout.strip()
    except Exception:
        return "unavailable"


def script_sha256():
    """Content hash of this pipeline, so a validated run is tied to the code."""
    with open(os.path.abspath(__file__), "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?", default="data")
    ap.add_argument("--mode", choices=["permuted", "real"], required=True)
    ap.add_argument("--draws", type=int, default=200)
    ap.add_argument("--registered", default=None,
                    help="OSF registration DOI or URL; required for --mode real")
    ap.add_argument("--target", default="AChE")
    args = ap.parse_args()

    if args.mode == "real":
        check_unlocked(args)

    t0 = time.time()
    rng = np.random.default_rng(SEED)
    out = []

    def say(line=""):
        print(line)
        out.append(line)

    commit = current_commit()

    say("=" * 78)
    say(f"CONFIRMATORY RUN - mode: {args.mode.upper()}")
    say("=" * 78)
    if args.mode == "permuted":
        say("LABELS ARE PERMUTED. Nothing here is a result. This run exists to show")
        say("the harness produces no dAUC when there is no signal to find.")
    else:
        say(f"Registration: {args.registered}")
        say("Real labels. One run. Any analysis beyond this script is post hoc.")
    say(f"commit {commit}   seed {SEED}   draws {args.draws}")
    say(f"pipeline sha256 {script_sha256()}")
    say(f"python {platform.python_version()}  numpy {np.__version__}  "
        f"sklearn {sklearn.__version__}")
    say()

    # ------------------------------------------------------------------ build sets
    fps, y, props, discordant = load_b3db(args.data)
    say(f"B3DB labelled reference: {len(fps)} skeletons "
        f"({discordant} discordant excluded)   BBB+ {int(y.sum())}  BBB- {int((1 - y).sum())}")

    target_fps = load_target(args.data, args.target)
    say(f"{args.target} actives under primary recipe: {len(target_fps)}")

    sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, target_fps)) for f in fps])
    prox_idx = np.where(sims >= CUTOFF)[0]
    say(f"proximal holdout at Tanimoto {CUTOFF}: n={len(prox_idx)}  "
        f"BBB+ {int(y[prox_idx].sum())}  BBB- {int((1 - y[prox_idx]).sum())}")

    if args.mode == "permuted":
        y = rng.permutation(y)
        say(f"labels permuted; proximal class counts are now "
            f"{int(y[prox_idx].sum())}/{int((1 - y[prox_idx]).sum())}")

    n_pos, n_neg = int(y[prox_idx].sum()), int((1 - y[prox_idx]).sum())
    distal_pool = np.where(sims < CUTOFF)[0]
    full_pool = np.arange(len(y))
    X = fp_matrix(fps)
    say()

    # ------------------------------------------------------------- property profile
    say("Physicochemical profile (the confound arm C removes)")
    say(f"{'set':>12} {'MW':>14} {'cLogP':>12} {'TPSA':>14}")
    for name, idx in (("proximal", prox_idx), ("distal", distal_pool)):
        p = props[idx]
        say(f"{name:>12} {p[:, 0].mean():7.1f}+-{p[:, 0].std():<5.1f} "
            f"{p[:, 1].mean():5.2f}+-{p[:, 1].std():<4.2f} "
            f"{p[:, 2].mean():7.1f}+-{p[:, 2].std():<5.1f}")
    say("SMD proximal vs distal:  " + "  ".join(
        f"{n} {smd(props[prox_idx][:, i], props[distal_pool][:, i]):+.2f}"
        for i, n in enumerate(("MW", "cLogP", "TPSA"))))
    say()

    # --------------------------------------------------------------------- tuning
    params, cv_auc = tune(X, y, prox_idx, SEED)
    say(f"hyperparameters (CV inside the proximal arm's training partition): "
        f"{params}   inner CV AUC {cv_auc:.3f}")
    say("Shared across arms by construction, so tuning cannot advantage one arm.")
    say()

    # ----------------------------------------------------------------- arm A: real
    say("=" * 78)
    say("ARM A - proximal holdout")
    say("=" * 78)
    model, threshold, n_train = fit_arm(X, y, prox_idx, params, SEED)
    prox_metrics, prox_p = evaluate(model, X[prox_idx], y[prox_idx], threshold)
    say(f"trained on {n_train}   decision threshold {threshold:.2f} "
        f"(from training folds only)")
    say("  " + "  ".join(f"{k}={v:.4f}" if isinstance(v, float) else f"{k}={v}"
                         for k, v in prox_metrics.items()))
    say()

    # ---------------------------------------------------------------- control arms
    ps = propensity_scores(props, (sims >= CUTOFF).astype(int))

    arms = {}
    for arm, label in (("random", "ARM B - size/class-matched random holdout"),
                       ("property", "ARM C - property-matched holdout (GOVERNS)")):
        say("=" * 78)
        say(label)
        say("=" * 78)
        aucs, rows, contam, smds = [], [], [], []
        for d in range(args.draws):
            if arm == "random":
                # pre-registration wording: "a random set of identical size and
                # class balance", drawn from the whole labelled set. Proximal
                # compounds can therefore appear; the share is reported.
                hold = draw_random(rng, full_pool, y, n_pos, n_neg)
            else:
                hold = draw_propensity(rng, distal_pool, y, prox_idx, ps)
            mdl, thr, _ = fit_arm(X, y, hold, params, SEED + d)
            m, _ = evaluate(mdl, X[hold], y[hold], thr)
            aucs.append(m["auc"])
            rows.append(m)
            contam.append(np.isin(hold, prox_idx).mean())
            smds.append([smd(props[hold][:, i], props[prox_idx][:, i]) for i in range(3)])
            if (d + 1) % 10 == 0 or d == args.draws - 1:
                print(f"    draw {d + 1}/{args.draws}  AUC {m['auc']:.3f}", flush=True)
        aucs = np.array(aucs)
        arms[arm] = dict(aucs=aucs, rows=rows)
        say(f"{args.draws} draws   AUC mean {aucs.mean():.4f}  median "
            f"{np.median(aucs):.4f}  sd {aucs.std(ddof=1):.4f}  "
            f"[{np.percentile(aucs, 2.5):.4f}, {np.percentile(aucs, 97.5):.4f}]")
        for k in ("mcc", "bacc", "brier", "ece"):
            v = np.array([r[k] for r in rows])
            say(f"  {k:>6} mean {v.mean():.4f}  sd {v.std(ddof=1):.4f}")
        say(f"  proximal compounds inside the control holdout: "
            f"{100 * np.mean(contam):.1f}% mean")
        s = np.array(smds).mean(axis=0)
        say("  match quality vs proximal (SMD, |x|<0.1 is good):  " + "  ".join(
            f"{n} {s[i]:+.2f}" for i, n in enumerate(("MW", "cLogP", "TPSA"))))
        say()

    # ------------------------------------------------------------- primary endpoint
    say("=" * 78)
    say("PRIMARY ENDPOINT - dAUC = AUC(property-matched) - AUC(proximal)")
    say("=" * 78)

    # bootstrap the proximal AUC (stratified), pair each resample with a random
    # control draw, so the interval carries both sources of variability
    pos_i = np.where(y[prox_idx] == 1)[0]
    neg_i = np.where(y[prox_idx] == 0)[0]
    yp = y[prox_idx]
    boot = np.empty(BOOTSTRAP)
    for b in range(BOOTSTRAP):
        take = np.concatenate([rng.choice(pos_i, len(pos_i), replace=True),
                               rng.choice(neg_i, len(neg_i), replace=True)])
        boot[b] = roc_auc_score(yp[take], prox_p[take])

    results = {}
    for arm in ("property", "random"):
        c = arms[arm]["aucs"]
        delta = float(np.median(c) - prox_metrics["auc"])
        dist = c[rng.integers(0, len(c), BOOTSTRAP)] - boot
        lo, hi = float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))
        # one-sided empirical p: how often a control draw is no better than proximal
        p_emp = float((c <= prox_metrics["auc"]).mean())
        results[arm] = dict(delta=delta, lo=lo, hi=hi, p_emp=p_emp,
                            control_auc=float(np.median(c)))
        tag = "  <- PRIMARY" if arm == "property" else ""
        say(f"{arm:>9}: dAUC {delta:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]   "
            f"empirical p {p_emp:.4f}{tag}")
    say(f"  proximal AUC {prox_metrics['auc']:.4f}  "
        f"bootstrap 95% CI [{np.percentile(boot, 2.5):.4f}, "
        f"{np.percentile(boot, 97.5):.4f}]")
    say()

    # ------------------------------------------------------------- decision rules
    d = results["property"]
    if d["delta"] >= SUPPORT_DELTA and d["lo"] > 0:
        verdict = "SUPPORT"
        gloss = (f"dAUC {d['delta']:.3f} >= {SUPPORT_DELTA} with a CI excluding zero. "
                 "BBB prediction degrades on target-proximal chemistry.")
    elif d["lo"] >= -REFUTE_BAND and d["hi"] <= REFUTE_BAND:
        verdict = "REFUTATION (null result)"
        gloss = (f"The CI [{d['lo']:+.3f}, {d['hi']:+.3f}] lies inside +-{REFUTE_BAND}. "
                 "Nearest-neighbour domain distance does not predict BBB prediction "
                 "error in this setting.")
    else:
        verdict = "INCONCLUSIVE"
        gloss = (f"dAUC {d['delta']:+.3f}, CI [{d['lo']:+.3f}, {d['hi']:+.3f}]: neither "
                 f">= {SUPPORT_DELTA} with a CI excluding zero, nor contained within "
                 f"+-{REFUTE_BAND}. Not to be resolved by adding metrics, cutoffs, "
                 "models or targets.")
    say("=" * 78)
    say(f"PRE-SPECIFIED VERDICT: {verdict}")
    say("=" * 78)
    say(gloss)
    if args.mode == "permuted":
        say()
        say("Permuted labels: the verdict above is a harness check, not a finding.")
        say("Expected: arm AUCs near 0.500 and a dAUC CI covering zero. If the CI")
        say("excludes zero here, the pipeline is biased and must be fixed before")
        say("any real-label run.")
    if d["delta"] < SUPPORT_DELTA and d["hi"] > REFUTE_BAND:
        say()
        say(f"Note (preregistration section 9): minimum detectable dAUC at this "
            f"sample size is ~0.061. A null must be reported as 'no degradation "
            f"larger than ~0.06 AUC', never as no degradation.")
    say()
    say(f"elapsed {time.time() - t0:.0f}s")

    # ---------------------------------------------------------------------- output
    path = f"results/confirmatory_{args.mode}.txt"
    with open(path, "w") as fh:
        fh.write("\n".join(out) + "\n")
    manifest = dict(
        mode=args.mode, commit=commit, script_sha256=script_sha256(),
        seed=SEED, draws=args.draws,
        target=args.target, cutoff=CUTOFF, registered=args.registered,
        recipe={k: sorted(v) if isinstance(v, (set, tuple)) else v
                for k, v in RECIPE.items()},
        hyperparameters={k: str(v) for k, v in params.items()},
        threshold=threshold, n_train=n_train,
        proximal=prox_metrics, results=results, verdict=verdict,
        versions=dict(python=platform.python_version(), numpy=np.__version__,
                      sklearn=sklearn.__version__, pandas=pd.__version__),
        elapsed_s=round(time.time() - t0, 1),
    )
    with open(f"results/confirmatory_{args.mode}.json", "w") as fh:
        json.dump(manifest, fh, indent=2, default=float)
    print(f"\nwrote {path} and results/confirmatory_{args.mode}.json")


if __name__ == "__main__":
    main()
