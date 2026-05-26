"""Restructure project card footers: note above, tags + link in proj-card-actions row."""
import re
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "index.html"
text = p.read_text(encoding="utf-8")

pat_note = re.compile(
    r'(<div class="proj-card-footer">\s*)'
    r'<div class="proj-tags">(.*?)</div>\s*'
    r'<div class="proj-card-bottom">\s*'
    r'(<p class="proj-card-note">.*?</p>)\s*'
    r'(<a href="[^"]+"[^>]*class="proj-github"[^>]*>.*?</a>)\s*'
    r'</div>\s*</div>',
    re.DOTALL,
)
text, n1 = pat_note.subn(
    r"\1\3\n"
    r"                <div class=\"proj-card-actions\">\n"
    r"                <div class=\"proj-tags\">\2</div>\n"
    r"                  \4\n"
    r"                </div>\n"
    r"              </div>",
    text,
)

pat_plain = re.compile(
    r'(<div class="proj-card-footer">\s*)'
    r'<div class="proj-tags">(.*?)</div>\s*'
    r'<div class="proj-card-bottom">\s*'
    r'(<a href="[^"]+"[^>]*class="proj-github"[^>]*>.*?</a>)\s*'
    r'</div>\s*</div>',
    re.DOTALL,
)
text, n2 = pat_plain.subn(
    r"\1"
    r'<div class="proj-card-actions">\n'
    r"                <div class=\"proj-tags\">\2</div>\n"
    r"                  \3\n"
    r"                </div>\n"
    r"              </div>",
    text,
)

print("note", n1, "plain", n2)
if n1 + n2 != 8:
    raise SystemExit(f"expected 8 cards, got {n1 + n2}")
p.write_text(text, encoding="utf-8")
