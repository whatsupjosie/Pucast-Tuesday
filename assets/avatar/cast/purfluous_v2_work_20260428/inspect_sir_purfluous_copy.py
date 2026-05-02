import json
import os

import bpy
from mathutils import Vector


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_GLB = os.path.join(SCRIPT_DIR, "sir_purfluous_v1_sourcecopy.glb")
OUTPUT_JSON = os.path.join(SCRIPT_DIR, "sir_purfluous_v1_copy_inspection.json")


def bounds_for(obj):
    corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]
    mins = [min(c[i] for c in corners) for i in range(3)]
    maxs = [max(c[i] for c in corners) for i in range(3)]
    return {"min": mins, "max": maxs}


bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete()
bpy.ops.import_scene.gltf(filepath=INPUT_GLB)

objects = []
for obj in bpy.context.scene.objects:
    entry = {
        "name": obj.name,
        "type": obj.type,
        "location": list(obj.location),
        "scale": list(obj.scale),
    }
    if obj.type == "MESH":
        entry["bounds"] = bounds_for(obj)
        entry["materials"] = [slot.material.name if slot.material else "" for slot in obj.material_slots]
        entry["vertex_count"] = len(obj.data.vertices)
    elif obj.type == "ARMATURE":
        entry["bones"] = [bone.name for bone in obj.data.bones]
    objects.append(entry)

with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
    json.dump({"input": INPUT_GLB, "objects": objects}, f, indent=2)

print(f"Wrote {OUTPUT_JSON}")
