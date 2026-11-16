"""Power simulation for the pre-registered primary endpoint (ΔROC-AUC).

Sample sizes are the curated ones from scripts/curate_gate.py, not the raw ones.
Generates the table and the minimum-detectable-effect figures quoted in
docs/preregistration.md section 9.

Model: binormal. Positives ~ N(d, 1), negatives ~ N(0, 1), with
d = sqrt(2) * Phi^-1(AUC), which gives a population AUC equal to the target.
AUC is computed rank-based (Mann-Whitney U) so ties are handled as in practice.

Usage: ./env/bin/python -I scripts/power.py
"""
import numpy as np
from math import sqrt
from scipy.stats import norm

SEED = 42
REPS = 4000
# 80% power, two-sided alpha = 0.05 -> z_(1-a/2) + z_(power) = 1.96 + 0.84
Z = 1.96 + 0.84

rng = np.random.default_rng(SEED)


def auc(pos, neg):
    """Rank-based AUC (Mann-Whitney U), tie-aware."""
    ranks = np.concatenate([pos, neg]).argsort().argsort() + 1
    n1, n0 = len(pos), len(neg)
    return (ranks[:n1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


def simulate(n_pos, n_neg, target_auc, reps=REPS):
    d = norm.ppf(target_auc) * sqrt(2)
    return np.array([auc(rng.normal(d, 1, n_pos), rng.normal(0, 1, n_neg))
                     for _ in range(reps)])


def mde(n_pos, n_neg, baseline):
    """Minimum detectable AUC difference against an equally sized holdout."""
    se_diff = simulate(n_pos, n_neg, baseline).std() * sqrt(2)
    return Z * se_diff, se_diff


print(f"binormal simulation | {REPS} replicates | seed {SEED}")
print("sample sizes are post-curation (InChIKey-skeleton deduplicated)\n")

print("=" * 72)
print("AChE-proximal holdout at Tanimoto 0.35: 464 BBB+ / 182 BBB-")
print("=" * 72)
print(f"{'true AUC':>10} {'SE':>8} {'95% CI width':>15}")
for a in [0.95, 0.90, 0.85, 0.80]:
    s = simulate(464, 182, a)
    print(f"{a:>10.2f} {s.std():>8.4f} {'+/-' + format(1.96 * s.std(), '.3f'):>15}")

print("\nMinimum detectable dAUC vs a size- and class-matched random holdout")
print("(80% power, two-sided alpha = 0.05; conservative - repeated control draws do better)")
for a in [0.90, 0.85]:
    m, se = mde(464, 182, a)
    print(f"  baseline AUC {a:.2f}:  SE(diff) {se:.4f}   MDE dAUC ~ {m:.3f}")

print("\n" + "=" * 72)
print("Alternatives, for the record (none is the pre-registered primary)")
print("=" * 72)
alts = {
    "AChE at 0.4":            (218, 93),
    "BACE1 at 0.35":          (64, 37),
    "BACE1 at 0.4":           (18, 10),
}
for label, (n1, n0) in alts.items():
    m, se = mde(n1, n0, 0.90)
    print(f"  {label:>16} (n={n1 + n0:>4}): SE {se / sqrt(2):.4f}   MDE dAUC ~ {m:.3f}")

print("""
Pre-registered sufficiency criterion: >=200 labelled compounds with >=50 per class
at the 0.35 cutoff. AChE (611; 464/182) passes. BACE1 (101) fails, and its MDE of
~0.124 confirms that measuring error there could not distinguish signal from noise.

BACE1 class counts above are apportioned by the overall B3DB class ratio, since the
BACE1-proximal set is too small to split reliably. They are indicative only; the
sufficiency criterion is evaluated on the actual total, which fails regardless.
""")
