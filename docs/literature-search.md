# Systematic literature search

Purpose: close the "possible scoop" risk recorded in `docs/decisions.md` before any
pre-registration is written. This file is the reproducible record of that search and
is intended to be reusable as the basis of a methods paragraph.

**Searched 2026-11-16.** Every citation below was verified against the Europe PMC
REST API by DOI or exact title; none are reported from a search-engine snippet alone.
One web-search result cited a PMC ID (`PMC13757966`) that does not resolve — the
paper is real but has no PMC record. Treat snippet-level identifiers as unverified.

## Queries run

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

## Verdict: the specific question is unclaimed

No published work measures whether BBB predictors are valid for the chemistry they
are actually applied to in target-directed screening. Queries 1 and 3 returning
zero is the strongest single signal.

## The sharper finding

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

## Key citations and how each is used

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

## Residual risk

Low but non-zero. Europe PMC does not fully index ChemRxiv, bioRxiv chemistry or
the ACS/Wiley/RSC back catalogue at abstract level, and a scoop could sit in a
methods section of a paper whose abstract advertises something else — not
reachable by abstract search. Re-run queries 1 and 3 before submission.

## Actions for the pre-registration

1. Deduplicate B3DB on InChIKey skeleton; report the discordant-label count.
2. Frame the headline against the ~94% self-reported coverage figures above.
3. Pre-commit to measuring error directly in AChE space, with the
   `10.1016/j.compbiolchem.2026.109356` null result cited as the reason.
4. State that the overlap numbers in `README.md` are exploratory, pre-dating this.
