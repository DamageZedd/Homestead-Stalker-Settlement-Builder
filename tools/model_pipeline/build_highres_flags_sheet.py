import os
import sys
import numpy as np
from PIL import Image, ImageFilter

REPO_ROOT = r"C:\Users\hocke\OneDrive\Documents\GitHub\Homestead-Stalker-Settlement-Builder\.claude\worktrees\laughing-turing-46d9eb"
WD_PATCH_DIR = r"C:\GAMMA\mods\Wearable Devices\gamedata\textures\wd\bracer_rigid\customization\faction_patches"
VTEX_DIR = r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures"
OUT_TEX_DIR = os.path.join(REPO_ROOT, r"HomesteadHF\gamedata\textures\homestead_hf")

FACTIONS = [
    # (name, col, row, patch_file)
    ('stalker', 0, 0, 'patch_loners.dds'),
    ('bandit', 1, 0, 'patch_bandits.dds'),
    ('csky', 2, 0, 'patch_clearsky.dds'),
    ('dolg', 3, 0, 'patch_duty.dds'),
    ('freedom', 0, 1, 'patch_freedom.dds'),
    ('killer', 1, 1, 'patch_merc.dds'),
    ('army', 2, 1, 'patch_military.dds'),
    ('ecolog', 3, 1, 'patch_ecolog.dds'),
    ('monolith', 0, 2, 'patch_monolith.dds'),
    ('greh', 1, 2, 'patch_sin.dds'),
    ('renegade', 2, 2, 'patch_renegades.dds'),
    ('isg', 3, 2, 'patch_isg.dds'),
    ('zombied', 0, 3, None),
    ('base', 1, 3, None),
]

def build_sheet():
    print("Building 2048x2048 high-resolution settlement flags sheet...")
    canvas_path = os.path.join(VTEX_DIR, r"prop\prop_brezent.dds")
    canvas_base = Image.open(canvas_path).convert("RGBA").resize((512, 512), Image.Resampling.LANCZOS)
    
    # Master sheet
    sheet = Image.new("RGBA", (2048, 2048), (50, 50, 45, 255))
    
    p_size = int(512 * 0.74) # ~378px
    offset_x = (512 - p_size) // 2
    offset_y = (512 - p_size) // 2
    
    for fid, col, row, patch_file in FACTIONS:
        print(f"  Compositing [{col}, {row}]: {fid}...")
        canvas = canvas_base.copy()
        
        if fid == 'zombied':
            # Use generated zombied patch with alpha
            patch_p = r"C:\Users\hocke\.gemini\antigravity\brain\1250b0a1-f73b-4096-b1f7-9997a7d13804\patch_zombied_512_rgba.png"
            patch_im = Image.open(patch_p)
        elif fid == 'base':
            # Base unaligned flag: use loner patch slightly desaturated/neutral, or loner patch
            patch_p = os.path.join(WD_PATCH_DIR, "patch_loners.dds")
            patch_im = Image.open(patch_p).convert("RGBA")
        else:
            patch_p = os.path.join(WD_PATCH_DIR, patch_file)
            patch_im = Image.open(patch_p).convert("RGBA")
            
        patch_resized = patch_im.resize((p_size, p_size), Image.Resampling.LANCZOS)
        alpha = patch_resized.split()[3]
        
        # Drop shadow
        shadow = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        shadow.paste((0, 0, 0, 150), (offset_x, offset_y + 3), alpha)
        shadow = shadow.filter(ImageFilter.GaussianBlur(4))
        
        canvas.alpha_composite(shadow)
        canvas.paste(patch_resized, (offset_x, offset_y), patch_resized)
        
        sheet.paste(canvas, (col * 512, row * 512))
        
    out_png = os.path.join(REPO_ROOT, r"tools\model_pipeline\settlement_flags.png")
    sheet.save(out_png)
    print("Saved master PNG:", out_png)
    
    # Convert to DXT1 .dds
    out_dds = os.path.join(OUT_TEX_DIR, "settlement_flags.dds")
    from make_dds import main as encode_dds
    encode_dds(out_png, out_dds)
    print("Encoded DDS:", out_dds, f"({os.path.getsize(out_dds)} bytes)")

if __name__ == "__main__":
    sys.path.insert(0, os.path.join(REPO_ROOT, "tools/model_pipeline"))
    build_sheet()
