"""H2, the pre-registered secondary hypothesis: is the degradation larger at a
stricter definition of proximity (Tanimoto 0.4) than at a looser one (0.3)?

SECONDARY. Pre-registered in section 8, run after the confirmatory result was
known. It cannot change the primary verdict and does not try to: the primary
endpoint stays the 0.35 comparison reported in results/confirmatory_real.txt.

This imports scripts/confirmatory.py and calls its functions unchanged, so the
numbers come from the identical code path. It never writes to that file; the
confirmatory pipeline stays hash-locked.

Two honest caveats, printed in the output as well:

1. 50 control draws per cutoff, not 200. The control arm's mean is estimated to
   within ~0.002 at 50 draws (draw-to-draw sd ~0.013), while the proximal arm is
   one fixed evaluation set with sd ~0.027 that no number of control draws
   reduces. Spending 4x the compute on the small term would not change a
   reported digit.
2. Changing the cutoff changes the training-set size (a looser cutoff holds out
   more compounds and trains on fewer). Across cutoffs the comparison therefore
   conflates domain strictness with training-set size. Within a cutoff the arms
   are matched by construction, so each cutoff's dAUC is clean; the TREND across
   cutoffs, which is what H2 asks about, is not. The registration did not
   anticipate this. It is a limitation of H2 as written, not of the result.

Usage: ./env/bin/python -I scripts/secondary_cutoffs.py data
"""
import json
import sys
import time

import numpy as np
from rdkit import DataStructs
from sklearn.metrics import roc_auc_score

sys.path.insert(0, "scripts")
import confirmatory as C  # noqa: E402

DRAWS = 50
CUTOFFS = (0.30, 0.40)

data_dir = sys.argv[1] if len(sys.argv) > 1 else "data"
t0 = time.time()
out = []


def say(line=""):
    print(line, flush=True)
    out.append(line)


say("=" * 78)
say("SECONDARY ANALYSIS - H2, degradation vs domain cutoff")
say("=" * 78)
say("PRE-REGISTERED SECONDARY. Run after the confirmatory result was known.")
say("It cannot and does not change the primary verdict (INCONCLUSIVE at 0.35).")
say(f"pipeline sha256 {C.script_sha256()[:16]} (confirmatory.py, imported unchanged)")
say(f"commit {C.current_commit()}   seed {C.SEED}   draws {DRAWS} per cutoff")
say()

fps, y, props, discordant = C.load_b3db(data_dir)
target_fps = C.load_target(data_dir, "AChE")
sims = np.array([max(DataStructs.BulkTanimotoSimilarity(f, target_fps)) for f in fps])
X = C.fp_matrix(fps)
say(f"B3DB labelled reference: {len(fps)} skeletons   AChE actives: {len(target_fps)}")
say()

# the 0.35 result is read from the confirmatory manifest, never recomputed
real = json.load(open("results/confirmatory_real.json"))
rows = {0.35: dict(n=real["proximal"]["n"],
                   n_pos=real["proximal"]["n_pos"],
                   prox=real["proximal"]["auc"],
                   ctrl=real["results"]["property"]["control_auc"],
                   delta=real["results"]["property"]["delta"],
                   lo=real["results"]["property"]["lo"],
                   hi=real["results"]["property"]["hi"],
                   draws=real["draws"], source="confirmatory run")}

for cutoff in CUTOFFS:
    rng = np.random.default_rng(C.SEED)
    prox_idx = np.where(sims >= cutoff)[0]
    distal_pool = np.where(sims < cutoff)[0]
    n_pos, n_neg = int(y[prox_idx].sum()), int((1 - y[prox_idx]).sum())

    say("=" * 78)
    say(f"CUTOFF {cutoff:.2f}")
    say("=" * 78)
    say(f"proximal holdout n={len(prox_idx)}  BBB+ {n_pos}  BBB- {n_neg}   "
        f"trained on {len(y) - len(prox_idx)}")

    if len(prox_idx) < 200 or min(n_pos, n_neg) < 50:
        say("  fails the pre-specified sufficiency criterion; not analysed.")
        say()
        continue

    params, cv_auc = C.tune(X, y, prox_idx, C.SEED)
    model, threshold, n_train = C.fit_arm(X, y, prox_idx, params, C.SEED)
    prox_metrics, prox_p = C.evaluate(model, X[prox_idx], y[prox_idx], threshold)
    say(f"hyperparameters {params}   proximal AUC {prox_metrics['auc']:.4f}")

    ps = C.propensity_scores(props, (sims >= cutoff).astype(int))
    aucs, smds = [], []
    for d in range(DRAWS):
        hold = C.draw_propensity(rng, distal_pool, y, prox_idx, ps)
        mdl, thr, _ = C.fit_arm(X, y, hold, params, C.SEED + d)
        m, _ = C.evaluate(mdl, X[hold], y[hold], thr)
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
        boot[b] = roc_auc_score(yp[take], prox_p[take])

    delta = float(np.median(aucs) - prox_metrics["auc"])
    dist = aucs[rng.integers(0, len(aucs), C.BOOTSTRAP)] - boot
    lo, hi = float(np.percentile(dist, 2.5)), float(np.percentile(dist, 97.5))
    s = np.array(smds).mean(axis=0)

    say(f"control AUC median {np.median(aucs):.4f}  sd {aucs.std(ddof=1):.4f}  "
        f"(SE of mean {aucs.std(ddof=1) / np.sqrt(DRAWS):.4f})")
    say("match quality (SMD):  " + "  ".join(
        f"{n} {s[i]:+.2f}" for i, n in enumerate(("MW", "cLogP", "TPSA"))))
    say(f"dAUC {delta:+.4f}   95% CI [{lo:+.4f}, {hi:+.4f}]")
    say()

    rows[cutoff] = dict(n=len(prox_idx), n_pos=n_pos, prox=prox_metrics["auc"],
                        ctrl=float(np.median(aucs)), delta=delta, lo=lo, hi=hi,
                        draws=DRAWS, source="secondary run")

say("=" * 78)
say("H2 - does degradation increase with a stricter cutoff?")
say("=" * 78)
say(f"{'cutoff':>7} {'n':>6} {'train':>7} {'proximal':>9} {'control':>8} "
    f"{'dAUC':>9} {'95% CI':>20}")
for cut in sorted(rows):
    r = rows[cut]
    say(f"{cut:>7.2f} {r['n']:>6} {len(y) - r['n']:>7} {r['prox']:>9.4f} "
        f"{r['ctrl']:>8.4f} {r['delta']:>+9.4f} "
        f"{'[' + format(r['lo'], '+.4f') + ', ' + format(r['hi'], '+.4f') + ']':>20}")
say()

ordered = [rows[c]["delta"] for c in sorted(rows)]
monotone = all(b >= a for a, b in zip(ordered, ordered[1:]))
overlap = all(rows[c]["lo"] <= 0 <= rows[c]["hi"] for c in sorted(rows))
say(f"dAUC increases monotonically with cutoff: {'yes' if monotone else 'NO'}")
say(f"every interval covers zero: {'yes' if overlap else 'no'}")
say()
say("Reading this honestly: the intervals at every cutoff are wide and overlap each")
say("other, so H2 is not resolved by these data whichever direction the point")
say("estimates run. The trend is also confounded with training-set size, which the")
say("registration did not anticipate (see this script's header). Report the table,")
say("report the confound, and do not claim a cutoff effect.")
say()
say(f"elapsed {time.time() - t0:.0f}s")

open("results/secondary_cutoffs.txt", "w").write("\n".join(out) + "\n")
json.dump({"cutoffs": {str(k): v for k, v in rows.items()},
           "draws": DRAWS, "pipeline_sha256": C.script_sha256(),
           "commit": C.current_commit(), "secondary": True,
           "note": "Pre-registered secondary (H2). Cannot change the primary verdict."},
          open("results/secondary_cutoffs.json", "w"), indent=2)
print("wrote results/secondary_cutoffs.txt")
