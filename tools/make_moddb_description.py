#!/usr/bin/env python3
"""Convert README.md into an HTML description for the ModDB mod page.

Usage:  python tools/make_moddb_description.py
Output: docs/moddb_description.html  (paste into ModDB's description box, HTML mode)

Stdlib only. Handles the Markdown subset the README uses (headings, lists, pipe
tables, blockquotes, code fences, rules, inline emphasis/links/images) and passes
the README's raw HTML blocks through. Relative paths are rewritten to GitHub:
images -> raw.githubusercontent.com, other files -> github.com/.../blob/main.
Any ?v=N cache-buster written in the README is kept as is.
"""
import html
import re
import sys
from pathlib import Path

REPO = "DamageZedd/Homestead-Stalker-Settlement-Builder"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
BLOB = f"https://github.com/{REPO}/blob/main/"

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.md"
DST = ROOT / "docs" / "moddb_description.html"


def is_relative(url):
    return not re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|//)", url, re.I)


def fix_img(url):
    return RAW + url.lstrip("./") if is_relative(url) else url


def fix_link(url):
    return BLOB + url.lstrip("./") if is_relative(url) else url


def fix_raw_html(s):
    """Rewrite relative src/href inside raw HTML lines."""
    s = re.sub(r'(src=")([^"]+)(")', lambda m: m[1] + fix_img(m[2]) + m[3], s)
    s = re.sub(r'(href=")([^"]+)(")', lambda m: m[1] + fix_link(m[2]) + m[3], s)
    s = re.sub(r"<div\s+align=\"center\">", "<center>", s)
    return s.replace("</div>", "</center>")


def esc_amp(s):
    return re.sub(r"&(?!#?\w+;)", "&amp;", s)


def inline(s):
    codes = []

    def stash(m):
        codes.append("<code>" + html.escape(m[1], quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, s)
    s = esc_amp(s)
    # linked image [![alt](img)](url), then plain image, then link
    s = re.sub(
        r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)",
        lambda m: f'<a href="{fix_link(m[3])}"><img src="{fix_img(m[2])}" alt="{m[1]}"></a>',
        s,
    )
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", lambda m: f'<img src="{fix_img(m[2])}" alt="{m[1]}">', s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: f'<a href="{fix_link(m[2])}">{m[1]}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<i>\1</i>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m[1])], s)


def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def convert(text):
    lines = text.replace("\r\n", "\n").split("\n")
    out = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        if line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(html.escape(lines[i], quote=False))
                i += 1
            i += 1
            out.append("<pre>" + "\n".join(buf) + "</pre>")
        elif line.lstrip().startswith("<"):
            buf = []
            while i < n and lines[i].strip():
                buf.append(fix_raw_html(lines[i]))
                i += 1
            out.append("\n".join(buf))
        elif m := re.match(r"^(#{1,6})\s+(.*)", line):
            lvl = len(m[1])
            out.append(f"<h{lvl}>{inline(m[2])}</h{lvl}>")
            i += 1
        elif re.match(r"^-{3,}\s*$", line):
            out.append("<hr>")
            i += 1
        elif line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(inline(lines[i][1:].strip()))
                i += 1
            out.append("<blockquote>" + "<br>\n".join(buf) + "</blockquote>")
        elif line.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = split_row(line)
            aligns = []
            for c in split_row(lines[i + 1]):
                aligns.append("center" if c.startswith(":") and c.endswith(":") else "right" if c.endswith(":") else "left")
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1

            def cell(tag, c, a):
                return f'<{tag} align="{a}">{inline(c)}</{tag}>'

            t = ['<table border="1" cellpadding="4">']
            t.append("<tr>" + "".join(cell("th", c, aligns[k]) for k, c in enumerate(head)) + "</tr>")
            for r in rows:
                t.append("<tr>" + "".join(cell("td", c, aligns[k]) for k, c in enumerate(r)) + "</tr>")
            t.append("</table>")
            out.append("\n".join(t))
        elif re.match(r"^(?:[-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\d+\.", line))
            tag = "ol" if ordered else "ul"
            items = []
            while i < n:
                m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)", lines[i])
                if m:
                    items.append([inline(m[1])])
                    i += 1
                    continue
                # indented continuation, possibly after one blank line
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and lines[j].startswith("  ") and items and not lines[j].strip().startswith(("-", "*")):
                    items[-1].append("<p>" + inline(lines[j].strip()) + "</p>")
                    i = j + 1
                else:
                    break
            lis = []
            for it in items:
                first, rest = it[0], "".join(it[1:])
                lis.append(f"<li>{first}{rest}</li>")
            out.append(f"<{tag}>\n" + "\n".join(lis) + f"\n</{tag}>")
        else:
            buf = []
            while i < n and lines[i].strip() and not re.match(r"^(#|```|>|\||<|-{3,}\s*$|(?:[-*]|\d+\.)\s)", lines[i]):
                buf.append(inline(lines[i].strip()))
                i += 1
            if not buf:  # unrecognised line: avoid an endless loop
                buf.append(inline(lines[i].strip()))
                i += 1
            out.append("<p>" + "<br>\n".join(buf) + "</p>")
    return "\n\n".join(out) + "\n"


def main():
    body = convert(SRC.read_text(encoding="utf-8"))
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(body, encoding="utf-8", newline="\n")
    print(f"wrote {DST.relative_to(ROOT)} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
