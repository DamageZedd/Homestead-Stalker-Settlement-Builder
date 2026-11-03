#!/usr/bin/env python3
"""Convert README.md into the styled HTML description for the ModDB mod page.

Usage:  python tools/make_moddb_description.py
Output: docs/moddb_description.html  (paste into ModDB's description box, HTML/source mode)

Stdlib only. The README is parsed into blocks (headings, paragraphs, lists, pipe tables,
raw HTML hero tables, code, quotes) and rendered with the dark "stalker" card design used
on the ModDB page (inline styles only, ModDB's editor strips classes and <style>).
Relative paths are rewritten to GitHub: images -> raw.githubusercontent.com, other files
-> github.com/.../blob/main. Any ?v=N cache-buster written in the README is kept as is.
"""
import html
import re
import sys
from pathlib import Path

REPO = "DamageZedd/Homestead-Stalker-Settlement-Builder"
RAW = f"https://raw.githubusercontent.com/{REPO}/main/"
BLOB = f"https://github.com/{REPO}/blob/main/"
REPO_URL = f"https://github.com/{REPO}"

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "README.md"
DST = ROOT / "docs" / "moddb_description.html"

# "New in" items rendered with a FIXED badge instead of NEW
FIXED_TITLES = re.compile(r"fix|rival camps", re.I)

GOLD, GREEN, ORANGE, SAND, TEXT_GOLD = "#e0a43c", "#8fae5a", "#d9663a", "#b9a572", "#e0c478"
CARD = ("padding: 20px; margin: 14px 0; background-color: #1f1d17; border: 1px solid #4a4333; "
        "box-shadow: inset 0 1px 0 rgba(255,236,190,0.06), 0 3px 12px rgba(0,0,0,0.3);")
CARD_GREEN = CARD.replace("border: 1px solid #4a4333;", f"border: 1px solid #4a4333; border-top: 3px solid {GREEN};")
CARD_ORANGE = CARD.replace("border: 1px solid #4a4333;", f"border: 1px solid #4a4333; border-left: 4px solid {ORANGE};")
CARD_AMBER = ("padding: 20px; margin: 14px 0; background-color: #2b2012; border: 1px solid #5a4d33; "
              f"border-left: 4px solid {GOLD}; box-shadow: 0 3px 12px rgba(0,0,0,0.3);")
CARD_WARN = ("padding: 18px 20px; margin: 14px 0; background-color: #2b2012; border: 1px solid #5a4d33; "
             f"border-left: 4px solid {ORANGE}; box-shadow: 0 3px 12px rgba(0,0,0,0.3);")
ROW = ("padding: 12px 14px; margin: 8px 0; background-color: #171510; border: 1px solid #332d20; "
       f"border-left: 3px solid {GOLD};")
IMG = "max-width: 100%; border: 1px solid #4a4333;"


def is_relative(url):
    return not re.match(r"^(?:[a-z][a-z0-9+.-]*:|#|//)", url, re.I)


def fix_img(url):
    return RAW + url.lstrip("./") if is_relative(url) else url


def fix_link(url):
    return BLOB + url.lstrip("./") if is_relative(url) else url


def esc_amp(s):
    return re.sub(r"&(?!#?\w+;)", "&amp;", s)


def span(color, text, extra=""):
    return f'<span style="color: {color};{extra}">{text}</span>'


def inline(s):
    codes = []

    def stash(m):
        codes.append('<code style="background-color: #14130f; padding: 1px 5px;">'
                     + html.escape(m[1], quote=False) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    s = re.sub(r"`([^`]+)`", stash, s)
    s = esc_amp(s)
    s = re.sub(
        r"\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)",
        lambda m: f'<a href="{fix_link(m[3])}"><img src="{fix_img(m[2])}" alt="{m[1]}" style="{IMG}"></a>', s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)",
               lambda m: f'<img src="{fix_img(m[2])}" alt="{m[1]}" style="{IMG}">', s)
    s = re.sub(r"\[((?:[^\[\]]|\[[^\[\]]*\])+)\]\(([^)]+)\)",
               lambda m: f'<a href="{fix_link(m[2])}" style="color: {GOLD};">{m[1]}</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m[1])], s)


def plain(s):
    """Inline markdown stripped to text, for titles."""
    s = re.sub(r"\[((?:[^\[\]]|\[[^\[\]]*\])+)\]\([^)]+\)", r"\1", s)
    return re.sub(r"[*`]", "", s).strip()


def title_text(s):
    """Heading text without leading emoji, uppercased."""
    return esc_amp(re.sub(r"^[^\w(]+", "", plain(s)).upper())


# --------------------------------------------------------------------------- parsing

def split_row(line):
    return [c.strip() for c in line.strip().strip("|").split("|")]


def parse_blocks(text):
    lines = text.replace("\r\n", "\n").split("\n")
    blocks = []
    i, n = 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
        elif line.startswith("```"):
            i += 1
            buf = []
            while i < n and not lines[i].startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1
            blocks.append(("code", "\n".join(buf)))
        elif line.lstrip().startswith("<"):
            buf = []
            while i < n and lines[i].strip():
                buf.append(lines[i])
                i += 1
            blocks.append(("html", "\n".join(buf)))
        elif m := re.match(r"^(#{1,6})\s+(.*)", line):
            blocks.append(("h", (len(m[1]), m[2])))
            i += 1
        elif re.match(r"^-{3,}\s*$", line):
            blocks.append(("hr", None))
            i += 1
        elif line.startswith(">"):
            buf = []
            while i < n and lines[i].startswith(">"):
                buf.append(lines[i][1:].strip())
                i += 1
            blocks.append(("quote", buf))
        elif line.startswith("|") and i + 1 < n and re.match(r"^\|[\s:|-]+\|\s*$", lines[i + 1]):
            head = split_row(line)
            i += 2
            rows = []
            while i < n and lines[i].startswith("|"):
                rows.append(split_row(lines[i]))
                i += 1
            blocks.append(("table", (head, rows)))
        elif re.match(r"^(?:[-*]|\d+\.)\s+", line):
            ordered = bool(re.match(r"^\d+\.", line))
            items = []
            while i < n:
                m = re.match(r"^(?:[-*]|\d+\.)\s+(.*)", lines[i])
                if m:
                    items.append([m[1]])
                    i += 1
                    continue
                j = i
                while j < n and not lines[j].strip():
                    j += 1
                if j < n and lines[j].startswith("  ") and items and not lines[j].strip().startswith(("-", "*")):
                    items[-1].append(lines[j].strip())
                    i = j + 1
                else:
                    break
            blocks.append(("list", (ordered, items)))
        else:
            buf = []
            while i < n and lines[i].strip() and not re.match(r"^(#|```|>|\||<|-{3,}\s*$|(?:[-*]|\d+\.)\s)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            if not buf:
                buf.append(lines[i].strip())
                i += 1
            blocks.append(("para", buf))
    return blocks


# --------------------------------------------------------------------------- rendering

def hero_card(fragment):
    """One image + bold title + small caption, from a README <td>/<p> fragment."""
    img = re.search(r'<img[^>]*?src="([^"]+)"[^>]*?alt="([^"]*)"', fragment)
    if not img:
        return ""
    bold = re.search(r"<b>(.*?)</b>(.*?)(?:<br>|$)", fragment, re.S)
    sub = re.search(r"<sub>(.*?)</sub>", fragment, re.S)
    out = f'<img src="{fix_img(img[1])}" alt="{img[2]}" style="{IMG}">'
    if bold:
        out += f"<br><strong>{span(GOLD, bold[1])}</strong>{bold[2]}"
    if sub:
        out += "<br>" + span(SAND, sub[1].strip(), " font-size: 12px;")
    return f'<div style="{CARD}"><p>{out}</p></div>'


def render_html_block(raw):
    if re.match(r"^\s*</?div", raw):
        return ""
    if "<table" in raw:
        cells = re.findall(r"<td[^>]*>(.*?)</td>", raw, re.S)
        return "\n".join(hero_card(c) for c in cells if "<img" in c)
    if "<img" in raw:
        parts = [x for x in re.split(r"(?<=</p>)", raw) if "<img" in x]
        return "\n".join(hero_card(x) for x in parts)
    return raw


def render_table(head, rows):
    out = []
    if len(rows) > 1:  # one row per entry: name, description, extra columns
        for r in rows:
            name = r[0]
            new = "🆕" in name
            name = re.sub(r"\s*🆕", "", name)
            parts = [f"<strong>{span(GREEN if new else GOLD, title_text(name))}</strong>"]
            if len(r) > 1:
                parts.append(span("#d9d2bc", inline(r[1]), " font-size: 13px;"))
            for extra in r[2:]:
                if extra and extra != "—":
                    parts.append(span(SAND, inline(extra), " font-size: 11px;"))
            out.append(f'<div style="{ROW}">' + "<br>".join(parts) + "</div>")
    else:  # header row holds the names, single data row the values
        row = rows[0]
        parts = []
        for h, v in zip(head, row):
            parts.append(f"<strong>{span(GOLD, title_text(h))}</strong><br>"
                         + span("#d9d2bc", inline(v), " font-size: 13px;"))
        out.append(f'<div style="{ROW}">' + "<br>".join(parts) + "</div>")
    return "\n".join(out)


def render_para(lines):
    text = " ".join(lines)
    if m := re.match(r"^\*\*(Tab \d+ [—-] .+?)\.?\*\*\s*(.*)$", text):
        return (f"<p><strong>{span(TEXT_GOLD, title_text(m[1]))}</strong><br>{inline(m[2])}</p>")
    return "<p>" + "<br>\n".join(inline(l) for l in lines) + "</p>"


def render_list(ordered, items):
    tag = "ol" if ordered else "ul"
    lis = []
    for it in items:
        lis.append("<li>" + inline(it[0]) + "".join("<p>" + inline(x) + "</p>" for x in it[1:]) + "</li>")
    return f"<{tag}>\n" + "\n".join(lis) + f"\n</{tag}>"


def render_block(kind, data):
    if kind == "html":
        return render_html_block(data)
    if kind == "h":
        lvl, t = data
        return f"<p><strong>{span(GOLD, title_text(t), ' font-size: 17px;')}</strong></p>"
    if kind == "hr":
        return ""
    if kind == "para":
        return render_para(data)
    if kind == "list":
        return render_list(*data)
    if kind == "table":
        return render_table(*data)
    if kind == "code":
        return ('<pre style="background-color: #14130f; border: 1px solid #332d20; padding: 10px;">'
                + html.escape(data, quote=False) + "</pre>")
    if kind == "quote":
        return "<blockquote>" + "<br>".join(inline(l) for l in data) + "</blockquote>"
    return ""


def h2(text):
    return (f'<h2><span style="color: {GOLD}; font-size: 20px; letter-spacing: 2px;">'
            f"{title_text(text)}</span></h2>")


def render_header(pre):
    html_raw = "\n".join(d for k, d in pre if k == "html")
    sub = re.search(r"<sub>(.*?)</sub>", html_raw, re.S)
    h1 = next((d[1] for k, d in pre if k == "h" and d[0] == 1), "")
    h3 = next((d[1] for k, d in pre if k == "h" and d[0] == 3), "")
    tagline = next((" ".join(d) for k, d in pre if k == "para" and d[0].startswith("*") and "http" not in d[0]), "")
    badges = next((" ".join(d) for k, d in pre if k == "para" and "img.shields.io" in " ".join(d)), "")
    links = next((" ".join(d) for k, d in pre if k == "para" and d[0].startswith("**[")), "")
    version = re.search(r"badge/version-(v[\d.]+)-", badges)
    author = re.search(r"badge/by-(.+?)-", badges)

    chips = ""
    if version:
        chips += (f'<span style="display: inline-block; padding: 3px 14px; background-color: {GOLD}; '
                  f'color: #14130f; font-weight: bold; font-size: 13px; letter-spacing: 1px;">{version[1]}</span><br>')
    if author:
        chips += (f'<span style="display: inline-block; padding: 3px 14px; border: 1px solid {GOLD}; '
                  f'color: {GOLD}; font-size: 13px; letter-spacing: 1px;">BY '
                  f'{author[1].replace("__", "_").upper()}</span>')

    buttons = [(t, u) for t, u in re.findall(r"\[([^\]]+)\]\(([^)]+)\)", links) if "moddb.com" not in u]
    buttons.append(("GitHub", REPO_URL))
    btn = []
    for k, (t, u) in enumerate(buttons):
        solid = k == 0
        style = ("display: inline-block; padding: 8px 20px; margin: 4px 6px; font-weight: bold; "
                 "text-decoration: none; letter-spacing: 1px; "
                 + (f"background-color: {GOLD}; color: #14130f; border: 1px solid #f1c46e;" if solid
                    else f"background-color: transparent; color: {GOLD}; border: 1px solid {GOLD};"))
        btn.append(f'<a href="{fix_link(u)}" style="{style}">{t.upper()}</a>')

    return (
        '<div style="padding: 28px 22px; margin: 0 0 14px 0; text-align: center; background-color: #221f17; '
        'background-image: linear-gradient(180deg, rgba(224,164,60,0.18), rgba(0,0,0,0.25)); '
        f'border: 1px solid #5a4d33; border-bottom: 3px solid {GOLD}; box-shadow: 0 3px 14px rgba(0,0,0,0.4);">'
        f"<p>{sub[1] if sub else ''}</p>"
        f'<p><strong><span style="font-size: 40px; letter-spacing: 3px; color: #f4e8c8;">{title_text(h1)}</span></strong></p>'
        f'<p><span style="font-size: 15px; letter-spacing: 3px; color: {GOLD};">{title_text(h3)}</span></p>'
        f"<p>{inline(plain(tagline))}</p>"
        f"<p>{chips}</p>"
        f"<p><br>{'<br>'.join(btn)}</p></div>"
    )


def render_new_in(title, blocks):
    out = [f'<div style="{CARD_GREEN}">', f'<h2><span style="color: {GREEN}; font-size: 22px; letter-spacing: 2px;">'
           f"{title_text(title)}</span></h2>"]
    items, cur = [], None
    for k, d in blocks:
        if k == "h":
            cur = [d[1], []]
            items.append(cur)
        elif cur is not None and k != "hr":
            cur[1].append((k, d))
    parts = []
    for t, body in items:
        fixed = bool(FIXED_TITLES.search(t))
        badge = (f'<span style="display: inline-block; padding: 2px 10px; background-color: {GREEN}; color: #14130f; '
                 f'font-weight: bold; font-size: 12px; letter-spacing: 1px;">{"FIXED" if fixed else "NEW"}</span>')
        parts.append(f"<p>{badge} <strong>{span(GOLD, title_text(t), ' font-size: 17px;')}</strong></p>"
                     + "\n".join(render_block(k, d) for k, d in body))
    out.append("<hr>".join(parts))
    out.append("</div>")
    return "\n".join(out)


def render_section(title, blocks):
    low = title.lower()
    style = CARD_AMBER if "required" in low else CARD_ORANGE if "combat" in low else CARD
    body = "\n".join(x for x in (render_block(k, d) for k, d in blocks) if x)
    return f'<div style="{style}">{h2(title)}\n{body}</div>'


def convert(text):
    blocks = parse_blocks(text)
    first = next(i for i, (k, d) in enumerate(blocks) if k == "h" and d[0] == 2)
    pre, rest = blocks[:first], blocks[first:]

    sections, cur = [], None
    for k, d in rest:
        if k == "h" and d[0] == 2:
            cur = [d[1], []]
            sections.append(cur)
        else:
            cur[1].append((k, d))

    warn = next(((k, d) for k, d in pre if k == "quote"), None)
    intro = [d for k, d in pre if k == "para" and not d[0].startswith(("*", "!["))
             and "http" not in d[0]]

    out = ['<div style="max-width: 940px; margin: 0 auto; padding: 22px; background-color: #14130f; '
           'background-image: linear-gradient(180deg, #1c1a14 0%, #14130f 40%, #12110d 100%); color: #d9d2bc; '
           'font-family: Arial, sans-serif; font-size: 14px; line-height: 1.5; overflow-wrap: anywhere;">']
    out.append(render_header(pre))
    for title, body in sections:
        if title.lower().startswith("🆕") or "new in" in title.lower():
            out.append(render_new_in(title, body))
    if warn:
        first_line, *others = warn[1]
        out.append(f'<div style="{CARD_WARN}"><p><strong>{span("#f08a5d", inline(first_line).replace("<strong>", "").replace("</strong>", ""), " letter-spacing: 1px;")}</strong></p>'
                   f'<p>{inline(" ".join(others))}</p></div>')
    if intro:
        out.append(f'<div style="{CARD}">' + "".join(f"<p>{inline(p[0])}</p>" for p in intro) + "</div>")
    for title, body in sections:
        if "new in" in title.lower():
            continue
        out.append(render_section(title, body))
    out.append("</div>")
    return tighten("\n".join(out)) + "\n"


# ModDB turns every newline in the description into a <br> and keeps the browser's default block
# margins, which opens big gaps. So the output is one line (newlines kept only inside <pre>, as <br>)
# and the block tags carry small explicit margins.
TIGHT = [
    ("<p>", '<p style="margin: 0 0 8px 0;">'),
    ("<ul>", '<ul style="margin: 4px 0 8px 0; padding-left: 22px;">'),
    ("<ol>", '<ol style="margin: 4px 0 8px 0; padding-left: 22px;">'),
    ("<li>", '<li style="margin: 0 0 3px 0;">'),
    ("<h2>", '<h2 style="margin: 0 0 10px 0;">'),
    ("<hr>", '<hr style="margin: 12px 0;">'),
    ("<blockquote>", '<blockquote style="margin: 4px 0 8px 0;">'),
]


def tighten(s):
    # ModDB escapes the description's ampersands itself, so a written-out &amp; shows up literally
    s = s.replace("&amp;", "&")
    parts = re.split(r"(<pre\b.*?</pre>)", s, flags=re.S)
    for i, part in enumerate(parts):
        if i % 2:
            parts[i] = part.replace("\n", "<br>")
            continue
        part = part.replace("<p><br></p>", "").replace("<p><br>", "<p>").replace("<br>\n", "<br>")
        part = re.sub(r"\n+", "", part)
        for old, new in TIGHT:
            part = part.replace(old, new)
        parts[i] = part
    return "".join(parts)


def main():
    body = convert(SRC.read_text(encoding="utf-8"))
    DST.parent.mkdir(parents=True, exist_ok=True)
    DST.write_text(body, encoding="utf-8", newline="\n")
    print(f"wrote {DST.relative_to(ROOT)} ({len(body)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
