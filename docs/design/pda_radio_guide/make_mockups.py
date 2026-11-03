"""Renders the Radio Feed and How to Play PDA mockups (panel 564x536 UI units, drawn at 2x).
Run: python make_mockups.py   -> concept_*.png and comparison_*.png in this folder."""
import os, re
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.dirname(os.path.abspath(__file__))
S = 2
W, H = 564, 536
F = "C:/Windows/Fonts/"
def font(sz, bold=False):
    return ImageFont.truetype(F + ("segoeuib.ttf" if bold else "segoeui.ttf"), int(sz * S))

BG = (20, 24, 29); PANEL = (29, 36, 44); HDR = (37, 44, 53); LINE = (44, 54, 64)
GOLD = (238, 196, 112); BLUE = (100, 200, 255); GREEN = (144, 238, 144); RED = (255, 100, 100)
TXT = (200, 200, 200); DIM = (138, 146, 156); ON = (74, 67, 38); ONB = (168, 144, 64)
COL = {"combat": RED, "exp": BLUE, "work": GREEN}


class Canvas:
    def __init__(self):
        self.im = Image.new("RGB", (W * S, H * S), BG)
        self.d = ImageDraw.Draw(self.im)

    def rect(self, x, y, w, h, fill, outline=None, left=None):
        self.d.rectangle([x * S, y * S, (x + w) * S - 1, (y + h) * S - 1], fill=fill, outline=outline)
        if left:
            self.d.rectangle([x * S, y * S, (x + left[1]) * S - 1, (y + h) * S - 1], fill=left[0])

    def text(self, x, y, s, sz=12, col=TXT, bold=False, anchor="l"):
        f = font(sz, bold)
        w = self.d.textlength(s, font=f) / S
        if anchor == "c": x = x - w / 2
        if anchor == "r": x = x - w
        self.d.text((x * S, y * S), s, font=f, fill=col)
        return w

    def rich(self, x, y, w, s, sz=12, lh=16, bold_all=False):
        """s uses {g}gold {b}blue {n}green {r}red {/} reset markup; wraps at width w; returns end y."""
        cols = {"g": GOLD, "b": BLUE, "n": GREEN, "r": RED, "d": DIM, "/": TXT}
        f = font(sz); fb = font(sz, True)
        cx, cy, col = x, y, TXT
        for line in s.split("\n"):
            for part in re.split(r"(\{[gbnrd/]\})", line):
                m = re.fullmatch(r"\{([gbnrd/])\}", part)
                if m: col = cols[m.group(1)]; continue
                for word in re.findall(r"\s*\S+|\s+", part):
                    ww = self.d.textlength(word, font=f) / S
                    if cx + ww > x + w and word.strip():
                        cx = x + 14 if line.startswith("-") else x; cy += lh; word = word.lstrip()
                        ww = self.d.textlength(word, font=f) / S
                    self.d.text((cx * S, cy * S), word, font=f, fill=col)
                    cx += ww
            col = TXT; cx = x; cy += lh
        return cy

    def btn(self, x, y, w, h, label, on=False, red=False, sz=12):
        self.rect(x, y, w, h, ON if on else (35, 42, 51), ONB if on else (56, 66, 78))
        c = GOLD if on else ((238, 28, 36) if red else (154, 163, 173))
        self.text(x + w / 2, y + (h - sz * 1.3) / 2, label, sz, c, on, "c")

    def header(self, title, col=GOLD):
        self.rect(0, 0, W, 24, HDR)
        self.d.line([0, 24 * S, W * S, 24 * S], fill=(58, 68, 82))
        self.text(W / 2, 3, title, 13, col, True, "c")

    def sec(self, x, y, w, label):
        self.rect(x, y, w, 22, (34, 42, 51), None, (GOLD, 3))
        self.text(x + 10, y + 3, label, 11.5, (230, 230, 230), True)

    def scroll(self, y, h, thumb_y, thumb_h):
        self.rect(W - 10, y, 10, h, (14, 17, 21), LINE)
        self.rect(W - 9, thumb_y, 8, thumb_h, (74, 85, 99))

    def note(self, label):
        self.rect(0, H - 18, W, 18, (14, 17, 21), LINE)
        self.text(8, H - 17, label, 10.5, (108, 117, 128))

    def save(self, name):
        self.im.save(os.path.join(OUT, name))


LOGS = [
    ("14:32", "combat", "COMBAT ALERT // DEFENSE", "Raiders approach Army Warehouses from the north. 4 hostiles. Defense 95 / 150."),
    ("14:20", "exp", "SCAVENGER // EXPEDITION", "Vasya returned from Garbage with 6 items and 2,400 RU."),
    ("13:55", "work", "SETTLEMENT // LOGISTICS", "Petrovich cooked 4 rations in the field kitchen."),
    ("13:41", "work", "SETTLEMENT // LOGISTICS", "Water purifier: 12 L pumped. Tank 80%."),
    ("13:10", "exp", "SCAVENGER // EXPEDITION", "Misha left for Cordon, ETA 40 min."),
    ("12:48", "combat", "COMBAT ALERT // DEFENSE", "Raid repelled. 3 raiders down, 1 settler wounded."),
    ("12:02", "work", "SETTLEMENT // LOGISTICS", "Sidor repaired 2 weapons at the repair bench."),
    ("11:30", "exp", "SCAVENGER // EXPEDITION", "Misha reached the Rostok checkpoint."),
    ("11:05", "work", "SETTLEMENT // LOGISTICS", "Timber: 5 logs cut, 2 charcoal burned."),
]
SHORT = {"combat": "DEF", "exp": "EXP", "work": "WRK"}


# ---------------------------------------------------------------- RADIO
def radio_A():
    c = Canvas(); c.header("SETTLEMENT RADIO FEED", BLUE)
    x = 4
    for i, (t, w) in enumerate([("All  9", 80), ("Expeditions  3", 104), ("Work  4", 80), ("Combat  2", 90)]):
        c.btn(x, 30, w, 26, t, i == 0); x += w + 2
    c.btn(x + 6, 30, 56, 26, "Scan"); c.btn(x + 64, 30, 56, 26, "Clear", red=True)
    c.sec(4, 60, 540, "TODAY")
    y = 86
    for t, cat, tag, txt in LOGS[:8]:
        two = len(txt) > 62
        h = 46 if two else 40
        c.rect(4, y, 540, h, PANEL, LINE, (COL[cat], 4))
        c.text(16, y + 3, tag, 10.5, COL[cat]); c.text(534, y + 3, t, 10.5, DIM, anchor="r")
        c.rich(16, y + 19, 516, txt, 12, 15)
        y += h + 3
    c.scroll(28, H - 46, 40, 130)
    c.note("A  Stripe cards: current card list + colour stripe, counts on filters, day dividers")
    c.save("radio_A.png")


def radio_B():
    c = Canvas(); c.header("SETTLEMENT RADIO FEED", BLUE)
    chans = [("ALL SETTLEMENTS", 9, 1), ("Army Warehouses", 5, 0), ("Rostok Outpost", 3, 0), ("Cordon Farm", 1, 0)]
    y = 30
    for n, k, a in chans:
        c.rect(4, y, 150, 30, ON if a else PANEL, ONB if a else LINE)
        c.text(12, y + 6, n, 11.5, GOLD if a else (176, 182, 189), a)
        c.text(146, y + 6, str(k), 11.5, DIM, anchor="r"); y += 33
    c.text(6, y + 8, "SHOW", 10, DIM); y += 26
    for lab, col in [("Expeditions", BLUE), ("Work", GREEN), ("Combat", RED)]:
        c.rect(8, y + 3, 13, 13, (35, 42, 51), ONB); c.text(10, y + 1, "x", 11, GOLD, True)
        c.text(28, y, lab, 12, col); y += 24
    c.btn(4, y + 14, 150, 26, "Scan Now"); c.btn(4, y + 44, 150, 26, "Clear Log", red=True)
    c.sec(162, 30, 382, "ALL SETTLEMENTS  -  LATEST FIRST")
    y = 56
    for t, cat, tag, txt in LOGS:
        two = len(txt) > 52
        h = 38 if two else 24
        c.d.line([162 * S, (y + h) * S, 544 * S, (y + h) * S], fill=(35, 43, 52))
        c.text(166, y + 3, t, 10.5, DIM)
        c.rect(200, y + 3, 28, 14, (22, 27, 33), COL[cat]); c.text(214, y + 3.5, SHORT[cat], 9, COL[cat], True, "c")
        c.rich(236, y + 2, 300, txt, 11.5, 14)
        y += h + 2
    c.scroll(28, H - 46, 36, 110)
    c.note("B  Channels: pick one settlement or all; compact rows; tick the types you want")
    c.save("radio_B.png")


def radio_C():
    c = Canvas(); c.header("SETTLEMENT RADIO FEED", BLUE)
    c.rect(4, 30, 540, 26, (58, 26, 26), (160, 48, 48))
    c.text(12, 34, "ALERT", 11.5, (255, 144, 144), True); c.text(60, 34, "14:32  Raiders approach Army Warehouses from the north", 11.5, (255, 170, 170))
    tiles = [("LAST RAID", "2 h ago", RED), ("EXPEDITIONS OUT", "2 scavengers", BLUE), ("LAST WORKSHOP", "13:55 cooked", GREEN), ("FEED", "9 reports", GOLD)]
    for i, (a, b, col) in enumerate(tiles):
        x = 4 + i * 136
        c.rect(x, 60, 132, 46, PANEL, LINE); c.text(x + 8, 63, a, 9.5, DIM); c.text(x + 8, 80, b, 14, col, True)
    x = 4
    for i, (t, w) in enumerate([("All", 70), ("Expeditions", 100), ("Work", 70), ("Combat", 76)]):
        c.btn(x, 112, w, 26, t, i == 0); x += w + 2
    c.btn(x + 56, 112, 56, 26, "Scan"); c.btn(x + 114, 112, 56, 26, "Clear", red=True)
    y = 144
    for t, cat, tag, txt in LOGS[:7]:
        two = len(txt) > 62
        h = 46 if two else 38
        c.rect(4, y, 540, h, (32, 26, 26) if cat == "combat" else (26, 32, 39), None, (COL[cat], 3))
        c.text(14, y + 2, t, 10.5, DIM); c.text(52, y + 2, tag.split(" // ")[0], 10.5, COL[cat], True)
        c.rich(14, y + 17, 520, txt, 12, 15)
        y += h + 2
    c.scroll(140, H - 158, 150, 100)
    c.note("C  Dispatch board: red alert banner + 4 summary tiles above the feed")
    c.save("radio_C.png")


# ---------------------------------------------------------------- GUIDE
def guide_A():
    c = Canvas(); c.header("HOW TO PLAY")
    x = 4
    for i, t in enumerate(["Start", "Build", "Settlers", "Defense", "Economy", "Setup"]):
        c.btn(x, 30, 88, 26, t, i == 0); x += 90
    c.sec(4, 60, 540, "1. ESTABLISHING A SETTLEMENT")
    y = c.rich(14, 90, 512,
        "{g}>> 1. PLACING A SETTLEMENT HUB{/}\n \n- {g}Settlement Flag:{/} Plant a HomesteadHF {b}Settlement Flag{/} (crafted at a workbench). It is the hub of your settlement, holds 300 kg of storage, and picking it up dismantles the settlement.\n- {g}Auto-Registration:{/} Placing the flag registers the location as an active hub.\n- {n}Zone Network:{/} up to {n}8 settlements{/} across any connected maps.\n \n{g}>> 2. TERRITORY & BOUNDARY RADIUS{/}\n \n- {g}Active Radius:{/} 50 m by default, 20 to 100 in MCM.\n- {g}Structure Recognition:{/} Beds, workbenches, stoves, clinics, chests, barricades and turrets inside it are linked automatically.\n \n{g}>> 3. SMART STORAGE & SUPPLY CHAINS{/}", 12.5, 17)
    c.btn(4, 488, 170, 28, "< Previous"); c.btn(188, 488, 188, 28, "Chapter 1 of 6   -   page 1 / 3"); c.btn(390, 488, 154, 28, "Next >", True)
    c.note("A  Chapter tabs: 6 groups, one page per screen with Next / Previous")
    c.save("guide_A.png")


def guide_B():
    c = Canvas(); c.header("HOW TO PLAY")
    idx = ["Start Here", "1  Settlement Hubs", "2  Building Kit", "3  Recruitment", "4  Professions", "     Guard", "     Scavenger", "     Cook", "     Medic", "5  Storage", "6  Raids", "7  Rivals", "8  Radio", "9  Morale & Needs", "10 MCM Options"]
    y = 30
    for i, n in enumerate(idx):
        a = i == 0
        c.rect(4, y, 150, 25, ON if a else (27, 33, 40), None, (GOLD if a else LINE, 3))
        c.text(14, y + 4, n.replace("     ", "   "), 12, GOLD if a else (168, 174, 182), a); y += 27
    c.scroll(28, H - 46, 36, 90)
    c.sec(162, 30, 372, "START HERE: 8 STEPS")
    c.rich(170, 62, 356,
        "1. Plant a {b}Settlement Flag{/} in a safe shelter.\n \n2. Place a {b}Storage Chest{/} inside the boundary.\n \n3. Place at least 2 {n}Sleeping Beds{/}.\n \n4. Build walls and a roof with the {b}Building Kit{/} (R rotates, G toggles snapping).\n \n5. Recruit friendly stalkers; they take the free beds.\n \n6. Assign jobs: guards first, then a cook.\n \n7. Add turrets and barricades for {n}Defense{/}.\n \n8. Check the Overview tab for morale and needs.", 12.5, 17)
    c.btn(162, 456, 180, 28, "< Prev topic"); c.btn(354, 456, 180, 28, "Next topic >", True)
    c.note("B  Index + reader: left list of topics, right shows only the picked one")
    c.save("guide_B.png")


def guide_C():
    c = Canvas(); c.header("HOW TO PLAY")
    c.sec(4, 30, 540, "QUICK START")
    c.rect(4, 56, 540, 82, PANEL, LINE)
    steps = ["1  Plant a Settlement Flag", "2  Place a Storage Chest", "3  Two Sleeping Beds", "4  Walls and roof", "5  Recruit stalkers", "6  Assign jobs", "7  Turrets, barricades", "8  Check Overview"]
    for i, s in enumerate(steps):
        x = 14 + (i // 4) * 270; y = 62 + (i % 4) * 18
        c.rect(x, y + 2, 11, 11, (35, 42, 51), ONB); c.text(x + 18, y - 1, s, 12.5, TXT)
    c.sec(4, 144, 540, "TOPICS  (click to read)")
    topics = [("Settlements", "hubs, radius"), ("Building", "kit, snapping"), ("Settlers", "beds, recruiting"), ("Jobs", "14 professions"), ("Storage", "routing, water"), ("Defense", "turrets, raids"),
              ("Rivals", "enemy camps"), ("Radio", "feed, filters"), ("Morale", "specs, savings"), ("Needs", "food, water"), ("Trade", "caravans"), ("MCM", "options")]
    for i, (a, b) in enumerate(topics):
        x = 4 + (i % 4) * 136; y = 172 + (i // 4) * 60
        c.rect(x, y, 132, 54, PANEL, LINE, (GOLD, 3)); c.text(x + 12, y + 8, a, 13, GOLD, True); c.text(x + 12, y + 30, b, 11, DIM)
    c.rect(4, 360, 540, 1, LINE)
    c.text(8, 368, "A topic opens its full text on one page, with a Back to topics button.", 11, DIM)
    c.note("C  Quick-start home: checklist first, 12 topic tiles open the long text")
    c.save("guide_C.png")


def compare(prefix, title, names):
    ims = [Image.open(os.path.join(OUT, f"{prefix}_{n}.png")) for n in names]
    pad = 16; hh = 56
    w = sum(i.width for i in ims) + pad * (len(ims) + 1)
    out = Image.new("RGB", (w, ims[0].height + hh + pad), (10, 12, 15))
    d = ImageDraw.Draw(out)
    d.text((pad, 14), title, font=ImageFont.truetype(F + "segoeuib.ttf", 28), fill=GOLD)
    x = pad
    for im in ims:
        out.paste(im, (x, hh)); x += im.width + pad
    out.save(os.path.join(OUT, f"comparison_{prefix}.png"))


if __name__ == "__main__":
    radio_A(); radio_B(); radio_C(); guide_A(); guide_B(); guide_C()
    compare("radio", "RADIO FEED  -  A: stripe cards   |   B: channels   |   C: dispatch board", "ABC")
    compare("guide", "HOW TO PLAY  -  A: chapter pages   |   B: index + reader   |   C: quick-start home", "ABC")
