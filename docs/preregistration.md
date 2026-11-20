# Pre-registration

**Title.** Applicability domain of blood–brain barrier predictors in Alzheimer's
target chemical space: a methods audit

**Authors.** Shreyan Kancharla, Davidson College (first author). Sam [surname to be
filled in], Davidson College (second author; physicochemical interpretation,
synthetic accessibility, target-chemistry literature context).

**Authorship order fixed 2026-11-19: first and second, not co-first.** An earlier
co-first arrangement with an equal-contribution footnote was considered and is not
adopted. The division of work in section 13 is a first/second split rather than an
equal one, and an equal-contribution note that the work does not support would be a
misstatement on the paper itself.

**REGISTERED 2026-11-19 on OSF Registries.** DOI `10.17605/OSF.IO/UQR62`
(<https://osf.io/uqr62>), public and not embargoed, against commit
`134ab6065bb6cbc79000944e52837932f7fe7219`. This document is frozen as of that
commit; subsequent changes are appended as dated amendments, never rewritten.
The registration record, field by field, is `docs/osf-submission.md`.

**Version 1.1, 2026-11-16.** Supersedes v1.0 of the same date, which was never
registered externally; both versions are in this repository's git history. The
revision fixes the ChEMBL curation recipe that v1.0 left provisional, and updates
the sample sizes and power that follow from it. Written before any modelling or
error analysis has been run. Once registered, amendments are appended, never
rewritten, with dates and reasons.

---

## 1. Question

Alzheimer's virtual-screening pipelines routinely rank compounds for activity
against a target — commonly BACE1 or acetylcholinesterase (AChE) — then pass the
hits through an off-the-shelf blood–brain barrier (BBB) predictor to ask whether
they can reach the brain. Those predictors are trained on literature-derived data
that skews toward approved and CNS-active drugs. Target inhibitor series are narrow,
heavily optimised medicinal chemistry.

**Are BBB predictions valid for the compounds they are actually applied to?**

## 2. What is already established, and what is not

Established, and deliberately not re-tested here:

- Out-of-domain BBB predictions are less accurate. A B3DB-trained logBB model
  reports in-domain R² = 0.641 versus out-of-domain R² = 0.164
  (`10.3390/pharmaceutics18060670`); its out-of-domain estimate rests on 13
  compounds.
- B3DB benchmark performance is inflated by stereochemical redundancy and is
  sensitive to split strategy (`10.20944/preprints202609.2002.v1`,
  `10.3390/pharmaceutics18081018`).
- Chemical-space distance does not always predict error. A QSAR ADMET study found a
  0.32–0.39 AUC generalisation gap while its applicability-domain analysis showed
  complete structural coverage (`10.1016/j.compbiolchem.2026.109356`).

Not established, and the gap this study addresses: **every applicability-domain
analysis in this literature is computed on the model's own held-out test set.** All
therefore report high coverage — 93.9%, 94.8%, "complete coverage" in three separate
2026 papers. A held-out split is drawn from the training distribution, so that
figure is near-guaranteed by construction and carries no information about
deployment. No published work measures domain coverage against the target-directed
chemistry these filters are deployed on. A systematic Europe PMC search
(`docs/literature-search.md`, 2026-11-16) returned zero hits for BBB plus
applicability domain in title, and zero for BBB plus chemical space plus coverage.

## 3. Confirmatory and exploratory work, separated

**Already run, therefore exploratory, and will be labelled as such in the
manuscript.** All chemical-space overlap and physicochemical comparison numbers in
`README.md`, `results/scoping_overlap.txt` and `results/curated_overlap.txt`,
including the headline figures that 86.0% of BACE1 actives and 26.8% of AChE actives
have no B3DB neighbour above Tanimoto 0.3. These motivated the study; they are not
confirmatory tests of it, and no p-value will be attached to them.

**Confirmatory, pre-registered here, not yet run.** Everything in sections 6–9. No
model has been trained and no error has been measured at the time of writing.

## 4. Data

| Source | Version | Licence |
| --- | --- | --- |
| B3DB classification set | GitHub `main`, fetched 2026-11-14 | CC0 1.0 |
| ChEMBL | ChEMBL_37, released 2026-05-01 | CC BY-SA 3.0 |

Targets: BACE1 (CHEMBL4822) and AChE (CHEMBL220), both human.

**Activity definition, fixed (`docs/curation-decisions.md`):** IC50 or Ki (Kd
excluded), `standard_relation = '='`, no `data_validity_comment`, units nM, assay
type B, **assay confidence score 9** (direct single-protein assignment), replicates
aggregated by median pChEMBL, threshold **pChEMBL ≥ 6**.

The confidence-score filter is the substantive one: score-9 assays are 100%
*Homo sapiens* in these targets, while score-8 assays have organism unspecified or
non-human, which matters for AChE where non-human enzyme assays are common.

Resulting sets: **BACE1 5,157 actives, AChE 2,391 actives.**

These decisions are justified by citation and by sensitivity analysis rather than
by expert assertion, because no enzyme-kinetics specialist is on the author list.
Every contested choice is reported as a variant in `results/sensitivity.txt`;
across all of them BACE1 out-of-domain ranges 81.8–89.4% and AChE 21.7–36.4%, so
the headline contrast survives every available alternative with a ≥45-point margin.

No data refetch after this date without a dated amendment. ChEMBL is a live API.

## 5. Curation (settled, see `docs/decisions.md` 2026-11-16)

Both B3DB and the ChEMBL target sets are deduplicated on the **first block of the
InChIKey** — connectivity only, dropping stereochemical and protonation layers.
Canonical-SMILES deduplication finds zero duplicates in B3DB, because SMILES
distinguish stereoisomers that 2D Morgan fingerprints cannot; deduplicating finer
than the skeleton is incoherent for a fingerprint model.

Resulting sets: B3DB 7,805 records → 4,022 skeletons, of which 130 carry both BBB+
and BBB− labels. Discordant skeletons are **excluded from the labelled set**
(contradictory ground truth) and **retained for domain geometry** (structure only).
Labelled reference set: 3,892 compounds, 2,472 BBB+ / 1,420 BBB−. Targets: BACE1
6,918 skeletons, AChE 3,014.

## 6. Domain definition

**Primary.** Maximum Tanimoto similarity to the training set, Morgan fingerprints,
radius 2, 2048 bits. A compound is in-domain at cutoff *t* if its nearest training
neighbour is at similarity ≥ *t*. **Primary cutoff: t = 0.35**, fixed here, chosen
because it is the cutoff at which the AChE-proximal set is large enough to measure
error (section 9) while remaining a defensible neighbourhood.

The 0.3 cutoff would give better power (1,066 compounds, minimum detectable
ΔAUC 0.041, versus 492 and 0.061 at 0.35). It is deliberately **not** adopted:
Tanimoto 0.3 on Morgan fingerprints is a weak claim of similarity, and buying power
by loosening the definition of "in domain" would undercut the paper's own argument.
0.35 was fixed before the class counts were known.

**Reported in full regardless.** The complete cutoff sweep 0.3–0.8, because
out-of-domain fractions are known to be threshold-sensitive and reporting a single
cutoff would be selective.

**Sensitivity analyses, all pre-specified.** Leverage (Williams plot, OECD
guidance); Mahalanobis distance on the descriptor set; Bemis–Murcko scaffold
membership. These are reported whatever they show. If they disagree with the
primary definition, the disagreement is the result and is reported as such.

## 7. Models

Three, fixed here. None is novel; the point is to audit what the field uses.

1. **ECFP4 random forest** — the common fingerprint baseline. *Primary model.*
2. **2D descriptor gradient boosting** (Mordred, curated feature set) — the common
   descriptor baseline.
3. **An off-the-shelf published BBB tool**, run as distributed, if one can be
   executed reproducibly with a recorded version. If none can, this is dropped and
   the omission reported; it is not replaced with a substitute chosen after seeing
   results.

Hyperparameters are tuned by cross-validation **within the training partition
only**. Thresholds and probability calibration are derived from validation folds
only, never from the evaluation set.

## 8. Primary design: proximal holdout versus matched random holdout

The question is what happens when a model is applied to target chemistry. So:

1. **Proximal holdout.** Remove from training every labelled B3DB compound within
   0.35 of AChE chemistry (**n = 492; 366 BBB+, 126 BBB−**). Train on the
   remainder. Evaluate on the held-out proximal set.
2. **Matched random holdout.** Remove instead a random set of identical size and
   class balance. Train identically. Evaluate on it. Repeat over 200 draws to build
   a null distribution rather than relying on one comparison.
3. **Property-matched random holdout.** As above, but drawn to match the proximal
   set's molecular weight, cLogP and TPSA distributions by propensity matching.

Design 3 exists because designs 1 and 2 share a confound: target-proximal compounds
are larger and more lipophilic than B3DB's average (BACE1 mean MW 472 vs BBB+ 318),
so a performance drop could reflect molecular complexity rather than domain
novelty. Design 3 is the one that separates those. **If designs 2 and 3 disagree,
design 3 governs the conclusion** and the gap between them is reported as the
magnitude of the property confound.

Training-set size is identical across all three arms by construction, so no arm is
advantaged by having more data.

**Primary endpoint.** ΔROC-AUC between the proximal holdout and the property-matched
random holdout, for the ECFP4 random forest.

**Secondary endpoints.** MCC; balanced accuracy; and calibration error (Brier score,
expected calibration error). Calibration matters practically: a filter that is
merely miscalibrated out of domain still misranks compounds even if its AUC holds.

**Multiplicity.** One primary endpoint on one model against one control. Everything
else — the other two models, the other two controls, the secondary metrics, the
cutoff sweep — is secondary and reported without inferential claims of primacy.

## 9. Power, and what a null result would mean

Simulated (`scripts/power.py`; binormal, 4,000 replicates, rank-based AUC) at the
actual curated sample size of 366 BBB+ / 126 BBB−:

| True AUC | SE of AUC | 95% CI width |
| --- | --- | --- |
| 0.95 | 0.010 | ±0.020 |
| 0.90 | 0.016 | ±0.030 |
| 0.85 | 0.019 | ±0.038 |

Minimum detectable ΔAUC at 80% power, two-sided α = 0.05, against a matched holdout:
**≈ 0.061** if baseline AUC is 0.90, ≈ 0.077 if 0.85. Repeated draws on the control
arm will improve on this, since the control's contribution to the variance shrinks
over 200 draws; 0.061 is the conservative figure.

**Stated plainly: this study is not powered to detect a small effect.** If the true
degradation is on the order of 0.01–0.03 AUC, we will not find it, and a null result
must be reported as "no degradation larger than ~0.06 AUC" — not as evidence of no
degradation. Given that the abandoned predecessor idea foundered on an effect of
0.00–0.03 AUC, this is a live possibility and is stated in advance so it cannot be
quietly reframed later.

For reference, the effects this design is built to detect are much larger than its
floor: the in/out-of-domain gap reported for a B3DB logBB model is R² 0.641 vs 0.164
(`10.3390/pharmaceutics18060670`), and a comparable QSAR generalisation study found
AUC gaps of 0.32–0.39 (`10.1016/j.compbiolchem.2026.109356`). If the effect is of
that order, 0.061 is ample. The risk is a genuinely small effect, not a blind spot.

**Pre-specified decision rules.**

- **Support:** ΔAUC ≥ 0.06 against the property-matched control, CI excluding zero.
- **Refutation:** ΔAUC CI contained within ±0.03. Reported as a null result, in
  those words, with the conclusion that nearest-neighbour domain distance does not
  predict BBB prediction error in this setting — which would corroborate
  `10.1016/j.compbiolchem.2026.109356` and remains publishable.
- **Inconclusive:** anything between. Reported as inconclusive. Not resolved by
  adding metrics, cutoffs, models or targets until something clears.

No outcome licenses a search for a different endpoint, cutoff or target that gives a
better number. Any such analysis run after seeing results is labelled post hoc.

## 10. BACE1 is declared unmeasurable in advance

Pre-specified sufficiency criterion for measuring error in a target-proximal
neighbourhood: **≥ 200 labelled compounds with ≥ 50 in each class** at the primary
0.35 cutoff.

- AChE: **492 compounds, 366 BBB+ / 126 BBB−. Passes.**
- BACE1: **89 compounds at 0.35, 60 BBB+ / 29 BBB−. Fails on both counts** — fewer
  than 200 total and fewer than 50 in the minority class. Simulated minimum
  detectable ΔAUC at that size is ≈ 0.136, which could not distinguish a real effect
  from noise.

So BACE1 error will not be measured, and this is recorded before any attempt rather
than reported as a failure afterwards. **The absence is a primary finding:** for
BACE1 chemical space there is essentially no public BBB ground truth, so BBB filters
applied to BACE1 hits in the published literature cannot be validated with existing
data. BACE1 shares 14 Bemis–Murcko scaffolds with B3DB out of 2,591, and exactly one
identical skeleton.

If a BACE1-proximal labelled set meeting the criterion is located during the project,
the analysis is added as a dated amendment, not slipped in.

## 11. Second component: AChE candidate shortlist

A shortlist of AChE-directed candidate compounds produced using **only in-domain
BBB predictions**, with synthetic accessibility assessed by the chemistry
co-author. This demonstrates the audit's constructive use.

**Declared exploratory and hypothesis-generating.** No claim of activity, no claim
of brain penetration, no claim of therapeutic potential. Compounds are described as
prioritised for evaluation, never as hits or leads. Causal and efficacy language is
excluded. No in vitro or in vivo work is proposed and none is required.

## 12. Deviations

Every deviation from this document is appended to `docs/decisions.md` with date,
reason, and whether it was decided before or after seeing affected results.
Deviations made after seeing results are stated as such in the manuscript. The
pre-registration file is never silently edited; this file's git history is the audit
trail, and the repository is public.

## 13. Roles and disclosure

**First author (Shreyan Kancharla):** the question; the pre-registration; ChEMBL and
B3DB curation decisions; the domain and error analysis; the confirmatory pipeline
and its validation; the design-proposal enumeration; the manuscript.

**Second author (Sam):** physicochemical interpretation; synthetic accessibility
assessment of the shortlist and of the design proposals; literature context for the
target chemistry; corresponding manuscript sections.

**Order is first/second, not co-first** (fixed 2026-11-19). The split above is not
an equal one, and an equal-contribution footnote the work does not support would
misstate the record.

**Changed from v1.0.** Curation and assay-comparability decisions were originally
assigned to the second author. They were instead made from published curation
standards and verified empirically (`docs/curation-decisions.md`), because the
specialist kinetics judgement that assignment assumed was not available. The
manuscript must defend them by citation and sensitivity analysis, and must not
imply specialist review that did not occur.

**AI use will be disclosed** in the manuscript per target-journal policy. Claude
Code (Anthropic) was used for: the scoping and sensitivity analyses; the systematic
literature search in `docs/literature-search.md`; drafting this pre-registration;
the analysis code in `scripts/`; and **proposing the ChEMBL curation decisions in
`docs/curation-decisions.md`, together with the published basis for each**. All
numerical results are produced by scripts in this repository and are reproducible
from the recorded data versions. No AI system is an author.

**Condition on registration.** The decisions in `docs/curation-decisions.md` are
attributed to the first author in the roles statement above, which is only accurate
if the first author can independently defend each one. Before this document is
registered externally, the first author must have read
`10.1371/journal.pone.0061007` and `10.1021/acs.jcim.4c00049` and be able to state,
unprompted, why confidence score 9 was required, why IC50 and Ki were pooled without
an offset, and why the primary cutoff was not moved to 0.3. Authorship means
responsibility for the choices, not authorship of the keystrokes; but responsibility
that cannot survive a reviewer's question is not responsibility.

Target journal: *Journal of Cheminformatics* (leading candidate; APC and waiver
terms to be confirmed from the publisher's own fees page, not third-party listings).

---

# Amendments

Appended, never rewritten. Each states its date, what changed, why, and whether it
was decided before or after seeing any affected result.

## Amendment A1 — 2026-11-19 — Component 2 specified; a design component added

**Status of both parts: exploratory and hypothesis-generating.** Neither bears on
the confirmatory primary endpoint in sections 6–9, neither carries a p-value, and
the confirmatory analysis is unaffected. Written **after** the exploratory scoping
and sensitivity results were known — in particular after it was known that 58.3% of
curated AChE actives fall outside the 0.35 domain cutoff — and **before** any
compound selection or structure enumeration has been run.

### A1.1 — Section 11 was ambiguous; the shortlist is selected, not generated

Section 11 committed to "a shortlist of AChE-directed candidate compounds produced
using only in-domain BBB predictions" without saying where the candidates come
from. That is specified now:

**The shortlist is selected from the 2,391 curated AChE actives**, which are
compounds with *measured* activity against human AChE. Nothing is generated for
this component. The procedure:

1. Partition the curated actives by domain membership at the primary cutoff
   (Tanimoto 0.35 to the B3DB labelled reference set).
2. **Discard the out-of-domain fraction** — not because those compounds are poor,
   but because no BBB prediction on them can be defended. On current numbers this
   removes 58.3% of the pool before any prediction is made, and that figure is
   itself reported as the constructive counterpart to the audit's finding.
3. Apply the audited BBB model to the in-domain remainder only; retain predicted
   permeant compounds with calibrated probabilities reported.
4. Apply synthetic accessibility (Ertl SA score) and standard property triage.
5. Report what survives, with every filter value per compound.

"Candidate" here means candidate for **brain penetration**, not for activity:
activity is measured, penetration is predicted. The manuscript must use that
wording.

### A1.2 — New component: domain-constrained design proposals

**Rationale.** The audit finds that target-directed chemistry sits largely outside
the applicability domain of the BBB predictors applied to it. The constructive form
of that finding is a design constraint: can AChE-directed chemistry be proposed
that remains *inside* the domain, so that a BBB prediction on it is defensible? A
structure proposed under that constraint is downstream of this paper's thesis
rather than appended to it.

**No generative model is used, and this is deliberate.** A learned generator has
its own applicability domain, which would be unexamined — committing, inside this
paper, the exact error the paper documents. Structures are produced by
**enumeration** instead: a fixed catalogue of single medicinal-chemistry
transformations applied to parent compounds with measured activity. Every proposed
structure is therefore traceable to one named parent and one named transformation,
and the whole component is reproducible from the repository.

**Procedure, fixed here before enumeration.**

*Parents.* The in-domain AChE actives from A1.1 — compounds with measured activity
whose own BBB prediction is already defensible.

*Transformations.* A fixed catalogue of common bioisosteric and R-group
replacements, encoded as RDKit reaction SMARTS and listed in full in the
implementing script:

| Class | Transformations |
| --- | --- |
| Acid isosteres | carboxylic acid → tetrazole, acylsulfonamide |
| Aromatic N-walk | phenyl → pyridyl (2-, 3-, 4-) |
| Ring replacement | benzene → thiophene, furan; piperidine ↔ piperazine ↔ morpholine |
| Linker | amide → reversed amide, sulfonamide; ether O → S, NH, CH₂ |
| Small alkyl | methyl → ethyl, cyclopropyl, CF₃, Cl |
| Halogen | F ↔ Cl ↔ Br |
| Fluorine scan | aromatic C–H → C–F |

**One transformation per parent.** Single-edit products only, to keep every
structure traceable and to avoid a combinatorial explosion that no one can inspect.

*Filters, all pre-declared, applied in this order, with a funnel table reporting
how many structures survive each:*

| # | Filter | Threshold |
| --- | --- | --- |
| 1 | Valid structure, parses and sanitises | RDKit |
| 2 | **In-domain by construction** | max Tanimoto to B3DB labelled set ≥ 0.35 |
| 3 | BBB predicted permeant by the audited model | calibrated probability reported |
| 4 | Synthetic accessibility | Ertl SA score ≤ 4.0 |
| 5 | Novelty | InChIKey skeleton absent from ChEMBL and PubChem |
| 6 | Scaffold retention | shares Bemis–Murcko scaffold with its parent |
| 7 | Property window | MW ≤ 450, cLogP 1–4, TPSA ≤ 90 |
| 8 | No PAINS | RDKit FilterCatalog |

*Ranking and cap.* At most **20** structures reported, ranked by maximum Tanimoto
to the B3DB reference set (descending — most defensible prediction first), ties
broken by SA score (ascending). The ranking deliberately contains **no activity
estimate**; see below.

*Novelty check.* ChEMBL is checked locally. PubChem is checked by API; if it is
unavailable the component reports ChEMBL-only novelty and says so explicitly rather
than implying a broader check than was run.

**No activity prediction is applied, and this is a deliberate omission.** Ranking
novel structures by a QSAR activity model would mean applying a model to novel
chemistry without auditing that model's own domain — again, the error this paper
documents. Auditing an activity model as well is a separate project. The
consequence is stated plainly: these structures have **no predicted potency**, and
the only activity-related claim available is that each shares a scaffold with a
compound of measured activity.

**Permitted claims.** Each proposed structure is novel, synthetically accessible by
the stated metric, derived by one named transformation from a compound with
measured human AChE activity, and — the point of the exercise — positioned such
that the BBB prediction made on it falls inside the model's demonstrated domain.

**Prohibited claims.** That any structure is active, that it penetrates the brain,
that it is a hit, lead, candidate drug, or has therapeutic potential. Causal and
efficacy language is excluded, as in section 11. No in vitro or in vivo work is
proposed, and none is required for any claim made.

**Stated weakness, which is also the scientific content.** Requiring in-domain
membership biases the proposals toward chemistry resembling B3DB, which is enriched
in approved and CNS-active drugs. That may trade away target potency: the
transformations that move a compound into the BBB domain are not chosen to preserve
AChE binding, and single-edit bioisosteric replacement does not guarantee retained
activity. **This component therefore trades plausibility-of-activity for
defensibility-of-prediction, and it cannot evaluate that trade without activity
data it does not have.** The trade is the honest subject of the component and must
be described as such, not buried.

**Follow-on work, explicitly out of scope here.** Synthesis of any proposed
structure, and any biochemical assay, belong to a separate project. Should an AChE
assay ever be run, note that commercially available enzyme is typically
*Electrophorus* or *Torpedo*, which decision D2 excluded from the training data on
the grounds of divergent inhibitor SAR; measured data from such an assay would fail
this study's own inclusion criterion and would have to be reported with that
qualification.
