# Supplementary Information

**Applicability domain of blood–brain barrier predictors in Alzheimer's target chemical space: a methods audit and domain-constrained design**

Pre-registered on OSF Registries, 2026-11-19, [10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62). All code, data manifests and result files: <https://github.com/shreyansk6-stack/bbb-domain-alzheimers>

> Every table in this document is generated directly from the recorded result files by `scripts/build_supplementary.py`. Nothing is retyped, so the SI cannot drift from the analyses it documents.

**Contents** — S1 domain-constrained design · S2 registration, amendments and decision log · S3 label-permuted validation · S4 curation sensitivity · S5 literature search record · S6 scaffold-filter sensitivity

---

## S1. Domain-constrained design, full treatment

**Exploratory throughout.** This component post-dates the registration, specified in Amendment A1.2 and with its ranking rule replaced by Amendment A2 (S2). No activity model was applied and no compound was synthesised or assayed. Nothing here supports a claim of activity, permeability or therapeutic use.

### S1.1 Transformation catalogue

Ten single medicinal-chemistry transformations, fixed before enumeration. The `status` and review note for each were set on 2026-11-21 from the literature-grounded assessment in `docs/catalogue-review.md`; **that assessment was not made by a practising medicinal chemist**, which the main text reports as a limitation.

| id | transformation | class | status | survivors |
| --- | --- | --- | --- | --- |
| T01 | Carboxylic acid to tetrazole | acid isostere | **rejected** | 0 |
| T02 | Carboxylic acid to primary amide | acid isostere | **approved** | 0 |
| T03 | Methyl ester to primary amide | linker swap | **approved** | 0 |
| T04 | Benzene to pyridine (aromatic N-walk) | aromatic N-walk | **approved** | 0 |
| T05 | Aromatic fluorine scan | fluorine scan | **approved** | 471 |
| T06 | Aromatic chlorination | halogen | **approved** | 267 |
| T07 | Methyl to ethyl homologation | small alkyl | **approved** | 11 |
| T08 | Tertiary amine N-demethylation | small alkyl | **approved** | 44 |
| T09 | Morpholine to piperidine | ring replacement | **approved** | 0 |
| T10 | Piperidine to morpholine | ring replacement | **diagnostic** | 0 |

Survivor counts are post-novelty (the 793 of S1.4). Per-entry rationale and the full review note for each transformation are in `config/transformations.json` and `docs/catalogue-review.md`.

**Two entries were changed by the review after enumeration had run.** T01 (carboxylic acid → tetrazole) was rejected, because tetrazole's pKa leaves the molecule anionic at physiological pH and so retains the charge that obstructs passive diffusion — a correct acid isostere in general, the wrong move for brain exposure. T10 (piperidine → morpholine) was reclassified as a model diagnostic rather than a design proposal, since it and T09 cannot both be improvements. **Neither change alters any reported output**: both transformations contributed zero survivors, having been eliminated by the scaffold filter (S1.2) before chemistry was considered. The enumeration was therefore not re-run, and its recorded header still describes the catalogue as provisional.

The catalogue's largest gap, identified by the same review, is the absence of any **hydrogen-bond-donor-reducing** transformation — N-methylation of a secondary amide, the inverse of T08, which is present. HBD count is among the strongest simple determinants of CNS exposure.

### S1.2 Filters and funnel

Eight filters, ordered so the expensive network-bound novelty check runs last, on survivors only.

```
raw products generated          : 40534
F1 valid and different          : 40534
F6 scaffold retained            : 38944
F7 inside property window       : 4336
F8 PAINS-free                   : 3974
F4 SA <= 4.0                    : 3860
unique structures               : 2943

F2 in domain (max Tanimoto >= 0.35) : 1116
F3 predicted BBB+ (p >= 0.68)        : 905
```

Filter F5 (novelty) is deliberately absent from this funnel; S1.4 explains why and reports it separately.

```
F5 NOVELTY - NOT APPLIED, AND WHY
A1.2 specifies novelty against ChEMBL and PubChem. Neither can be checked
offline: the local snapshot holds only AChE actives, not either database in
full, and there is no bulk structure-lookup that avoids one network call per
structure. Applying it to every enumerated product was never feasible. It is
feasible on the survivors, which is why it is ordered last here. Run it as a
separate, rate-limited step and record the date, because both databases are
live and a novelty claim is only true as of a given day.
```

### S1.3 Survivors by transformation

```
SURVIVORS BY TRANSFORMATION
  T01       0   Carboxylic acid to tetrazole
  T02       0   Carboxylic acid to primary amide
  T03       0   Methyl ester to primary amide
  T04       0   Benzene to pyridine (aromatic N-walk)
  T05     529   Aromatic fluorine scan
  T06     303   Aromatic chlorination
  T07      12   Methyl to ethyl homologation
  T08      61   Tertiary amine N-demethylation
  T09       0   Morpholine to piperidine
  T10       0   Piperidine to morpholine
```

**These counts are before the novelty check** and sum to 905, the F3 survivors of S1.2. The novelty check (S1.4) removes 112 of them, leaving the 793 in the S1.1 table and in the full structure table. Both sets of counts appear in this document and they are not the same number.

**93% of the surviving set is a single aromatic fluorination or chlorination.** Halogen scanning is real medicinal chemistry, but it is optimisation performed iteratively against assay feedback rather than hypothesis-generating design. Proposed cold, it is the smallest edit that keeps a molecule inside the predictor's domain. We report this component as a demonstration of the constraint, not as a drug-design contribution.

### S1.4 Novelty

```
EXPLORATORY. Query date 2026-11-21. Both databases are live, so this
result is only true as of that date and the date must be reported.

survivors checked        : 905
  exact match found      : 112  (not novel)
  no exact match         : 793
  lookup failed          : 0

  of the matched: PubChem only 67, ChEMBL only 0, both 45

novel survivors by transformation:
  T05  471
  T06  267
  T07  11
  T08  44
distinct parents among novel: 177
```

**Caveats, which apply to every novelty statement in this paper.** Lookup is exact-structure matching on the full InChIKey, so a stereoisomer, tautomer or salt of a known compound reads as unmatched. *No exact match* is not *no close analogue*: these are single edits of known actives, so close analogues exist by construction. Absence from ChEMBL and PubChem is not absence from the literature or from patents, neither of which was searched. Both databases are live, so the result is true only as of the query date.

### S1.5 Reported compounds under Amendment A2

One representative per scaffold, ranked by synthetic accessibility, capped at 20 — **20 distinct parents and 20 distinct scaffolds**.

| # | tx | SA | max Tanimoto | p(BBB+) | MW | cLogP | TPSA | HBD | parent | BRENK alert |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | T05 | 1.7 | 0.418 | 0.796 | 342.4 | 3.69 | 41.6 | 1 | CHEMBL6144349 | — |
| 2 | T05 | 1.75 | 0.351 | 0.737 | 356.4 | 3.33 | 58.6 | 1 | CHEMBL5268019 | — |
| 3 | T05 | 1.85 | 0.473 | 0.903 | 405.9 | 2.79 | 44.8 | 1 | CHEMBL5169781 | — |
| 4 | T06 | 1.87 | 0.353 | 0.919 | 356.9 | 3.9 | 49.4 | 1 | CHEMBL3415558 | Aliphatic_long_chain |
| 5 | T06 | 1.87 | 0.431 | 0.845 | 402.9 | 3.76 | 50.8 | 1 | CHEMBL5177371 | — |
| 6 | T06 | 1.88 | 0.406 | 0.686 | 416.9 | 3.53 | 67.9 | 1 | CHEMBL4455013 | — |
| 7 | T05 | 1.93 | 0.391 | 0.875 | 447.6 | 3.81 | 44.8 | 1 | CHEMBL5204532 | — |
| 8 | T05 | 1.96 | 0.368 | 0.904 | 244.3 | 3.67 | 16.1 | 0 | CHEMBL1459962 | — |
| 9 | T05 | 1.98 | 0.361 | 0.932 | 334.4 | 3.86 | 15.3 | 1 | CHEMBL4443695 | halogenated_ring_1 |
| 10 | T07 | 2.02 | 0.483 | 0.765 | 292.4 | 3.87 | 34.1 | 0 | CHEMBL1995010 | disulphide |
| 11 | T05 | 2.03 | 0.385 | 0.913 | 354.4 | 3.72 | 40.6 | 0 | CHEMBL4091683 | Aliphatic_long_chain |
| 12 | T08 | 2.03 | 0.435 | 0.704 | 337.4 | 3.97 | 51.5 | 1 | CHEMBL3586574 | Aliphatic_long_chain |
| 13 | T06 | 2.04 | 0.424 | 0.791 | 400.9 | 3.9 | 50.8 | 1 | CHEMBL1720480 | — |
| 14 | T08 | 2.05 | 0.414 | 0.748 | 409.6 | 2.89 | 60.5 | 2 | CHEMBL6120750 | — |
| 15 | T05 | 2.09 | 0.36 | 0.849 | 368.4 | 3.11 | 50.7 | 0 | CHEMBL5557329 | — |
| 16 | T05 | 2.1 | 0.353 | 0.888 | 372.4 | 3.91 | 49.4 | 1 | CHEMBL3415564 | Aliphatic_long_chain |
| 17 | T06 | 2.1 | 0.429 | 0.838 | 398.9 | 3.62 | 50.7 | 0 | CHEMBL5517663 | — |
| 18 | T05 | 2.16 | 0.352 | 0.899 | 366.4 | 3.18 | 57.7 | 0 | CHEMBL4085450 | diketo_group |
| 19 | T05 | 2.16 | 0.383 | 0.806 | 410.4 | 3.34 | 71.8 | 1 | CHEMBL4290940 | — |
| 20 | T05 | 2.17 | 0.397 | 0.889 | 408.5 | 3.96 | 62.6 | 1 | CHEMBL4286799 | — |

SMILES for each, with parent SMILES and scaffold, are in the machine-readable table (S1.8).

**A tradeoff we report rather than hide.** Ranking by synthetic accessibility selects simpler molecules, which are less similar to the reference set. Maximum Tanimoto across these 20 is 0.351–0.483 against a 0.35 cutoff — several compounds sit within 0.01 of the applicability-domain boundary. The superseded rule (S1.6) returned 0.672–0.818. The reported set trades depth-in-domain for chemical diversity and makeability; readers wanting depth-in-domain should use S1.6.

### S1.6 The superseded ranking

Amendment A1.2 as registered ranked by Tanimoto descending, then synthetic accessibility ascending. Executing it revealed that the rule **selected against the novelty it was meant to ensure**: the three highest-ranked products were at Tanimoto 1.000 to a B3DB compound — already-known structures — and the 20 collapsed onto 7 parents and 6 scaffolds, largely positional isomers of one another. Amendment A2 replaced it. Both rankings are published; this is the original.

```
TOP 20 BY THE PRE-REGISTERED RANKING (Tanimoto desc, then SA asc)
  #   tx   Tani  p(BBB+)    SA     MW  cLogP   TPSA  parent
  1  T06  1.000    0.755  1.97  269.8   1.99   58.4  CHEMBL640
  2  T08  1.000    0.888  3.13  337.4   3.67   44.8  CHEMBL131825
  3  T08  1.000    0.921  3.44  275.4   1.77   44.8  CHEMBL308043
  4  T05  0.818    0.871  3.18  355.4   3.81   44.8  CHEMBL74926
  5  T05  0.817    0.830  3.43  395.5   3.75   36.0  CHEMBL1243298
  6  T05  0.817    0.819  3.43  395.5   3.75   36.0  CHEMBL1243298
  7  T05  0.807    0.848  3.23  355.4   3.81   44.8  CHEMBL74926
  8  T05  0.778    0.803  3.48  395.5   3.75   36.0  CHEMBL1243298
  9  T05  0.778    0.808  3.50  395.5   3.75   36.0  CHEMBL1243298
 10  T05  0.759    0.818  3.22  355.4   3.81   44.8  CHEMBL74926
 11  T05  0.730    0.837  3.49  395.5   3.75   36.0  CHEMBL1243298
 12  T05  0.730    0.813  3.52  395.5   3.75   36.0  CHEMBL1243298
 13  T08  0.714    0.856  3.43  363.5   3.27   44.8  CHEMBL1243298
 14  T05  0.712    0.854  3.30  355.4   3.81   44.8  CHEMBL74926
 15  T05  0.712    0.847  3.33  355.4   3.81   44.8  CHEMBL74926
 16  T05  0.710    0.824  3.27  385.4   3.81   54.0  CHEMBL74950
 17  T08  0.698    0.817  3.41  345.5   3.77   53.6  CHEMBL433041
 18  T05  0.690    0.791  3.29  385.4   3.81   54.0  CHEMBL74950
 19  T06  0.690    0.897  3.30  385.9   4.00   44.8  CHEMBL74257
 20  T06  0.690    0.884  3.31  385.9   4.00   44.8  CHEMBL80221
```

### S1.7 Structural alerts

Filter F8 applies the PAINS catalogue. Inspection of the reported structures found compound #10 to be an **aryl thiosulfonate** — a thiol-reactive electrophile, used deliberately as a cysteine-modifying reagent — which PAINS does not match. A broader alert scan was therefore run over all 793 novel survivors.

| catalogue | flagged |
| --- | --- |
| PAINS (filter F8, already applied) | 0 / 793 |
| NIH | 4 / 793 |
| **BRENK** | **200 / 793** |

Leading BRENK alerts across the 793: aliphatic long chain (61), Michael acceptor (24), nitro group (21), aldehyde (17), diketo (14). **7 of the reported 20 carry an alert** (S1.5).

These liabilities are **inherited from the parent ChEMBL actives, not created by the single edits**. That is a real distinction and not a defence: a proposal list should surface them. They are **flagged, not removed** — removing them would mean adding a filter after seeing the output, which this project declined to do elsewhere. We report the finding as a caution against treating a PAINS pass as sufficient screening hygiene.

### S1.8 Full structure table

All **793** novel survivors, with SMILES, parent SMILES, parent ChEMBL id, transformation, Bemis–Murcko scaffold, maximum Tanimoto, predicted p(BBB+), Ertl SA, MW, cLogP, TPSA, HBD, BRENK alert and novelty query date, are provided as a machine-readable CSV: **`results/design_proposals.csv`** (Additional file 2).

---

## S2. Registration, amendments and decision log

The registration itself is public and immutable at [10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62), registered against commit `134ab60`. Foreknowledge was declared as *"authors have observed the data, but have not performed the proposed analyses"*. The two amendments below post-date it and are reproduced in full, since they are not on OSF.

### Amendments

Appended, never rewritten. Each states its date, what changed, why, and whether it
was decided before or after seeing any affected result.

#### Amendment A1 — 2026-11-19 — Component 2 specified; a design component added

**Status of both parts: exploratory and hypothesis-generating.** Neither bears on
the confirmatory primary endpoint in sections 6–9, neither carries a p-value, and
the confirmatory analysis is unaffected. Written **after** the exploratory scoping
and sensitivity results were known — in particular after it was known that 58.3% of
curated AChE actives fall outside the 0.35 domain cutoff — and **before** any
compound selection or structure enumeration has been run.

##### A1.1 — Section 11 was ambiguous; the shortlist is selected, not generated

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

##### A1.2 — New component: domain-constrained design proposals

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

---

#### Amendment A2 — 2026-11-21 — A1.2 ranking rule replaced; it selected against novelty

**Decided with knowledge of the enumeration output.** This is a post hoc change to
a registered rule and is labelled as such wherever it is reported. The output under
the original rule is retained and published alongside the output under the new one,
so a reader can see exactly what the change did.

##### The defect

A1.2 ranks surviving products by "maximum Tanimoto to the labelled reference,
descending, then Ertl SA ascending". Maximum Tanimoto to the reference set is
maximised by changing the parent as little as possible, so the rule ranks products
by *how close they are to compounds that already exist*. It therefore selects
directly against the novelty filter A1.2 also specifies.

This is not a theoretical conflict. Under the original rule the three
highest-ranked products were already present in B3DB, and of the 905 filtered
survivors the 112 that the novelty check removed are concentrated at exactly the
top of the ranking. The rule promotes the compounds the filter deletes.

The rule also has no cap on products per parent. The original top 20 drew on five
distinct parent compounds and consisted largely of positional isomers of the same
single edit.

##### The replacement

Applied to the novelty-filtered survivors (793 structures, 95 distinct Bemis–Murcko
scaffolds, query date 2026-11-21):

1. **One representative per scaffold.** Within each scaffold, take the product with
   the lowest Ertl SA score; ties broken by higher predicted p(BBB+), then by
   canonical SMILES in lexicographic order, so the selection is fully deterministic.
2. **Rank the representatives by Ertl SA ascending** — most synthetically
   accessible first.
3. **Cap at 20.**
4. Maximum Tanimoto and predicted p(BBB+) are **reported as columns, not used to
   rank.**

##### Why this rule

Ranking must not be monotone in novelty, which excludes similarity-to-reference.
It should also not rank on the predicted BBB probability, because this paper's
subject is the unreliability of that very prediction and ranking on a model's own
output while auditing it invites the obvious objection — the probability is
therefore reported but not ranked on. Synthetic accessibility is the one criterion
that is independent of both the model under audit and the novelty requirement, and
it is the criterion a synthetic chemist would actually apply.

The per-scaffold representative rule replaces the missing per-parent cap and is
stricter than one, since scaffold retention (filter F6) means every product shares
its parent's scaffold.

##### What this does not change

No filter, threshold or endpoint is altered. The surviving set of 793 structures is
the same set under either ranking; only the order and the selection of the reported
20 differ. Nothing in the confirmatory analysis is touched, and the primary verdict
is unaffected.

### S2.1 Decision log

27 dated entries record every judgement call made during the study, including those that went against us. The full log is `docs/decisions.md` (Additional file 3); the index follows.

| date | decision |
| --- | --- |
| 2026-11-14 | Project scoped, not yet started |
| 2026-11-16 | Systematic literature search done; scoop risk closed |
| 2026-11-16 | Skeleton-level curation applied; headline holds, gate tightens |
| 2026-11-16 | Pre-registration v1.0 written |
| 2026-11-16 | Curation decided from literature, not from a collaborator |
| 2026-11-16 | OSF submission package prepared |
| 2026-11-16 | Confirmatory pipeline written, label-permuted validation running |
| 2026-11-16 | Two pipeline corrections found by running the permuted validation |
| 2026-11-16 | A false alarm, and the real defect under it (IC-5) |
| 2026-11-17 | Permuted validation complete; the real-label run is unlocked |
| 2026-11-19 | Amendment A1: Component 2 specified, design component added |
| 2026-11-19 | Authorship order fixed: first/second, not co-first |
| 2026-11-19 | REGISTERED on OSF |
| 2026-11-20 | CONFIRMATORY RUN COMPLETE. Verdict: INCONCLUSIVE |
| 2026-11-20 | H2 secondary analysis. Not supported, and a result that must be handled carefully |
| 2026-11-20 | A1.2 enumeration built, and the registered ranking rule is defective |
| 2026-11-20 | Domain-definition sensitivity. The conclusion holds; the definitions do not agree |
| 2026-11-21 | Secondary model (descriptor gradient boosting). Same sign, larger effect, still inconclusive |
| 2026-11-21 | Model 3 (off-the-shelf BBB tool) dropped. The omission is itself a finding |
| 2026-11-21 | A1.2 filter F5 run. 793 of 905 survivors have no exact match |
| 2026-11-21 | Amendment A2 applied. 20 proposals, and a tradeoff it creates |
| 2026-11-21 | F6 forbids four of the catalogue's own ten transformations. Cost quantified |
| 2026-11-21 | Chemistry review settled from the literature, not by a chemist |
| 2026-11-21 | Manuscript figures 1 and 3 |
| 2026-11-24 | Submission package finalised |
| 2026-11-24 | Full read-through: one real error, and missing context added |
| 2026-11-25 | Sole authorship, and a final read-through |

---

## S3. Label-permuted validation

Blinding is not available for a computational analysis the analyst wrote. We substituted label permutation: the complete pipeline was run on data whose BBB labels had been shuffled, where the true effect is zero by construction. A pipeline that reports an effect there is reporting an artefact of its own design.

```
pipeline under test : confirmatory.py sha256 922efb8f8c28b3ef
manifests found     : 8
all same pipeline   : yes
gate requires       : 6 runs, >=100 draws, mean |dAUC| <= 0.02

    seed  draws  proximal  control      dAUC               95% CI  covers 0
       1    200    0.5318   0.5139   -0.0179   [-0.0845, +0.0546]       yes
       7    200    0.4726   0.4919   +0.0193   [-0.0472, +0.0863]       yes
      13    200    0.5072   0.4803   -0.0269   [-0.1002, +0.0426]       yes
      42    200    0.4703   0.5212   +0.0509   [-0.0192, +0.1181]       yes
      99    200    0.4774   0.4777   +0.0003   [-0.0613, +0.0645]       yes
     777    200    0.5234   0.4948   -0.0286   [-0.0955, +0.0356]       yes
    2024    200    0.4659   0.5159   +0.0500   [-0.0134, +0.1239]       yes
   31415    200    0.4804   0.4936   +0.0132   [-0.0581, +0.0766]       yes

mean dAUC +0.0075   sd 0.0317   SE 0.0112   t vs 0: +0.67
signs: 5 positive, 3 negative
intervals covering zero: 8/8

VERDICT: PASS - harness shows no effect on data containing none
The per-run spread (sd 0.0317) is dominated by the proximal arm, which is
measured on one fixed set of compounds and so varies with sd ~0.027 between
permutations. Individual runs therefore reach +0.0509 by chance alone; the
first four seeds run during development were all positive, averaging +0.030,
which looked like bias and was not (docs/decisions.md IC-5). The mean over
8 runs is the quantity that carries information, and it is +0.0075.
```

The gate is enforced in code, not by assertion: `scripts/gate.py` compares the SHA-256 of the pipeline under test against the manifests and refuses the confirmatory run unless the permuted runs pass. The confirmatory script could therefore execute exactly once, on real labels, after the harness had demonstrated it finds nothing in nothing.

---

## S4. Curation sensitivity

Ten curation variants, crossing assay-type pooling, activity threshold, target confidence score, assay format and skeleton deduplication. The headline out-of-domain percentages in the main text are the ranges across these variants, not a single curation's number.

```
B3DB labelled reference set: 3892 skeletons (130 discordant skeletons excluded)
  BBB+: 2472   BBB-: 1420

BACE1: out-of-domain % of target actives (no B3DB neighbour above cutoff)
variant                                         n     <0.3    <0.35     <0.4  median
PRIMARY  IC50+Ki, p>=6, conf9, B, dedup      5157    85.8%    97.5%    99.4%   0.252
pool      + confidence 8 (homologous)        6787    86.0%    97.2%    99.4%   0.250   drift  0.3pp
types     IC50 only                          4164    85.9%    97.5%    99.4%   0.250   drift  0.1pp
types     Ki only                            1177    83.6%    97.2%    99.3%   0.259   drift  2.2pp
types     + Kd                               5161    85.8%    97.5%    99.4%   0.252   drift  0.0pp
thresh    pChEMBL >= 5                       6500    81.8%    95.5%    98.6%   0.256   drift  4.0pp
thresh    pChEMBL >= 7                       3434    88.0%    98.6%    99.7%   0.250   drift  2.2pp
thresh    pChEMBL >= 8                       1336    89.4%    98.5%    99.5%   0.244   drift  3.6pp
assay     B + F + A                          5157    85.8%    97.5%    99.4%   0.252   drift  0.0pp
dedup     no skeleton dedup                  5590    85.5%    97.5%    99.4%   0.253   drift  0.3pp

AChE: out-of-domain % of target actives (no B3DB neighbour above cutoff)
variant                                         n     <0.3    <0.35     <0.4  median
PRIMARY  IC50+Ki, p>=6, conf9, B, dedup      2391    28.4%    58.3%    77.2%   0.333
pool      + confidence 8 (homologous)        2966    27.0%    55.1%    73.1%   0.341   drift  4.1pp
types     IC50 only                          2221    29.6%    59.2%    77.7%   0.333   drift  1.2pp
types     Ki only                             378    21.7%    54.5%    78.8%   0.342   drift  6.7pp
types     + Kd                               2399    28.3%    58.1%    77.0%   0.333   drift  0.2pp
thresh    pChEMBL >= 5                       3946    30.0%    59.4%    78.8%   0.333   drift  1.6pp
thresh    pChEMBL >= 7                       1243    31.7%    61.7%    79.3%   0.328   drift  3.4pp
thresh    pChEMBL >= 8                        475    36.4%    66.3%    83.4%   0.318   drift  8.1pp
assay     B + F + A                          2411    28.2%    57.9%    76.9%   0.333   drift  0.4pp
dedup     no skeleton dedup                  2470    28.3%    57.7%    76.6%   0.333   drift  0.6pp

Interpretation: the primary recipe is the first row; "drift" is the largest
change in any out-of-domain percentage relative to it. Small drift means the
curation decision is not load-bearing for this study's conclusion.

FEASIBILITY GATE under the primary recipe
Labelled B3DB compounds within each cutoff of target chemistry. This is the
sample available for measuring prediction error, and it sets the power.

--- BACE1 (n=5157 actives) ---
 cutoff      n   BBB+   BBB-   ratio    sufficient?
    0.3    364    240    124   1.9:1           PASS
   0.35     89     60     29   2.1:1           fail
    0.4     22     13      9   1.4:1           fail
    0.5      3      1      2   0.5:1           fail

--- AChE (n=2391 actives) ---
 cutoff      n   BBB+   BBB-   ratio    sufficient?
    0.3   1066    778    288   2.7:1           PASS
   0.35    492    366    126   2.9:1           PASS
    0.4    224    166     58   2.9:1           PASS
```

**The out-of-domain finding is not an artefact of curation choices.** Across every variant, the great majority of BACE1 actives and a large minority of AChE actives have no B3DB neighbour above the cutoff. The variant with the largest drift is the permissive pChEMBL ≥ 5 threshold, and it moves the BACE1 figure by 4.0 percentage points — from 85.8% to 81.8% out of domain, which does not change the conclusion.

---

## S5. Literature search record

Purpose: close the "possible scoop" risk recorded in `docs/decisions.md` before any
pre-registration is written. This file is the reproducible record of that search and
is intended to be reusable as the basis of a methods paragraph.

**Searched 2026-11-16.** Every citation below was verified against the Europe PMC
REST API by DOI or exact title; none are reported from a search-engine snippet alone.
One web-search result cited a PMC ID (`PMC13757966`) that does not resolve — the
paper is real but has no PMC record. Treat snippet-level identifiers as unverified.

### Queries run

Europe PMC REST API (`/webservices/rest/search`, `resultType=core`), which indexes
PubMed, PMC and preprint servers. Hit counts as of the search date.

| # | Query | Hits |
| --- | --- | --- |
| 1 | `TITLE:"blood-brain barrier" AND TITLE:"applicability domain"` | **0** |
| 2 | `(ABSTRACT/TITLE:"applicability domain") AND ABSTRACT:"blood-brain barrier"` | 18 |
| 3 | `ABSTRACT:"blood-brain barrier" AND ABSTRACT:"chemical space" AND (ABSTRACT:"coverage" OR ABSTRACT:"overlap")` | **0** |
| 4 | `(ABSTRACT:"BACE1" OR "beta-secretase") AND ABSTRACT:"blood-brain barrier" AND (ABSTRACT:"applicability domain" OR "chemical space")` | 2 |
| 5 | `ABSTRACT:"B3DB" OR TITLE:"B3DB"` | 19 |

Queries 2, 4 and 5 gave 35 unique records. **All 35 abstracts were read**, not
sampled — the candidate pool is small enough to inspect exhaustively. Four
adjacency risks were read in full; the one open-access full text
(`PMC13306079`) was pulled and inspected directly.

Web search was also run on four phrasings of the question (applicability domain +
BBB reliability; BBB predictors applied to BACE1/AChE; B3DB coverage vs target
series; AD + BBB filter + prediction error). It surfaced no additional candidates
beyond the above.

### Verdict: the specific question is unclaimed

No published work measures whether BBB predictors are valid for the chemistry they
are actually applied to in target-directed screening. Queries 1 and 3 returning
zero is the strongest single signal.

### The sharper finding

Every applicability-domain analysis found in this literature is run on the model's
**own held-out test set**, and each therefore reports reassuringly high coverage:

| Paper | AD coverage reported | Domain assessed on |
| --- | --- | --- |
| Pharmaceutics 2026, `10.3390/pharmaceutics18060670` | 93.9% in domain | own 212-compound test set |
| Pharmaceutics 2026, `10.3390/pharmaceutics18081018` | 94.8% in domain | own B3DB test split |
| Comput Biol Chem 2026, `10.1016/j.compbiolchem.2026.109356` | "complete structural coverage" | external ChEMBL set |

Because a held-out split is drawn from the training distribution, that ~94% figure
is close to guaranteed and says nothing about deployment. Our scoping number is the
inverse of it: **85.8% of BACE1 actives have no B3DB neighbour above Tanimoto 0.3.**

The contribution is therefore not "out-of-domain predictions are less accurate" —
that is established (see below) — but that the field reports domain coverage on a
population no screening pipeline ever encounters, while the population it does
encounter sits outside the domain.

### Key citations and how each is used

**Supporting the premise — the error penalty is real.**
`10.3390/pharmaceutics18060670` (Pharmaceutics 2026, B3DB logBB gradient boosting,
Williams-plot AD under OECD guidance) reports in-domain R² = 0.641 versus
out-of-domain R² = 0.164 on its 212-compound test set, and a ±1.35 × RMSE 90%
prediction interval stated as valid for in-domain compounds only. This is the
citation that makes the audit matter: it supplies the price of being out of domain,
on exactly our dataset. Caveat to state — the out-of-domain figure rests on 13
compounds.

**Closest methodological neighbour.**
`10.20944/preprints202609.2002.v1` (preprint, 2026) stratifies test compounds by
maximum Tanimoto similarity to training chemistry — our exact domain metric — but
within B3DB only. It also reports that skeleton-level deduplication collapses B3DB
from 7,802 to 3,952 compounds and exposes 131 skeletons with discordant BBB+/BBB−
labels. **Two consequences for us:** our B3DB curation must deduplicate on InChIKey
skeleton, not canonical SMILES (which finds only 3 duplicates); and the discordant
labels bear on the label-quality risk already logged. Preprint — not peer reviewed.

**Confirms the abandoned idea was rightly abandoned.** The same preprint plus
`10.3390/pharmaceutics18081018` now cover benchmark-inflation and split-sensitivity
on B3DB. The original plan is comprehensively occupied.

**Cuts against us — distance need not predict error.**
`10.1016/j.compbiolchem.2026.109356` found a 0.32–0.39 AUC generalisation gap whose
AD analysis showed *complete* structural coverage, concluding that out-of-domain
extrapolation did not explain the gap. This is direct evidence for the
"distance may not predict error" risk in `README.md`. It reinforces the existing
design constraint: measure error directly in AChE-proximal space; never infer error
from distance alone. It is also a useful precedent for the shape of our argument
(strong internal metrics, weak external reality) and should be cited, not buried.

**Independent support for the coverage problem.**
`10.1039/d6me00041j` (Jia & Sosso, *Mol. Syst. Des. Eng.* 2026) screened ~117M
PubChem compounds with a B3DB-trained random forest and attributes mid-range
probabilities to B3DB's limited chemical coverage. A real-world pipeline naming our
problem as a caveat, without quantifying it. Not open access.

### Residual risk

Low but non-zero. Europe PMC does not fully index ChemRxiv, bioRxiv chemistry or
the ACS/Wiley/RSC back catalogue at abstract level, and a scoop could sit in a
methods section of a paper whose abstract advertises something else — not
reachable by abstract search. Re-run queries 1 and 3 before submission.

### Actions for the pre-registration

1. Deduplicate B3DB on InChIKey skeleton; report the discordant-label count.
2. Frame the headline against the ~94% self-reported coverage figures above.
3. Pre-commit to measuring error directly in AChE space, with the
   `10.1016/j.compbiolchem.2026.109356` null result cited as the reason.
4. State that the overlap numbers in `README.md` are exploratory, pre-dating this.

---

## S6. Scaffold-filter sensitivity

Filter F6 requires the Bemis–Murcko scaffold to be retained. Applied strictly, it **forbids four of the ten transformations in the catalogue** — T01, T04, T09 and T10 — because each alters a ring and so changes the scaffold by definition. The registered protocol therefore contained a filter that rejected 40% of its own catalogue, a defect invisible at registration and revealed only by execution.

A labelled post hoc sensitivity re-ran the pipeline with F6 relaxed to ring-topology equivalence (Murcko generic scaffold), which permits the ring-altering edits.

| stage | F6 strict (registered) | F6 topology (post hoc) |
| --- | --- | --- |
| F6 scaffold retained | 38944 | 40460 |
| F7 inside property window | 4336 | 4858 |
| F8 PAINS-free | 3974 | 4474 |
| F4 SA ≤ 4.0 | 3860 | 4358 |
| unique structures | 2943 | 3185 |
| F2 in domain | 1116 | 1221 |
| F3 predicted BBB+ | 905 | 991 |

**The cost is 86 compounds — and the count understates it.** 62 of the 86 are products of T04, benzene → pyridine, which the chemistry review judged the single most valuable transformation in the catalogue: the aromatic N-walk lowers logP by roughly one unit, adds an acceptor, and commonly reduces hERG liability. The registered filter blocked the catalogue's best entry entirely. The remaining 24 come from T09. T01 and T10 contribute nothing either way — T01 was rejected on CNS grounds and T10 is a diagnostic (S1.1).

The registered strict rule governs every number reported in the main text. This sensitivity is labelled post hoc and is reported because the defect is part of the paper's argument about what pre-registration does and does not catch.

