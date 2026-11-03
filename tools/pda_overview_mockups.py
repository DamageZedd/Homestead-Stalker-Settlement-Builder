"""Render design mockups of the PDA Overview detail panel (design aid only, not shipped).

Panel is 350 x 536 UI units (as in ui_stalker_camp_builder_pda.xml); drawn at 2x.
Usage: python tools/pda_overview_mockups.py [outdir]
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

S = 2
W, H = 350, 536
BG = (14, 17, 20)
CARD = (24, 29, 34)
HEAD = (38, 46, 54)
RULE = (62, 72, 80)
TXT = (200, 200, 200)
DIM = (140, 140, 140)
GOLD = (238, 196, 112)
GOOD = (144, 238, 144)
WARN = (238, 196, 80)
BAD = (238, 70, 70)
INFO = (100, 200, 255)

FONT = "C:/Windows/Fonts/arial.ttf"
FONTB = "C:/Windows/Fonts/arialbd.ttf"


def f(size, bold=False):
    return ImageFont.truetype(FONTB if bold else FONT, int(size * S))


class P:
    def __init__(self, w=W, h=H):
        self.im = Image.new("RGB", (w * S, h * S), BG)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x, y, w, h, fill=CARD, outline=RULE):
        self.d.rectangle([x * S, y * S, (x + w) * S, (y + h) * S], fill=fill, outline=outline)

    def text(self, x, y, s, col=TXT, size=11, bold=False, align="l", w=0):
        ft = f(size, bold)
        tw = self.d.textlength(s, font=ft)
        if align == "c":
            x = x + (w * S - tw) / 2 / S
        elif align == "r":
            x = x + (w * S - tw) / S
        self.d.text((x * S, y * S), s, font=ft, fill=col)

    def card(self, x, y, w, h, title=None, tcol=(220, 240, 255)):
        self.rect(x, y, w, h)
        if title:
            self.rect(x, y, w, 16, HEAD)
            self.text(x + 6, y + 2, title, tcol, 10, True)

    def bar(self, x, y, w, h, frac, col):
        self.rect(x, y, w, h, (10, 12, 14), RULE)
        self.d.rectangle([(x + 1) * S, (y + 1) * S, (x + 1 + (w - 2) * frac) * S, (y + h - 1) * S], fill=col)

    def btn(self, x, y, w, h, label, col=TXT, fill=(44, 52, 60)):
        self.rect(x, y, w, h, fill, RULE)
        self.text(x, y + (h - 12) / 2, label, col, 10.5, False, "c", w)

    def row(self, x, y, label, val, vcol=TXT, lw=92):
        self.text(x, y, label, DIM, 10)
        self.text(x + lw, y, val, vcol, 10.5)

    def save(self, path):
        self.im.save(path)


def header(p, y=0):
    p.rect(0, y, W, 38, CARD)
    p.text(0, y + 3, "Army Warehouses Settlement", GOLD, 13, True, "c", W)
    p.text(0, y + 21, "Region: Army Warehouses  |  Spec: Generic", DIM, 9.5, False, "c", W)


def buttons(p, y, compact=False):
    p.rect(0, y, W, 20 if not compact else 0 + 20, HEAD)
    p.text(8, y + 3, "COMMAND DIRECTIVES", GOLD, 10, True)
    y += 24
    p.btn(4, y, W - 8, 24, "Auto-Sort Stash")
    y += 28
    for a, b in (("Travel Here", "Show on Map"), ("Summon Trade Caravan", "Recall All Settlers"), ("Spec: Generic", "Rename")):
        p.btn(4, y, 168, 24, a)
        p.btn(178, y, 168, 24, b)
        y += 28
    p.btn(4, y, W - 8, 24, "Dismantle Camp", (255, 90, 90))


# ---------------------------------------------------------------- A: dashboard
def concept_a():
    p = P()
    header(p)
    # headline status strip
    p.rect(0, 42, W, 30, (52, 46, 22), WARN)
    p.text(0, 49, "SPAWN HAZARD  -  Defended", WARN, 13, True, "c", W)
    # four tiles
    tiles = [("SETTLERS", "15 / 17", GOLD), ("SECURITY", "95 / 150", INFO), ("MORALE", "100%", GOOD), ("NEEDS", "TIER 0", GOOD)]
    tw = 84
    for i, (a, b, c) in enumerate(tiles):
        x = i * (tw + 4.67)
        p.rect(x, 78, tw, 46)
        p.text(x, 83, a, DIM, 9, False, "c", tw)
        p.text(x, 99, b, c, 13, True, "c", tw)
    # bars
    p.card(0, 130, W, 128, "STATUS BARS")
    y = 152
    for lab, frac, col, val in (
        ("Bunks", 15 / 17, GOLD, "88%  (2 free)"),
        ("Security", 0.63, INFO, "63%  Defended"),
        ("Food", 0.8, GOOD, "6 days"),
        ("Water", 1.0, GOOD, "OK  2 pumps"),
        ("Storage", 0.04, INFO, "225 / 5150 kg"),
    ):
        p.text(8, y, lab, DIM, 10)
        p.bar(70, y + 1, 170, 12, frac, col)
        p.text(246, y, val, TXT, 9.5)
        y += 20
    # alert area
    p.card(0, 264, W, 52, "ALERTS")
    p.text(8, 284, "! Spawn hazard: mil_smart_terrain_7_8 (30 m)", WARN, 10)
    p.text(8, 298, "Threat level: ELEVATED   Perimeter: 10 walls, 1 guard, 4 turrets", DIM, 9)
    # compact order grid, 3 columns of small buttons
    p.rect(0, 322, W, 16, HEAD)
    p.text(8, 324, "ORDERS", GOLD, 10, True)
    y = 342
    names = [("Auto-Sort", ""), ("Travel", ""), ("Map", ""), ("Caravan", ""), ("Recall", ""), ("Spec", ""), ("Rename", ""), ("", ""), ("", "")]
    labels = ["Auto-Sort", "Travel", "Show Map", "Caravan", "Recall All", "Spec", "Rename"]
    bw = 110
    for i, lab in enumerate(labels):
        cx = (i % 3) * (bw + 10)
        cy = y + (i // 3) * 30
        p.btn(cx + 2, cy, bw, 26, lab)
    p.btn(2 + 2 * 120, y + 60, bw, 26, "Dismantle", (255, 90, 90))
    p.text(0, 440, "Needs row (when MCM on): Tier 1 THIN - food 2.1d, water 4d", DIM, 9, False, "c", W)
    return p


# ---------------------------------------------------------------- B: cards
def concept_b():
    p = P()
    header(p)
    # alert area, grows as needed
    p.rect(0, 42, W, 40, (52, 46, 22), WARN)
    p.text(8, 46, "ALERT  Spawn hazard 30 m inside perimeter", WARN, 11, True)
    p.text(8, 63, "Needs: Tier 1 THIN - 2 settlers hungry", WARN, 10)
    cw = 172
    gap = 6
    cards = [
        (0, 88, "PEOPLE", [("Settlers", "15 / 17", GOLD), ("Bunks free", "2", TXT), ("Occupancy", "88%", GOLD)]),
        (cw + gap, 88, "DEFENSE", [("Rating", "95 / 150", INFO), ("Level", "Defended", GOOD), ("Threat", "Elevated", WARN)]),
        (0, 178, "SUPPLIES", [("Food", "OK", GOOD), ("Water", "2 pumps OK", GOOD), ("Storage", "4% full", INFO)]),
        (cw + gap, 178, "MORALE", [("Morale", "100%", GOOD), ("Comfort", "High", GOOD), ("Needs", "Off / Tier 0", DIM)]),
    ]
    for x, y, t, rows in cards:
        p.card(x, y, cw, 84, t)
        yy = y + 22
        for a, b, c in rows:
            p.text(x + 6, yy, a, DIM, 10)
            p.text(x + 72, yy, b, c, 10.5)
            yy += 19
    # perimeter strip
    p.card(0, 268, W, 34)
    p.text(8, 272, "Perimeter", DIM, 10)
    p.text(8, 286, "10 barricades  |  1 guard  |  4 turrets", TXT, 10)
    # buttons: two columns
    p.rect(0, 308, W, 16, HEAD)
    p.text(8, 310, "ORDERS", GOLD, 10, True)
    y = 330
    p.btn(4, y, W - 8, 26, "Auto-Sort Stash")
    y += 30
    for a, b in (("Travel Here", "Show on Map"), ("Summon Caravan", "Recall Settlers"), ("Spec: Generic", "Rename")):
        p.btn(4, y, 168, 26, a)
        p.btn(178, y, 168, 26, b)
        y += 30
    p.btn(4, y, W - 8, 26, "Dismantle Camp", (255, 90, 90))
    return p


# ---------------------------------------------------------------- C: mini tabs
def tabbar(p, active):
    names = ["Status", "Defense", "Supplies", "Orders"]
    w = 84
    for i, n in enumerate(names):
        x = i * (w + 4.67)
        on = i == active
        p.rect(x, 42, w, 22, (60, 70, 50) if on else (30, 36, 42), GOLD if on else RULE)
        p.text(x, 46, n, GOLD if on else DIM, 10.5, on, "c", w)


def concept_c(tab):
    p = P()
    header(p)
    tabbar(p, tab)
    # always-visible one-line summary under the tabs
    p.rect(0, 68, W, 20, (30, 52, 34), GOOD)
    p.text(0, 71, "ALL CLEAR  |  15/17 settlers  |  Needs OK", GOOD, 10, False, "c", W)
    if tab == 0:
        p.card(0, 94, W, 110, "POPULATION")
        p.row(8, 116, "Settlers", "15 residents", GOLD)
        p.row(8, 134, "Bunks", "17 total, 2 free", TXT)
        p.bar(8, 152, 334, 12, 15 / 17, GOLD)
        p.text(8, 168, "Occupancy 88%", DIM, 9.5)
        p.card(0, 210, W, 94, "MORALE")
        p.row(8, 232, "Morale", "100%", GOOD)
        p.bar(8, 250, 334, 12, 1.0, GOOD)
        p.row(8, 270, "Comfort", "High", GOOD)
    elif tab == 1:
        p.card(0, 94, W, 120, "SECURITY")
        p.row(8, 116, "Rating", "95 / 150  (63%)", INFO)
        p.bar(8, 134, 334, 12, 0.63, INFO)
        p.row(8, 154, "Perimeter", "10 barricades", TXT)
        p.row(8, 172, "Guards", "1", TXT)
        p.row(8, 190, "Turrets", "4", TXT)
        p.card(0, 220, W, 70, "THREAT")
        p.row(8, 242, "Level", "Elevated", WARN)
        p.text(8, 262, "Spawn point mil_smart_terrain_7_8, 30 m", WARN, 9.5)
    elif tab == 2:
        p.card(0, 94, W, 190, "SUPPLIES")
        y = 116
        for lab, frac, col, val in (("Food", 0.8, GOOD, "6 days"), ("Water", 1.0, GOOD, "OK"), ("Storage", 0.04, INFO, "225/5150 kg")):
            p.text(8, y, lab, DIM, 10)
            p.bar(66, y + 1, 180, 12, frac, col)
            p.text(252, y, val, TXT, 9.5)
            y += 22
        p.rect(0, 190, W, 16, HEAD)
        p.text(8, 192, "LIVING NEEDS", GOLD, 10, True)
        p.row(8, 212, "Tier", "0  Fed", GOOD)
        p.row(8, 230, "Food", "6 days, variety 3/3", GOOD)
        p.row(8, 248, "Water", "OK", GOOD)
        p.row(8, 266, "Warnings", "none", DIM)
    else:
        p.card(0, 94, W, 160, "ORDERS")
        p.btn(4, 118, W - 8, 24, "Auto-Sort Stash")
        y = 146
        for a, b in (("Travel Here", "Show on Map"), ("Summon Caravan", "Recall Settlers"), ("Spec: Generic", "Rename")):
            p.btn(4, y, 168, 24, a)
            p.btn(178, y, 168, 24, b)
            y += 28
        p.btn(4, 262, W - 8, 24, "Dismantle Camp", (255, 90, 90))
    return p


def main():
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("docs/design/pda_overview")
    out.mkdir(parents=True, exist_ok=True)
    concept_a().save(out / "concept_A_dashboard.png")
    concept_b().save(out / "concept_B_cards.png")
    tabs = [concept_c(i).im for i in range(4)]
    sheet = Image.new("RGB", (W * S * 2 + 8, H * S // 2 + 8 + 0), BG)
    # C: show Status, Defense, Supplies, Orders side by side (cropped)
    crop_h = 310 * S
    sheet = Image.new("RGB", (W * S * 4 + 24, crop_h), (0, 0, 0))
    for i, im in enumerate(tabs):
        sheet.paste(im.crop((0, 0, W * S, crop_h)), (i * (W * S + 8), 0))
    sheet.save(out / "concept_C_tabs.png")
    # comparison sheet
    a, b = Image.open(out / "concept_A_dashboard.png"), Image.open(out / "concept_B_cards.png")
    c = tabs[0]
    cmp_ = Image.new("RGB", (W * S * 3 + 32, H * S), (0, 0, 0))
    for i, im in enumerate((a, b, c)):
        cmp_.paste(im, (i * (W * S + 16), 0))
    cmp_.save(out / "comparison.png")
    print("ok", out)


if __name__ == "__main__":
    main()
