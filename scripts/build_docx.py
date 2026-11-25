"""Produce the Word files the submission system requires, via pandoc.

Springer Nature's Snapp platform accepts only an editable manuscript — Word or
LaTeX — with figures and tables in the body of the text. The project writes
Markdown, so this converts it, rather than anyone hand-editing a .docx that
would then drift from the gated source.

Figures are embedded under their captions: 1-3 in the manuscript, 4 in the
supplementary file, which is where the manuscript says it belongs. The image
paths are stripped from the caption text once the image itself is in place.

Refuses to run unless scripts/check_consistency.py passes, for the same reason
finalize_submission.py does: nothing leaves this repo unverified.

Usage: ./env/bin/python -I scripts/build_docx.py
"""
import re
import subprocess
import sys
from pathlib import Path

OUT = Path("docs/submission")

# (source, output, {figure path: caption prefix to anchor it to})
JOBS = [
    ("docs/manuscript-submission.md", "manuscript.docx",
     ["results/fig1_chemical_space.png",
      "results/fig2_forest.png",
      "results/fig3_domain_definitions.png"]),
    ("docs/supplementary.md", "Additional_file_1_supplementary.docx", []),
    ("docs/decisions.md", "Additional_file_3_decision_log.docx", []),
]


# Figure 4 belongs with S1 per the manuscript, and S1.5 is the table whose first
# six rows it draws. The SI text never names the image, so it is placed here.
FIG4_ANCHOR = "### S1.6 The superseded ranking"
FIG4 = """![](results/design_proposals.png)

**Figure 4.** Representative domain-constrained design products beside their
parent compounds, changed atom highlighted. The six pairs are rows 1-6 of the
table above, in the same order.

"""


def embed_figures(text, figures):
    """Put each image above its caption and drop the path from the prose."""
    for path in figures:
        # the caption names the file in backticks, sometimes mid-sentence
        pat = re.compile(r"\s*\(`" + re.escape(path) + r"`\)")
        if not pat.search(text):
            if path not in text:
                continue
        text = pat.sub("", text)
        # anchor: the **Figure N.** paragraph that mentioned it
        n = re.search(r"fig(\d)_", path)
        label = f"**Figure {n.group(1)}.**" if n else "**Figure 4.**"
        if label in text:
            text = text.replace(label, f"![]({path})\n\n{label}", 1)
    return text


def main():
    r = subprocess.run([sys.executable, "-I", "scripts/check_consistency.py"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stdout[-2000:])
        sys.exit("consistency check FAILED - not writing Word files")
    print("consistency check:", r.stdout.strip().splitlines()[-1])

    OUT.mkdir(parents=True, exist_ok=True)
    for src, out, figures in JOBS:
        text = embed_figures(Path(src).read_text(), figures)
        if src.endswith("supplementary.md"):
            if FIG4_ANCHOR not in text:
                sys.exit(f"could not place Figure 4: {FIG4_ANCHOR!r} not found")
            text = text.replace(FIG4_ANCHOR, FIG4 + FIG4_ANCHOR, 1)
        tmp = OUT / (Path(src).stem + ".pandoc.md")
        tmp.write_text(text)
        dst = OUT / out
        subprocess.run(
            ["pandoc", str(tmp), "-f", "gfm+tex_math_dollars", "-t", "docx",
             "--resource-path=.", "--standalone", "-o", str(dst)],
            check=True)
        tmp.unlink()
        kb = dst.stat().st_size // 1024
        print(f"wrote {dst}  ({kb} KB)")

    print()
    print(f"Upload the files in {OUT}/. The Markdown stays the source of truth.")


if __name__ == "__main__":
    main()
