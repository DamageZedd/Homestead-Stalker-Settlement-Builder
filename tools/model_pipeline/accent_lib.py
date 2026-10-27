# Helpers to pull vanilla Anomaly .ogf props into Blender as accents (run inside Blender).
import bpy, os

VAN = r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad\vanilla\meshes"
TEX_DIRS = [r"C:\GAMMA\mods\PAT\gamedata\textures",
            r"C:\Users\hocke\AppData\Local\Temp\claude\C--Users-hocke--gemini-git-repo-homestead-Homestead\9b9ceea6-ee44-4aee-8343-201a00d5359f\scratchpad\vanilla_tex\textures",
            r"C:\anomaly\tools\_test_unpack\textures"]


def find_tex(rel):
    for d in TEX_DIRS:
        p = os.path.join(d, rel + ".dds")
        if os.path.exists(p):
            return p
    return None


def fix_images(objs):
    """Point every image on these objects' materials at PAT, or the vanilla unpack."""
    missing = set()
    for o in objs:
        if o.type != 'MESH':
            continue
        for m in o.data.materials:
            if not (m and m.node_tree):
                continue
            for n in m.node_tree.nodes:
                if n.type == 'TEX_IMAGE':
                    tex = m.xray.texture if hasattr(m, "xray") and getattr(m.xray, "texture", "") else m.name
                    tex = tex.split("~")[0] if "~" in tex else tex
                    p = find_tex(tex) or (n.image and find_tex(os.path.splitext(n.image.name)[0]))
                    if p:
                        n.image = bpy.data.images.load(p, check_existing=True)
                    else:
                        missing.add(tex)
    return missing


def import_ogf(rel, collection_name):
    """Import meshes\\<rel>.ogf; returns the new objects, linked into collection_name."""
    path = os.path.join(VAN, rel + ".ogf")
    col = bpy.data.collections.get(collection_name) or bpy.data.collections.new(collection_name)
    if col.name not in bpy.context.scene.collection.children:
        bpy.context.scene.collection.children.link(col)
    before = set(bpy.data.objects)
    d, f = os.path.split(path)
    bpy.ops.xray_import.ogf(directory=d, files=[{'name': f}])
    new = [o for o in bpy.data.objects if o not in before]
    for o in new:
        for c in list(o.users_collection):
            c.objects.unlink(o)
        col.objects.link(o)
    return new, fix_images(new)
