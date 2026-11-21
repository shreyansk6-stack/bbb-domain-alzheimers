"""Render a manuscript markdown file to one self-contained HTML page.

Figures are embedded as base64 data URIs, so the output is a single file that
can be emailed or opened anywhere with no sibling assets. Reading only - it
never touches the manuscript source.

Usage: ./env/bin/python -I scripts/render_manuscript.py \
           [docs/manuscript.md] [docs/manuscript.html]
"""
import base64
import html
import mimetypes
import os
import re
import sys

import markdown

src = sys.argv[1] if len(sys.argv) > 1 else "docs/manuscript.md"
dst = sys.argv[2] if len(sys.argv) > 2 else "docs/manuscript.html"
text = open(src).read()

title = next((ln.lstrip("# ").strip() for ln in text.splitlines()
              if ln.startswith("# ")), os.path.basename(src))


def embed(path):
    if not os.path.exists(path):
        return None
    mime = mimetypes.guess_type(path)[0] or "image/png"
    with open(path, "rb") as fh:
        return f"data:{mime};base64," + base64.b64encode(fh.read()).decode()


# Figure callouts in this manuscript name their file in backticks; turn each
# into an actual inline figure so the rendered page shows what the text cites.
def figure_block(m):
    label, body, path, rest = m.group(1), m.group(2), m.group(3), m.group(4)
    uri = embed(path)
    caption = " ".join(f"**{label}** {body} {rest}".split())
    cap = markdown.markdown(caption)
    if uri is None:
        return f'<figure class="missing"><figcaption>{cap}<br>'\
               f'<em>missing: {html.escape(path)}</em></figcaption></figure>'
    return (f'<figure><img src="{uri}" alt="{html.escape(label)}">'
            f'<figcaption>{cap}</figcaption></figure>')


FIGS = []


def stash(m):
    """Replace a figure caption paragraph with a placeholder, holding the
    rendered <figure> aside so markdown does not mangle the embedded URI."""
    FIGS.append(figure_block(m))
    return f"\n\n@@FIG{len(FIGS) - 1}@@\n\n"


# A caption paragraph: **Figure N.** <text> (`results/....png`) <trailing text>
# The caption may wrap over several lines but never across a blank line.
CAPTION = re.compile(
    r"\*\*(Figure \d+\.)\*\*[ \t]*"
    r"((?:[^\n]|\n(?!\n))*?)"
    r"\(`(results/[^`]+\.png)`\)"
    r"((?:[^\n]|\n(?!\n))*)")

text = CAPTION.sub(stash, text)

body = markdown.markdown(
    text, extensions=["extra", "sane_lists", "toc", "attr_list"])
for i, fig in enumerate(FIGS):
    body = body.replace(f"<p>@@FIG{i}@@</p>", fig).replace(f"@@FIG{i}@@", fig)

CSS = """
:root{--ink:#14140f;--muted:#5c5b53;--rule:#e2e0d8;--bg:#fbfaf7;
--accent:#2a78d6;--note:#fff8e6;--note-br:#e8c96a;--code:#f2f1ec;}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){
--ink:#eceadf;--muted:#a8a69a;--rule:#34332d;--bg:#15151299;
--accent:#6da7ec;--note:#2a2516;--note-br:#6d5a1f;--code:#232219;}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
font:16px/1.62 Charter,"Iowan Old Style",Georgia,serif;}
main{max-width:46rem;margin:0 auto;padding:4rem 16px 7rem}
h1{font-size:1.95rem;line-height:1.22;letter-spacing:-.01em;margin:0 0 1.4rem}
h2{font-size:1.3rem;margin:3.2rem 0 .9rem;padding-bottom:.35rem;
border-bottom:1px solid var(--rule)}
h3{font-size:1.06rem;margin:2.2rem 0 .6rem;color:var(--ink)}
p,li{hyphens:auto}
a{color:var(--accent)}
blockquote{margin:1.6rem 0;padding:.9rem 1.1rem;background:var(--note);
border-left:3px solid var(--note-br);border-radius:0 4px 4px 0;font-size:.94rem}
blockquote p{margin:.35rem 0}
code{background:var(--code);padding:.12em .36em;border-radius:3px;
font:0.85em/1.4 ui-monospace,SFMono-Regular,Menlo,monospace}
table{border-collapse:collapse;width:100%;margin:1.5rem 0;font-size:.88rem;
display:block;overflow-x:auto}
th,td{text-align:left;padding:.5rem .7rem;border-bottom:1px solid var(--rule);
white-space:nowrap}
th{font-weight:600;border-bottom:2px solid var(--rule)}
tbody tr:last-child td{border-bottom:none}
figure{margin:2.4rem 0;padding:0}
figure img{width:100%;height:auto;display:block;border:1px solid var(--rule);
border-radius:5px;background:#fff}
figcaption{margin-top:.7rem;font-size:.86rem;color:var(--muted);line-height:1.5}
figcaption strong{color:var(--ink)}
hr{border:0;border-top:1px solid var(--rule);margin:2.6rem 0}
em{color:inherit}
ol[start]{padding-left:1.4rem}
@media print{body{background:#fff}main{padding:0;max-width:none}
figure img{border:none}h2{page-break-after:avoid}figure{page-break-inside:avoid}}
"""

out = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title><style>{CSS}</style></head>
<body><main>{body}</main></body></html>"""

open(dst, "w").write(out)
print(f"wrote {dst}  ({len(out) / 1024:.0f} KB, {len(FIGS)} figures embedded)")
