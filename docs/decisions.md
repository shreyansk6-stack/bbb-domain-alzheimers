# Decision log

Dated record of real decisions and status changes, newest last. A collaborator — or a
different Claude session — should be able to pick up the state of the project from
this file without re-deriving it.

## 2026-11-14 — Project scoped, not yet started

**Topic chosen.** Applicability domain of blood–brain barrier (BBB) predictors in
Alzheimer's target chemical space. Two-part design: (1) validity audit of BBB
predictions for BACE1 and acetylcholinesterase inhibitor space; (2) an
acetylcholinesterase-focused candidate shortlist produced using only in-domain
predictions, with synthetic accessibility assessed.

**An earlier version of this project was abandoned.** The first plan was to show that
random train/test splits inflate BBB model performance. Rejected after literature
check: published twice already (JCIM 2025, "Overrepresentation Bias Leads to
Performance Overestimation in BBB Permeability Prediction Models"; Pharmaceutics 2026,
3D conformer descriptors on B3DB), and the effect size is ~0.00–0.03 AUC, sometimes
within run-to-run variance. Not enough to carry a paper.

**Scoping check run before committing.** Verified that the datasets exist, are
licensed for use, and contain enough data for the design. Results in
`results/scoping_overlap.txt`. Key numbers in `README.md`.

**Feasibility gate: passes for AChE, fails for BACE1.** Error can be measured in
AChE-proximal space (~942 labelled compounds above 0.35 similarity, both classes
represented). It cannot for BACE1 (145 at 0.35, 49 at 0.4, all weak matches). This
converts into the paper's sharpest claim rather than killing it: for BACE1 chemical
space there is essentially no public BBB ground truth, so published filters applied
to BACE1 hits are unvalidatable with existing data.

**Data versions.** B3DB fetched from GitHub `main` on 2026-11-14 (7,805 compounds
parsed: 4,956 BBB+, 2,849 BBB−). ChEMBL_37, released 2026-05-01, queried via API:
7,481 unique BACE1 actives, 3,125 AChE actives.

**Placeholder decisions awaiting a chemist's judgement.** These were chosen to get
numbers, not because they are right:
- Activity threshold: pChEMBL ≥ 6 on IC50/Ki only. ChEMBL mixes assay types, units
  and conditions; which measurements are comparable is a real decision.
- Representation: Morgan fingerprints, radius 2, 2048 bits.
- Domain definition: nearest-neighbour max Tanimoto. Leverage and Mahalanobis
  distance are alternatives and give different answers.

**Pre-registration constraint.** The scoping analysis above has already been run, so
those overlap numbers are exploratory and the pre-registration must state this
explicitly. The modelling and error analysis has not been touched and is what gets
pre-registered.

**Collaborator.** Sam, Davidson junior, chemistry major, works in a lab (bench access
not assumed and not required). Pitch document written and shared for his decision.
Python experience unknown — determines whether he owns the representation code or we
pair on it.

**Open before week 1.**
- Systematic literature search to confirm the specific question is unclaimed. Three
  targeted searches found nothing, which is suggestive, not conclusive.
- Target journal decided. Leading candidate: *Journal of Cheminformatics* (BMC /
  Springer Nature). APC figures from third-party listings conflict (~€1,790–1,990 /
  $2,190–2,290) and waiver terms were not found; read the publisher's own fees page.
- APC hardship waiver route: signed letter from the sponsored-programs office
  confirming no funding. Precedent exists with this publisher.
- Confirm Sam is in, and settle authorship in writing.

## 2026-11-16 — Systematic literature search done; scoop risk closed

**The specific question is unclaimed.** Full record, with queries and hit counts, in
`docs/literature-search.md`. Europe PMC returns zero papers with both "blood-brain
barrier" and "applicability domain" in the title, and zero for BBB + chemical space
+ coverage/overlap at abstract level. 35 unique candidate records were identified and
all 35 abstracts read; four adjacency risks read in full. Every citation was verified
against the Europe PMC API rather than taken from a search snippet — one web-search
result supplied a PMC ID that does not resolve.

**The framing sharpened, and this is the main outcome.** Every AD analysis in this
literature is run on the model's own held-out test set, so all of them report ~94%
in-domain coverage (93.9%, 94.8%, "complete coverage" in three separate 2026
papers). That number is near-guaranteed by construction and says nothing about
deployment. Our 85.8% out-of-domain for BACE1 is its inverse. The contribution is
not "out-of-domain predictions are worse" — that is already established — but that
the field certifies domain coverage on a population no screening pipeline meets.

**A prior result now supplies our premise.** Pharmaceutics 2026
(10.3390/pharmaceutics18060670) reports in-domain R² = 0.641 vs out-of-domain
R² = 0.164 on a B3DB logBB model. This is the cost of being out of domain, measured
on our own dataset, and it means we no longer have to establish that ourselves —
we establish the exposure. Caveat: their out-of-domain figure rests on 13 compounds.

**A prior null result cuts against us and must be cited, not buried.** Comput Biol
Chem 2026 (10.1016/j.compbiolchem.2026.109356) found a 0.32–0.39 AUC generalisation
gap while AD analysis showed complete structural coverage, concluding that
out-of-domain extrapolation did not explain it. This is direct evidence for the
"distance may not predict error" risk already logged, and it hardens the design
constraint: error gets measured directly in AChE-proximal space, never inferred
from distance.

**New curation requirement.** A 2026 preprint (10.20944/preprints202609.2002.v1)
shows deduplicating B3DB on canonical SMILES finds only 3 duplicates, while
InChIKey-skeleton deduplication collapses 7,802 compounds to 3,952 and exposes 131
skeletons carrying discordant BBB+/BBB- labels. Our curation must deduplicate on
skeleton and report the discordant count. The scoping numbers in `README.md` were
computed without this and will need recomputing once curation is fixed.

**Abandoning the original idea is confirmed correct.** Benchmark inflation and
split sensitivity on B3DB are now covered by that preprint plus
10.3390/pharmaceutics18081018, on top of the two papers already logged.

**Residual risk accepted as low.** Europe PMC does not fully index ChemRxiv or the
ACS/Wiley/RSC back catalogue at abstract level, and a scoop could sit in a methods
section whose abstract advertises something else. Re-run the two zero-hit queries
before submission.

**Next.** Write the pre-registration. It is now unblocked: the question is
confirmed unclaimed, the framing is fixed, and three design constraints above
(skeleton deduplication, direct error measurement, exploratory-numbers disclosure)
are settled going in.

## 2026-11-16 — Skeleton-level curation applied; headline holds, gate tightens

Done before writing the pre-registration, so that the pre-registered numbers are
ones that will not move. Script `scripts/curate_gate.py`, output
`results/curated_overlap.txt`, which supersedes `scoping_overlap.txt`.

**Curation decision, now settled.** Deduplicate both B3DB and the ChEMBL target
sets on the first block of the InChIKey (connectivity only; drops stereochemical
and protonation layers). Rationale: canonical-SMILES deduplication finds **0**
duplicates in B3DB, because SMILES distinguish stereoisomers that 2D Morgan
fingerprints cannot. Deduplicating on anything finer than the skeleton is
incoherent for a fingerprint-based model.

**Effect on B3DB.** 7,805 parsed records collapse to 4,022 skeletons; 1,488
skeletons have multiple members, largest group 9. 130 skeletons carry both BBB+
and BBB- labels. Discordant skeletons are **excluded from the labelled reference
set** (contradictory ground truth) but **retained for domain-coverage geometry**,
where only structure matters. Labelled reference set: 3,892 compounds, 2,472 BBB+
and 1,420 BBB-. Target sets: BACE1 7,481 -> 6,918; AChE 3,125 -> 3,014.

**Pipeline independently reproduces the published counts.** We get 4,022 skeletons
and 130 discordant labels; the preprint reports 3,952 and 131 from 7,802 records.
Small differences are expected from parse-failure handling and RDKit version. This
is a genuine check that our curation does what we think it does.

**The headline is robust — this was the main thing to find out.** BACE1
out-of-domain at 0.3 moves 85.8% -> 86.0%; AChE 26.4% -> 26.8%. Medians essentially
unchanged. The BACE1/AChE contrast is not a deduplication artefact, and the
pre-registration can quote these numbers.

**The feasibility gate tightened, and this matters for the design.** Labelled
ground truth within 0.35 of AChE chemistry falls from 942 to **611** compounds
(464 BBB+, 182 BBB-); within 0.4, from 458 to 300. For BACE1, from 145 to **101**
at 0.35 and 49 to **28** at 0.4. The earlier "~942 labelled compounds" figure in
the 2026-11-14 entry is superseded. AChE remains a viable positive control, but the
error analysis must be powered for ~600 compounds with 2.5:1 class imbalance, not
~950. BACE1 remains unmeasurable, as before.

**This is a second finding, not just a correction.** The labelled data sitting
nearest to target chemistry is disproportionately stereoisomer-redundant — roughly
a third of it collapses. So apparent ground-truth coverage near target space is
itself inflated, on top of being thin. Worth a paragraph in the paper.

**Scaffold overlap is starker after curation.** BACE1 shares 14 Bemis-Murcko
scaffolds with B3DB out of 2,591, and exactly 1 identical skeleton. AChE shares 36
of 1,493, and 27 identical skeletons.

**Environment note.** The venv was absent and was rebuilt; rdkit 2025.09.2 /
pandas 2.3.3 / Python 3.9.6, identical to the 2026-11-15 run, so the raw-vs-curated
comparison is not confounded by library versions. `data/` had survived.

## 2026-11-16 — Pre-registration v1.0 written

`docs/preregistration.md`. Written after curation so that its numbers are ones that
will not move, and before any model has been trained.

**Primary design settled: proximal holdout versus matched random holdout.** Remove
from training every labelled B3DB compound within 0.35 of AChE chemistry (n = 611),
train on the remainder, evaluate on the held-out proximal set; compare against a
size- and class-matched random holdout over 200 draws, and against a holdout
propensity-matched on MW, cLogP and TPSA. Training-set size is identical across arms
by construction.

**The property-matched arm exists for a real reason.** Target-proximal compounds are
larger and more lipophilic than B3DB's average (BACE1 mean MW 472 vs BBB+ 318), so a
performance drop could reflect molecular complexity rather than domain novelty. If
the simple and property-matched controls disagree, the property-matched one governs
the conclusion. Without this arm a reviewer would be right to reject the inference.

**Primary endpoint:** ΔROC-AUC, ECFP4 random forest, proximal versus
property-matched holdout. One endpoint, one model, one control. Everything else is
secondary and labelled so.

**Calibration added as a secondary endpoint.** A filter that is merely
miscalibrated out of domain still misranks compounds even when its AUC holds, which
is the practically relevant failure for a screening cutoff.

**Power computed, not asserted.** `scripts/power.py`, output `results/power.txt`.
At the curated 464/182 split the minimum detectable ΔAUC is **≈0.053** at 80% power.
Stated bluntly in the pre-registration: if the true degradation is 0.01-0.03 AUC we
will not detect it, and a null must be reported as "no effect larger than ~0.05",
not as no effect. The abandoned predecessor idea died on an effect of 0.00-0.03 AUC,
so this is a live possibility and is on the record in advance.

**Decision rules pre-specified**, including what counts as refutation (ΔAUC CI
within ±0.03, reported as a null in those words, corroborating
10.1016/j.compbiolchem.2026.109356) and what counts as inconclusive. No outcome
licenses switching endpoint, cutoff, model or target.

**BACE1 declared unmeasurable in advance** against a stated sufficiency criterion
(≥200 labelled compounds, ≥50 per class at 0.35). AChE passes at 611; BACE1 fails at
101, where the minimum detectable ΔAUC would be ≈0.124. Recording this before
attempting it converts a dead end into a stated finding.

**Component 2 (AChE shortlist) is declared exploratory and hypothesis-generating**,
with no claim of activity, brain penetration or therapeutic potential, and
causal/efficacy language excluded. No bench work proposed or required.

**Blocked on one thing:** the activity threshold (pChEMBL ≥ 6 on IC50/Ki) is still
provisional pending the chemistry co-author's judgement on assay comparability. If
it changes, the pre-registration is amended and dated before analysis runs. This is
now the critical path.

## 2026-11-16 — Curation decided from literature, not from a co-author

The second author is a chemistry major but not an enzyme-kinetics specialist, so the
"placeholder decisions awaiting a chemist's judgement" from 2026-11-14 could not be
resolved that way. They are now made from published curation standards and verified
empirically. Full reasoning and citations in `docs/curation-decisions.md`.

**Consequence for the manuscript, stated so it is not forgotten.** These decisions
are defended by citation and sensitivity analysis, not by expert assertion. The
paper must not imply specialist kinetics review that did not happen. Author roles in
the pre-registration were amended accordingly.

**The literature genuinely disagrees.** Kalliokoski et al. 2013
(10.1371/journal.pone.0061007) find pooling IC50 with Ki acceptable given a ~0.35
log offset; Landrum & Riniker 2024 (10.1021/acs.jcim.4c00049) find ~65% of paired
measurements differ by >0.3 log units and advise against casual pooling. Both are
about the accuracy of potency values.

**That controversy does not reach us, and we can show it rather than argue it.** No
potency value enters any model; the threshold decides set membership only. We
measured the replicate spread in our own data (BACE1 46.9% span >0.3 log units,
18.1% >1.0; AChE 34.0% and 17.2%) — the concern is real and present — and then
measured whether it matters. Across ten curation variants BACE1 out-of-domain spans
81.8-89.4% and AChE 21.8-36.4% at the 0.3 cutoff. **Worst case for the contrast
still leaves a 45-point gap.** `results/sensitivity.txt`.

**Decisions, in brief.** Pool IC50 and Ki with no offset, exclude Kd; assay
confidence score 9 only; assay type B; pChEMBL >= 6 with the 5-8 sweep reported;
replicates aggregated by median pChEMBL; no per-target threshold. Four further
filters (standard_relation, data_validity_comment, units, organism) are asserted in
code but verified to be no-ops in ChEMBL_37, and are recorded as such so nobody
later mistakes them for the filters that mattered.

**The confidence-score filter is the one that does real work, and the data decided
it.** Score-9 assays are 100% Homo sapiens for these targets; score-8 assays have
assay_organism unspecified or non-human (Cercopithecidae, Cavia porcellus), matching
relationship_type H. This matters most for AChE, where Electrophorus and Torpedo
enzyme assays are common and have different inhibitor SAR. Cost: 29.2% of BACE1 and
19.3% of AChE records. Verified by inspecting the assays, not assumed.

**New primary sets, superseding all earlier counts.** BACE1 5,157 actives
(85.8% / 97.5% / 99.4% out-of-domain at 0.3 / 0.35 / 0.4); AChE 2,391 actives
(28.4% / 58.3% / 77.2%).

**The feasibility gate tightened again, and the power with it.** Labelled B3DB
compounds within 0.35 of AChE: **492** (366 BBB+, 126 BBB-), down from 611.
Minimum detectable dAUC rises from 0.053 to **0.061**. BACE1: **89** (60/29), now
failing the sufficiency criterion on both the total and the minority class.

**Declined to move the primary cutoff to 0.3 despite better power** (1,066
compounds, MDE 0.041). Tanimoto 0.3 on Morgan fingerprints is a weak claim of
similarity, and buying power by loosening the definition of "in domain" would
undercut the paper's own argument. Recorded because the temptation was real and the
decision should be visible.

**Pre-registration amended to v1.1** with the fixed recipe, the new sample sizes,
the 0.061 power floor and the revised support threshold (dAUC >= 0.06). v1.0 was
never registered externally; both versions are in git history.

**No longer blocked.** The critical path is now external registration on OSF, then
the confirmatory analysis.

## 2026-11-16 — OSF submission package prepared

`docs/osf-submission.md`: paste-ready answers for every field of the OSF
Preregistration template, drawn from `docs/preregistration.md` v1.1.

**The "Existing data" answer is "Registration following analysis of the data."**
This is the honest answer and it will feel like the wrong one. The option covers
"calculation of descriptive statistics and observation of data distributions,"
which is exactly what the scoping, assay-metadata and sensitivity analyses did.
Claiming "before analysis" would be a misrepresentation, and a trivially detectable
one once the repository is public and timestamped. The template's "Explanation of
existing data" field is designed for this case and is used to state precisely what
was and was not done: no model trained, no error measured, no proximal-versus-
matched comparison computed.

**Analyst blinding, functional equivalent.** The confirmatory analysis code will be
written and validated on label-permuted data before being run once on real labels,
so the pipeline is fixed before any real outcome is observable. Recorded in the
registration under Blinding.

**Two blanks must be filled at submission:** the repository URL and the git commit
hash being registered against. The repo currently has no remote.

**Next:** a public remote (needed for the registration to reference), then register,
then write the confirmatory pipeline.

## 2026-11-16 — Confirmatory pipeline written, label-permuted validation running

`scripts/confirmatory.py` implements pre-registration sections 6–9 for the primary
endpoint. Committed before being run, so the permuted validation is tied to a
specific commit hash.

**The real-label run is gated in code, not by intention.** `--mode real` exits
unless four conditions hold: a registration identifier is supplied; a permuted run
is on record; that run used ≥ 100 draws; and it returned a ΔAUC confidence interval
covering zero. The permuted manifest must also match the current commit, so editing
the pipeline re-locks it. The pre-registered blinding substitute is therefore
enforced by the script rather than asserted in prose.

The pre-specified decision rules from section 9 are evaluated by the script and
printed as a verdict. A verdict computed by frozen code cannot be selected after
the number is known.

### Implementation clarifications the pre-registration did not settle

Both were decided and recorded **before any real-label run**. Neither changes a
pre-registered quantity; each resolves an ambiguity in how section 8 is realised.

**IC-1 — what pool the random control is drawn from.** Section 8 says "a random set
of identical size and class balance" without saying whether proximal compounds may
be drawn. Taken literally: arm B draws from the whole labelled set, so roughly 12.6%
of each control holdout is itself proximal. That dilution biases arm B **toward the
null**, making it the conservative reading, and it is the one adopted. The realised
share is reported per run (13.8% in the smoke test). Arm C draws from the distal
pool only, since a propensity-matched control containing proximal compounds would
defeat its purpose.

**IC-2 — hyperparameter tuning across arms.** Section 7 requires tuning "within the
training partition only." Tuning independently inside all 401 training partitions is
computationally gratuitous, and per-arm tuning would make the arms differ in two
ways at once. Resolution: tune once by 3-fold CV inside the **proximal arm's**
training partition — exactly as section 7 specifies for the primary arm — and share
that configuration with every control arm. A configuration identical across arms
cannot generate a between-arm difference, which is the only thing the primary
endpoint measures. Stated in the manuscript rather than left implicit, because the
control arms' evaluation compounds are inside the pool the configuration was chosen
on; with a four-point grid this is a very low-capacity channel and it is shared, not
differential.

**Threshold and calibration.** The decision threshold is chosen by maximising MCC on
out-of-fold predictions within each arm's own training partition, never on its
evaluation set. Calibration is Platt (sigmoid), which is monotonic and therefore
cannot change AUC — only the secondary Brier and ECE figures.

### What the smoke test already confirms about the design

Two draws are not a result, but the matching diagnostics are structural and do not
depend on the labels:

- **The property confound is real and large.** Proximal versus distal standardised
  mean differences: cLogP and TPSA around ±0.4. Arm B inherits that imbalance
  (cLogP −0.39, TPSA +0.38); arm C removes it (all three within ±0.05). This is
  precisely why section 8 makes arm C govern the conclusion, and the diagnostic now
  demonstrates the arms behave as designed.
- Permuted arm AUCs land near 0.5 as they must.

**Running:** 200-draw permuted validation, ~3 h. Until it returns null, the real
run stays locked.

**Still the critical path:** external registration on OSF. The pipeline can be
finished and validated without it, but the real-label run should not happen before
the registration is timestamped.

## 2026-11-16 — Two pipeline corrections found by running the permuted validation

The label-permuted run is a substitute for analyst blinding, but it also works as
what it is: a test harness on a null dataset. It caught two things before any real
labels were touched, which is the whole point of running it first.

**IC-3 — the primary endpoint is computed on the raw forest score, not the
calibrated probability.** Platt scaling is monotonic in expectation, so the original
code treated it as unable to affect AUC. That holds when there is signal to
calibrate. With permuted labels the fitted slope can come out *negative*, which
inverts the ranking and reflects AUC about 0.5. The permuted run showed it directly:
the proximal arm scored **AUC 0.470 raw against 0.535 calibrated** — the two sit on
opposite sides of chance, from one model on one evaluation set.

With real labels the slope will be firmly positive and the two will agree, so this
changes no expected result. It is fixed anyway, because an endpoint that depends on
the sign of a nuisance parameter is not a safe endpoint, and because the permuted
validation itself would otherwise be reading an inverted number. Calibration still
produces Brier and ECE and still sets the decision threshold. Both AUCs are
reported; `auc_calibrated` is retained in the output so the two can be compared.

**IC-4 — the permutation is varied, not fixed.** The proximal arm has exactly one
evaluation set, so a single permutation gives it a single realisation, and the
resulting ΔAUC could sit away from zero by luck rather than bias. `--permute-seed`
repeats the check across permutations; the canonical seed-42 run is the one the gate
reads, and the others are written beside it.

**Performance, no methodological content.** `ArmModel` replaces
`CalibratedClassifierCV` plus a nested `cross_val_predict` with one 3-fold loop that
retains its held-out predictions: identical quantities, three forest fits per arm
instead of twelve. `n_jobs` is fixed at 6 rather than -1, because nested parallelism
drove load average past 20 on a 10-core machine and throughput collapsed. A draw
costs about 3 s where it had been 3.5 min under contention.

**On the 4-draw numbers, which are not results.** Arm C sat about 0.02 above chance
and arm A about 0.03 below it. Four draws cannot distinguish that from noise — the
draw-to-draw spread was smaller than the sampling error of a single evaluation set,
which is what overlapping training partitions produce. The 200-draw runs across four
permutations are what settle it, and the gate will not unlock unless they return a
ΔAUC interval covering zero.

## 2026-11-16 — A false alarm, and the real defect under it (IC-5)

The first four permuted runs returned ΔAUC **+0.051, +0.019, +0.050, +0.000** —
every one positive, mean +0.030, which is half the pre-registered support threshold.
Two of them reported a descriptive tail probability of 0.010 and 0.005 on data
containing no signal whatsoever. The proximal arm's AUC across those four runs was
0.4703, 0.4726, 0.4659, 0.4774: mean 0.472, standard deviation 0.005, where the
Hanley–McNeil standard deviation for this class split is 0.028. An AUC varying five
times less than it should, sitting consistently below chance, looks like a biased
harness.

**It was not biased. The four seeds landed low together by chance.**
`scripts/validate_harness.py` establishes this with two tests, both on permuted
labels, and `results/harness_validation.txt` records the output:

- **Model frozen, evaluation labels permuted, 2,000 reps:** mean **0.4998**, sd
  **0.0277**, against a Hanley–McNeil prediction of **0.0274**. The metric is
  centred and has exactly the expected spread.
- **Joint permutation across twelve seeds:** mean **0.4913**, sd **0.0257**, range
  0.4556–0.5318, **t = −1.17** versus 0.5. The arm is centred under the null.

Recorded rather than quietly deleted, because the wrong conclusion was reachable
from the first four runs and the correction cost nothing but twelve more fits.

### IC-5 — the "empirical p" was invalid and has been removed

The defect the false alarm exposed. The quantity was the share of control draws
falling at or below the proximal AUC, printed as "empirical p". It compares **one**
proximal AUC against the spread of control **draws** — but the control median has a
small standard error over 200 draws, while the proximal arm carries its own sampling
error of ~0.028, which dominates and which this quantity ignores entirely. Whenever
the proximal arm landed a standard deviation low by chance, nearly every control
draw exceeded it and the number collapsed toward zero. **It manufactures
significance out of noise**, and on permuted data it duly produced 0.010 and 0.005.

It is now reported as a labelled descriptive share with an explicit note that it is
not a test. The confidence interval — which pairs a stratified bootstrap of the
proximal AUC with the control draw distribution, carrying both variance sources —
covered zero in all four permuted runs, as a correct interval should. It is the only
inferential quantity the study reports.

Had this run on real labels first, a chance-low proximal arm would have produced a
headline "p = 0.005" that no reviewer could have caught from the manuscript, because
the quantity sounds reasonable and the code was not public at the point the number
would have been quoted. This is the clearest justification the project has for
validating on permuted labels before real ones.

### The gate now judges six permutations, not one

One permutation characterises one realisation of a single fixed evaluation set.
`--mode real` therefore requires **six** valid permuted runs on the same pipeline
hash and tests their **mean** ΔAUC against ±0.02, in addition to the canonical run's
interval covering zero.

**Consequence for the power statement, which is unchanged but now better founded.**
The proximal arm's irreducible AUC spread of ~0.026–0.028 comes from measuring on
492 fixed compounds, and it is the reason the pre-registered minimum detectable
ΔAUC is ~0.061. The simulation in `scripts/power.py` said 0.061; the permutation
spread says the same thing by a different route. Section 9's warning — that a null
must be reported as "no degradation larger than ~0.06 AUC" — is now supported
empirically rather than only by simulation.

**Running:** eight 200-draw permuted runs, which is two more than the gate requires.

## 2026-11-17 — Permuted validation complete; the real-label run is unlocked

Eight 200-draw permuted runs on pipeline `922efb8f8c28`, summarised in
`results/permuted_validation_summary.txt` (regenerate with
`scripts/summarise_permuted.py`).

| | value |
| --- | --- |
| mean ΔAUC under the null | **+0.0075** |
| sd across runs | 0.0317 |
| t vs zero | **+0.67** |
| signs | 5 positive, 3 negative |
| intervals covering zero | **8 / 8** |

The gate's conditions are met: eight runs against a required six, all on one
pipeline hash, mean within ±0.02, every interval covering zero. Verified by calling
`check_unlocked()` directly rather than by starting a real run, so the pipeline file
was not touched and the eight runs stay pinned to it.

**This closes IC-5 cleanly.** The four development seeds were all positive with a
mean of +0.030; across eight seeds the signs are mixed and the mean is +0.0075.
Individual runs still reach +0.0509 and −0.0286 by chance, because each one's ΔAUC
is dominated by a proximal arm measured on a single fixed set of 492 compounds.
That is the same ~0.027 spread that sets the study's 0.061 minimum detectable
effect. Any single permuted run was always going to look like something.

**Note for the manuscript.** The methods section should report the mean across
permutations rather than a single validation run, and should say why: one
permutation validates one realisation. This is a small point that would be easy to
get wrong in writing up and is the kind of thing a reviewer of a pre-registered
methods audit will check.

### Environment failure, and what it cost

Five of the first eight runs never executed a line of Python. The interpreter died
in `site.py` reading `env/pyvenv.cfg` with `TimeoutError: [Errno 60]`. Cause: the
machine's iCloud account is at **175 bytes of remaining quota** with Desktop &
Documents sync enabled, and this repository sits in `~/Documents`, so iCloud was
failing to sync 333 MB of virtual environment while the local disk sat at 99% full.
Reads against the synced venv stalled. The same contention inflated completed runs
to 1 h and 3 h 39 m against about 20 minutes of actual work.

**Fixed:** the virtual environment now lives at `~/.venvs/bbb-domain-alzheimers`
with `env/` as a symlink, so `./env/bin/python` still works as documented
everywhere and the repository presents 15 MB rather than 333 MB to the sync daemon.
`requirements.txt` reproduces it exactly; versions are unchanged.

**Outstanding, and not a code issue:** the disk is still near capacity and the repo
still sits inside a permanently failing iCloud sync queue. Moving the project out of
`~/Documents` would remove a recurring source of non-deterministic failure in a
project whose whole value is reproducibility.

**Next, and now the only blocker:** OSF registration. The pipeline is finished,
validated and locked; `--mode real` requires a registration identifier and will
refuse without one.

## 2026-11-19 — Amendment A1: Component 2 specified, design component added

`docs/preregistration.md` now carries an **Amendments** section with A1, appended
rather than edited, per section 12.

**A1.1 closes a real gap.** Section 11 promised "a shortlist of AChE-directed
candidate compounds" and never said where the candidates came from. Three sentences,
all of them about what would *not* be claimed. Ambiguity in a pre-registered
component is what a reviewer attacks first. The shortlist is now specified as
**selected** from the 2,391 curated actives — compounds with measured human AChE
activity — with the out-of-domain 58.3% discarded *before* any BBB prediction is
made. "Candidate" means candidate for brain penetration; activity is measured,
penetration is predicted, and the manuscript must keep those words apart.

**A1.2 adds novel structures, by enumeration rather than generation.** The
distinction is the whole reason this is defensible. A learned generator carries its
own applicability domain, unexamined — which would reproduce, inside this paper, the
exact error the paper documents. Instead: a fixed catalogue of single
medicinal-chemistry transformations applied to in-domain parents, so every structure
traces to one named parent and one named transformation, and the component is
reproducible from the repository.

The framing is what makes it on-thesis rather than bolted on. The audit says
target-directed chemistry sits outside the predictors' domain; the constructive form
of that finding is a design constraint — **can AChE-directed chemistry be proposed
that stays inside the domain, so the BBB prediction on it is defensible?** Filter 2
makes in-domain membership a construction requirement rather than an outcome.

**No activity prediction is applied, deliberately.** Ranking novel structures by a
QSAR activity model would mean applying a model to novel chemistry without auditing
that model's domain. Omitting it costs the component any claim to potency, and that
cost is stated rather than hidden: the only activity-related claim available is
shared scaffold with a compound of measured activity.

**The weakness is the content.** Requiring in-domain membership biases proposals
toward chemistry resembling B3DB, which is enriched in approved and CNS-active
drugs, and the transformations are not chosen to preserve AChE binding. The
component trades plausibility-of-activity for defensibility-of-prediction and cannot
evaluate that trade without activity data. Written into the amendment in those
words.

Both components are exploratory, carry no p-values, and leave the confirmatory
analysis in sections 6–9 untouched. The amendment was written after the exploratory
58.3% figure was known and before any selection or enumeration was run; it says so.

`docs/osf-submission.md` updated to match under Exploratory analyses, so the
registration text and the pre-registration do not drift.

**Next for this component:** implement the enumeration. Filter thresholds are fixed
in writing first, which is what keeps it credible — they cannot be tuned once it is
visible what survives them.

## 2026-11-19 — Authorship order fixed: first/second, not co-first

Shreyan Kancharla first author, Sam second. An earlier co-first arrangement with an
equal-contribution footnote is **not** adopted.

The reason is simply that the work is not equal. The question, pre-registration,
curation decisions, confirmatory pipeline and its validation, domain and error
analysis, design-proposal enumeration and manuscript sit with the first author; the
second author's contribution is physicochemical interpretation, synthetic
accessibility, target-chemistry literature context and the corresponding sections.
That is a substantial second-author contribution and it is not an equal one. An
equal-contribution footnote the division of labour does not support would misstate
the record on the paper itself.

Recorded in `docs/preregistration.md` in both the Authors line and section 13.

**Owed to Sam directly.** Co-first authorship was floated to him earlier, and
`docs/project-pitch.pdf` — the version he has seen — still describes that
arrangement along with a curation role he no longer holds. He should hear the change
in a conversation rather than find it on a draft. Both the change and the reason are
defensible; being told late is what would not be.

## 2026-11-19 — REGISTERED on OSF

The pre-registration was submitted to OSF Registries and timestamped **2026-11-19**,
registered against commit `134ab6065bb6cbc79000944e52837932f7fe7219`. Public, not
embargoed. Schema: OSF Preregistration. Contributors: Shreyan Kancharla, Samuel
Siyanbola. Licence CC BY 4.0.

**DOI `10.17605/OSF.IO/UQR62`** — <https://osf.io/uqr62>. Archiving completed and the
registration accepted at 23:24:29 on 2026-11-19.

Title as registered: *Applicability domain of blood–brain barrier predictors in
Alzheimer's target chemical space: a methods audit and domain-constrained design.*
Broader than the working title, to cover the Amendment A1 design component.

**The exploratory/confirmatory boundary is now closed.** Everything computed before
this date is exploratory and must be labelled so in the manuscript. The confirmatory
analysis has not been run.

OSF's newer schema differs from the one `docs/osf-submission.md` was written
against: the old three-option "Existing data" question is replaced by an eight-level
"Foreknowledge of data or evidence" scale. The selected level was **"Authors have
observed the data, but have not performed the proposed analyses"** — which describes
this study exactly, where the old form forced a blunter answer. `docs/osf-submission.md`
should be rewritten against the newer schema so the repository records what was
actually registered rather than a form that no longer exists.

Material added at registration that is not in `docs/preregistration.md` and should
be carried into the manuscript's methods:

- **Negative control**, stated as a pre-registered precondition: the pipeline run on
  label-permuted data, eight permutations, mean ΔAUC +0.0075 (sd 0.0317, t = +0.67),
  all eight intervals covering zero.
- **Manipulation check** with a failure rule: property matching verified by
  standardised mean differences, target |SMD| < 0.1 on MW, cLogP and TPSA. If the
  property-matched arm misses that on any covariate, the matching is reported as
  failed and the primary comparison reported as confounded rather than quietly
  accepted.
- **Assumption handling**: the primary endpoint is rank-based and distribution-free;
  the bootstrap is stratified by class; non-convergence of the propensity model
  within 2,000 iterations would be treated as matching failure.

**Next:** retrieve the DOI, record it here and in the pre-registration, then run
`scripts/confirmatory.py --mode real --registered <DOI>`. The gate will refuse
without it.

## 2026-11-20 — CONFIRMATORY RUN COMPLETE. Verdict: INCONCLUSIVE

One run, real labels, registration `10.17605/OSF.IO/UQR62`, pipeline
`922efb8f8c28`, 8.9 hours. Full output in `results/confirmatory_real.txt` and
`results/confirmatory_real.json`.

### Primary endpoint

| Comparison | ΔAUC | 95% CI |
| --- | --- | --- |
| **vs property-matched (arm C, GOVERNS)** | **+0.0284** | **[−0.0164, +0.0749]** |
| vs size/class-matched random (arm B) | +0.0553 | [+0.0071, +0.1005] |

Proximal holdout AUC **0.8352** (bootstrap CI [0.7977, 0.8714]); arm B median
0.8905; arm C median 0.8636.

**Pre-specified verdict: INCONCLUSIVE.** ΔAUC is neither ≥ 0.06 with a CI excluding
zero (support) nor contained within ±0.03 (refutation). Evaluated by the frozen
script, not chosen afterwards.

Per section 9, this must be reported as **"no degradation larger than ~0.06 AUC"**
and never as no degradation. The minimum detectable effect is 0.061 and the point
estimate is 0.028: this study cannot resolve an effect of that size. That limitation
was stated in advance, which is the only reason it is a result rather than an
excuse.

### The property confound is real and it is about half the apparent effect

This is the substantive finding, and it is what the three-arm design existed to
produce.

Against the **unmatched** random control the gap is +0.0553 with a CI excluding
zero. Against the **property-matched** control it is +0.0284 with a CI covering
zero. **Roughly 49% of the apparent degradation is molecular-property difference,
not domain novelty.**

Section 8 pre-registered exactly this contingency — "if arms 2 and 3 disagree, arm 3
governs and the gap between them is reported as the magnitude of the property
confound" — so the number is reportable as specified rather than as a post hoc
observation. The practical lesson for the field is sharp: **a study that compared
target-proximal compounds against an unmatched random holdout would have reported a
significant degradation, and roughly half of it would have been molecular weight,
lipophilicity and polarity rather than the applicability domain.**

### A registered expectation that the data did not support

Sections 8 and the registration both state that target-proximal compounds are
"larger and more lipophilic" than the B3DB average, citing BACE1 mean MW 472 against
318. **For AChE that is half wrong.** Measured on the actual proximal set:

| | proximal | distal | SMD |
| --- | --- | --- | --- |
| MW | 345.3 ± 96.2 | 355.8 ± 168.7 | **−0.08** |
| cLogP | 3.28 ± 1.66 | 2.43 ± 2.14 | +0.44 |
| TPSA | 56.1 ± 34.6 | 78.1 ± 63.5 | −0.43 |

AChE-proximal compounds are **not larger** — they are marginally smaller, with a
negligible standardised difference. They are more lipophilic and distinctly less
polar. The MW claim was carried over from the BACE1 figures and does not hold for
the target actually analysed. The manuscript must state the AChE numbers and must
not repeat the "larger" claim. Recorded here because the registration contains it.

### Secondary endpoints, no inferential claim

Calibration is the one that moves. Expected calibration error on the proximal
holdout is **0.0971** against **0.0601** on the property-matched control, and Brier
0.1449 against 0.1283 — roughly 60% worse calibration error out of domain, while
discrimination (MCC 0.496 vs 0.519, balanced accuracy 0.775 vs 0.778) barely
differs. Section 8 anticipated this as the practically relevant failure mode: a
filter that is merely miscalibrated still misranks compounds even when its AUC
holds. It is secondary, has no pre-specified decision rule, and carries no p-value.

### What happens now, and what does not

The confirmatory analysis is **finished**. Section 9 forbids resolving an
inconclusive result by adding metrics, cutoffs, models or targets, and the
registration says any analysis run after this point is post hoc and must be labelled
so. The 0.3 and 0.4 cutoff sweeps and the other two models remain pre-registered
secondary analyses and may be run and reported as secondary — but none of them can
convert this verdict into a different one.

The paper does not depend on this outcome. The chemical-space mapping, the BACE1
unmeasurability finding, the held-out-test-set critique and the property-confound
magnitude all stand on their own, and the last of these is arguably more useful to
the field than a clean positive would have been.

## 2026-11-20 — H2 secondary analysis. Not supported, and a result that must be handled carefully

`scripts/secondary_cutoffs.py`, `results/secondary_cutoffs.txt`. Pre-registered
secondary, run after the confirmatory verdict was known, and labelled as such.
50 control draws per cutoff rather than 200: the control mean is estimated to
within ~0.002 at 50 draws while the proximal arm is one fixed evaluation set with
sd ~0.027 that no number of control draws reduces.

| cutoff | n | train | proximal | control | ΔAUC | 95% CI |
| --- | --- | --- | --- | --- | --- | --- |
| 0.30 | 1066 | 2826 | 0.8053 | 0.8724 | **+0.0672** | **[+0.0354, +0.0985]** |
| 0.35 | 492 | 3400 | 0.8352 | 0.8636 | +0.0284 | [−0.0164, +0.0749] |
| 0.40 | 224 | 3668 | 0.8500 | 0.8936 | +0.0436 | [−0.0172, +0.1058] |

**H2 is not supported.** It predicted that degradation increases at stricter
cutoffs. The pattern is non-monotonic, and the largest effect is at the *loosest*
cutoff — the opposite of the prediction.

### The 0.30 row is not evidence for H1, and must not be reported as if it were

At 0.30 the interval excludes zero and the point estimate exceeds the 0.06 support
threshold. Had 0.30 been the registered primary cutoff, the verdict would have been
SUPPORT rather than INCONCLUSIVE.

This is exactly the move section 9 forbids, and it is forbidden for a reason the
data illustrate. Three things differ at 0.30 besides strictness: n is 1066 rather
than 492, so the minimum detectable effect falls from 0.061 to 0.041; the training
set shrinks from 3400 to 2826, so the model is weaker on every arm; and "within
Tanimoto 0.30 on Morgan fingerprints" is a weak claim of chemical similarity. The
0.30 comparison is better powered and simultaneously measures something less
meaningful.

**The 0.35 cutoff was fixed before any of these class counts were known, and 0.30
was explicitly declined with the reasoning recorded (decision D9, section 6).** That
decision is what makes this reportable at all. The paper should state plainly that
the looser cutoff would have produced a positive headline, that it was declined in
advance on chemical grounds, and that the registered endpoint governs. A reader who
cannot verify that ordering has only our word for it; the git history and the OSF
timestamp mean they do not need to take it.

### A confound the registration did not anticipate

Changing the cutoff changes the training-set size, because a looser cutoff holds
out more compounds. Across cutoffs the comparison therefore conflates domain
strictness with training-set size. Within a cutoff the arms remain matched by
construction, so each row is internally clean; the *trend*, which is what H2 asks
about, is not. H2 as written could not have answered its own question. Reported as
a limitation.

## 2026-11-20 — A1.2 enumeration built, and the registered ranking rule is defective

`config/transformations.json`, `scripts/design_enumerate.py`,
`results/design_enumeration.txt`. Exploratory, post-registration.

Catalogue of 10 single medicinal-chemistry transformations, every entry carrying
its rationale and a `status` field that stays `proposed` until the chemistry
co-author signs off. All 10 parse, fire on real actives, and yield valid products.
From 2,391 curated AChE actives: 30,860 raw products → 906 survivors after scaffold
retention, the property window, PAINS, SA ≤ 4.0, in-domain membership and predicted
BBB+.

### Defect 1: the pre-registered ranking selects for compounds that already exist

A1.2 ranks survivors by "max Tanimoto descending, then SA ascending". Maximum
Tanimoto to the labelled reference is maximised by changing the parent as little as
possible, so the ranking optimises directly for *least novel*. It is not a
tie-break detail: the top three proposals at Tanimoto 1.000 are **already in B3DB**
— known compounds, reachable because a single halogen or N-demethyl edit lands on
one. Ranking by similarity-to-known and then filtering for novelty are opposed
objectives, and the registration contains both.

Three of the 906 survivors are already in B3DB. The novelty filter would remove
them, but it would be removing precisely the molecules the ranking promoted, which
means the rank order below them is also driven by the wrong objective.

**Not fixed unilaterally.** The ranking is a registered rule; changing it after
seeing the output is the kind of post hoc adjustment this project exists to avoid.
It needs a dated amendment stating the defect, the replacement rule, and that both
were decided with knowledge of the current output. The replacement should rank on
something that is not monotone in novelty — predicted margin above the decision
threshold, or distance into the domain rather than proximity to a specific
neighbour — and should cap products per parent, which the current rule also lacks.

### Defect 2: the novelty filter as written is not executable

A1.2 specifies novelty against ChEMBL and PubChem. Neither is checkable offline,
and there is no bulk lookup that avoids one network call per structure, so it could
never have been applied to 30,860 products. It is feasible on the survivors, which
is why the script orders it last and leaves it unapplied with the reason printed in
the output. Both databases are live, so any novelty claim must carry the date it
was checked.

### What the output says about the catalogue

Six of ten transformations contribute zero survivors (T01–T04, T09, T10). All
surviving products come from the aromatic fluorine scan (529), chlorination (303),
N-demethylation (61) and methyl→ethyl (12). The property window — cLogP 1–4 in
particular — removes the acid isosteres and ring replacements. A catalogue whose
output is 92% halogen scans is not proposing designs so much as decorating three
parent scaffolds, and the top 20 draws on only five distinct parents. This is a
chemistry judgement rather than a coding one and is the first thing the chemistry
co-author should rule on.

## 2026-11-20 — Domain-definition sensitivity. The conclusion holds; the definitions do not agree

`scripts/secondary_domain_defs.py`, `results/secondary_domain_defs.txt`.
Pre-registered secondary (section 8), run after the confirmatory verdict was known.
50 property-matched control draws per definition. Definitions C and D take the 492
closest compounds, matching the primary's n so that holdout size — and therefore
the minimum detectable effect — is held constant across definitions.

| definition | n | proximal | control | ΔAUC | 95% CI | match quality |
| --- | --- | --- | --- | --- | --- | --- |
| A nearest-neighbour Tanimoto | 492 | 0.8352 | 0.8636 | +0.0284 | [−0.0164, +0.0749] | **passes** |
| B Bemis–Murcko scaffold | 547 | 0.7983 | 0.7919 | −0.0064 | [−0.0460, +0.0365] | fails |
| C Mahalanobis | 492 | 0.8527 | 0.8846 | +0.0319 | [−0.0138, +0.0746] | fails |
| D leverage | 492 | 0.8527 | 0.8833 | +0.0306 | [−0.0140, +0.0746] | fails |

### The verdict is robust to the definition

Every interval covers zero. The INCONCLUSIVE verdict is not an artifact of having
chosen nearest-neighbour Tanimoto: no alternative definition turns it into an
effect, and none reverses its sign in a way the interval supports. This is the
result the sensitivity analysis existed to produce and it is reassuring.

### But the definitions disagree about which compounds are in domain

Jaccard overlap with the primary definition is **0.13–0.14**. Scaffold membership
recovers 26.4% of the nearest-neighbour proximal set; the descriptor-distance
definition recovers 23.2%. Three definitions that all claim to identify "compounds
inside the applicability domain" are, to a first approximation, selecting different
compounds.

That is a substantive finding and belongs in the paper rather than in a
supplementary table. The field reports applicability-domain coverage as though it
were one quantity. It is not: two papers using different standard AD methods on the
same model and the same dataset would be describing largely disjoint sets of
molecules. The agreement in ΔAUC across definitions therefore says the *conclusion*
is robust; it does not say the definitions measure the same thing, and the overlap
figures show they do not.

### Mahalanobis and leverage are the same statistic, not two checks

C and D select **identical** compound sets — 492 of 492, correlation 1.000. This is
expected once the descriptor matrix is centred on the target-set mean: leverage
h = xᵀ(XᵀX)⁻¹x and squared Mahalanobis distance differ only by scaling, and ranking
is invariant to it. The pre-registration lists them as separate sensitivity
analyses, which overstates the number of independent checks performed. The paper
should report **two** alternative definitions, not three, and say why.

### All three alternatives fail the registered matching criterion

The registered manipulation check requires |SMD| < 0.1 on MW, cLogP and TPSA, and
says that failing it means reporting the comparison as confounded rather than
quietly accepting it. Observed:

- A: MW −0.07, cLogP −0.03, TPSA −0.04 — **passes**
- B: MW +0.19, cLogP −0.07, TPSA +0.20 — fails
- C: MW −0.20, cLogP −0.11, TPSA −0.17 — fails
- D: MW −0.21, cLogP −0.11, TPSA −0.17 — fails

So the three alternative ΔAUC values above must be reported as confounded
comparisons. They are reported because the registration says to report them
whatever they show, not because they are clean.

For C and D the failure is **structural, not incidental**. Proximity is defined by
distance in a descriptor space that contains MW, cLogP and TPSA, so the definition
selects compounds that are extreme in precisely the covariates the control arm must
match on, and an adequately matched control pool does not exist. Any future study
defining its applicability domain on physicochemical descriptors and then
property-matching its controls faces the same circularity. Worth stating explicitly
in the discussion.

The primary definition is the only one of the four that both passes the matching
check and is independent of the matching covariates, which is a point in favour of
the pre-registered choice — decided, it should be noted, before any of this was
visible.

## 2026-11-21 — Secondary model (descriptor gradient boosting). Same sign, larger effect, still inconclusive

`scripts/secondary_descriptor_model.py`, `results/secondary_descriptor_model.txt`.
Model 2 of the three named in section 8. 50 property-matched draws.

### Declared deviation: RDKit descriptors substituted for Mordred

The registration specifies "curated 2D Mordred descriptors". Mordred is not a
dependency of this project and is unmaintained against current Python and numpy;
adding it would mean pinning an unmaintained package into the environment that
produced the registered results. The substantive requirement is a descriptor-based
baseline standing against the fingerprint-based primary model, not Mordred
specifically, so RDKit's 2D descriptor set was used instead.

Curation is unsupervised and label-free — non-finite columns, then zero-variance
columns, then one of each pair correlated above |r| = 0.95, dropped in fixed column
order — so it cannot leak outcome information. 210 descriptors → 209 → 202 → **173
retained**.

The deviation was decided knowing the confirmatory result but with no knowledge of
this model's result, since this is its first run. Recorded here, and to be stated in
the manuscript.

### Result

| model | proximal | control | ΔAUC | 95% CI |
| --- | --- | --- | --- | --- |
| ECFP4 random forest (**primary**) | 0.8352 | 0.8636 | +0.0284 | [−0.0164, +0.0749] |
| Descriptor gradient boosting (secondary) | 0.8175 | 0.8722 | **+0.0547** | **[+0.0075, +0.1030]** |

Match quality passes for this arm: MW −0.07, cLogP −0.04, TPSA −0.04, all inside
the registered |SMD| < 0.1 criterion. Unlike the alternative domain definitions,
this comparison is not confounded.

### What this does and does not license

**The primary verdict is unchanged.** Section 8 names the ECFP4 random forest as the
primary model and section 9 defines one endpoint on it. A secondary model's interval
excluding zero does not convert INCONCLUSIVE into SUPPORT, and the registration
anticipates exactly this by reporting secondary models "without inferential claims
of primacy".

**And it would not have, even as the primary.** Support requires ΔAUC ≥ 0.06 *and*
an interval excluding zero. At +0.0547 this falls short of 0.06, and it is outside
the ±0.03 refutation band, so judged by the registered rules this model is **also
INCONCLUSIVE** — inconclusive in a more suggestive direction, but inconclusive. The
two models agree on the verdict; they differ only on whether the interval clears
zero.

**The sign agrees and the magnitude is about double.** Both models find target-
proximal chemistry harder than property-matched controls. That consistency across
two quite different representations is worth reporting, and it is the honest
counterweight to the primary's null: the effect is probably real and probably small,
and this study is not powered to pin it down. The pre-registered reading — "no
degradation larger than ~0.06 AUC" — covers both results without strain.

### Secondary metrics diverge in an interesting direction

On the proximal holdout the descriptor model discriminates worse than the forest
(MCC 0.404 vs 0.496; balanced accuracy 0.699 vs 0.775) yet is *better calibrated*
(ECE 0.063 vs 0.097). It is also better than the forest on the matched controls
(0.872 vs 0.864). So the descriptor model is the stronger model in general and the
weaker one specifically on target-proximal chemistry, which is what produces its
larger gap. That is a cleaner demonstration of the paper's thesis than the primary
model gives, and it must be reported as a secondary observation rather than
promoted.

### Remaining

Model 3, the off-the-shelf published BBB tool, is still unrun. Section 8 provides
for dropping it if none can be executed reproducibly with a recorded version, and
requires the omission be reported rather than a substitute chosen after seeing
results.

## 2026-11-21 — Model 3 (off-the-shelf BBB tool) dropped. The omission is itself a finding

Section 8 provides for dropping model 3 "if none can be executed reproducibly with
a recorded version", requires the omission be reported, and forbids replacing it
with a substitute chosen after seeing results. It is dropped. Two independent
reasons, the second of which matters far more than the first.

### 1. Practical: nothing installs reproducibly with a recorded version

- **B3clf** (theochem, the B3DB authors) has no versioned package install. Its
  README directs you to clone the repository, build a conda environment on Python
  3.7 and run `pip install .` from the working tree. A clone is not a recorded
  version, and Python 3.7 is incompatible with this project's pinned 3.9
  environment. Its describing preprint was still unrefereed as of August 2025.
- **LightBBB** is distributed as a prediction web server with a downloadable
  dataset. No package, no pinnable version, and sending compounds to a third-party
  server is neither reproducible nor a recorded version.

### 2. Structural: the tools are trained on the only available ground truth

This is the dispositive reason, and it would hold even if the install were trivial.

**B3clf is trained on B3DB.** B3DB is this study's entire labelled reference set.
Every compound in the 492-compound proximal holdout is plausibly in B3clf's
training data, so its "prediction" on that holdout would be partly recall. The
resulting number would not measure generalisation to target-proximal chemistry; it
would measure memorisation, and it would be biased in the direction that makes BBB
filters look good.

This is not a quirk of one tool. B3DB was compiled from 50 published sources, which
are the same sources any public BBB model draws on. There is no large public BBB
dataset that is independent of B3DB, so **there is no off-the-shelf BBB predictor
that can be evaluated against B3DB without contamination, and no uncontaminated
public ground truth to evaluate one against instead.**

### Why this is a result rather than a gap

The paper's thesis is that published BBB models report applicability-domain
coverage on their own held-out test sets and therefore report coverage that is
near-guaranteed by construction. Model 3 fails for the same underlying reason: the
field's tools and the field's only public ground truth come from one literature
pool, so the tools cannot be independently validated at all — not by us, and not by
the papers that deploy them as screening filters.

That belongs in the discussion alongside the BACE1 unmeasurability finding. Both
say the same thing from different directions: the public data cannot support the
validation claims routinely made of it.

### Scope of the check, stated honestly

This was a documentation assessment of the tools we could identify, not an
exhaustive survey and not an attempted installation. An install was not attempted
because contamination is dispositive regardless of whether the software runs — a
successfully executed contaminated evaluation would be worse than no evaluation,
since it would produce a publishable-looking number that means nothing. If a
reviewer names a BBB tool with a pinnable version and a training set demonstrably
disjoint from B3DB, running it would be worthwhile and the result reported as post
hoc.
