"""Carves the Hunter Station's custom pelt art out of the old atlas into one small dedicated texture.
usage: python -I pack_pelts.py atlas.dds tris.json out.png out_map.json
tris.json (from Blender): {"tris": [{"owner", "pos": [[x,y,z]..], "uv": [[u,v]..]}], ...} - the shipped triangles of the pelt
polygons with their atlas UVs. Triangles that share UV corners form islands; each island's pixel box (+pad) is cut from the
atlas and shelf-packed into a power-of-two sheet. out_map.json holds the new UV of every triangle corner."""
import json, sys
from PIL import Image

PAD = 6


def main(atlas, tris_json, out_png, out_map):
    im = Image.open(atlas).convert("RGB")
    W, H = im.size
    data = json.load(open(tris_json))
    tris = data["tris"]
    # union-find over triangles sharing a UV corner (rounded)
    parent = list(range(len(tris)))

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    seen = {}
    for i, t in enumerate(tris):
        for uv in t["uv"]:
            k = (round(uv[0] * W), round(uv[1] * H))
            if k in seen:
                parent[find(i)] = find(seen[k])
            else:
                seen[k] = i
    isl = {}
    for i in range(len(tris)):
        isl.setdefault(find(i), []).append(i)
    boxes = []
    for r, ids in isl.items():
        xs = [uv[0] * W for i in ids for uv in tris[i]["uv"]]
        ys = [(1 - uv[1]) * H for i in ids for uv in tris[i]["uv"]]       # image rows run top-down
        x0, x1 = max(0, int(min(xs)) - PAD), min(W, int(max(xs)) + PAD + 1)
        y0, y1 = max(0, int(min(ys)) - PAD), min(H, int(max(ys)) + PAD + 1)
        boxes.append((r, x0, y0, x1, y1))
    area = sum((b[3] - b[1]) * (b[4] - b[2]) for b in boxes)
    boxes.sort(key=lambda b: -(b[4] - b[2]))
    for side in (256, 512, 1024, 2048):
        for sh in (side, side * 2):
            x = y = row_h = 0; place = {}; ok = True
            for r, x0, y0, x1, y1 in boxes:
                w, h = x1 - x0, y1 - y0
                if w > side:
                    ok = False; break
                if x + w > side:
                    x = 0; y += row_h; row_h = 0
                if y + h > sh:
                    ok = False; break
                place[r] = (x, y); x += w; row_h = max(row_h, h)
            if ok:
                break
        if ok:
            break
    else:
        raise SystemExit("islands do not fit 2048x4096: %d px" % area)
    SW, SH = side, sh
    sheet = Image.new("RGB", (SW, SH), (96, 80, 64))
    newuv = {}
    for r, x0, y0, x1, y1 in boxes:
        px, py = place[r]
        sheet.paste(im.crop((x0, y0, x1, y1)), (px, py))
        for i in isl[r]:
            newuv[i] = [[(px + uv[0] * W - x0) / SW, 1 - (py + (1 - uv[1]) * H - y0) / SH] for uv in tris[i]["uv"]]
    sheet.save(out_png)
    json.dump({"size": [SW, SH], "uv": {str(i): v for i, v in newuv.items()}}, open(out_map, "w"))
    print("islands", len(boxes), "source px", area, "sheet", SW, SH)


if __name__ == "__main__":
    main(*sys.argv[1:5])
