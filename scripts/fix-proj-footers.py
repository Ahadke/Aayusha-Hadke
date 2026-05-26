import re
from pathlib import Path

path = Path(__file__).resolve().parent.parent / "portfolio.html"
html = path.read_text(encoding="utf-8")

link_svg = (
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">'
    '<path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6"/>'
    '<polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/>'
    "</svg>"
)

pat = re.compile(
    r'<div class="proj-card-footer"><div class="proj-tags">(.*?)</div>'
    r'(?:<div class="proj-card-meta"><p class="proj-card-note">(.*?)</p>\s*)?'
    r'<a href="([^"]+)"([^>]*)class="proj-github"([^>]*)><svg[\s\S]*?</svg></a></div></div>',
    re.DOTALL,
)


def repl(m: re.Match) -> str:
    tags, note, href, pre, post = m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)
    note_html = f'<p class="proj-card-note">{note}</p>\n                  ' if note else ""
    return (
        '<div class="proj-card-footer">\n'
        f'                <div class="proj-tags">{tags}</div>\n'
        '                <div class="proj-card-bottom">\n'
        f"                  {note_html}"
        f'<a href="{href}"{pre}class="proj-github"{post} aria-label="Open project repository">{link_svg}</a>\n'
        "                </div>\n"
        "              </div>"
    )


pat2 = re.compile(
    r'<div class="proj-card-footer"><div class="proj-tags">(.*?)</div>\s*'
    r'<a href="([^"]+)"([^>]*)class="proj-github"([^>]*)><svg[\s\S]*?</svg></a></div>',
    re.DOTALL,
)


def repl2(m: re.Match) -> str:
    tags, href, pre, post = m.group(1), m.group(2), m.group(3), m.group(4)
    return (
        '<div class="proj-card-footer">\n'
        f'                <div class="proj-tags">{tags}</div>\n'
        '                <div class="proj-card-bottom">\n'
        f'<a href="{href}"{pre}class="proj-github"{post} aria-label="Open project repository">{link_svg}</a>\n'
        "                </div>\n"
        "              </div>"
    )


new_html, n = pat.subn(repl, html)
new_html, n2 = pat2.subn(repl2, new_html)
print(f"replacements: {n} + {n2}")
path.write_text(new_html, encoding="utf-8")
