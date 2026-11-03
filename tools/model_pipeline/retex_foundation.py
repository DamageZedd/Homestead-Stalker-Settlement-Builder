"""Swaps the concrete texture of a shipped foundation piece (run headless in Blender with the XRay addon):

    blender -b -P retex_foundation.py -- hs_foundation <out_dir> [new_texture]

Imports the shipped <name>.object, renames the concrete material and its image node to the new vanilla
texture path and re-exports <name>.object/.ogf into <out_dir>; bones and collision come through untouched.
"""
import os
import sys

import bpy

REPO = os.environ.get("HSHF_REPO", r"C:\Users\hocke\.gemini\git repo homestead\Homestead")
SRC = os.path.join(REPO, r"HomesteadHF\gamedata\meshes\dynamics\HomesteadHF\building")
VTEX = os.environ.get("HSHF_VTEX", r"C:\Users\hocke\AppData\Local\Temp\claude_sp\vtex\textures")
OLD = "grnd\grnd_concrete_2"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import export_lib as xl  # noqa: E402


def main():
    args = sys.argv[sys.argv.index("--") + 1:]
    name, out = args[0], args[1]
    new = args[2] if len(args) > 2 else "wall\wall_house_white_02"
    bpy.ops.wm.read_homefile(use_empty=True)
    bpy.ops.xray_import.object(directory=SRC, files=[{'name': name + ".object"}])
    arm = bpy.data.objects[name + ".object"]
    hit = 0
    for c in arm.children:
        for m in c.data.materials:
            if m.name.replace("/", "\\").lower() != OLD:
                continue
            hit += 1
            node = next(n for n in m.node_tree.nodes if n.type == 'TEX_IMAGE')
            node.image = bpy.data.images.load(os.path.join(VTEX, new + ".dds"), check_existing=True)
            node.name = node.label = new
            m.name = new
    assert hit, "no %s material found" % OLD
    os.makedirs(out, exist_ok=True)
    print("EXPORT", name, xl.export(arm, out, name)[:2], "retextured materials:", hit)


main()
