# Cover letter — *Journal of Cheminformatics*

> Draft. `[AUTHORS]` marks the two decisions we cannot make for you: suggested
> reviewers, and the corresponding-author line. Everything else is ready to paste
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

**[AUTHORS: suggested reviewers — most systems ask for three or four. We have not
named any, since suggesting the authors of work the paper critiques is a judgement
call you should make, and we cannot verify current affiliations or addresses.]**

Thank you for your consideration.

Sincerely,

**[AUTHORS: corresponding author name, institutional email, postal address.]**

Shreyan Kancharla and Samuel Siyanbola
Davidson College, Davidson, North Carolina, USA
