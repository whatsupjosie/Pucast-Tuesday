"""
Sir Purfluous v3 bound actor build.

Avatar-only, non-destructive:
- Reads the copied v1 GLB in this work folder.
- Writes new v3 outputs in this work folder only.
- Binds added identity/details meshes to the existing armature bones.
"""

import math
import os

import bpy


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_GLB = os.path.join(SCRIPT_DIR, "sir_purfluous_v1_sourcecopy.glb")
OUTPUT_GLB = os.path.join(SCRIPT_DIR, "sir_purfluous_v3_bound_actor.glb")
OUTPUT_BLEND = os.path.join(SCRIPT_DIR, "sir_purfluous_v3_bound_actor.blend")


def make_material(name, color, roughness=0.8, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return material


MAT_SKIN = make_material("purfluous_v3_warm_aged_skin", (0.78, 0.58, 0.43, 1), 0.88)
MAT_HAIR = make_material("purfluous_v3_silver_white_hair", (0.87, 0.86, 0.80, 1), 0.96)
MAT_SUIT = make_material("purfluous_v3_tawny_brown_suit", (0.48, 0.27, 0.09, 1), 0.84)
MAT_SUIT_DARK = make_material("purfluous_v3_dark_inner_brown", (0.20, 0.12, 0.055, 1), 0.86)
MAT_SHIRT = make_material("purfluous_v3_warm_cream_shirt", (0.92, 0.86, 0.74, 1), 0.9)
MAT_GOLD = make_material("purfluous_v3_old_gold", (0.95, 0.61, 0.20, 1), 0.38, 0.55)
MAT_WHITE = make_material("purfluous_v3_pocket_square_cream", (0.96, 0.93, 0.86, 1), 0.9)
MAT_BOOT = make_material("purfluous_v3_polished_brown_boots", (0.24, 0.12, 0.045, 1), 0.55)


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_source():
    bpy.ops.import_scene.gltf(filepath=INPUT_GLB)


def get_armature():
    for item in bpy.context.scene.objects:
        if item.type == "ARMATURE":
            return item
    raise RuntimeError("No armature found in source GLB")


def object_named(name):
    return bpy.data.objects.get(name)


def assign_material(name, material):
    target = object_named(name)
    if target and target.type == "MESH":
        target.data.materials.clear()
        target.data.materials.append(material)


def bind_mesh_to_bone(mesh_obj, armature, bone_name):
    """Rigidly skin every vertex in a detail mesh to one existing bone."""
    if mesh_obj.type != "MESH":
        return mesh_obj
    world = mesh_obj.matrix_world.copy()
    group = mesh_obj.vertex_groups.new(name=bone_name)
    indices = [vertex.index for vertex in mesh_obj.data.vertices]
    group.add(indices, 1.0, "ADD")
    modifier = mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    modifier.object = armature
    mesh_obj.parent = armature
    mesh_obj.matrix_parent_inverse = armature.matrix_world.inverted()
    mesh_obj.matrix_world = world
    return mesh_obj


def add_uv_sphere(name, location, scale, material, armature, bone, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    item = bpy.context.object
    item.name = name
    item.scale = scale
    item.data.materials.append(material)
    bind_mesh_to_bone(item, armature, bone)
    return item


def add_cube(name, location, scale, material, armature, bone, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    item = bpy.context.object
    item.name = name
    item.scale = scale
    item.data.materials.append(material)
    bind_mesh_to_bone(item, armature, bone)
    return item


def add_cylinder(name, location, radius, depth, material, armature, bone, vertices=32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    item = bpy.context.object
    item.name = name
    item.data.materials.append(material)
    bind_mesh_to_bone(item, armature, bone)
    return item


def shape_existing_body():
    """Improve silhouette and material read while preserving source rig."""
    scale_map = {
        "node_sir_torso_underlayer": (1.10, 1.04, 1.02),
        "node_sir_jacket_body": (1.18, 1.08, 1.05),
        "node_sir_pelvis_mesh": (1.11, 1.02, 1.02),
        "node_sir_jacket_sleeve_l": (1.06, 1.0, 1.03),
        "node_sir_jacket_sleeve_r": (1.06, 1.0, 1.03),
        "node_sir_forearm_l": (1.03, 1.0, 1.0),
        "node_sir_forearm_r": (1.03, 1.0, 1.0),
        "node_sir_thigh_l": (1.06, 1.0, 1.0),
        "node_sir_thigh_r": (1.06, 1.0, 1.0),
        "node_sir_shin_l": (1.04, 1.0, 1.0),
        "node_sir_shin_r": (1.04, 1.0, 1.0),
        "node_sir_neck": (1.08, 1.0, 0.92),
        "node_sir_face_mesh": (1.04, 0.99, 1.07),
        "node_sir_hair_cap": (1.12, 1.03, 1.03),
        "node_sir_hair_side_l": (1.22, 1.08, 1.18),
        "node_sir_hair_side_r": (1.22, 1.08, 1.18),
        "node_sir_hair_fringe": (1.28, 1.06, 1.10),
    }
    for name, scale in scale_map.items():
        target = object_named(name)
        if target:
            target.scale.x *= scale[0]
            target.scale.y *= scale[1]
            target.scale.z *= scale[2]

    suit_parts = (
        "node_sir_jacket_body", "node_sir_lapel_l", "node_sir_lapel_r",
        "node_sir_jacket_sleeve_l", "node_sir_jacket_sleeve_r",
        "node_sir_thigh_l", "node_sir_thigh_r", "node_sir_shin_l", "node_sir_shin_r",
        "node_sir_pelvis_mesh",
    )
    for name in suit_parts:
        assign_material(name, MAT_SUIT)
    assign_material("node_sir_torso_underlayer", MAT_SHIRT)
    for name in ("node_sir_hair_cap", "node_sir_hair_side_l", "node_sir_hair_side_r", "node_sir_hair_fringe"):
        assign_material(name, MAT_HAIR)
    for name in ("node_sir_face_mesh", "node_sir_neck", "node_sir_hand_l", "node_sir_hand_r"):
        assign_material(name, MAT_SKIN)
    for name in ("node_sir_boot_l", "node_sir_boot_r"):
        assign_material(name, MAT_BOOT)


def add_character_details(armature):
    # Source avatar front is negative Y.
    add_uv_sphere("purfluous_v3_mustache_left_tight", (0.030, -0.108, 1.418), (0.040, 0.006, 0.011), MAT_HAIR, armature, "head", 24, 8)
    add_uv_sphere("purfluous_v3_mustache_right_tight", (-0.030, -0.108, 1.418), (0.040, 0.006, 0.011), MAT_HAIR, armature, "head", 24, 8)
    add_uv_sphere("purfluous_v3_mustache_center", (0.0, -0.109, 1.413), (0.026, 0.005, 0.010), MAT_HAIR, armature, "head", 20, 8)
    add_uv_sphere("purfluous_v3_beard_chin_tight", (0.0, -0.108, 1.372), (0.052, 0.007, 0.030), MAT_HAIR, armature, "head", 24, 8)
    add_uv_sphere("purfluous_v3_beard_cheek_l_tight", (0.058, -0.106, 1.392), (0.018, 0.005, 0.031), MAT_HAIR, armature, "head", 16, 8)
    add_uv_sphere("purfluous_v3_beard_cheek_r_tight", (-0.058, -0.106, 1.392), (0.018, 0.005, 0.031), MAT_HAIR, armature, "head", 16, 8)

    add_cube("purfluous_v3_brow_l", (0.038, -0.106, 1.487), (0.041, 0.004, 0.006), MAT_HAIR, armature, "brow_l", (0, 0, math.radians(10)))
    add_cube("purfluous_v3_brow_r", (-0.038, -0.106, 1.487), (0.041, 0.004, 0.006), MAT_HAIR, armature, "brow_r", (0, 0, math.radians(-10)))

    add_cube("purfluous_v3_cream_pocket_square", (-0.095, -0.180, 1.205), (0.032, 0.006, 0.025), MAT_WHITE, armature, "spine_03", (0, 0, math.radians(-12)))
    add_cylinder("purfluous_v3_pocket_watch_face", (-0.070, -0.187, 1.035), 0.021, 0.006, MAT_GOLD, armature, "spine_02", 32, (math.radians(90), 0, 0))
    add_cylinder("purfluous_v3_watch_chain_left", (-0.040, -0.188, 1.075), 0.004, 0.088, MAT_GOLD, armature, "spine_02", 12, (0, math.radians(54), 0))
    add_cylinder("purfluous_v3_watch_chain_right", (-0.103, -0.188, 1.075), 0.004, 0.073, MAT_GOLD, armature, "spine_02", 12, (0, math.radians(-48), 0))

    for index, z in enumerate((1.18, 1.12, 1.06, 1.00), start=1):
        add_cylinder(f"purfluous_v3_vest_button_{index}", (0.0, -0.187, z), 0.009, 0.004, MAT_GOLD, armature, "spine_02", 18, (math.radians(90), 0, 0))
    add_cube("purfluous_v3_narrow_brown_tie", (0.0, -0.184, 1.205), (0.018, 0.006, 0.087), MAT_SUIT_DARK, armature, "spine_03")

    # Slight theatrical coat-tail read from side/back.
    add_cube("purfluous_v3_coat_tail_l", (0.105, 0.135, 0.900), (0.035, 0.020, 0.145), MAT_SUIT_DARK, armature, "spine_01", (0, 0, math.radians(-5)))
    add_cube("purfluous_v3_coat_tail_r", (-0.105, 0.135, 0.900), (0.035, 0.020, 0.145), MAT_SUIT_DARK, armature, "spine_01", (0, 0, math.radians(5)))


def add_shape_keys():
    face = object_named("node_sir_face_mesh")
    if not face or face.type != "MESH":
        return
    bpy.context.view_layer.objects.active = face
    face.select_set(True)
    if not face.data.shape_keys:
        face.shape_key_add(name="Basis", from_mix=False)
    existing = set(face.data.shape_keys.key_blocks.keys())
    keys = [
        "thoughtful", "amused", "angry", "shocked", "contemptuous", "passionate",
        "brow_raise_l", "brow_raise_r", "brow_furrow", "mouth_open",
        "mouth_smile_l", "mouth_smile_r", "jaw_open",
        "viseme_aa", "viseme_ee", "viseme_oo", "viseme_mm", "viseme_th",
    ]
    for key_name in keys:
        if key_name not in existing:
            face.shape_key_add(name=key_name, from_mix=False).value = 0.0


def save_and_export():
    bpy.ops.wm.save_as_mainfile(filepath=OUTPUT_BLEND)
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.export_scene.gltf(
        filepath=OUTPUT_GLB,
        export_format="GLB",
        export_animations=False,
        export_morph=True,
        export_morph_normal=True,
        export_skins=True,
        export_apply=False,
        use_selection=False,
    )


if __name__ == "__main__":
    clean_scene()
    import_source()
    armature = get_armature()
    shape_existing_body()
    add_character_details(armature)
    add_shape_keys()
    save_and_export()
    print("Sir Purfluous v3 bound actor build complete.")
    print(OUTPUT_GLB)
    print(OUTPUT_BLEND)
