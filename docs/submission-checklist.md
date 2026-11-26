# Submission checklist — *Journal of Cheminformatics*

> **SUBMITTED 2026-11-25.** In Technical Check. See `docs/submission-record.md`
> for what was uploaded and the outstanding APC waiver deadline (2026-12-09).
> `docs/decisions.md` is frozen at 27 entries until revision.

Run `./env/bin/python -I scripts/check_consistency.py` before submitting. It
verifies every headline number in the manuscript, SI and cover letter against the
recorded result files and fails loudly on leftover placeholders.

---

## Ready

| | Item | File |
| --- | --- | --- |
| ✅ | Manuscript, formatted to the journal's structure | `docs/manuscript.md` |
| ✅ | Figures 1–3, verified 300 dpi | `results/fig{1,2,3}_*.png` |
| ✅ | Figure 4 (structures, → SI), 300 dpi via `scripts/make_fig4.py` | `results/design_proposals.png` |
| ✅ | Additional file 1 — Supplementary Information S1–S6 | `docs/supplementary.md` |
| ✅ | Additional file 2 — all 793 structures | `results/design_proposals.csv` |
| ✅ | Additional file 3 — decision log, 27 entries | `docs/decisions.md` |
| ✅ | Cover letter | `docs/cover-letter.md` |
| ✅ | APC waiver request | `docs/apc-waiver-request.md` |
| ✅ | Suggested reviewers — deliberately none; reasoning in the cover letter | — |
| ✅ | Declarations block (ethics, consent, competing interests, funding, AI use) | in manuscript |
| ✅ | Keywords (8) | in manuscript |
| ✅ | References, all DOIs Crossref-verified 2026-11-21; every one cited in text, gated by `check_consistency.py` | in manuscript |
| ✅ | Corresponding author + ORCID `0009-0009-8654-110X` (verified) | cover letter |
| ✅ | ORCID on the title block, verified against the public record | in manuscript |
| ✅ | Pre-registration public | [10.17605/OSF.IO/UQR62](https://doi.org/10.17605/OSF.IO/UQR62) |
| ✅ | Code and data manifests public | GitHub repo |

## Waiting on

Nothing. **The paper is single-author as of 2026-11-25** — the prospective second
author made no contribution and asked not to be included, and was removed from the
OSF contributor list. The contributions statement, declarations, cover letter and
waiver request were all rewritten to match. The §4.4 limitation on
medicinal-chemistry review stands and is now the only honest reading: the catalogue
assessment is literature-grounded reasoning by the author, not bench judgement.

## Do at submission, in this order

1. Run **`./env/bin/python -I scripts/finalize_submission.py`**. It runs the
   consistency check, and only if that passes does it write
   `docs/manuscript-submission.md` — the draft banner stripped, verified free of
   placeholders. If the check fails it writes nothing.
2. Upload **`docs/manuscript-submission.md`**, three figures, three additional
   files. `docs/manuscript.md` stays as the working draft; never upload it.
3. **Submit the APC waiver request in the waiver field.** BMC will not consider
   a request made during review or after acceptance. This is the one step that
   cannot be undone later.
4. Enter the ORCID `0009-0009-8654-110X`. Single author — add no co-author.
5. Paste the cover letter.

## Notes

- **In-text citations are author–year; the reference list is numbered.** Springer
  Nature accepts format-free initial submission, so this can be reconciled at
  revision rather than now.
- **§3.9 is a summary**; the full design component is in SI S1. If a reviewer asks
  for it in the main text, the material is written and can be moved back.
- **The §4.4 limitation on medicinal-chemistry review is permanent.** No chemist
  reviewed the catalogue; `docs/catalogue-review.md` is literature-grounded
  reasoning by the author. Do not soften it.
- Two working copies exist: `~/Documents/bbb-domain-alzheimers` (original, was
  TCC-blocked) and `~/Desktop/bbb-domain-alzheimers` (clone, current). Everything
  is pushed to GitHub; `git pull` in the original once file access is restored,
  then delete whichever copy you do not want.
