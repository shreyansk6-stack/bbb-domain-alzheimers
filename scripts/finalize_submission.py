"""Produce the submission-ready manuscript from the working draft.

The working draft carries a DRAFT banner of notes to the authors. Rather than
rely on anyone remembering to delete it, this writes a separate clean copy and
leaves the draft untouched, so the thing you upload is generated rather than
edited.

Refuses to produce output if the consistency check fails, or if anything that
looks like an unresolved placeholder survives into the clean copy.

Usage: ./env/bin/python -I scripts/finalize_submission.py
"""
import re
import subprocess
import sys

SRC = "docs/manuscript.md"
DST = "docs/manuscript-submission.md"

print("running consistency check ...")
r = subprocess.run([sys.executable, "-I", "scripts/check_consistency.py"],
                   capture_output=True, text=True)
if r.returncode != 0:
    print(r.stdout[-2000:])
    sys.exit("consistency check FAILED - not writing a submission copy")
print("  " + r.stdout.strip().splitlines()[-1])

text = open(SRC).read()

# Drop the leading blockquote banner: the run of '>' lines after the header.
clean, n = re.subn(r"\n> \*\*DRAFT.*?(?=\n\n(?!>))", "", text, count=1,
                   flags=re.S)
if n != 1:
    sys.exit("could not find the DRAFT banner - check the manuscript header")
clean = re.sub(r"\n{3,}", "\n\n", clean)

for pat, why in [(r"\[AUTHORS", "an [AUTHORS] marker"),
                 (r"\bDRAFT\b", "the word DRAFT"),
                 (r"\bTODO\b", "a TODO"),
                 (r"XXX|FIXME", "a placeholder")]:
    if re.search(pat, clean):
        sys.exit(f"submission copy still contains {why}")

open(DST, "w").write(clean)
print(f"wrote {DST}")
print(f"  {len(clean.split())} words, banner removed, no placeholders")
print()
print("Upload this file. docs/manuscript.md stays as the working draft.")
