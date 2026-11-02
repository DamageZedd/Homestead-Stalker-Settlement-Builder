import collections
import os
from pathlib import Path
import struct
import sys

REPO_ROOT = Path(__file__).resolve().parent.parent
HOMESTEAD_DIR = REPO_ROOT / "HomesteadHF"


def parse_chunks(buf, offset=0, end=None):
    if end is None:
        end = len(buf)
    chunks = []
    pos = offset
    while pos + 8 <= end:
        cid = int.from_bytes(buf[pos : pos + 4], "little")
        csize = int.from_bytes(buf[pos + 4 : pos + 8], "little")
        pos += 8
        if pos + csize > end:
            break
        chunks.append((cid, pos, pos + csize))
        pos += csize
    return chunks


def audit_object_file(path):
    issues = []
    surfaces = []
    data = open(path, "rb").read()

    # .object files wrap chunks inside 0x7777
    top_chunks = parse_chunks(data)
    inner_data = None
    for cid, s, e in top_chunks:
        if cid == 0x7777:
            inner_data = data[s:e]
            break
    if inner_data is None:
        sub_chunks = top_chunks
        chunk_source = data
    else:
        sub_chunks = parse_chunks(inner_data)
        chunk_source = inner_data

    surf_chunk = None
    for cid, s, e in sub_chunks:
        if cid == 0x0907:  # EOBJ_CHUNK_SURFACES_2
            surf_chunk = chunk_source[s:e]
            break

    if surf_chunk is None:
        issues.append("Missing chunk 0x0907 (SURFACES_2)")
        return issues, surfaces

    d = surf_chunk
    cnt = struct.unpack_from("<I", d, 0)[0]
    p = 4
    for i in range(cnt):
        strs = []
        for _ in range(6):
            end = d.find(b"\x00", p)
            if end == -1:
                issues.append(f"Surface {i}: truncated string data")
                return issues, surfaces
            strs.append(d[p:end].decode("cp1251", errors="replace"))
            p = end + 1
        if p + 12 > len(d):
            issues.append(f"Surface {i}: truncated flags/fvf/uv_count")
            return issues, surfaces
        flags, fvf, uv_count = struct.unpack_from("<III", d, p)
        p += 12
        s_name, eshader, cshader, gamemtl, texture, vmap = strs
        surfaces.append(
            {
                "name": s_name,
                "eshader": eshader,
                "cshader": cshader,
                "gamemtl": gamemtl,
                "texture": texture,
                "vmap": vmap,
                "flags": flags,
                "fvf": fvf,
                "uv_count": uv_count,
            }
        )

        # Validation checks
        if not eshader.startswith("models\\"):
            issues.append(f"Surface '{s_name}': non-standard eshader '{eshader}'")
        if cshader != "default":
            issues.append(
                f"Surface '{s_name}': unexpected cshader '{cshader}' (expected 'default')"
            )
        if (
            gamemtl != "default_object"
            and not gamemtl.startswith("materials\\")
            and not gamemtl.startswith("default")
        ):
            issues.append(
                f"Surface '{s_name}': unexpected gamemtl '{gamemtl}' (expected 'default_object')"
            )
        if not texture or texture.strip() == "":
            issues.append(f"Surface '{s_name}': empty texture")
        if texture.lower().endswith(".dds"):
            issues.append(
                f"Surface '{s_name}': texture has .dds extension in definition '{texture}'"
            )

    if p != len(d):
        issues.append(
            f"SURFACES_2 chunk has {len(d) - p} trailing unparsed bytes (parse desync)"
        )

    return issues, surfaces


def audit_ogf_file(path):
    issues = []
    materials = []
    data = open(path, "rb").read()

    def walk(buf, start, end):
        ch = parse_chunks(buf, start, end)
        for cid, s, e in ch:
            if cid == 2:  # OGF_TEXTURE
                cdata = buf[s:e]
                parts = cdata.split(b"\x00")
                if len(parts) >= 2:
                    tex = parts[0].decode("cp1251", errors="replace")
                    sh = parts[1].decode("cp1251", errors="replace")
                    materials.append((tex, sh))
                    if not sh.startswith("models\\"):
                        issues.append(f"OGF shader is not models\\*: '{sh}'")
                    if not tex or tex.strip() == "":
                        issues.append("OGF texture is empty")
                    if tex.lower().endswith(".dds"):
                        issues.append(
                            f"OGF texture contains .dds extension: '{tex}'"
                        )
            elif cid == 9:  # OGF_CHILDREN
                sub = parse_chunks(buf, s, e)
                for scid, ss, se in sub:
                    walk(buf, ss, se)

    walk(data, 0, len(data))
    return issues, materials


def main():
    print("=== EXHAUSTIVE MATERIAL AUDIT FOR HOMESTEAD ===")

    object_files = sorted(HOMESTEAD_DIR.rglob("*.object"))
    ogf_files = sorted(HOMESTEAD_DIR.rglob("*.ogf"))

    print(
        f"Discovered: {len(object_files)} .object files and {len(ogf_files)} .ogf files."
    )

    total_object_issues = 0
    all_obj_eshaders = collections.Counter()
    all_obj_cshaders = collections.Counter()
    all_obj_gamemtls = collections.Counter()
    all_obj_textures = set()
    total_obj_surfaces = 0

    print("\n--- Auditing .object files ---")
    for obj_path in object_files:
        rel = obj_path.relative_to(HOMESTEAD_DIR)
        issues, surfs = audit_object_file(obj_path)
        total_obj_surfaces += len(surfs)
        for s in surfs:
            all_obj_eshaders[s["eshader"]] += 1
            all_obj_cshaders[s["cshader"]] += 1
            all_obj_gamemtls[s["gamemtl"]] += 1
            all_obj_textures.add(s["texture"])
        if issues:
            total_object_issues += len(issues)
            print(f"[FAIL] {rel}:")
            for iss in issues:
                print(f"       - {iss}")

    print(
        f"\nResult .object: {total_object_issues} issues across {total_obj_surfaces} surfaces in {len(object_files)} files."
    )
    print(f"  eshader distribution: {dict(all_obj_eshaders)}")
    print(f"  cshader distribution: {dict(all_obj_cshaders)}")
    print(f"  gamemtl distribution: {dict(all_obj_gamemtls)}")

    print("\n--- Auditing .ogf files ---")
    total_ogf_issues = 0
    ogf_shaders = collections.Counter()
    ogf_textures = set()
    total_ogf_materials = 0
    for ogf_path in ogf_files:
        rel = ogf_path.relative_to(HOMESTEAD_DIR)
        issues, mats = audit_ogf_file(ogf_path)
        total_ogf_materials += len(mats)
        for tex, sh in mats:
            ogf_shaders[sh] += 1
            ogf_textures.add(tex)
        if issues:
            total_ogf_issues += len(issues)
            print(f"[FAIL] {rel}:")
            for iss in issues:
                print(f"       - {iss}")

    print(
        f"\nResult .ogf: {total_ogf_issues} issues across {total_ogf_materials} materials in {len(ogf_files)} files."
    )
    print(f"  Shader distribution: {dict(ogf_shaders)}")
    print(f"  Total unique textures: {len(ogf_textures)}")

    # Check for missing textures or atlas leftovers
    print("\n--- Atlas references check ---")
    atlas_refs = [t for t in (all_obj_textures | ogf_textures) if "atlas_" in t]
    if atlas_refs:
        print(f"[WARNING] Found lingering atlas references: {atlas_refs}")
    else:
        print("[OK] Zero 'atlas_' texture references remain in any .object or .ogf model!")

    # Check .object vs .ogf consistency
    print("\n--- Cross-check .object vs .ogf textures ---")
    diff_obj_vs_ogf = all_obj_textures.symmetric_difference(ogf_textures)
    if diff_obj_vs_ogf:
        print(f"Textures in .object but not in .ogf: {all_obj_textures - ogf_textures}")
        print(f"Textures in .ogf but not in .object: {ogf_textures - all_obj_textures}")
        for ogf_path in ogf_files:
            issues, mats = audit_ogf_file(ogf_path)
            for tex, sh in mats:
                if tex in (ogf_textures - all_obj_textures):
                    print(
                        f"  Referenced by: {ogf_path.relative_to(HOMESTEAD_DIR)}: {tex}"
                    )
    else:
        print("[OK] .object and .ogf texture sets match perfectly!")

    # Model file count check
    print("\n--- Model file count check ---")
    obj_names = {p.stem for p in object_files}
    ogf_names = {p.stem for p in ogf_files}
    if ogf_names - obj_names:
        print(f"OGF files without matching .object: {sorted(ogf_names - obj_names)}")
    if obj_names - ogf_names:
        print(f".object files without matching .ogf: {sorted(obj_names - ogf_names)}")


if __name__ == "__main__":
    main()
