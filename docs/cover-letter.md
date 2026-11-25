# Cover letter — *Journal of Cheminformatics*

> Draft. One decision left: suggested reviewers. Everything else is ready to paste
> into the submission system.

---

Dear Editors,

We submit for your consideration **"Applicability domain of blood–brain barrier
predictors in Alzheimer's target chemical space: a methods audit and
domain-constrained design."**

A standard Alzheimer's virtual-screening pipeline ranks compounds for predicted
target activity and then filters the hits through a published blood–brain barrier
model. The first stage receives intense methodological scrutiny; the second is
treated as a commodity. We asked whether that BBB filter is being applied inside its
own applicability domain, and found the question had not been asked: a systematic
Europe PMC search (five queries, 35 candidate records, all abstracts read, recorded
in full in the repository) returned no study measuring BBB-model domain coverage
against target inhibitor chemistry.

**We should state plainly that our pre-registered primary endpoint is inconclusive.**
Prediction degradation on target-proximal chemistry was ΔAUC +0.028, 95% CI
[−0.016, +0.075], against a registered support threshold of 0.06 and a minimum
detectable effect of 0.061. We report it as "no degradation larger than
approximately 0.06 AUC," never as no degradation.

We submit the paper because the surrounding analyses are, we think, the more
consequential result, and because each is a finding about *method* rather than about
effect size:

- **Published applicability-domain coverage figures are correct and uninformative.**
  Three recent reports (from two groups) give 93.9%, 94.8% and "complete structural
  coverage" — all computed on held-out splits of the training distribution, where
  high coverage follows by construction. Measured instead against the chemistry the
  filter is deployed on, 81.8–89.4% of BACE1 actives and 21.7–36.4% of AChE actives
  fall outside the domain.
- **Roughly half of a naively measured domain effect is physicochemical
  confounding.** An unmatched random control gives +0.055; a propensity-matched
  control on MW, cLogP and TPSA gives +0.028. Studies using unmatched controls will
  overstate domain effects.
- **Two standard domain definitions are the same statistic.** Mahalanobis distance
  and leverage select *identical* compound sets (Jaccard 1.000) once descriptors are
  centred on the target mean, while scaffold membership is very nearly disjoint from
  both (0.010). Reporting them as independent corroboration is an error.
- **For BACE1 the question cannot be asked at all**, and **no off-the-shelf BBB tool
  can be independently evaluated**, because the available tools are trained on the
  only available public ground truth. These are limits on what public data can
  currently support, and we think the field should know them.

The study was pre-registered on OSF Registries before analysis
([10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62)), with the analysis
pipeline SHA-256 gated so the confirmatory script could run exactly once, and
label-permutation validation standing in for blinding. All code, the registration
with its amendments, a dated decision log and every result file are public.

One section may interest you beyond the cheminformatics. **Pre-registration
constrained our analytic flexibility as intended, but did not prevent us from
registering a design protocol that was internally inconsistent.** Execution revealed
three defects invisible at registration: a ranking rule that selected *against* the
novelty it was meant to ensure, a novelty filter not executable as written, and a
structural filter that forbade 40% of its own transformation catalogue — including
the single most valuable transformation in it. We report all three, with their
downstream costs quantified, rather than silently repairing them. We are not aware
of this failure mode being documented in cheminformatics, and we think registered
computational protocols need a dry-run requirement that registered clinical
protocols effectively get for free.

The work fits the journal's stated interest in detailed evaluations of computational
tools and benchmarking frameworks. It is original, is not under consideration
elsewhere, and all authors have approved the submission. We declare no competing
interests.

**Funding and APC.** This research received no specific grant from any funding
agency in the public, commercial or not-for-profit sectors; no compound reported was
synthesised or assayed, and all costs were computational. The work was conducted by
undergraduate authors without grant support or an institutional open-access fund
covering fully open-access BMC titles. **We therefore request an article processing
charge waiver on grounds of financial need, and make this request at submission as
your policy requires.**

**[AUTHORS: suggested reviewers — see the note at the end of this file.]**

Thank you for your consideration.

Sincerely,

**Shreyan Kancharla**, corresponding author
Davidson College, Davidson, NC 28035, USA
shkancharla@davidson.edu
ORCID: [0009-0009-8654-110X](https://orcid.org/0009-0009-8654-110X)

on behalf of the authors: Shreyan Kancharla and Samuel Siyanbola.

---

## Note on suggested reviewers

Most submission systems ask for three or four, with name, institution and email.
They are suggestions only; the editor is free to ignore them, and naming someone
does not mean they will be asked.

Reasonable sources for this paper:

- **Applicability-domain methodology.** Authors of recent AD or model-validation
  work in *J Cheminform* or *JCIM*. This is the closest fit to what the paper
  argues.
- **BBB permeability modelling.** Authors of B3DB-based models — but note the paper
  argues such models cannot currently be evaluated without contamination, so expect
  a sharp review.
- **Benchmarking and reproducibility in cheminformatics**, which is where the
  pre-registration argument in §4.3 would be judged most fairly.

**The authors of the three coverage papers we cite (Tiwari et al. 2026a, 2026b;
Prabhakar et al. 2026) are a judgement call.** They know the specific literature
better than anyone, and the paper's point is that their coverage figures are
measured on the training distribution — which is a methodological criticism, not an
attack on their work. Some editors welcome the suggestion; some authors would
review it fairly and some would not. We have not named them.

Whoever is chosen, verify the current affiliation and institutional email on the
publisher's page for their most recent paper — stale contact details are a common
reason suggestions are dropped.
