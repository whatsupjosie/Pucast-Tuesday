"""
Build Sir Purfluous v2 from copied v1 assets.

Non-destructive rule:
- Reads sir_purfluous_v1_sourcecopy.glb from this work folder.
- Writes new files in this work folder only.
- Does not edit or replace the repo's original v1 avatar.
"""

import math
import os

import bpy
from mathutils import Vector


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_GLB = os.path.join(SCRIPT_DIR, "sir_purfluous_v1_sourcecopy.glb")
OUTPUT_GLB = os.path.join(SCRIPT_DIR, "sir_purfluous_v2_actor.glb")
OUTPUT_BLEND = os.path.join(SCRIPT_DIR, "sir_purfluous_v2_actor.blend")


def mat(name, color, roughness=0.75, metallic=0.0):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    bsdf = material.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return material


MAT_SKIN = mat("purfluous_v2_warm_aged_skin", (0.78, 0.58, 0.43, 1), 0.88)
MAT_HAIR = mat("purfluous_v2_silver_white_hair", (0.86, 0.84, 0.78, 1), 0.95)
MAT_SUIT = mat("purfluous_v2_tawny_brown_suit", (0.48, 0.27, 0.09, 1), 0.82)
MAT_DARK_SUIT = mat("purfluous_v2_deep_brown_shadow", (0.20, 0.12, 0.06, 1), 0.85)
MAT_SHIRT = mat("purfluous_v2_warm_cream_shirt", (0.92, 0.86, 0.73, 1), 0.9)
MAT_GOLD = mat("purfluous_v2_old_gold", (0.95, 0.62, 0.20, 1), 0.35, 0.55)
MAT_WHITE = mat("purfluous_v2_pocket_square", (0.96, 0.93, 0.86, 1), 0.9)
MAT_INK = mat("purfluous_v2_stage_ink_lines", (0.05, 0.04, 0.035, 1), 0.9)


def clean_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_source():
    bpy.ops.import_scene.gltf(filepath=INPUT_GLB)


def obj(name):
    return bpy.data.objects.get(name)


def set_material(obj_name, material):
    target = obj(obj_name)
    if target and target.type == "MESH":
        target.data.materials.clear()
        target.data.materials.append(material)


def reshape_existing_body():
    """Push v1 toward the canonical Vincent Holloway/Sir Purfluous silhouette."""
    scales = {
        "node_sir_torso_underlayer": (1.16, 1.07, 1.04),
        "node_sir_jacket_body": (1.18, 1.08, 1.06),
        "node_sir_pelvis_mesh": (1.10, 1.02, 1.02),
        "node_sir_jacket_sleeve_l": (1.06, 1.0, 1.02),
        "node_sir_jacket_sleeve_r": (1.06, 1.0, 1.02),
        "node_sir_thigh_l": (1.08, 1.0, 1.0),
        "node_sir_thigh_r": (1.08, 1.0, 1.0),
        "node_sir_shin_l": (1.05, 1.0, 1.0),
        "node_sir_shin_r": (1.05, 1.0, 1.0),
        "node_sir_neck": (1.10, 1.0, 0.92),
        "node_sir_face_mesh": (1.03, 0.98, 1.06),
        "node_sir_hair_cap": (1.08, 1.02, 1.02),
        "node_sir_hair_side_l": (1.15, 1.05, 1.12),
        "node_sir_hair_side_r": (1.15, 1.05, 1.12),
        "node_sir_hair_fringe": (1.22, 1.05, 1.08),
    }
    for name, scale in scales.items():
        target = obj(name)
        if target:
            target.scale.x *= scale[0]
            target.scale.y *= scale[1]
            target.scale.z *= scale[2]

    for name in (
        "node_sir_jacket_body", "node_sir_lapel_l", "node_sir_lapel_r",
        "node_sir_jacket_sleeve_l", "node_sir_jacket_sleeve_r",
        "node_sir_thigh_l", "node_sir_thigh_r", "node_sir_shin_l", "node_sir_shin_r",
    ):
        set_material(name, MAT_SUIT)
    for name in ("node_sir_torso_underlayer",):
        set_material(name, MAT_SHIRT)
    for name in ("node_sir_hair_cap", "node_sir_hair_side_l", "node_sir_hair_side_r", "node_sir_hair_fringe"):
        set_material(name, MAT_HAIR)
    for name in ("node_sir_face_mesh", "node_sir_neck", "node_sir_hand_l", "node_sir_hand_r"):
        set_material(name, MAT_SKIN)


def add_uv_sphere(name, location, scale, material, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, location=location)
    sphere = bpy.context.object
    sphere.name = name
    sphere.scale = scale
    sphere.data.materials.append(material)
    return sphere


def add_cube(name, location, scale, material, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=location, rotation=rotation)
    cube = bpy.context.object
    cube.name = name
    cube.scale = scale
    cube.data.materials.append(material)
    return cube


def add_cylinder(name, location, radius, depth, material, vertices=32, rotation=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    cyl = bpy.context.object
    cyl.name = name
    cyl.data.materials.append(material)
    return cyl


def add_identity_details():
    # Front of face is negative Y in the source asset.
    add_uv_sphere("purfluous_v2_left_mustache_sweep", (0.035, -0.122, 1.415), (0.050, 0.012, 0.016), MAT_HAIR)
    add_uv_sphere("purfluous_v2_right_mustache_sweep", (-0.035, -0.122, 1.415), (0.050, 0.012, 0.016), MAT_HAIR)
    add_uv_sphere("purfluous_v2_beard_chin", (0.0, -0.122, 1.365), (0.070, 0.018, 0.045), MAT_HAIR)
    add_uv_sphere("purfluous_v2_beard_left_cheek", (0.070, -0.118, 1.395), (0.026, 0.012, 0.042), MAT_HAIR)
    add_uv_sphere("purfluous_v2_beard_right_cheek", (-0.070, -0.118, 1.395), (0.026, 0.012, 0.042), MAT_HAIR)

    brow_angle = math.radians(10)
    add_cube("purfluous_v2_left_theatrical_brow", (0.036, -0.116, 1.485), (0.038, 0.007, 0.007), MAT_HAIR, (0, 0, brow_angle))
    add_cube("purfluous_v2_right_theatrical_brow", (-0.036, -0.116, 1.485), (0.038, 0.007, 0.007), MAT_HAIR, (0, 0, -brow_angle))

    add_cube("purfluous_v2_cream_pocket_square", (-0.095, -0.178, 1.205), (0.030, 0.006, 0.024), MAT_WHITE, (0, 0, math.radians(-12)))
    add_cylinder("purfluous_v2_pocket_watch_face", (-0.070, -0.184, 1.035), 0.020, 0.006, MAT_GOLD, 32, (math.radians(90), 0, 0))
    add_cylinder("purfluous_v2_watch_chain_1", (-0.040, -0.186, 1.075), 0.004, 0.085, MAT_GOLD, 12, (0, math.radians(54), 0))
    add_cylinder("purfluous_v2_watch_chain_2", (-0.102, -0.186, 1.075), 0.004, 0.070, MAT_GOLD, 12, (0, math.radians(-48), 0))

    # Vest buttons and a narrow tie help the brown suit read as a three-piece actor costume.
    for z in (1.18, 1.12, 1.06, 1.00):
        add_cylinder(f"purfluous_v2_vest_button_{z:.2f}", (0.0, -0.184, z), 0.009, 0.004, MAT_GOLD, 16, (math.radians(90), 0, 0))
    add_cube("purfluous_v2_narrow_brown_tie", (0.0, -0.181, 1.205), (0.018, 0.006, 0.085), MAT_DARK_SUIT)


def add_face_shape_keys():
    face = obj("node_sir_face_mesh")
    if not face or face.type != "MESH":
        return
    bpy.context.view_layer.objects.active = face
    face.select_set(True)
    if not face.data.shape_keys:
        face.shape_key_add(name="Basis", from_mix=False)

    keys = [
        "neutral", "thoughtful", "amused", "angry", "shocked", "contemptuous",
        "passionate", "brow_raise_l", "brow_raise_r", "mouth_open",
        "viseme_aa", "viseme_ee", "viseme_oo", "viseme_mm", "viseme_th",
    ]
    existing = set(face.data.shape_keys.key_blocks.keys())
    for key_name in keys:
        if key_name not in existing:
            face.shape_key_add(name=key_name, from_mix=False).value = 0.0


def add_lights_camera_preview():
    bpy.ops.object.light_add(type="AREA", location=(0, -3.2, 2.8))
    key = bpy.context.object
    key.name = "purfluous_v2_preview_key_light"
    key.data.energy = 450
    key.data.size = 4

    bpy.ops.object.camera_add(location=(0, -4.0, 1.25), rotation=(math.radians(78), 0, 0))
    bpy.context.scene.camera = bpy.context.object
    bpy.context.object.name = "purfluous_v2_preview_camera"
    bpy.context.scene.render.resolution_x = 1200
    bpy.context.scene.render.resolution_y = 1600
    bpy.context.scene.eevee.taa_render_samples = 64


def export_outputs():
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
    reshape_existing_body()
    add_identity_details()
    add_face_shape_keys()
    add_lights_camera_preview()
    export_outputs()
    print("Sir Purfluous v2 actor build complete.")
    print(OUTPUT_GLB)
    print(OUTPUT_BLEND)
