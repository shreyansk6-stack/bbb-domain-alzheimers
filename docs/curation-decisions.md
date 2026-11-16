# ChEMBL curation decisions

**Decided 2026-11-16**, from the literature and from the actual metadata
distribution in our own data, and fixed before any modelling. Each decision states
what was chosen, why, what it costs, and whether it changes the result.

This supersedes the "placeholder decisions awaiting a chemist's judgement" recorded
on 2026-11-14. The second author is a chemistry major but not specialised in enzyme
kinetics, so these are made from published curation standards and verified
empirically rather than by domain authority. **The manuscript must therefore justify
them by citation and sensitivity analysis, not by expert assertion.** That is a
weaker rhetorical position and a stronger scientific one.

## The evidence base

Two primary papers disagree, and the disagreement is real:

- **Kalliokoski, Kramer, Vulpetti & Gedeck, *PLoS ONE* 2013**
  (`10.1371/journal.pone.0061007`). Analysed ChEMBL IC50 reproducibility across
  independent measurements of identical protein–ligand systems. The standard
  deviation of IC50 data is only ~25% larger than that of Ki data, so "mixing IC50
  data from different assays, even not knowing assay conditions details, only adds
  a moderate amount of noise." Pooling Ki with IC50 is acceptable given an offset
  correction, pIC50 running ~0.35 log units above pKi.
- **Landrum & Riniker, *J. Chem. Inf. Model.* 2024**
  (`10.1021/acs.jcim.4c00049`). Same approach, blunter conclusion: under minimal
  curation, almost 65% of paired points differ by more than 0.3 log units, 27% by
  more than one log unit, Kendall's τ only 0.51. Maximal curation improves this to
  48% / 13% / τ = 0.71 at the cost of data volume. They find similar noise when
  pooling Ki data from different sources, and recommend against casual combination.

Supporting: **Papadatos, Gaulton, Hersey & Overington, *J. Comput. Aided Mol. Des.*
2015** (`10.1007/s10822-015-9860-5`) on ChEMBL's own curation and filter strategy,
and **Araripe, Seal, Béquignon & van Westen, *JCIM* 2026**
(`10.1021/acs.jcim.6c00802`, CAPRICHO) for current practice, whose design principle
— flag quality issues and preserve data for inspection rather than silently
deleting it — this document follows.

**We measured the disagreement in our own data** (`scripts/probe_chembl.py`). Among
compounds with more than one measurement against the same target: BACE1, 46.9% span
more than 0.3 log units and 18.1% more than 1.0; AChE, 34.0% and 17.2%. Landrum and
Riniker are describing something real and present here.

## Why that controversy does not govern this study

Both papers are about **the accuracy of potency values**. Their concern is fatal to
regression modelling of pIC50 from pooled sources.

**We do not model potency.** ChEMBL is used here only to answer "what chemistry has
medicinal chemistry produced against this target," so that we can ask whether BBB
predictors cover it. The activity threshold determines *set membership*, nothing
more. No potency value enters any model, any endpoint, or any reported result.

So the question is not "are these values accurate" but "does the composition of the
compound set change the conclusion." That is empirical, and
`scripts/sensitivity.py` answers it directly (see the table at the end).

## Decisions

### D1 — Pool IC50 and Ki; exclude Kd

Pooled, with **no offset correction**. An offset is a potency correction and we
report no potencies; applying one would only move compounds across the threshold
boundary.

Cost: accepts the pooling noise both papers describe. Justified because set
membership, not potency, is at stake, and because the sensitivity analysis shows
IC50-only drifts the result by ≤1.2 pp.

Kd excluded: 26 BACE1 and 59 AChE records, and Kd for a competitive enzyme
inhibitor is not measuring the same thing. Including it changes the result by
≤0.2 pp, so this is cosmetic rather than substantive.

**Pre-registered sensitivity:** IC50-only and Ki-only, reported separately.

### D2 — Confidence score 9 only (direct single-protein assignment)

**This is the one substantive filter**, and it was decided by inspecting the data.

ChEMBL's confidence score describes certainty in target assignment; 9 is a directly
assigned single protein, 8 a homologous one. Our records split 70.8% / 29.2%
(BACE1) and 80.7% / 19.3% (AChE) between 9 and 8.

Checking what the score-8 assays actually are: **score-9 assays are 100%
*Homo sapiens*, while score-8 assays have `assay_organism` unspecified, or
non-human — *Cercopithecidae*, *Cavia porcellus*.** That matches `relationship_type`
H (homologous) exactly. This matters disproportionately for AChE, where assays on
*Electrophorus* and *Torpedo* enzyme are common in the literature and have different
inhibitor SAR from the human protein.

Since the claim is about chemistry directed at a **human** target, only direct
assignments qualify. Cost: 29.2% of BACE1 and 19.3% of AChE records. Including
score 8 drifts the result by 0.3 pp (BACE1) and 4.1 pp (AChE).

### D3 — Assay type B (binding) only

99.9% of BACE1 and 99.3% of AChE records are already type B. Dropping the 17
functional and 33 ADMET records costs essentially nothing and removes a category
that measures something different. Effect on the result: ≤0.4 pp.

### D4 — Activity threshold pChEMBL ≥ 6

Retained. 1 µM is the conventional cut for "active" in QSAR dataset construction,
and it is what the scoping analysis used, so keeping it avoids the appearance of
having tuned a threshold after seeing overlap numbers.

It is the loosest-held decision here, so the sweep is pre-registered and reported in
full: pChEMBL ≥ 5, 6, 7, 8. Drift across that whole range is ≤4.0 pp for BACE1 and
≤8.1 pp for AChE, the largest at ≥8 where n falls to 475.

**No per-target threshold.** Tempting, since the targets have different potency
distributions, but a threshold chosen per target is a free parameter per target, and
with two targets and one headline contrast that is exactly the parameter a skeptical
reviewer would suspect of being fitted. One threshold for both, swept.

### D5 — Replicate aggregation by median pChEMBL

Where a compound has several measurements against a target, take the **median**
pChEMBL and apply the threshold once to that. Median rather than mean, because the
spread we measured is heavy-tailed (BACE1 max 4.47 log units).

Compounds are **not** excluded for wide replicate spread. Following CAPRICHO's
flag-don't-delete principle, the spread is reported as a data-quality statistic. A
compound measured inconsistently is still a compound medicinal chemistry made
against the target, which is all we require of it.

### D6 — Filters asserted although currently no-ops

`standard_relation = '='`, `data_validity_comment is null`, `standard_units = 'nM'`,
`target_organism = 'Homo sapiens'`. All four are **already 100% satisfied** in
ChEMBL_37 for these targets, because ChEMBL only assigns `pchembl_value` to clean,
uncensored records. They are asserted in code anyway: free insurance if ChEMBL's
behaviour changes, and the manuscript can state them as applied rather than leaving
a reader to wonder.

Recorded explicitly as verified no-ops so that no one later mistakes them for the
filters that did the work. D2 did the work.

### D7 — Primary domain cutoff stays 0.35

Flagged because there is a temptation here and it should be on the record. At the
0.3 cutoff the AChE-proximal set is 1,066 compounds with a minimum detectable ΔAUC
of 0.041; at 0.35 it is 492 compounds and 0.061. Looser cutoff, better power.

**Keeping 0.35.** Tanimoto 0.3 on Morgan fingerprints is a weak claim of chemical
similarity, and the paper's entire argument is about what counts as inside a domain —
buying power by loosening that definition would undercut the thing being argued. The
0.3 and 0.4 cutoffs are pre-registered as secondary and reported regardless.

Stated plainly: 0.35 was fixed before these class counts were known, and moving it
afterwards to gain power would be endpoint selection.

## Does any of it change the answer? No.

Out-of-domain percentage of target actives, every variant
(`results/sensitivity.txt`):

| | BACE1 <0.3 | AChE <0.3 |
| --- | --- | --- |
| **Primary recipe** | **85.8%** | **28.4%** |
| + confidence 8 | 86.0% | 27.0% |
| IC50 only | 85.9% | 29.6% |
| Ki only | 83.6% | 21.7% |
| + Kd | 85.8% | 28.3% |
| pChEMBL ≥ 5 | 81.8% | 30.0% |
| pChEMBL ≥ 7 | 88.0% | 31.7% |
| pChEMBL ≥ 8 | 89.4% | 36.4% |
| assay B+F+A | 85.8% | 28.2% |
| no skeleton dedup | 85.5% | 28.3% |

Across every recipe, BACE1 ranges 81.8–89.4% and AChE 21.7–36.4%. **The worst case
for the contrast still leaves a 45-point gap** (BACE1 81.8% vs AChE 36.4%). The
finding is not an artefact of any curation decision available to us.

This table is the answer to the reviewer who asks why these thresholds. Not "a
chemist chose them" but "here is every alternative, and none of them matters."

## Resulting primary sets

| | actives | B3DB labelled within 0.35 | gate |
| --- | --- | --- | --- |
| BACE1 | 5,157 | 89 (60 BBB+, 29 BBB−) | **fails** |
| AChE | 2,391 | 492 (366 BBB+, 126 BBB−) | passes |

BACE1 remains unmeasurable on the pre-registered criterion (≥200 compounds, ≥50 per
class), now failing on both counts rather than one. AChE passes with less margin
than before: 492 rather than 611, giving a minimum detectable ΔAUC of **0.061**.
