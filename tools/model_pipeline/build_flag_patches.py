"""Build the per-faction settlement flag patch textures (512x512 DXT5 with alpha).

Each patch is the Wearable Devices faction patch, cropped to its artwork and centred in the
window of the texture that the flag's patch quad shows (WINDOW below, in 0..1 texture units,
v measured from the top). The flag script swaps these in at run time by the player's faction;
Factions of the Zone's own patch art is shown through the same window, as it is on the bracer.

usage: python -I build_flag_patches.py <out_dir> [<wd_patch_dir>]
"""
import os
import subprocess
import sys
import tempfile

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_dds  # noqa: E402

WD_PATCH_DIR = r"C:\GAMMA\mods\Wearable Devices\gamedata\textures\wd\bracer_rigid\customization\faction_patches"

# (flag name, Wearable Devices patch file); zombied is derived from the loner patch
PATCHES = [
    ("stalker", "patch_loners.dds"), ("bandit", "patch_bandits.dds"),
    ("csky", "patch_clearsky.dds"), ("dolg", "patch_duty.dds"),
    ("freedom", "patch_freedom.dds"), ("killer", "patch_merc.dds"),
    ("army", "patch_military.dds"), ("ecolog", "patch_ecolog.dds"),
    ("monolith", "patch_monolith.dds"), ("greh", "patch_sin.dds"),
    ("renegade", "patch_renegades.dds"), ("isg", "patch_isg.dds"),
]

# the part of the 512 texture the patch quad shows: u 0.02..0.82, v 0.10..0.90 from the top
WINDOW = (0.02, 0.10, 0.82, 0.90)
FILL = 0.96


def place(patch):
    """Crop a patch to its artwork and centre it in WINDOW on a transparent 512x512 sheet."""
    alpha = patch.getchannel("A").point(lambda p: 255 if p > 10 else 0)
    art = patch.crop(alpha.getbbox())
    box = int(round((WINDOW[2] - WINDOW[0]) * 512 * FILL))
    s = box / max(art.size)
    art = art.resize((max(1, round(art.width * s)), max(1, round(art.height * s))), Image.LANCZOS)
    out = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    cx = round((WINDOW[0] + WINDOW[2]) / 2 * 512)
    cy = round((WINDOW[1] + WINDOW[3]) / 2 * 512)
    out.paste(art, (cx - art.width // 2, cy - art.height // 2), art)
    return out


def zombied(loner):
    """The loner patch bleached and rotted, by make_flag_zombied.py, keeping the loner's outline."""
    with tempfile.TemporaryDirectory() as d:
        src, dst = os.path.join(d, "in.png"), os.path.join(d, "out.png")
        flat = Image.new("RGB", loner.size, (40, 40, 36))
        flat.paste(loner, (0, 0), loner)
        flat.save(src)
        subprocess.check_call([sys.executable, "-I", os.path.join(HERE, "make_flag_zombied.py"), src, dst])
        rot = Image.open(dst).convert("RGBA")
    rot.putalpha(loner.getchannel("A"))
    return rot


def main(out_dir, wd_dir=WD_PATCH_DIR):
    os.makedirs(out_dir, exist_ok=True)
    placed = {}
    for name, fn in PATCHES:
        placed[name] = place(Image.open(os.path.join(wd_dir, fn)).convert("RGBA"))
    placed["zombied"] = zombied(placed["stalker"])
    for name, im in placed.items():
        # transparent pixels carry the edge colour so mip levels do not bleed black into the rim
        a = np.asarray(im).copy()
        solid = a[..., 3] > 10
        if solid.any():
            a[~solid, :3] = a[solid, :3].mean(axis=0).astype(np.uint8)
        png = os.path.join(tempfile.gettempdir(), f"flag_patch_{name}.png")
        Image.fromarray(a).save(png)
        make_dds.main(png, os.path.join(out_dir, f"flag_patch_{name}.dds"), "DXT5")


if __name__ == "__main__":
    main(*sys.argv[1:3])
