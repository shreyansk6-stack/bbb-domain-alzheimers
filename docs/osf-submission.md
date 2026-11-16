# OSF registration: paste-ready answers

For the **OSF Preregistration** template at
[osf.io/registries](https://www.cos.io/registries). Field names vary slightly
between template versions — match by meaning, and check the live form.

Content is drawn from `docs/preregistration.md` v1.1. **If that document changes,
this one is stale.** Register the version in git at the time of submission and note
the commit hash in the "Other" field.

---

## Read this before you submit

**The "Existing data" question has three options and the correct answer is the
third one: "Registration following analysis of the data."**

That will feel like the wrong answer. It is the right one. The option covers
"preliminary analysis of variables, calculation of descriptive statistics, and
observation of data distributions" — which is exactly what the scoping and
sensitivity analyses did. Choosing "before analysis" would be a misrepresentation,
and it is the kind that is trivially caught, because the repository's git history is
public and timestamped.

The template provides an "Explanation of existing data" field for precisely this
situation. Used properly it is a strength: it says the exploratory work is disclosed,
bounded, and separated from the confirmatory test. Text for it is below.

---

## Study Information

**Title**

> Applicability domain of blood–brain barrier predictors in Alzheimer's target
> chemical space: a methods audit

**Description**

> Alzheimer's virtual-screening pipelines commonly rank compounds for activity
> against a target such as BACE1 or acetylcholinesterase, then pass the hits through
> an off-the-shelf blood–brain barrier (BBB) permeability predictor to judge whether
> they can reach the brain. Those predictors are trained on literature-derived data
> that skews toward approved and CNS-active drugs, while target inhibitor series are
> narrow, heavily optimised medicinal chemistry.
>
> Published BBB models report applicability-domain coverage on their own held-out
> test sets, and therefore report high coverage — 93.9%, 94.8% and "complete
> coverage" in three separate 2026 papers. Because a held-out split is drawn from the
> training distribution, that figure is near-guaranteed by construction and carries
> no information about deployment.
>
> This study measures domain coverage against the chemistry these filters are
> actually applied to, and measures directly whether BBB prediction error increases
> on target-proximal compounds. A systematic Europe PMC search (2026-11-16) found the
> specific question unclaimed.

**Hypotheses**

> H1 (confirmatory, primary). A BBB permeability classifier trained on B3DB performs
> measurably worse on compounds structurally proximal to acetylcholinesterase
> inhibitor chemistry than on compounds matched for molecular weight, cLogP, TPSA,
> sample size and class balance. Operationalised as ΔROC-AUC ≥ 0.06 with a confidence
> interval excluding zero.
>
> H2 (confirmatory, secondary). The degradation in H1 is larger at stricter
> definitions of proximity (Tanimoto 0.4) than at looser ones (0.3).
>
> H3 (stated in advance, not a statistical test). For BACE1 chemical space there is
> insufficient public BBB ground truth to measure prediction error at all. Only 89
> labelled B3DB compounds fall within Tanimoto 0.35 of BACE1 chemistry (60 BBB+, 29
> BBB−), failing a pre-specified sufficiency criterion of ≥200 compounds with ≥50 per
> class. The consequence is that BBB filters applied to BACE1 screening hits in the
> published literature cannot be validated with existing public data.
>
> A null result on H1 is a meaningful outcome and is pre-specified as such: it would
> indicate that nearest-neighbour domain distance does not predict BBB prediction
> error in this setting, corroborating a prior null finding
> (10.1016/j.compbiolchem.2026.109356).

## Design Plan

**Study type**

> Observational / computational. Secondary analysis of existing public databases. No
> human or animal subjects. No laboratory work.

**Blinding**

> No blinding of participants, since there are none. Analyst blinding is not
> applicable in the usual sense; the functional equivalent is implemented as follows.
> The confirmatory analysis code will be written and validated on label-permuted data
> before being run once on the real labels, so that the pipeline is fixed before any
> real outcome is observable.

**Study design**

> Three-arm holdout comparison on a single labelled dataset (B3DB, 3,892 curated
> compounds with BBB+/BBB− labels).
>
> Arm 1, proximal holdout: every labelled B3DB compound within Tanimoto 0.35 of
> acetylcholinesterase inhibitor chemistry is removed from training (n = 492; 366
> BBB+, 126 BBB−); the model is trained on the remainder and evaluated on the
> held-out proximal set.
>
> Arm 2, size- and class-matched random holdout: an equally sized holdout with
> identical class balance is drawn at random, over 200 independent draws, to build a
> null distribution rather than a single comparison.
>
> Arm 3, property-matched random holdout: as arm 2, but drawn by propensity matching
> on molecular weight, cLogP and TPSA.
>
> Arm 3 is the control that governs the primary conclusion. Arms 1 and 2 share a
> confound: target-proximal compounds are larger and more lipophilic than the B3DB
> average (BACE1 mean MW 472 versus 318 for BBB+ compounds), so a performance drop
> could reflect molecular complexity rather than domain novelty. If arms 2 and 3
> disagree, arm 3 governs and the gap between them is reported as the magnitude of
> the property confound.
>
> Training-set size is identical across all three arms by construction, so no arm is
> advantaged by having more training data.

**Randomization**

> Random holdout draws in arms 2 and 3 use a fixed seed recorded in the analysis
> code. 200 draws per arm.

## Sampling Plan

**Existing data**

> Registration following analysis of the data.

**Explanation of existing data**

> The datasets are public and pre-existing (B3DB, ChEMBL), and exploratory analysis
> of them has already been performed and is fully disclosed. Specifically: chemical
> space overlap between target inhibitor sets and B3DB, physicochemical property
> comparisons, assay metadata distributions, curation sensitivity analyses, and a
> power simulation. Those results are public at the project repository with
> timestamped git history and will be labelled exploratory in any manuscript. No
> p-value will be attached to them.
>
> What has NOT been done, and is what this registration covers: no BBB model has
> been trained, no prediction error has been measured, and no comparison between
> proximal and matched holdouts has been computed. The confirmatory analysis in the
> Analysis Plan has not been run in any form.
>
> The exploratory work motivated the study and determined its feasibility. It
> established that the usable AChE-proximal sample is 492 compounds and that the
> BACE1-proximal sample is too small to analyse, which is why the sufficiency
> criterion and the power floor are stated here in advance rather than discovered
> later.

**Data collection procedures**

> B3DB classification dataset fetched from its GitHub repository on 2026-11-14
> (CC0 1.0). ChEMBL_37 (released 2026-05-01, CC BY-SA 3.0) queried via its REST API
> for human BACE1 (CHEMBL4822) and human acetylcholinesterase (CHEMBL220).
>
> Activity definition, fixed in advance: IC50 or Ki (Kd excluded), standard_relation
> "=", no data_validity_comment, units nM, assay type B, assay confidence score 9
> (direct single-protein target assignment), replicate measurements aggregated by
> median pChEMBL, threshold pChEMBL ≥ 6. Resulting sets: 5,157 BACE1 actives, 2,391
> AChE actives.
>
> The confidence-score filter is the substantive one: score-9 assays for these
> targets are 100% Homo sapiens, while score-8 assays have assay organism
> unspecified or non-human, which matters particularly for acetylcholinesterase
> where non-human enzyme assays are common in the literature.
>
> All compound structures are deduplicated on the first block of the InChIKey
> (connectivity only, dropping stereochemical and protonation layers), because
> deduplication on canonical SMILES finds zero duplicates in B3DB while the 2D
> fingerprints used here cannot distinguish the stereoisomers it preserves. B3DB
> reduces from 7,805 records to 4,022 skeletons, of which 130 carry contradictory
> BBB+/BBB− labels and are excluded from the labelled set while being retained for
> structural domain geometry. Labelled reference set: 3,892 compounds (2,472 BBB+,
> 1,420 BBB−).
>
> No data will be refetched after the registration date without a dated amendment.

**Sample size**

> Primary analysis: 492 compounds in the proximal holdout (366 BBB+, 126 BBB−),
> against 200 matched random holdouts of the same size and class balance. Training
> partition: 3,400 compounds in every arm.

**Sample size rationale**

> The sample is fixed by the data, not chosen; it is every labelled B3DB compound
> within Tanimoto 0.35 of AChE chemistry. Power was therefore computed for the
> available sample rather than used to set it.
>
> Simulation (binormal, 4,000 replicates, rank-based AUC; code in the repository) at
> 366 versus 126 gives a standard error on AUC of 0.016 at a true AUC of 0.90, and a
> minimum detectable ΔAUC of approximately 0.061 at 80% power and two-sided
> alpha = 0.05.
>
> This study is therefore not powered to detect a small effect. If the true
> degradation is 0.01–0.03 AUC it will not be detected, and a null must be reported
> as "no degradation larger than approximately 0.06 AUC" rather than as evidence of
> no degradation. For comparison, the effects this design targets are far larger:
> a reported in- versus out-of-domain gap of R² 0.641 against 0.164 on a B3DB logBB
> model (10.3390/pharmaceutics18060670), and AUC gaps of 0.32–0.39 in a comparable
> QSAR generalisation study (10.1016/j.compbiolchem.2026.109356).
>
> The 0.3 cutoff would yield 1,066 compounds and a minimum detectable ΔAUC of 0.041.
> It is deliberately not adopted as primary: Tanimoto 0.3 on Morgan fingerprints is
> a weak claim of chemical similarity, and buying statistical power by loosening the
> definition of "in domain" would undercut the study's own argument. The 0.35 cutoff
> was fixed before these class counts were known.

**Stopping rule**

> Not applicable; the dataset is fixed and fully available at registration. No
> sequential or interim analysis, and no data-dependent stopping.

## Variables

**Manipulated variables**

> Holdout composition, which is the single manipulated factor, at three levels:
> target-proximal, size- and class-matched random, and property-matched random.

**Measured variables**

> Primary outcome: ROC-AUC of the BBB permeability classifier on the holdout, and
> its difference between arms (ΔROC-AUC).
>
> Secondary outcomes: Matthews correlation coefficient; balanced accuracy; and
> calibration, as Brier score and expected calibration error. Calibration is included
> because a filter that is merely miscalibrated out of domain still misranks
> compounds even when its discrimination holds, which is the practically relevant
> failure mode for a screening cutoff.
>
> Domain membership is defined by maximum Tanimoto similarity to the training set
> using Morgan fingerprints, radius 2, 2048 bits. Pre-specified sensitivity analyses
> use leverage (Williams plot, OECD guidance), Mahalanobis distance on the descriptor
> set, and Bemis–Murcko scaffold membership. These are reported whatever they show;
> if they disagree with the primary definition, the disagreement is the result.

**Indices**

> Out-of-domain fraction: the proportion of a compound set whose nearest training-set
> neighbour falls below a given Tanimoto cutoff. Reported across the full cutoff
> sweep 0.3 to 0.8, because out-of-domain fractions are known to be
> threshold-sensitive and reporting a single cutoff would be selective.

## Analysis Plan

**Statistical models**

> Three BBB classifiers, fixed in advance. None is novel; the object of study is what
> the field already uses.
>
> 1. ECFP4 random forest — the common fingerprint baseline. Primary model.
> 2. Gradient boosting on curated 2D Mordred descriptors — the common descriptor
>    baseline.
> 3. An off-the-shelf published BBB prediction tool, run as distributed, if one can be
>    executed reproducibly with a recorded version. If none can, this arm is dropped
>    and the omission reported; it will not be replaced with a substitute chosen after
>    seeing results.
>
> Hyperparameters are tuned by cross-validation within the training partition only.
> Classification thresholds and probability calibration are derived from validation
> folds only, never from the evaluation set.
>
> Primary endpoint: ΔROC-AUC between the proximal holdout and the property-matched
> random holdout, for the ECFP4 random forest. Confidence intervals by bootstrap on
> the holdout and across the 200 control draws.

**Transformations**

> Structures standardised and deduplicated as described under data collection
> procedures. Potency values are used only to determine set membership via the
> pChEMBL threshold; no potency value enters any model, endpoint or reported result.
> This is why the known disagreement over pooling IC50 with Ki
> (10.1371/journal.pone.0061007 against 10.1021/acs.jcim.4c00049) does not govern
> this study, and it is tested rather than asserted: across ten curation variants the
> out-of-domain fraction spans 81.8–89.4% for BACE1 and 21.7–36.4% for AChE, leaving
> at least a 45-percentage-point contrast in every case.

**Inference criteria**

> Primary endpoint ΔROC-AUC, two-sided alpha = 0.05.
>
> Support for H1: ΔAUC ≥ 0.06 against the property-matched control with a confidence
> interval excluding zero.
>
> Refutation: a ΔAUC confidence interval contained within ±0.03, reported as a null
> result in those words.
>
> Inconclusive: anything between the two, reported as inconclusive and not resolved
> by adding metrics, cutoffs, models or targets until something clears.
>
> Multiplicity: one primary endpoint, on one model, against one control. The other two
> models, the other two control arms, the secondary metrics and the cutoff sweep are
> all secondary and reported without inferential claims of primacy.
>
> No outcome licenses a search for a different endpoint, cutoff or target that gives a
> better number. Any analysis run after seeing results will be labelled post hoc.

**Data exclusion**

> Compounds whose structures cannot be parsed by RDKit are excluded and counted.
> B3DB skeletons carrying contradictory BBB+/BBB− labels (130) are excluded from the
> labelled set as unusable ground truth, while being retained for structural domain
> geometry where only connectivity matters. ChEMBL records are excluded by the fixed
> activity definition above. Compounds are NOT excluded for wide replicate spread;
> the spread is reported as a data-quality statistic, since a compound measured
> inconsistently is still a compound that was synthesised against the target, which
> is all that is required of it here.

**Missing data**

> Compounds with missing SMILES or missing pChEMBL values are excluded at the
> filtering stage and counted. No imputation is performed anywhere.

**Exploratory analyses**

> All chemical-space overlap figures, physicochemical comparisons, scaffold overlap
> counts, assay metadata distributions and curation sensitivity analyses already
> computed are exploratory and will be labelled as such.
>
> A second, explicitly exploratory and hypothesis-generating component will produce a
> shortlist of acetylcholinesterase-directed candidate compounds prioritised using
> only in-domain BBB predictions, with synthetic accessibility assessed. No claim of
> activity, brain penetration or therapeutic potential will be made; compounds will be
> described as prioritised for evaluation, never as hits or leads. Causal and efficacy
> language is excluded. No laboratory work is proposed or required.

## Other

**Other**

> Full pre-registration, analysis code, decision log and literature search record:
> https://github.com/shreyansk6-stack/bbb-domain-alzheimers
>
> Registered against commit [run `git rev-parse HEAD` at submission and paste it].
>
> AI use disclosure: Claude Code (Anthropic) was used for the exploratory and
> sensitivity analyses, the systematic literature search, drafting this
> pre-registration, the analysis code, and proposing the ChEMBL curation decisions
> together with the published basis for each. All numerical results are produced by
> scripts in the repository and are reproducible from the recorded data versions. No
> AI system is an author; the authors are responsible for all decisions.
>
> Deviations from this registration will be recorded in the repository's decision log
> with date and reason, and stated in the manuscript, distinguishing those decided
> before from those decided after seeing affected results.
