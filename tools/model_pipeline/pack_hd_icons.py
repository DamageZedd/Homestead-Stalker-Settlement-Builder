"""Pack the HD icon renders (render_icons.py output) into DXT5 sheets and write the icon_override ltx.
usage: python -I pack_hd_icons.py <png_dir> <out_gamedata_dir>
Items come from HomesteadHF items_homestead_*.ltx (model basename -> <png_dir>/<model>.png).
The renders are 200 px per inventory cell (4x); inv_grid_* are in 50 px units of the sheet and
inv_grid_scale = 4 shrinks them back to the real cell size (HD Inventory Icons Framework)."""
import glob, math, os, re, subprocess, sys
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", ".."))
CELL, SCALE, SHEET_CELLS = 200, 4, 20      # 20 cells = 4000 px wide, inside a 4096 sheet


def items():
    out = []
    for f in sorted(glob.glob(os.path.join(REPO, "HomesteadHF/gamedata/configs/items/items/items_homestead_*.ltx"))):
        cur = None
        d = {}
        for l in open(f, encoding="cp1251", errors="replace"):
            m = re.match(r"\[(\w+)\]", l)
            if m:
                cur = m.group(1)
                d[cur] = {}
            elif cur and "=" in l:
                k, v = l.split("=", 1)
                d[cur][k.strip()] = v.split(";")[0].strip()
        for s, p in d.items():
            if "icons_texture" in p and "visual" in p:
                out.append((s, os.path.splitext(os.path.basename(p["visual"].replace("\\", "/")))[0],
                            int(p["inv_grid_width"]), int(p["inv_grid_height"])))
    return out


def main(png_dir, gd):
    its = items()
    models = {}
    for s, m, w, h in its:
        models.setdefault(m, (w, h))
    h4 = sorted([m for m, (w, h) in models.items() if h == 4])
    h3 = sorted([m for m, (w, h) in models.items() if h == 3], key=lambda m: (-models[m][0], m))
    h2_3 = sorted([m for m, (w, h) in models.items() if h == 2 and w == 3])
    h2_1 = sorted([m for m, (w, h) in models.items() if h == 2 and w < 3])
    h1 = sorted([m for m, (w, h) in models.items() if h == 1])
    order = h4 + h2_3[:10] + h3 + h2_3[10:] + h2_1 + h1
    sheets = []                     # 2D grid packing in cell units
    place = {}
    for m in order:
        w, h = models[m]
        for si, sh in enumerate(sheets):
            grid = sh["grid"]
            placed = False
            for y in range(SHEET_CELLS - h + 1):
                for x in range(SHEET_CELLS - w + 1):
                    if all(grid[y + dy][x + dx] == 0 for dy in range(h) for dx in range(w)):
                        for dy in range(h):
                            for dx in range(w):
                                grid[y + dy][x + dx] = 1
                        sh["y"] = max(sh["y"], y + h)
                        place[m] = (si, x, y)
                        placed = True
                        break
                if placed:
                    break
            if placed:
                break
        else:
            grid = [[0] * SHEET_CELLS for _ in range(SHEET_CELLS)]
            for dy in range(h):
                for dx in range(w):
                    grid[dy][dx] = 1
            sheets.append({"grid": grid, "y": h})
            place[m] = (len(sheets) - 1, 0, 0)
    tex_dir = os.path.join(gd, "textures", "ui")
    os.makedirs(tex_dir, exist_ok=True)
    for i, sh in enumerate(sheets):
        hpx = 1 << math.ceil(math.log2(sh["y"] * CELL))
        img = Image.new("RGBA", (4096, hpx), (0, 0, 0, 0))
        for m, (si, x, y) in place.items():
            if si == i:
                im = Image.open(os.path.join(png_dir, m + ".png")).convert("RGBA")
                w, h = models[m]
                assert im.size == (w * CELL, h * CELL), (m, im.size)
                img.paste(im, (x * CELL, y * CELL))
        png = os.path.join(png_dir, "sheet_hd_%d.png" % (i + 1))
        img.save(png)
        dds = os.path.join(tex_dir, "ui_icon_homestead_hd_%d.dds" % (i + 1))
        subprocess.check_call([sys.executable, "-I", os.path.join(HERE, "make_dds.py"), png, dds, "DXT5"])
        print(dds, img.size)
    cfg = os.path.join(gd, "configs", "icon_override")
    os.makedirs(cfg, exist_ok=True)
    lines = ["; HomesteadHF HD inventory icons for the HD Inventory Icons Framework.",
             "; Renders at %dx (%d px per cell); inv_grid_* are in 50 px sheet units, inv_grid_scale = %d." % (SCALE, CELL, SCALE), ""]
    for s, m, w, h in its:
        si, x, y = place[m]
        lines += ["[%s]" % s, "icons_texture = ui" + chr(92) + "ui_icon_homestead_hd_%d" % (si + 1),
                  "inv_grid_x = %d" % (x * SCALE), "inv_grid_y = %d" % (y * SCALE),
                  "inv_grid_width = %d" % (w * SCALE), "inv_grid_height = %d" % (h * SCALE),
                  "inv_grid_scale = %d" % SCALE, ""]
    open(os.path.join(cfg, "ico_homestead.ltx"), "w", newline="\r\n").write("\n".join(lines))
    open(os.path.join(cfg, "icon_override.ltx"), "w", newline="\r\n").write(
        ";imports any ltx in the same folder starting with ico_\n"
        ";ico_ ltx files should have a section that matches that of the item and have entries for:\n"
        ";icons_texture pointing to the new icon .dds\n"
        ";inv_grid_x and inv_grid_y pointing to the locaton in the file\n"
        ";inv_grid_height and inv_grid_height describing how many cells in the dds grid the icon uses.\n\n\n"
        '#include "ico_*.ltx"\n')


main(sys.argv[1], sys.argv[2])
