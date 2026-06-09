# md_to_html.py  (part of the md-to-html skill)
# Convert a Markdown report to a single, self-contained HTML file.
#   - All local images are base64-embedded (no broken paths when emailing).
#   - LaTeX math ($...$ / $$...$$) rendered via MathJax v3 CDN.
#   - Tables, fenced code blocks, footnotes supported.
#
# Usage (from workspace root):
#   $env:PYTHONPATH='.'; .\.venv\Scripts\python.exe .agents/skills/md-to-html/scripts/md_to_html.py <input.md> <output.html>
#
# If output path is omitted, replaces the .md extension with .html in the same directory.

import sys
import re
import base64
import markdown
from pathlib import Path

# ── paths ─────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[4]   # workspace root (.agents/skills/md-to-html/scripts/ is 4 levels deep)

if len(sys.argv) >= 2:
    md_path = Path(sys.argv[1])
    if not md_path.is_absolute():
        md_path = ROOT / md_path
else:
    print("[ERROR] Please supply an input Markdown path as the first argument.")
    sys.exit(1)

if len(sys.argv) >= 3:
    out_path = Path(sys.argv[2])
    if not out_path.is_absolute():
        out_path = ROOT / out_path
else:
    out_path = md_path.with_suffix(".html")

if not md_path.exists():
    print(f"[ERROR] Input file not found: {md_path}")
    sys.exit(1)

# ── read markdown ─────────────────────────────────────────────────────────────
raw_md = md_path.read_text(encoding="utf-8")

# Strip YAML front-matter (---...---) if present
if raw_md.startswith("---"):
    end = raw_md.find("---", 3)
    if end != -1:
        raw_md = raw_md[end + 3:].lstrip()

# ── pre-process: embed images as base64 ──────────────────────────────────────
embedded_count = 0

def embed_image(match):
    global embedded_count
    alt  = match.group(1)
    path = match.group(2)

    # Skip already-embedded data URIs
    if path.startswith("data:"):
        return match.group(0)

    img_path = (md_path.parent / path).resolve()
    if img_path.exists():
        ext  = img_path.suffix.lower().lstrip(".")
        mime = {
            "png":  "image/png",
            "jpg":  "image/jpeg",
            "jpeg": "image/jpeg",
            "gif":  "image/gif",
            "svg":  "image/svg+xml",
        }.get(ext, "image/png")
        b64 = base64.b64encode(img_path.read_bytes()).decode()
        embedded_count += 1
        return f"![{alt}](data:{mime};base64,{b64})"
    else:
        print(f"  [WARN] Image not found: {img_path}")
        return match.group(0)

raw_md = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", embed_image, raw_md)

# ── convert Markdown -> HTML ──────────────────────────────────────────────────
extensions = [
    "tables",
    "fenced_code",
    "footnotes",
    "toc",
    "attr_list",
    "pymdownx.arithmatex",
]
extension_configs = {
    "pymdownx.arithmatex": {
        "generic": True,   # outputs \(...\) and \[...\] for MathJax v3
    },
}

body_html = markdown.markdown(
    raw_md,
    extensions=extensions,
    extension_configs=extension_configs,
)

# ── derive page title from filename ──────────────────────────────────────────
title = md_path.stem.replace("_", " ")

# ── full HTML shell ───────────────────────────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{title}</title>

  <!-- MathJax v3: renders \\( \\) inline and \\[ \\] display math -->
  <script>
    window.MathJax = {{
      tex: {{
        inlineMath:  [['\\\\(', '\\\\)']],
        displayMath: [['\\\\[', '\\\\]']],
      }},
      options: {{ skipHtmlTags: ['script','noscript','style','textarea','pre'] }},
    }};
  </script>
  <script async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js"></script>

  <style>
    *, *::before, *::after {{ box-sizing: border-box; }}
    html {{ font-size: 16px; }}
    body {{
      font-family: 'Segoe UI', Helvetica, Arial, sans-serif;
      line-height: 1.75;
      color: #1a1a2e;
      background: #f4f6fb;
      margin: 0;
      padding: 2rem 1rem;
    }}

    /* Paper */
    .paper {{
      max-width: 900px;
      margin: 0 auto;
      background: #ffffff;
      border-radius: 10px;
      box-shadow: 0 4px 32px rgba(0,0,0,0.10);
      padding: 3rem 4rem;
    }}

    /* Headings */
    h1 {{
      font-size: 1.9rem;
      font-weight: 700;
      color: #0d3b66;
      border-bottom: 3px solid #1a73e8;
      padding-bottom: .4rem;
      margin-bottom: 1.5rem;
    }}
    h2 {{
      font-size: 1.35rem;
      font-weight: 700;
      color: #1a3a5c;
      border-left: 4px solid #1a73e8;
      padding-left: .65rem;
      margin-top: 2.2rem;
    }}
    h3 {{
      font-size: 1.1rem;
      font-weight: 600;
      color: #2c5282;
      margin-top: 1.6rem;
    }}

    /* Text */
    p {{ margin: .75rem 0; }}
    ul, ol {{ padding-left: 1.6rem; }}
    li {{ margin: .3rem 0; }}
    strong {{ color: #0d3b66; }}
    hr {{ border: none; border-top: 1px solid #dce3f0; margin: 2.5rem 0; }}

    /* Tables */
    table {{
      width: 100%;
      border-collapse: collapse;
      font-size: .88rem;
      margin: 1.4rem 0;
      overflow-x: auto;
      display: block;
    }}
    thead tr {{ background: #1a73e8; color: #fff; }}
    thead th {{
      padding: .55rem .9rem;
      text-align: left;
      font-weight: 600;
      white-space: nowrap;
    }}
    tbody tr {{ border-bottom: 1px solid #e2e8f0; }}
    tbody tr:nth-child(even) {{ background: #f0f5ff; }}
    tbody td {{ padding: .45rem .9rem; vertical-align: top; }}

    /* Images */
    img {{
      max-width: 100%;
      height: auto;
      display: block;
      margin: 1.2rem auto;
      border-radius: 6px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.12);
    }}

    /* Code */
    code {{
      background: #eef2ff;
      border-radius: 4px;
      padding: .15em .4em;
      font-size: .9em;
      font-family: 'Courier New', monospace;
    }}
    pre code {{ background: none; padding: 0; }}
    pre {{
      background: #1e2a3a;
      color: #cdd6f4;
      border-radius: 6px;
      padding: 1rem 1.2rem;
      overflow-x: auto;
    }}

    /* Footer */
    .footer {{
      margin-top: 3rem;
      padding-top: 1rem;
      border-top: 1px solid #dce3f0;
      font-size: .78rem;
      color: #6b7280;
      text-align: center;
    }}

    /* Print */
    @media print {{
      body {{ background: #fff; padding: 0; }}
      .paper {{ box-shadow: none; padding: 1rem 1.5rem; }}
      a {{ color: inherit; text-decoration: none; }}
    }}
  </style>
</head>
<body>
  <div class="paper">
    {body_html}
    <div class="footer">
      Generated from <em>{md_path.name}</em> &mdash; NESDC Economic Research Unit
    </div>
  </div>
</body>
</html>
"""

# ── write output ──────────────────────────────────────────────────────────────
out_path.parent.mkdir(parents=True, exist_ok=True)
out_path.write_text(html, encoding="utf-8")

size_kb = out_path.stat().st_size / 1024
print(f"[OK] Self-contained HTML saved: {out_path.relative_to(ROOT)}")
print(f"     File size     : {size_kb:.1f} KB")
print(f"     Images embedded: {embedded_count}")
print(f"     MathJax       : yes (CDN)")
