# OSF registration — as submitted

**Registered 2026-11-19, 11:24:29 PM** on OSF Registries. Schema: **OSF
Preregistration**. Public, not embargoed. Status: Accepted. Registered against commit
`134ab6065bb6cbc79000944e52837932f7fe7219`.

**DOI:** [`10.17605/OSF.IO/UQR62`](https://doi.org/10.17605/OSF.IO/UQR62) — registration at <https://osf.io/uqr62>

This file was previously a set of paste-ready answers for an older version of the OSF
Preregistration template. It is now a **verbatim record of what was registered**, so
the repository and the registration cannot drift apart. The authoritative plan remains
`docs/preregistration.md`; this is the form transcript.

## The schema changed between drafting and submission

The old **"Existing data"** question offered three options, of which "Registration
following analysis of the data" was the least inaccurate. The live schema replaces it
with an eight-level **"Foreknowledge of data or evidence"** scale, and one level
describes this study exactly:

> **Authors have observed the data, but have not performed the proposed analyses.**

Precisely true: the scoping, assay-metadata and sensitivity work observed the data
enough to influence analysis decisions, and none of the confirmatory analyses had been
run. The final option — "Analyses in this plan have been conducted already" — denotes
retrospective registration and does not apply.

The live schema also asks directly for **controls, manipulation checks and assumption
tests**. That put three things into the registered record which
`docs/preregistration.md` does not state in those terms, all under *Statistical models*
below, and all of which belong in the manuscript's methods:

- the label-permuted run as a **negative control**, declared a pre-registered
  precondition rather than a post hoc check;
- the property-matching **manipulation check**, with an explicit failure rule —
  |SMD| < 0.1 on MW, cLogP and TPSA, or the comparison is reported as confounded;
- **assumption handling** — rank-based endpoint, class-stratified bootstrap, and
  propensity-model non-convergence treated as matching failure.

Two further differences. The registered **title** is broader than the working title, to
cover the Amendment A1 design component. And **Study type** has no "methods audit"
option; *Simulation study* was selected, its definition being "using existing or
synthetic data to assess performance of a model… demonstration of methods".

---

# Metadata

**Title**

> Applicability domain of blood–brain barrier predictors in Alzheimer's target chemical
> space: a methods audit and domain-constrained design

**Contributors.** Shreyan Kancharla (sole author). The second contributor named
at registration was removed on 2026-11-25; he made no contribution to the work.

**Licence.** CC-By Attribution 4.0 International.

**Subjects.** Neuroscience and Neurobiology; Medicinal and Pharmaceutical Chemistry;
Life Sciences; Medicine and Health Sciences; Pharmacy and Pharmaceutical Sciences;
Computational Neuroscience; Bioinformatics.

**Tags.** acetylcholinesterase, Alzheimer's disease, applicability domain, B3DB, BACE1,
blood-brain barrier, ChEMBL, cheminformatics, QSAR, virtual screening.

**Description**

> Alzheimer's virtual-screening pipelines commonly rank compounds for activity against a
> target such as BACE1 or acetylcholinesterase, then pass the hits through an
> off-the-shelf blood–brain barrier (BBB) permeability predictor to judge whether they
> can reach the brain. Those predictors are trained on literature-derived data that skews
> toward approved and CNS-active drugs, while target inhibitor series are narrow, heavily
> optimised medicinal chemistry. Published BBB models report applicability-domain
> coverage on their own held-out test sets, and therefore report high coverage — 93.9%,
> 94.8% and "complete coverage" in three separate 2026 papers. Because a held-out split
> is drawn from the training distribution, that figure is near-guaranteed by construction
> and carries no information about deployment. This study measures domain coverage
> against the chemistry these filters are actually applied to, and measures directly
> whether BBB prediction error increases on target-proximal compounds. A systematic
> Europe PMC search (2026-11-16) found the specific question unclaimed. The confirmatory
> analysis is the audit. Two further components are explicitly exploratory and
> hypothesis-generating, and demonstrate the audit's constructive use: a shortlist
> selected from acetylcholinesterase inhibitors of measured activity, retaining only
> those on which a BBB prediction can be defended; and a set of novel structures produced
> by enumerating fixed medicinal-chemistry transformations under the constraint that the
> product remain inside the predictor's applicability domain. Neither component claims
> activity, brain penetration or therapeutic potential, and no laboratory work is
> proposed or required.

**Attachments.** None. One file (`docs/curation-decisions.md`) was uploaded during
drafting and removed before submission, after a failed upload left a dangling reference
that blocked registration. Nothing is lost: every file is in the public repository at
the registered commit, which the *Other* field points to. If archiving independent of
GitHub is wanted later, files can be added to the OSF **project** the registration
created — permanent, though outside the immutable snapshot.

---

# Overview

**Research questions or hypotheses**

> H1 (confirmatory, primary). A BBB permeability classifier trained on B3DB performs
> measurably worse on compounds structurally proximal to acetylcholinesterase inhibitor
> chemistry than on compounds matched for molecular weight, cLogP, TPSA, sample size and
> class balance. Operationalised as ΔROC-AUC ≥ 0.06 with a confidence interval excluding
> zero.
>
> H2 (confirmatory, secondary). The degradation in H1 is larger at stricter definitions
> of proximity (Tanimoto 0.4) than at looser ones (0.3).
>
> H3 (stated in advance, not a statistical test). For BACE1 chemical space there is
> insufficient public BBB ground truth to measure prediction error at all. Only 89
> labelled B3DB compounds fall within Tanimoto 0.35 of BACE1 chemistry (60 BBB+, 29
> BBB−), failing a pre-specified sufficiency criterion of ≥200 compounds with ≥50 per
> class. The consequence is that BBB filters applied to BACE1 screening hits in the
> published literature cannot be validated with existing public data.
>
> A null result on H1 is a meaningful outcome and is pre-specified as such: it would
> indicate that nearest-neighbour domain distance does not predict BBB prediction error
> in this setting, corroborating a prior null finding
> (10.1016/j.compbiolchem.2026.109356).

**Foreknowledge of data or evidence** — selected:

> Authors have observed the data, but have not performed the proposed analyses.

**Explanation of foreknowledge and managing unintended influences**

> The datasets are public and pre-existing (B3DB, ChEMBL). Exploratory analysis of them
> has already been performed and is fully disclosed: chemical space overlap between
> target inhibitor sets and B3DB, physicochemical property comparisons, assay metadata
> distributions, curation sensitivity analyses, and a power simulation. Those results are
> public in the project repository with timestamped git history and will be labelled
> exploratory in any manuscript. No p-value will be attached to them.
>
> What has NOT been done, and is what this registration covers: no BBB model has been
> trained on the real labels, no prediction error has been measured, and no comparison
> between proximal and matched holdouts has been computed.
>
> Actions taken to reduce the risk of unintended influence:
>
> 1. Analyst blinding is not possible in a computational study with one analyst, so a
> functional equivalent was implemented. The confirmatory pipeline was written and
> validated entirely on label-permuted data before any real-label run. Across eight
> independent permutations of 200 draws each, the primary endpoint returned a mean ΔAUC
> of +0.0075 (sd 0.0317, t = +0.67), with all eight confidence intervals covering zero.
>
> 2. The real-label mode of the analysis script refuses to execute unless a registration
> identifier is supplied, at least six label-permuted runs are on record, those runs are
> pinned to a SHA-256 hash of the current analysis code, and their mean ΔAUC falls within
> ±0.02 of zero. Editing the pipeline re-locks it. The ordering constraint is therefore
> enforced by the code, not asserted.
>
> 3. The pre-specified decision rules are evaluated by the frozen script and printed as a
> verdict, so the reported conclusion cannot be selected after the effect size is known.
>
> 4. The permuted validation changed the analysis before any real labels were seen: it
> revealed that Platt calibration can fit a negative slope when there is no signal,
> inverting the model ranking, and that a tail probability computed against the control
> draw distribution ignores the proximal arm's dominant sampling error. Both were
> corrected in advance and are recorded in the repository decision log.
>
> 5. The primary similarity cutoff (Tanimoto 0.35) was fixed before the resulting class
> counts were known. A looser cutoff of 0.3 would yield better statistical power and was
> explicitly declined, with the reasoning recorded, because loosening the definition of
> "in domain" would undercut the study's own argument.

---

# Research Design

**Study type.** Simulation study.

**Intention for causal interpretation.** Indirect inference on causal relationship(s).

**Blinding of experimental treatments.** "Subjects will not be aware of the assigned
treatment during data collection (either because the subjects are not human participants
or because of blinding procedures)" — true by construction; the subjects are molecules.
The option asserting that coders are unaware of assigned treatments was **not** selected,
because arm assignments are known to the analyst.

**Additional blinding during research or analysis**

> Analyst blinding in the conventional sense is not available: there is one analyst, the
> data are public, and the arm assignments are structural rather than hidden. A
> functional equivalent was implemented instead.
>
> The confirmatory pipeline was written and validated entirely on label-permuted data
> before any real-label run. Across eight independent permutations of 200 control draws
> each, the primary endpoint returned a mean ΔAUC of +0.0075 (sd 0.0317, t = +0.67), with
> all eight confidence intervals covering zero.
>
> The real-label mode of the analysis script refuses to execute unless a registration
> identifier is supplied, at least six label-permuted runs are on record, those runs are
> pinned to a SHA-256 hash of the current analysis code, and their mean ΔAUC falls within
> ±0.02 of zero. Editing the pipeline re-locks the gate. The ordering constraint is
> enforced by the code rather than asserted in prose.
>
> The pre-specified decision rules are evaluated by the frozen script and printed as a
> verdict, so the reported conclusion cannot be selected after the effect size is known.
>
> This procedure changed the analysis before any real labels were observed. It revealed
> that Platt calibration can fit a negative slope when there is no signal to calibrate,
> inverting the model's ranking and reflecting AUC about 0.5; and that a tail probability
> computed against the control draw distribution ignores the proximal arm's dominant
> sampling error, manufacturing apparent significance from noise. Both were corrected in
> advance and are recorded in the repository decision log.

**Study design**

> Three-arm holdout comparison on a single labelled dataset (B3DB, 3,892 curated
> compounds with BBB+/BBB− labels, deduplicated to InChIKey skeletons).
>
> Arm 1, proximal holdout: every labelled B3DB compound within Tanimoto 0.35 of
> acetylcholinesterase inhibitor chemistry is removed from training (n = 492; 366 BBB+,
> 126 BBB−); the model is trained on the remainder and evaluated on the held-out proximal
> set.
>
> Arm 2, size- and class-matched random holdout: an equally sized holdout with identical
> class balance is drawn at random, over 200 independent draws, to build a null
> distribution rather than a single comparison.
>
> Arm 3, property-matched random holdout: as arm 2, but drawn by propensity matching on
> molecular weight, cLogP and TPSA, also over 200 draws.
>
> Arm 3 is the control that governs the primary conclusion. Arms 1 and 2 share a
> confound: target-proximal compounds are larger and more lipophilic than the B3DB
> average, so a performance drop could reflect molecular complexity rather than domain
> novelty. Measured standardised mean differences between the proximal set and arm 2 are
> approximately −0.39 for cLogP and +0.38 for TPSA; arm 3 reduces all three property
> differences to within ±0.05. If arms 2 and 3 disagree, arm 3 governs and the gap between
> them is reported as the magnitude of the property confound.
>
> Training-set size is identical across all three arms by construction, so no arm is
> advantaged by having more training data.
>
> The design is unpaired between arms: each arm evaluates a different set of compounds.
> The proximal arm has a single fixed evaluation set, which is the dominant source of
> variance in the primary endpoint and the reason the minimum detectable effect is
> approximately 0.061 ΔAUC rather than something smaller.

**Randomization**

> Random holdout draws in arms 2 and 3 use a fixed seed (42) recorded in the analysis
> code, with 200 independent draws per arm.
>
> Arm 2: simple random sampling without replacement, stratified by class to match the
> proximal set's BBB+/BBB− counts exactly.
>
> Arm 3: propensity-score matching. A logistic regression on standardised molecular
> weight, cLogP and TPSA estimates each compound's probability of being proximal. For each
> proximal compound, one match is drawn uniformly from its five nearest unmatched
> same-class neighbours in propensity score, sampling without replacement. Drawing from
> the five nearest rather than taking the single nearest is what makes repeated draws a
> distribution rather than one deterministic set.
>
> Arm 3 draws from the distal pool only. Arm 2 draws from the whole labelled set,
> following the literal pre-registered wording, so approximately 12.6% of each arm-2
> holdout is itself proximal; this dilutes the contrast and is the conservative reading.
> The realised share is reported for every run.

---

# Sampling

**Data collection procedures**

> B3DB classification dataset fetched from its GitHub repository on 2026-11-14 (CC0 1.0).
> ChEMBL_37 (released 2026-05-01, CC BY-SA 3.0) queried via its REST API for human BACE1
> (CHEMBL4822) and human acetylcholinesterase (CHEMBL220). Both are public, pre-existing
> databases; no new data are generated.
>
> Inclusion criteria for target activity, fixed in advance: IC50 or Ki (Kd excluded),
> standard_relation "=", no data_validity_comment, units nM, assay type B (binding), assay
> confidence score 9 (direct single-protein target assignment), replicate measurements
> aggregated by median pChEMBL, activity threshold pChEMBL ≥ 6. Resulting sets: 5,157
> BACE1 actives, 2,391 AChE actives.
>
> The confidence-score filter is the substantive one: score-9 assays for these targets are
> 100% Homo sapiens, while score-8 assays have assay organism unspecified or non-human,
> which matters particularly for acetylcholinesterase where Electrophorus and Torpedo
> enzyme assays are common in the literature and have different inhibitor
> structure-activity relationships from the human protein. Four further filters
> (standard_relation, data_validity_comment, units, organism) are asserted in code but
> verified to be no-ops in ChEMBL_37 for these targets, and are recorded as such so they
> are not mistaken for the filters that did the work.
>
> All compound structures are deduplicated on the first block of the InChIKey
> (connectivity only, dropping stereochemical and protonation layers), because
> deduplication on canonical SMILES finds zero duplicates in B3DB while the 2D Morgan
> fingerprints used here cannot distinguish the stereoisomers it preserves. B3DB reduces
> from 7,805 records to 4,022 skeletons, of which 130 carry contradictory BBB+/BBB−
> labels; these are excluded from the labelled set and retained only for structural domain
> geometry. Labelled reference set: 3,892 compounds (2,472 BBB+, 1,420 BBB−).
>
> Every contested curation choice is reported as a variant in a sensitivity analysis
> already in the repository. Across all ten variants the headline out-of-domain fraction
> ranges 81.8–89.4% for BACE1 and 21.7–36.4% for AChE, so no curation decision is
> load-bearing for the study's conclusion.
>
> No data will be refetched after the registration date without a dated amendment. ChEMBL
> is a live API and its contents change.

**Sample size**

> Unit of analysis: the compound.
>
> Primary analysis: 492 compounds in the proximal holdout (366 BBB+, 126 BBB−), compared
> against 200 independent matched random holdouts of identical size and class balance, and
> 200 independent property-matched holdouts of identical size and class balance.
>
> Training partition: 3,400 compounds in every arm, identical by construction.
>
> Labelled reference set from which all arms are drawn: 3,892 compounds (2,472 BBB+, 1,420
> BBB−).
>
> BACE1 is not analysed. Only 89 labelled compounds fall within Tanimoto 0.35 of BACE1
> chemistry (60 BBB+, 29 BBB−), which fails the pre-specified sufficiency criterion on
> both the total and the minority class.

**Sample size rationale**

> The sample is fixed by the data rather than chosen: it is every labelled B3DB compound
> within Tanimoto 0.35 of AChE chemistry. Power was therefore computed for the available
> sample rather than used to set it.
>
> Simulation (binormal, 4,000 replicates, rank-based AUC; code in the repository) at 366
> versus 126 gives a standard error on AUC of 0.016 at a true AUC of 0.90, and a minimum
> detectable ΔAUC of approximately 0.061 at 80% power and two-sided alpha = 0.05. This
> figure was independently reproduced by a second route: across eight label permutations
> the proximal arm's AUC varied with a standard deviation of approximately 0.027, which is
> the irreducible spread of a single fixed evaluation set of this size.
>
> This study is therefore not powered to detect a small effect. If the true degradation is
> 0.01–0.03 AUC it will not be detected, and a null must be reported as "no degradation
> larger than approximately 0.06 AUC" rather than as evidence of no degradation. For
> comparison, the effects this design targets are far larger: a reported in- versus
> out-of-domain gap of R² 0.641 against 0.164 on a B3DB logBB model
> (10.3390/pharmaceutics18060670), and AUC gaps of 0.32–0.39 in a comparable QSAR
> generalisation study (10.1016/j.compbiolchem.2026.109356).
>
> A pre-specified sufficiency criterion of ≥200 compounds with ≥50 in each class
> determines whether a target is analysable at all. AChE passes (492; 366/126). BACE1
> fails on both counts (89; 60/29), with a simulated minimum detectable ΔAUC of
> approximately 0.136 at that size, and is declared unmeasurable in advance rather than
> reported as a failure afterwards.
>
> The 0.3 cutoff would yield 1,066 compounds and a minimum detectable ΔAUC of 0.041. It is
> deliberately not adopted as primary: Tanimoto 0.3 on Morgan fingerprints is a weak claim
> of chemical similarity, and buying statistical power by loosening the definition of "in
> domain" would undercut the study's own argument. The 0.35 cutoff was fixed before these
> class counts were known.

**Starting and stopping rules**

> Not applicable in the conventional sense: the dataset is fixed, public and fully
> available at registration. There is no recruitment, no sequential analysis, no interim
> look, and no data-dependent stopping.
>
> Pilot testing is separable from the study by construction. All pipeline development and
> validation was performed on label-permuted data, which contains no signal by design;
> those runs are not pilot results and no quantity from them enters the study's
> conclusions. Data collection in the ordinary sense ended on 2026-11-16, the date of the
> last ChEMBL query, and no refetch will occur without a dated amendment.
>
> The confirmatory analysis is a single run on the real labels. Repeated runs, additional
> cutoffs, additional models or additional targets executed after that run are post hoc by
> definition and will be labelled as such.

---

# Variables

**Manipulated variables**

> Holdout composition is the single manipulated factor, at three levels:
>
> 1. Target-proximal: every labelled compound within Tanimoto 0.35 of AChE inhibitor
> chemistry (n = 492; 366 BBB+, 126 BBB−). Not randomised — membership is determined by
> chemical structure.
>
> 2. Size- and class-matched random: an equally sized holdout with identical class
> balance, drawn at random over 200 independent draws.
>
> 3. Property-matched random: as level 2, but drawn by propensity matching on molecular
> weight, cLogP and TPSA, over 200 independent draws.
>
> Training-set size is held constant at 3,400 compounds across all three levels by
> construction. Level 3 is the comparator that governs the primary conclusion.

**Measured variables**

> Primary outcome: ROC-AUC of the BBB permeability classifier on the holdout, and its
> difference between arms (ΔROC-AUC, defined as control minus proximal, so that positive
> values indicate worse performance on target-proximal chemistry).
>
> ROC-AUC is computed on the uncalibrated random-forest score rather than the calibrated
> probability. Platt scaling is monotonic in expectation but can fit a negative slope when
> there is no signal to calibrate, which inverts the ranking and reflects AUC about 0.5;
> this was observed during label-permuted validation. Calibration therefore informs the
> secondary endpoints and the decision threshold but does not touch the primary endpoint.
>
> Secondary outcomes: Matthews correlation coefficient; balanced accuracy; and
> calibration, as Brier score and expected calibration error (10 equal-width bins).
> Calibration is included because a filter that is merely miscalibrated out of domain
> still misranks compounds even when its discrimination holds, which is the practically
> relevant failure mode for a screening cutoff.
>
> Predictor variables: ECFP4 Morgan fingerprints (radius 2, 2048 bits) for the primary
> model; curated 2D Mordred descriptors for the secondary model.
>
> Covariates used for matching, not for prediction: molecular weight, cLogP, TPSA.
>
> Domain membership is defined by maximum Tanimoto similarity to the training set using
> Morgan fingerprints, radius 2, 2048 bits. Pre-specified sensitivity analyses use leverage
> (Williams plot, OECD guidance), Mahalanobis distance on the descriptor set, and
> Bemis–Murcko scaffold membership. These are reported whatever they show; if they
> disagree with the primary definition, the disagreement is itself the result.
>
> Variables used for subsetting or exclusion: InChIKey skeleton (deduplication); BBB label
> concordance across a skeleton (130 discordant skeletons excluded from the labelled set,
> retained for structural domain geometry); ChEMBL assay confidence score, assay type,
> standard type, and pChEMBL value (target set construction).

**Indices**

> Out-of-domain fraction: the proportion of a compound set whose nearest labelled-reference
> neighbour falls below a given Tanimoto cutoff. Computed as the share of compounds for
> which max over reference compounds of Tanimoto(Morgan r=2, 2048 bits) is less than t.
> Reported across the full cutoff sweep 0.3 to 0.8, because out-of-domain fractions are
> known to be threshold-sensitive and reporting a single cutoff would be selective.
>
> ΔROC-AUC: median ROC-AUC across the 200 control draws, minus the ROC-AUC on the proximal
> holdout. Positive values indicate worse performance on target-proximal chemistry.
>
> Confidence interval on ΔROC-AUC: constructed by pairing a stratified bootstrap of the
> proximal holdout AUC (2,000 resamples, resampled within class) with a randomly drawn
> control-arm AUC, and taking the 2.5th and 97.5th percentiles of the resulting difference
> distribution. This carries both the proximal arm's sampling error and the control arm's
> draw-to-draw variability. It is the only inferential quantity reported; a tail
> probability computed against the control draw distribution alone was tested, found to
> ignore the proximal arm's dominant sampling error, and discarded.
>
> Propensity score: probability of proximal membership estimated by logistic regression on
> standardised molecular weight, cLogP and TPSA. Used only for matching, never as a model
> input.
>
> Expected calibration error: sum over 10 equal-width probability bins of (bin count /
> total) multiplied by the absolute difference between the observed positive rate and the
> mean predicted probability in that bin.
>
> Replicate aggregation for ChEMBL activity: median pChEMBL across all qualifying
> measurements for a compound against a target, with the activity threshold applied once
> to that median.

---

# Analysis Plan

**Statistical models**

> Three BBB classifiers, fixed in advance. None is novel; the object of study is what the
> field already uses.
>
> 1. ECFP4 random forest (500 trees) — the common fingerprint baseline. PRIMARY MODEL.
> 2. Gradient boosting on curated 2D Mordred descriptors — the common descriptor baseline.
> 3. An off-the-shelf published BBB prediction tool, run as distributed, if one can be
> executed reproducibly with a recorded version. If none can, this arm is dropped and the
> omission reported; it will not be replaced with a substitute chosen after seeing results.
>
> Model specification for the primary model. Inputs: 2048-bit Morgan fingerprints, radius
> 2. Output: binary BBB+/BBB−. Hyperparameters selected by 3-fold cross-validated grid
> search over max_features in {sqrt, 0.03} and class_weight in {none, balanced}, scored by
> ROC-AUC, inside the proximal arm's training partition only. The selected configuration
> is shared across all three arms: an identical configuration cannot produce a between-arm
> difference, which is the only quantity the primary endpoint measures. Tuning
> independently within all 401 training partitions is computationally gratuitous and would
> make the arms differ in two ways at once.
>
> Probability calibration: Platt scaling fitted per cross-validation fold on held-out data,
> with fold models averaged at prediction time. The decision threshold is chosen by
> maximising Matthews correlation coefficient on held-out training-fold predictions within
> each arm's own training partition, never on its evaluation set.
>
> Primary test. ΔROC-AUC between the proximal holdout and the property-matched random
> holdout, for the ECFP4 random forest. Interval estimation by pairing a stratified
> bootstrap of the proximal holdout AUC (2,000 resamples) with a randomly drawn control-arm
> AUC, taking the 2.5th and 97.5th percentiles of the difference distribution. There is no
> omnibus test and no follow-up contrast: one endpoint, one model, one comparison.
>
> NEGATIVE CONTROL. The entire pipeline is run on label-permuted data, which contains no
> signal by construction. Eight independent permutations of 200 control draws each returned
> a mean ΔAUC of +0.0075 (sd 0.0317, t = +0.67), with all eight confidence intervals
> covering zero. This is a pre-registered precondition, not a post hoc check: the analysis
> script refuses to execute on real labels unless at least six such runs are on record,
> pinned to a hash of the analysis code, with mean ΔAUC within ±0.02 of zero.
>
> MANIPULATION CHECK. Property matching is verified by standardised mean differences
> between each control holdout and the proximal set on molecular weight, cLogP and TPSA,
> reported for every run. Target: |SMD| < 0.1 for the property-matched arm. Observed in
> validation: the unmatched random arm inherits the confound (cLogP −0.39, TPSA +0.38)
> while the property-matched arm reduces all three to within ±0.05. If the property-matched
> arm fails to achieve |SMD| < 0.1 on all three covariates, the matching is reported as
> failed and the primary comparison is reported as confounded rather than quietly accepted.
>
> ASSUMPTION TESTS. The primary endpoint is rank-based and distribution-free, so no
> parametric distributional assumptions are made. The bootstrap is stratified by class to
> preserve the holdout's class balance. No convergence criteria apply to random forests;
> for the logistic propensity model, failure to converge within 2,000 iterations would be
> reported and the matching treated as failed per the criterion above.

**Transformations**

> No transformation is applied to the outcome variable.
>
> Structures are standardised and deduplicated as described under data collection
> procedures: deduplication on the first block of the InChIKey, dropping stereochemical and
> protonation layers.
>
> Fingerprint features are binary and are not scaled, centred or otherwise transformed;
> tree ensembles are invariant to monotone feature scaling. The three covariates used for
> propensity matching (molecular weight, cLogP, TPSA) are standardised to zero mean and
> unit variance before the logistic regression, and are used only for matching, never as
> model inputs.
>
> Categorical coding: BBB+ is coded 1 and BBB− is coded 0. No other categorical variables
> enter any model.
>
> Potency values are used only to determine set membership via the pChEMBL threshold; no
> potency value enters any model, endpoint or reported result. This is why the known
> disagreement over pooling IC50 with Ki (10.1371/journal.pone.0061007 against
> 10.1021/acs.jcim.4c00049) does not govern this study, and it is tested rather than
> asserted: across ten curation variants the out-of-domain fraction spans 81.8–89.4% for
> BACE1 and 21.7–36.4% for AChE, leaving at least a 45-percentage-point contrast in every
> case.

**Inference criteria**

> Primary endpoint ΔROC-AUC, two-sided, alpha = 0.05. Inference is by confidence interval
> rather than p-value.
>
> Support for H1: ΔAUC ≥ 0.06 against the property-matched control, with a 95% confidence
> interval excluding zero.
>
> Refutation: a ΔAUC 95% confidence interval contained entirely within ±0.03, reported as a
> null result in those words, with the conclusion that nearest-neighbour domain distance
> does not predict BBB prediction error in this setting.
>
> Inconclusive: anything between the two, reported as inconclusive and not resolved by
> adding metrics, cutoffs, models or targets until something clears.
>
> These three rules are evaluated by the analysis script itself and printed as a verdict,
> so the reported conclusion cannot be selected after the effect size is known.
>
> Multiplicity: one primary endpoint, on one model, against one control. The other two
> models, the other two control arms, the secondary metrics and the cutoff sweep are all
> secondary and reported without inferential claims of primacy. No correction for multiple
> comparisons is applied because no family of confirmatory tests is being conducted — there
> is a single confirmatory comparison.
>
> No tail probability is reported for the primary endpoint. A one-sided empirical quantity
> comparing the proximal AUC against the control draw distribution was implemented, tested
> on permuted data, found to return values of 0.010 and 0.005 on data containing no signal,
> and discarded: it ignores the proximal arm's sampling error of approximately 0.027, which
> dominates. Any such quantity appearing in output is labelled descriptive.
>
> No outcome licenses a search for a different endpoint, cutoff or target that gives a
> better number. Any analysis run after seeing results will be labelled post hoc in the
> manuscript.

**Data inclusion and exclusion**

> Compounds whose structures cannot be parsed or sanitised by RDKit are excluded and
> counted.
>
> B3DB skeletons carrying contradictory BBB+/BBB− labels (130 of 4,022) are excluded from
> the labelled set as unusable ground truth, while being retained for structural domain
> geometry where only connectivity matters. Records that collapse to the same InChIKey
> skeleton are represented once.
>
> ChEMBL records are excluded by the fixed activity definition given under data collection
> procedures: standard type other than IC50 or Ki, assay confidence score below 9, assay
> type other than B, censored relations, records carrying a data validity comment, units
> other than nM, or a median pChEMBL below 6.
>
> Compounds are NOT excluded for wide replicate spread. The spread is reported as a
> data-quality statistic instead, following the flag-don't-delete principle: a compound
> measured inconsistently is still a compound that was synthesised against the target,
> which is all that is required of it here.
>
> No outlier removal of any kind is performed on the outcome. There is no basis for
> declaring a compound an outlier with respect to a binary permeability label, and removing
> poorly predicted compounds would directly bias the quantity being measured.
>
> The proximal holdout is defined by a structural criterion applied to every labelled
> compound; no compound within the cutoff is excluded from it for any reason.

**Missing data**

> There are no missing outcome data. Every compound in the labelled reference set carries a
> BBB+/BBB− label by construction; compounds without one are not in the set.
>
> Missing structures: records lacking a parseable SMILES are excluded at the parsing stage
> and counted, not imputed.
>
> Missing covariates: molecular weight, cLogP and TPSA are computed from structure rather
> than measured, so they are present for every parseable compound. If a descriptor
> computation fails for a compound, that compound is excluded from the propensity model and
> the exclusion is counted.
>
> No imputation is performed anywhere in the analysis.

**Other planned analysis**

> Secondary confirmatory analyses, pre-specified: the same comparison against the size- and
> class-matched random control (arm 2); the same comparison for the Mordred
> gradient-boosting model and, if runnable, the off-the-shelf tool; the secondary endpoints
> MCC, balanced accuracy, Brier score and expected calibration error; and the domain cutoff
> sweep from 0.3 to 0.8.
>
> Pre-specified sensitivity analyses on the definition of the applicability domain:
> leverage (Williams plot, OECD guidance), Mahalanobis distance on the descriptor set, and
> Bemis–Murcko scaffold membership. These are reported whatever they show. If they disagree
> with the nearest-neighbour definition, the disagreement is itself a reportable result.
>
> Pre-specified sensitivity analyses on curation: ten variants covering IC50-only, Ki-only,
> inclusion of Kd, inclusion of confidence score 8, pChEMBL thresholds of 5, 7 and 8,
> inclusion of functional and ADMET assay types, and no skeleton deduplication. Already
> computed and public; reported as exploratory.
>
> Two exploratory, hypothesis-generating components, specified in Amendment A1 of the full
> pre-registration and written before either was run:
>
> (a) A shortlist selected from the 2,391 curated acetylcholinesterase actives — compounds
> of measured activity against the human enzyme — discarding those outside the
> applicability domain before any BBB prediction is made, then applying the audited model
> to the in-domain remainder only, with synthetic accessibility and property triage.
>
> (b) Domain-constrained design proposals: novel structures generated by enumerating a
> fixed, pre-declared catalogue of single medicinal-chemistry transformations applied to
> in-domain parent compounds, filtered on in-domain membership, predicted permeability,
> synthetic accessibility (Ertl SA score ≤ 4.0), novelty against ChEMBL and PubChem,
> Bemis–Murcko scaffold retention, a property window and PAINS. No generative model is used
> and no activity prediction is applied, deliberately: both would mean applying a model to
> novel chemistry without auditing that model's own applicability domain, which is the
> error this study documents.
>
> Neither exploratory component carries a p-value, and neither claims activity, brain
> penetration or therapeutic potential. No laboratory work is proposed or required for any
> claim made.

---

# Other

**Context and additional information**

> Full pre-registration, analysis code, decision log, literature search record and all
> exploratory results are public at:
>
> https://github.com/shreyansk6-stack/bbb-domain-alzheimers
>
> Registered against commit 134ab6065bb6cbc79000944e52837932f7fe7219
>
> That commit contains the complete pre-registration (docs/preregistration.md, sections
> 1-13 plus Amendment A1), the ChEMBL curation decisions with their published basis
> (docs/curation-decisions.md), the dated decision log (docs/decisions.md), the systematic
> literature search record (docs/literature-search.md), the confirmatory analysis code
> (scripts/confirmatory.py), the harness validation code and results, and every exploratory
> result quoted in this registration. Later commits will add the confirmatory results; this
> hash marks the state of the project at registration.
>
> CONTEXT ON THE RESEARCH QUESTION. Published applicability-domain analyses of BBB models
> are computed on the model's own held-out test set. A held-out split is drawn from the
> training distribution, so high coverage is near-guaranteed by construction, and three
> separate 2026 papers duly report 93.9%, 94.8% and "complete coverage". No published work
> measures domain coverage against the target-directed chemistry these filters are actually
> deployed on. A systematic Europe PMC search conducted 2026-11-16 (five queries, 35 unique
> candidate records, all abstracts read, four near neighbours read in full) returned zero
> hits for blood-brain barrier combined with applicability domain in the title, and zero
> for blood-brain barrier combined with chemical space and coverage.
>
> PRIOR WORK THAT CUTS AGAINST THE HYPOTHESIS, cited here deliberately rather than buried:
> a 2026 QSAR ADMET study (10.1016/j.compbiolchem.2026.109356) reported a 0.32-0.39 AUC
> generalisation gap while its applicability-domain analysis showed complete structural
> coverage. If that result generalises, the primary hypothesis of this study may fail. That
> is one reason a null result is pre-specified as a publishable outcome.
>
> AI USE DISCLOSURE. Claude Code (Anthropic) was used for the exploratory and sensitivity
> analyses, the systematic literature search, drafting this registration and the
> pre-registration document, the analysis code in scripts/, and proposing the ChEMBL
> curation decisions together with the published basis for each. All numerical results are
> produced by scripts in the repository and are reproducible from the recorded data
> versions. No AI system is an author; the author is responsible for all decisions.
>
> DEVIATIONS. Any deviation from this registration will be recorded in the repository's
> decision log with its date and reason, and stated in the manuscript, distinguishing
> deviations decided before from those decided after seeing affected results.
