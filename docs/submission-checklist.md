# Submission checklist — *Journal of Cheminformatics*

Run `./env/bin/python -I scripts/check_consistency.py` before submitting. It
verifies every headline number in the manuscript, SI and cover letter against the
recorded result files and fails loudly on leftover placeholders.

---

## Ready

| | Item | File |
| --- | --- | --- |
| ✅ | Manuscript, formatted to the journal's structure | `docs/manuscript.md` |
| ✅ | Figures 1–3, 300 dpi | `results/fig{1,2,3}_*.png` |
| ✅ | Figure 4 (structures, → SI) | `results/design_proposals.png` |
| ✅ | Additional file 1 — Supplementary Information S1–S6 | `docs/supplementary.md` |
| ✅ | Additional file 2 — all 793 structures | `results/design_proposals.csv` |
| ✅ | Additional file 3 — decision log, 24 entries | `docs/decisions.md` |
| ✅ | Cover letter | `docs/cover-letter.md` |
| ✅ | APC waiver request | `docs/apc-waiver-request.md` |
| ✅ | Declarations block (ethics, consent, competing interests, funding, AI use) | in manuscript |
| ✅ | Keywords (8) | in manuscript |
| ✅ | References, all DOIs Crossref-verified 2026-11-21 | in manuscript |
| ✅ | Corresponding author + ORCID `0009-0009-8654-110X` (verified) | cover letter |
| ✅ | Pre-registration public | [10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62) |
| ✅ | Code and data manifests public | GitHub repo |

## Waiting on

| | Item | Who |
| --- | --- | --- |
| ⬜ | **Sam's ORCID** — requested, not yet received | S.S. |
| ⬜ | **Sam reads and approves the manuscript** — the contributions statement says he critically revised it, which is not yet true | S.S. |
| ⬜ | **Suggested reviewers**, 3–4 with institution and email | S.K. |
| ⬜ | Confirm postal address / campus box | S.K. |

## Do at submission, in this order

1. **Delete the DRAFT banner** at the top of the manuscript.
2. Re-run `scripts/check_consistency.py`. It must pass.
3. Upload manuscript, three figures, three additional files.
4. **Submit the APC waiver request in the waiver field.** BMC will not consider
   a request made during review or after acceptance. This is the one step that
   cannot be undone later.
5. Enter both ORCIDs.
6. Paste the cover letter, with suggested reviewers filled in.

## Notes

- **In-text citations are author–year; the reference list is numbered.** Springer
  Nature accepts format-free initial submission, so this can be reconciled at
  revision rather than now.
- **§3.9 is a summary**; the full design component is in SI S1. If a reviewer asks
  for it in the main text, the material is written and can be moved back.
- **The §4.4 limitation on medicinal-chemistry review** can be softened only if
  Sam genuinely works through `docs/catalogue-review.md`. If he does, tell Claude
  and both that limitation and the contributions line should be revised.
- Two working copies exist: `~/Documents/bbb-domain-alzheimers` (original, was
  TCC-blocked) and `~/Desktop/bbb-domain-alzheimers` (clone, current). Everything
  is pushed to GitHub; `git pull` in the original once file access is restored,
  then delete whichever copy you do not want.
