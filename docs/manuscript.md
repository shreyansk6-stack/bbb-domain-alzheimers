# Applicability domain of blood–brain barrier predictors in Alzheimer's target chemical space: a methods audit and domain-constrained design

**Shreyan Kancharla¹, Samuel Siyanbola¹**

¹ _[affiliation — to be completed]_

**Pre-registered** on OSF Registries, 2026-11-19, DOI
[10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62), against commit
`134ab60`. Analysis code, decision log, literature search and all results:
<https://github.com/shreyansk6-stack/bbb-domain-alzheimers>

> **DRAFT.** Numbers are final and traceable to `results/`. Passages needing author
> input are marked **[AUTHORS]**. Reference list is in author-year placeholder form
> and needs formatting to the target journal **[AUTHORS]**.

---

## Abstract

Alzheimer's virtual-screening pipelines routinely rank compounds for activity
against a target such as BACE1 or acetylcholinesterase (AChE), then pass the hits
through an off-the-shelf blood–brain barrier (BBB) permeability predictor. Those
predictors are trained on literature-derived data dominated by approved and
CNS-active drugs, while target inhibitor series are narrow, heavily optimised
medicinal chemistry. Published BBB models report applicability-domain (AD) coverage
on their own held-out test sets and therefore report high coverage — 93.9%, 94.8%
and "complete structural coverage" in three 2026 reports. Because a held-out split
is drawn from the training distribution, that figure is near-guaranteed by
construction and carries no information about deployment.

We pre-registered a three-arm audit measuring whether a B3DB-trained BBB classifier
degrades on compounds structurally proximal to AChE inhibitor chemistry, against
controls matched on size, class balance and physicochemical properties. The primary
endpoint was ΔROC-AUC with a pre-specified support threshold of 0.06.

The result is **inconclusive**: ΔAUC +0.028, 95% CI [−0.016, +0.075], against a
minimum detectable effect of 0.061. We report this as "no degradation larger than
approximately 0.06 AUC", not as evidence of no degradation.

Four findings are more consequential than the primary endpoint. First, **about half
the apparent domain effect is physicochemical confounding**: against an unmatched
random control the gap is +0.055 with an interval excluding zero, and
property-matching halves it. Second, **BACE1 chemistry cannot be audited at all** —
only 89 labelled compounds fall within Tanimoto 0.35 of it, failing a pre-specified
sufficiency criterion, so BBB filters applied to BACE1 hits in the literature cannot
be validated with public data. Third, **standard AD definitions disagree about which
compounds they include**, overlapping at Jaccard 0.13–0.14, and two of the three we
tested are the same statistic. Fourth, **no off-the-shelf BBB tool can be evaluated
without contamination**, because the available tools are trained on the only
available public ground truth.

We also report a domain-constrained design exercise producing 793 structures with no
exact match in ChEMBL or PubChem, and three internal inconsistencies in our own
pre-registered design that only execution revealed.

---

## 1. Introduction

**[AUTHORS: this section is the thinnest and most conventional part of the draft;
it needs your framing and additional citations.]**

A standard Alzheimer's virtual-screening workflow has two stages. Compounds are
ranked for predicted activity against a target — most commonly BACE1 or AChE — and
the resulting hits are filtered for predicted brain penetration using a published
BBB permeability model. The second stage is treated as a commodity: a model is
selected, applied, and its output used as a gate.

That treatment assumes the BBB model's predictions are valid for the compounds it is
being applied to. The assumption is rarely examined, and there is structural reason
to doubt it. BBB training sets are literature compilations weighted toward approved
drugs and CNS-active agents. Target inhibitor series are the product of iterative
medicinal-chemistry optimisation around a small number of scaffolds. There is no
reason for the two distributions to coincide.

The standard instrument for this question is the applicability domain. In practice
AD coverage is almost always computed on the model's own held-out test set. A
held-out split is drawn from the training distribution, so high coverage follows by
construction. Three 2026 reports illustrate this directly: 93.9% coverage on a
212-compound internal test set (Pharmaceutics 2026a), 94.8% on an internal B3DB
split (Pharmaceutics 2026b), and "complete structural coverage" (Comput Biol Chem
2026). None measures coverage against the target-directed chemistry the filter is
deployed on.

A systematic Europe PMC search (2026-11-16; five queries, 35 unique candidate
records, all abstracts read, four near neighbours read in full; recorded in
`docs/literature-search.md`) returned no study measuring BBB-model domain coverage
against target inhibitor chemistry, and none measuring BBB prediction error as a
function of distance from that chemistry.

We pre-registered an audit of exactly that question. We state at the outset that the
study was powered for a moderate effect and returned an inconclusive primary result,
and that its contribution lies in what the surrounding analyses establish about
whether the question can be answered with public data at all.

---

## 2. Methods

Full detail, including every decision and its rejected alternatives, is in
`docs/preregistration.md` and `docs/decisions.md`. This section summarises; nothing
here departs from the registration except where explicitly flagged as a deviation or
amendment.

### 2.1 Data

**BBB labels.** B3DB classification dataset (Meng et al. 2021), fetched 2026-11-14,
CC0. Structures were deduplicated on the first block of the InChIKey — connectivity
only, dropping stereochemical and protonation layers — because deduplication on
canonical SMILES finds no duplicates in B3DB while the 2D Morgan fingerprints used
here cannot distinguish the stereoisomers it preserves. 7,805 records reduced to
4,022 skeletons, of which 130 carried contradictory BBB+/BBB− labels and were
excluded as unusable ground truth, retained only for structural geometry. **Labelled
reference set: 3,892 compounds (2,472 BBB+, 1,420 BBB−).**

**Target actives.** ChEMBL_37 (released 2026-05-01, CC BY-SA 3.0) queried 2026-11-16
for human BACE1 (CHEMBL4822) and human AChE (CHEMBL220). Inclusion fixed in advance:
IC50 or Ki, standard relation "=", no data-validity comment, units nM, assay type B,
**assay confidence score 9**, replicates aggregated by median pChEMBL, threshold
pChEMBL ≥ 6. Yield: **5,157 BACE1 actives, 2,391 AChE actives.**

The confidence-score filter is the one that does work. Score-9 assays for these
targets are 100% *Homo sapiens*, while score-8 assays have assay organism
unspecified or non-human — material for AChE, where *Electrophorus* and *Torpedo*
enzyme assays are common and have different inhibitor SAR. Four other filters
(relation, validity comment, units, organism) are asserted in code but verified to
be no-ops in ChEMBL_37 for these targets; we record this so they are not mistaken
for the filters that mattered.

Potency enters only through set membership; no potency value enters any model or
endpoint. The known disagreement over pooling IC50 with Ki (Kalliokoski et al. 2013;
Landrum & Riniker 2024) therefore does not govern this study, and we test rather
than assert it: across ten curation variants the headline out-of-domain fraction
spans 81.8–89.4% for BACE1 and 21.7–36.4% for AChE, leaving at least a
45-percentage-point contrast in every case.

No data were refetched after registration.

### 2.2 Domain definition

Primary: **maximum Tanimoto similarity ≥ 0.35** to the target active set, on Morgan
fingerprints (radius 2, 2048 bits). The cutoff was fixed before the resulting class
counts were known. A looser cutoff of 0.30 would have yielded better power and was
explicitly declined, with the reasoning recorded, on the grounds that Tanimoto 0.30
on Morgan fingerprints is a weak claim of chemical similarity and that buying power
by loosening the definition of "in domain" would undercut the study's own argument.

Pre-specified alternatives, reported whatever they showed: Bemis–Murcko scaffold
membership, Mahalanobis distance and leverage over an 11-descriptor space (§3.5).

### 2.3 Design

Three arms on the single labelled set:

- **Arm A, proximal holdout.** Every labelled compound within Tanimoto 0.35 of AChE
  chemistry is removed from training (n = 492; 366 BBB+, 126 BBB−); the model trains
  on the remainder and is evaluated on the held-out proximal set.
- **Arm B, size- and class-matched random holdout.** Equal size and class balance,
  drawn at random, 200 independent draws.
- **Arm C, property-matched holdout.** As B, but drawn by propensity matching on
  molecular weight, cLogP and TPSA; 200 draws. **Arm C governs.**

Training-set size is identical across arms (3,400) by construction. Arm C exists
because arms A and B share a confound: if proximal compounds differ systematically
in bulk properties, a performance drop could reflect molecular character rather than
domain novelty. Propensity matching draws each control from the five nearest
same-class neighbours in propensity score, so repeated draws form a distribution
rather than one deterministic set. Arm B draws from the whole labelled set,
following the registered wording, so a fraction of each arm-B holdout is itself
proximal (13.3% realised); this dilutes the contrast and is the conservative
reading.

**Manipulation check**, registered: |SMD| < 0.1 on all three covariates for arm C, or
the comparison is reported as confounded rather than accepted.

### 2.4 Models

1. **ECFP4 random forest** (500 trees), Morgan radius 2, 2048 bits. **Primary.**
2. **Gradient boosting on curated 2D descriptors.** Secondary. *Deviation:* the
   registration specifies Mordred; Mordred is not a dependency of this project and
   is unmaintained against current Python and numpy, so RDKit's 2D descriptor set
   was substituted. Curation is unsupervised and label-free (non-finite, then
   zero-variance, then one of each pair with |r| > 0.95, in fixed column order),
   retaining 173 of 210 descriptors. Declared in `docs/decisions.md`.
3. **An off-the-shelf published BBB tool.** **Dropped**; see §3.7.

Hyperparameters were selected by 3-fold cross-validated grid search inside arm A's
training partition only and shared across arms, since an identical configuration
cannot produce a between-arm difference. Selected: `max_features = 0.03`,
`class_weight = None`, inner CV AUC 0.887.

Probabilities were calibrated by per-fold Platt scaling with fold models averaged.
Decision thresholds were chosen by maximising MCC on held-out training-fold
predictions within each arm's own training partition, never on its evaluation set.

**ROC-AUC is computed on the uncalibrated score.** Platt scaling is monotone in
expectation but can fit a negative slope when there is no signal, inverting the
ranking and reflecting AUC about 0.5. We observed this during label-permuted
validation and corrected it before any real-label run.

### 2.5 Endpoints and decision rules

Primary: **ΔROC-AUC = AUC(arm C) − AUC(arm A)**, positive meaning worse on proximal
chemistry. Interval estimation pairs a class-stratified bootstrap of the proximal
AUC (2,000 resamples) with a randomly drawn control AUC, carrying both the proximal
arm's sampling error and the controls' draw-to-draw variability.

Registered decision rules, evaluated by the analysis script and printed as a
verdict:

| verdict | condition |
| --- | --- |
| support | ΔAUC ≥ 0.06 **and** 95% CI excludes zero |
| refutation | 95% CI contained entirely within ±0.03 |
| inconclusive | anything else |

No tail probability is reported. A one-sided quantity comparing the proximal AUC
against the control *draw* distribution was implemented, tested on permuted data,
found to return 0.010 and 0.005 on data containing no signal, and discarded: it
ignores the proximal arm's sampling error (~0.027), which dominates.

Power: simulation at 366 versus 126 gives SE(AUC) = 0.016 at a true AUC of 0.90 and
a **minimum detectable ΔAUC of 0.061** at 80% power, two-sided α = 0.05. A
pre-specified sufficiency criterion — ≥200 compounds with ≥50 per class — determines
whether a target is analysable at all.

### 2.6 Pre-registration and validation of the analysis

Analyst blinding is unavailable in a single-analyst computational study, so a
functional equivalent was implemented. The pipeline was written and validated
entirely on **label-permuted data** before any real-label run: across eight
independent permutations of 200 draws each, the primary endpoint returned mean ΔAUC
+0.0075 (sd 0.0317, t = +0.67), with all eight intervals covering zero. Two further
null checks confirmed the harness is unbiased rather than lucky (`results/
harness_validation.txt`).

**The ordering constraint is enforced by code, not asserted.** The real-label mode
refuses to execute unless a registration identifier is supplied, at least six
permuted runs are on record, those runs are pinned to a SHA-256 hash of the current
analysis code, and their mean ΔAUC falls within ±0.02 of zero. Editing the pipeline
re-locks it.

This procedure changed the analysis before any real label was seen: it surfaced the
calibration sign inversion (§2.4) and the invalid tail probability (§2.5). Both were
corrected in advance.

---

## 3. Results

### 3.1 The coverage gap

Against the labelled B3DB reference, **81.8–89.4% of BACE1 actives and 21.7–36.4% of
AChE actives fall outside the applicability domain** at Tanimoto 0.35, across all
ten curation variants.

Published AD coverage for BBB models, computed on internal test splits, is 93.9%,
94.8% and "complete". The contrast is the paper's starting point: coverage measured
on the training distribution is not coverage measured where the model is used.

### 3.2 BACE1 cannot be audited

Only **89** labelled B3DB compounds fall within Tanimoto 0.35 of BACE1 chemistry (60
BBB+, 29 BBB−), failing the pre-specified sufficiency criterion on both the total
and the minority class. Simulated minimum detectable ΔAUC at that size is 0.136.

BACE1 was therefore declared unmeasurable **in advance** rather than reported as a
failure afterwards. The consequence is not about our study: **BBB filters applied to
BACE1 screening hits in the published literature cannot be validated against
existing public data.** The ground truth does not exist in sufficient quantity.

### 3.3 Primary endpoint: inconclusive

| arm | n | AUC | ΔAUC vs proximal | 95% CI |
| --- | --- | --- | --- | --- |
| A proximal | 492 | 0.8352 | — | [0.7977, 0.8714]† |
| C property-matched | 492 | 0.8636 | **+0.0284** | **[−0.0164, +0.0749]** |
| B random | 492 | 0.8905 | +0.0553 | [+0.0071, +0.1005] |

† bootstrap CI on the proximal AUC itself.

**Verdict: INCONCLUSIVE.** ΔAUC is neither ≥ 0.06 with an interval excluding zero,
nor contained within ±0.03. Against a minimum detectable effect of 0.061 and a point
estimate of 0.028, this study cannot resolve an effect of the size it observes.

This must be read as **"no degradation larger than approximately 0.06 AUC"**. It is
not evidence of no degradation.

### 3.4 Half the apparent effect is physicochemical confounding

The two control arms disagree, and the registration specified in advance that arm C
governs and that the gap between arms be reported as the magnitude of the confound.

Against the **unmatched** control the gap is +0.0553 with an interval excluding
zero. Against the **property-matched** control it is +0.0284 with an interval
covering zero. **Approximately 49% of the apparent degradation is molecular-property
difference rather than domain novelty.**

Match quality confirms the mechanism:

| arm | SMD MW | SMD cLogP | SMD TPSA |
| --- | --- | --- | --- |
| B random | −0.02 | −0.35 | +0.28 |
| C property-matched | −0.07 | −0.03 | −0.04 |

Arm C passes the registered |SMD| < 0.1 criterion on all three; arm B inherits the
confound.

**This is the paper's most directly actionable result.** A study comparing
target-proximal compounds against an unmatched random holdout would report a
significant degradation, roughly half of which is molecular weight, lipophilicity
and polarity.

> **Correction to the registration.** The pre-registration describes proximal
> compounds as "larger and more lipophilic", a figure carried over from BACE1. For
> AChE this is half wrong. Measured: MW 345.3 ± 96.2 proximal versus 355.8 ± 168.7
> distal (**SMD −0.08** — not larger); cLogP 3.28 ± 1.66 versus 2.43 ± 2.14 (+0.44);
> TPSA 56.1 ± 34.6 versus 78.1 ± 63.5 (−0.43). AChE-proximal compounds are more
> lipophilic and distinctly less polar, but not larger.

### 3.5 Standard domain definitions do not agree

| definition | n | ΔAUC | 95% CI | matching |
| --- | --- | --- | --- | --- |
| A nearest-neighbour Tanimoto | 492 | +0.0284 | [−0.0164, +0.0749] | **passes** |
| B Bemis–Murcko scaffold | 547 | −0.0064 | [−0.0460, +0.0365] | fails |
| C Mahalanobis | 492 | +0.0319 | [−0.0138, +0.0746] | fails |
| D leverage | 492 | +0.0306 | [−0.0140, +0.0746] | fails |

Definitions C and D take the 492 closest compounds, holding holdout size — and
therefore the minimum detectable effect — constant, so differences reflect *which*
compounds are selected rather than how many.

**The conclusion is robust.** Every interval covers zero; no alternative definition
converts the verdict into an effect.

**The definitions are not.** Jaccard overlap with the primary definition is
**0.13–0.14**: scaffold membership recovers 26.4% of the primary proximal set,
descriptor distance 23.2%. Three methods that each claim to identify "compounds
inside the applicability domain" select largely disjoint molecules. Two papers using
different standard AD methods on the same model and dataset would be describing
different chemistry.

**Two of the three are one.** Definitions C and D select identical sets — 492 of
492, correlation 1.000 — which follows once descriptors are centred on the target
mean, since leverage and squared Mahalanobis distance then differ only by scaling
and rank identically. We report two alternative definitions, not three.

All three alternatives fail the registered |SMD| < 0.1 matching criterion, so their
ΔAUC values are reported as confounded. For C and D the failure is **structural**:
proximity is defined by distance in a descriptor space containing MW, cLogP and
TPSA, so the definition selects compounds extreme in exactly the covariates the
control must match on, and no adequately matched pool exists. Any study defining its
domain on physicochemical descriptors and then property-matching its controls faces
the same circularity.

### 3.6 Secondary hypothesis and secondary model

**H2 (effect increases with cutoff strictness) is not supported.** The pattern is
non-monotonic and the largest effect is at the *loosest* cutoff.

| cutoff | n | train | ΔAUC | 95% CI |
| --- | --- | --- | --- | --- |
| 0.30 | 1066 | 2826 | +0.0672 | [+0.0354, +0.0985] |
| 0.35 | 492 | 3400 | +0.0284 | [−0.0164, +0.0749] |
| 0.40 | 224 | 3668 | +0.0436 | [−0.0172, +0.1058] |

**We report explicitly that the 0.30 comparison would have produced a SUPPORT
verdict had 0.30 been the registered primary cutoff.** It was declined in advance,
on chemical grounds, with the reasoning recorded, before these counts existed. Three
things differ at 0.30 besides strictness: n doubles so the minimum detectable effect
falls to 0.041; the training set shrinks, weakening every arm; and Tanimoto 0.30 is a
weak similarity claim. The comparison is better powered and simultaneously measures
something less meaningful.

H2 is additionally confounded: changing the cutoff changes training-set size, so the
*trend* across cutoffs conflates domain strictness with training data volume. **H2 as
registered could not have answered its own question.**

**Secondary model.** Descriptor gradient boosting gives ΔAUC **+0.0547, 95% CI
[+0.0075, +0.1030]** — an interval excluding zero, with matching passing
(−0.07/−0.04/−0.04). By the registered rules this is nonetheless **also
inconclusive**, falling short of the 0.06 support threshold. The two models agree on
verdict and on sign and differ only on whether the interval clears zero. Two
unrelated molecular representations pointing the same way is the honest counterweight
to the primary null: the effect is probably real, probably small, and not resolvable
at this sample size.

### 3.7 No off-the-shelf tool can be evaluated without contamination

Model 3 is dropped. The registration permits this if none can be executed
reproducibly with a recorded version, requires the omission be reported, and forbids
substituting a tool chosen after seeing results.

Practically, nothing installs reproducibly: B3clf directs users to clone a
repository and build a Python 3.7 conda environment (a clone is not a recorded
version); LightBBB is a web server with no package.

Structurally — and this is dispositive — **B3clf is trained on B3DB**, which is this
study's entire labelled reference set. Every compound in the proximal holdout is
plausibly in its training data, so its predictions there would be partly recall,
biased toward making BBB filters look good. This is not one tool's quirk: B3DB was
compiled from 50 published sources, the same literature pool any public BBB model
draws on. **There is no public BBB predictor evaluable against B3DB without
contamination, and no uncontaminated public ground truth to use instead.**

### 3.8 Calibration degrades where discrimination does not

| metric | arm A proximal | arm C matched |
| --- | --- | --- |
| ROC-AUC | 0.8352 | 0.8636 |
| MCC | 0.4963 | 0.5189 |
| balanced accuracy | 0.7754 | 0.7783 |
| Brier | 0.1449 | 0.1283 |
| **ECE** | **0.0971** | **0.0601** |

Expected calibration error is ~60% worse on proximal chemistry while discrimination
barely moves. For a filter applied at a fixed probability threshold — which is how
BBB models are used in screening — miscalibration is the failure mode that bites,
and it is invisible to AUC. Secondary, no decision rule, no p-value.

### 3.9 Domain-constrained design

**[AUTHORS: on review this component is recommended for supplementary, with this
section reduced to a short main-text paragraph. Retained here in full pending that
decision.]**

Exploratory. Specified in Amendment A1 before execution, with ranking subsequently
replaced by Amendment A2 (§4.3). A fixed catalogue of ten single medicinal-chemistry
transformations was applied to the 2,391 curated AChE actives. No generative model,
and deliberately no activity prediction — predicting activity on novel chemistry
without auditing that model's own domain is the error this paper documents.

40,534 raw products → 905 surviving validity, scaffold retention, a property window,
PAINS, Ertl SA ≤ 4.0, in-domain membership and predicted BBB+ → **793 with no exact
structure match in ChEMBL or PubChem as of 2026-11-21**, spanning 177 parents and 95
scaffolds, mean Ertl SA 2.69.

Under Amendment A2 the reported set is one representative per scaffold ranked by
synthetic accessibility, capped at 20: **20 distinct parents and 20 distinct
scaffolds**, against 7 and 6 under the original rule.

**A tradeoff we report rather than hide.** Ranking by synthetic accessibility selects
simpler molecules, which are less similar to the reference set. Maximum Tanimoto
across the reported 20 is **0.351–0.483** against a 0.35 cutoff, where the original
rule returned 0.672–0.818. The reported set sits just inside the applicability
domain, several compounds within 0.01 of the boundary, and trades depth-in-domain
for chemical diversity and makeability. Readers wanting depth-in-domain should use
the alternative table, published for that purpose.

These are compounds on which a BBB prediction can be *defended*. They are not
predicted to be active, and no activity model was applied.

**They are also, mostly, minimal perturbations.** 93% of the surviving set is a
single aromatic fluorination or chlorination. Halogen scanning is real medicinal
chemistry, but it is optimisation performed iteratively against assay feedback, not
hypothesis-generating design; proposed cold it is the smallest edit that keeps a
molecule inside the predictor's domain. The honest description of this component is
that it demonstrates the constraint and shows what domain-constrained enumeration
mostly yields, rather than that it contributes drug design. Novelty is exact
full-InChIKey matching, so a stereoisomer, tautomer or salt of a known compound
reads as unmatched; close analogues exist by construction; and no literature or
patent search was performed.

---

## 4. Discussion

### 4.1 What this study does and does not establish

It does not establish that BBB predictors fail on target-proximal chemistry. The
primary endpoint is inconclusive and the honest statement is bounded: no degradation
larger than approximately 0.06 AUC. A study powered for the effect sizes reported in
comparable work — R² 0.641 versus 0.164 for in- versus out-of-domain logBB
(Pharmaceutics 2026a), AUC gaps of 0.32–0.39 (Comput Biol Chem 2026) — would have
detected those easily. We detected nothing of that magnitude, which is itself
informative about effect size in this setting.

What it establishes is a set of constraints on the question:

1. **Half of a naive domain effect is physicochemical confounding** (§3.4).
2. **BACE1 is unmeasurable with public data** (§3.2).
3. **The tools cannot be independently validated** (§3.7).
4. **"Applicability domain" is not a single concept** (§3.5).

Findings 2, 3 and 4 share a structure: the public data cannot support the validation
claims routinely made of it. The field's BBB models and the field's only public BBB
ground truth come from one literature pool; the chemistry those models are deployed
on is largely outside their domain; and the instrument used to assess that is not
one instrument but several that disagree.

### 4.2 Implications for practice

**Match your controls.** Comparing a structurally defined subset against an unmatched
random holdout overstates domain effects roughly twofold in our data.

**State your AD method and expect it to matter.** Reporting "within the applicability
domain" without naming the method is uninformative when standard methods overlap at
Jaccard 0.13. Leverage and Mahalanobis distance over the same descriptor space are
not independent checks.

**Report calibration, not only discrimination.** A filter whose AUC holds but whose
ECE degrades by 60% out of domain still misassigns compounds at the threshold.

**Treat a BBB filter on BACE1-like chemistry as unvalidated.** Not as wrong — as
unvalidated, because the public data to validate it does not exist.

### 4.3 Pre-registration caught analytic flexibility; it did not catch internal inconsistency

Registration and the permuted-label harness worked as intended. Two genuine defects
were caught before any real label was seen: Platt calibration fitting a negative
slope on signal-free data, inverting model ranking; and a tail probability that
returned 0.010 and 0.005 on data containing no signal. The code-enforced gate made
the ordering verifiable rather than asserted.

Registration did **not** prevent three internal inconsistencies in the registered
design itself, each discoverable only by execution:

1. **The A1.2 ranking rule selected against novelty.** Ranking by maximum Tanimoto
   descending maximises similarity to existing compounds, directly opposing the
   novelty filter specified in the same amendment. Its three top-ranked products were
   already in B3DB. Replaced by Amendment A2, post hoc and labelled as such, with
   output under both rules published.
2. **The novelty filter was not executable as written.** Novelty against ChEMBL and
   PubChem admits no bulk lookup, so it could never have been applied to 40,534
   products; it is feasible only on the filtered survivors.
3. **A filter forbade 40% of its own catalogue.** Scaffold retention rejects 100% of
   the four transformations that alter a ring atom — 1,551 products — before any
   chemistry is considered. We did not relax it. A labelled post hoc sensitivity
   quantifies the cost at **86 compounds** (905 → 991), because the extra products
   mostly fail the property window specified in the same amendment. **The count
   understates the cost in quality terms**: 62 of the 86 are the aromatic N-walk,
   which the chemistry review judged the single most valuable entry in the catalogue
   (lowers logP by roughly one unit, adds an acceptor, commonly reduces hERG
   liability). The filter blocked the catalogue's best transformation entirely.

Similarly, H2 conflated cutoff strictness with training-set size and could not have
answered its own question (§3.6).

These are worth reporting because pre-registration is usually discussed as a remedy
for flexible analysis. Our experience suggests a second failure mode it does not
address: a registered plan can be internally inconsistent, and specificity makes this
*more* likely, since more interacting constraints mean more opportunities for two of
them to contradict. We suggest a dry run on permuted or synthetic data as a check on
the design, not only the analysis.

### 4.4 Limitations

- **Power.** MDE 0.061 against a point estimate of 0.028. Effects of 0.01–0.03 are
  undetectable here.
- **One target.** AChE only; BACE1 failed the sufficiency criterion.
- **One labelled dataset.** B3DB is the only public set of sufficient size, which is
  also what makes the contamination problem (§3.7) unavoidable.
- **2D representations.** Morgan fingerprints and 2D descriptors; no conformational
  or 3D information, and stereochemistry is dropped at deduplication.
- **Arm B contamination.** 13.3% of each unmatched control holdout is itself
  proximal, following the registered wording. This dilutes the arm-B contrast, so the
  49% confound estimate is conservative.
- **The design component claims nothing about activity.** No activity model was
  applied and no compound was synthesised or assayed.
- **No independent medicinal-chemistry review.** The transformation catalogue and
  the curation criteria were assessed from the literature rather than by a
  practising medicinal chemist (`docs/catalogue-review.md`). The assessment rejected
  one transformation, reclassified another as a model diagnostic, and identified the
  absence of any hydrogen-bond-donor-reducing edit as the catalogue's largest gap —
  but it is reasoning from precedent, not bench judgement.
- **Structural alerts inherited from parents.** 200 of the 793 survivors, and 7 of
  the reported 20, carry a BRENK structural alert — long aliphatic chains, Michael
  acceptors, nitro groups, aldehydes. These come from the parent ChEMBL actives, not
  from the edits. They are flagged in the output rather than removed, since removing
  them would mean adding a filter after seeing the result. Notably **PAINS, which
  filter F8 applies, matches none of them**, which is a useful caution against
  treating a PAINS pass as sufficient screening hygiene.
- **Deviation.** RDKit descriptors substituted for Mordred (§2.4).

### 4.5 Conclusion

A pre-registered audit of BBB predictors on Alzheimer's target chemistry returns an
inconclusive primary result: no degradation larger than approximately 0.06 AUC. The
surrounding analyses are more consequential. Half of a naively measured domain effect
is physicochemical confounding; BACE1 chemistry cannot be audited with public data at
all; off-the-shelf BBB tools cannot be evaluated without contamination because they
are trained on the only available ground truth; and standard applicability-domain
methods select largely disjoint compound sets while two common ones are the same
statistic. The routine practice of filtering Alzheimer's screening hits through an
off-the-shelf BBB model rests on validation that the public data cannot currently
supply.

---

## Data and code availability

All code, the full pre-registration with amendments, the dated decision log, the
systematic literature search record and every result file are at
<https://github.com/shreyansk6-stack/bbb-domain-alzheimers>, registered against
commit `134ab60`.

`data/` is not redistributed: ChEMBL is CC BY-SA 3.0 and share-alike would propagate
to the repository. `docs/data-manifest.sha256` pins the exact registered snapshot.
B3DB is CC0 and available from the authors' repository.

## Registration

OSF Registries, 2026-11-19, [10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62).
Foreknowledge declared as "authors have observed the data, but have not performed the
proposed analyses". Amendments A1 (2026-11-19) and A2 (2026-11-21) are in
`docs/preregistration.md`; A2 is post hoc and labelled wherever reported.

## Author contributions

**[AUTHORS: confirm.]** S.K. conceived the study, wrote the pre-registration,
implemented the analysis and drafted the manuscript. S.S. contributed medicinal-
chemistry judgement on curation criteria and the transformation catalogue, and
critical revision.

## AI use disclosure

Claude Code (Anthropic) was used for exploratory and sensitivity analyses, the
systematic literature search, drafting the pre-registration and this manuscript, the
analysis code, and proposing ChEMBL curation decisions together with the published
basis for each. All numerical results are produced by scripts in the repository and
are reproducible from the recorded data versions. No AI system is an author; the
authors are responsible for all decisions.

## References

**[AUTHORS: format to target journal.]**

1. Meng F, et al. A curated diverse molecular database of blood-brain barrier
   permeability with chemical descriptors. *Sci Data* 2021. doi:10.1038/s41597-021-01069-5
2. Pharmaceutics 2026a. doi:10.3390/pharmaceutics18060670
3. Pharmaceutics 2026b. doi:10.3390/pharmaceutics18081018
4. Comput Biol Chem 2026. doi:10.1016/j.compbiolchem.2026.109356
5. Kalliokoski T, et al. Comparability of mixed IC50 data. *PLoS One* 2013.
   doi:10.1371/journal.pone.0061007
6. Landrum GA, Riniker S. Combining IC50 or Ki values from different sources.
   *J Chem Inf Model* 2024. doi:10.1021/acs.jcim.4c00049
7. Jia & Sosso. *Mol Syst Des Eng* 2026. doi:10.1039/d6me00041j
8. Ertl P, Schuffenhauer A. Estimation of synthetic accessibility score. *J Cheminform* 2009.
9. Bemis GW, Murcko MA. The properties of known drugs. 1. Molecular frameworks.
   *J Med Chem* 1996.
10. Hanley JA, McNeil BJ. The meaning and use of the area under a ROC curve.
    *Radiology* 1982.
11. OECD. Guidance Document on the Validation of (Q)SAR Models. 2007.
12. ChEMBL_37, released 2026-05-01.
