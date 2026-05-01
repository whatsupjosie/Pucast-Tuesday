import pygltflib
import numpy as np
import struct
import json

# ── helpers ──────────────────────────────────────────────────────────────────
def pack_floats(data):
    return struct.pack(f'{len(data)}f', *data)

def pack_ushorts(data):
    return struct.pack(f'{len(data)}H', *data)

def pack_ubytes(data):
    return struct.pack(f'{len(data)}B', *data)

def make_cylinder(radius_top, radius_bot, height, segs=12, cap=True):
    """Simple cylinder verts+normals+uvs+tris, centered at origin, Y up."""
    verts, norms, uvs = [], [], []
    tris = []
    for i in range(segs):
        a = 2 * np.pi * i / segs
        cos_a, sin_a = np.cos(a), np.sin(a)
        for y_frac, r in ((0.0, radius_bot), (1.0, radius_top)):
            y = y_frac * height - height / 2
            verts += [r * cos_a, y, r * sin_a]
            norms += [cos_a, 0, sin_a]
            uvs   += [i / segs, y_frac]
    # side quads
    for i in range(segs):
        n = (i + 1) % segs
        b0, b1 = i * 2, n * 2
        t0, t1 = i * 2 + 1, n * 2 + 1
        tris += [b0, b1, t0, b1, t1, t0]
    if cap:
        # top cap
        ci = len(verts) // 3
        verts += [0, height / 2, 0]; norms += [0, 1, 0]; uvs += [0.5, 0.5]
        for i in range(segs):
            n = (i + 1) % segs
            tris += [ci, i * 2 + 1, n * 2 + 1]
        # bottom cap
        ci2 = len(verts) // 3
        verts += [0, -height / 2, 0]; norms += [0, -1, 0]; uvs += [0.5, 0.5]
        for i in range(segs):
            n = (i + 1) % segs
            tris += [ci2, n * 2, i * 2]
    return np.array(verts, np.float32), np.array(norms, np.float32), \
           np.array(uvs, np.float32), np.array(tris, np.uint16)

def make_box(w, h, d):
    hw, hh, hd = w/2, h/2, d/2
    v = np.array([
        -hw,-hh,-hd,  hw,-hh,-hd,  hw, hh,-hd, -hw, hh,-hd,
        -hw,-hh, hd,  hw,-hh, hd,  hw, hh, hd, -hw, hh, hd,
    ], np.float32)
    n = np.array([
        0,0,-1, 0,0,-1, 0,0,-1, 0,0,-1,
        0,0, 1, 0,0, 1, 0,0, 1, 0,0, 1,
    ], np.float32)
    uv = np.array([0,0,1,0,1,1,0,1]*2, np.float32)
    t = np.array([0,1,2,0,2,3, 4,5,6,4,6,7], np.uint16)
    return v, n, uv, t

def make_sphere(radius, segs=10):
    verts, norms, uvs, tris = [], [], [], []
    for i in range(segs + 1):
        theta = np.pi * i / segs
        for j in range(segs + 1):
            phi = 2 * np.pi * j / segs
            x = radius * np.sin(theta) * np.cos(phi)
            y = radius * np.cos(theta)
            z = radius * np.sin(theta) * np.sin(phi)
            verts += [x, y, z]
            norms += [x/radius, y/radius, z/radius]
            uvs   += [j/segs, i/segs]
    for i in range(segs):
        for j in range(segs):
            a = i*(segs+1)+j
            tris += [a, a+1, a+segs+1, a+1, a+segs+2, a+segs+1]
    return np.array(verts,np.float32), np.array(norms,np.float32), \
           np.array(uvs,np.float32), np.array(tris,np.uint16)

# ── bone skeleton (mirrors pete_rig_56) ──────────────────────────────────────
# Each bone: (name, parent_idx, [tx,ty,tz])  — Y-up, metres
BONES = [
    ("root",         -1, [0, 0, 0]),
    ("pelvis",        0, [0, 0.92, 0]),
    ("spine_01",      1, [0, 0.10, 0]),
    ("spine_02",      2, [0, 0.10, 0]),
    ("spine_03",      3, [0, 0.10, 0]),
    ("neck_01",       4, [0, 0.14, 0]),
    ("head",          5, [0, 0.10, 0]),
    ("jaw",           6, [0, -0.04, 0.04]),
    ("eye_l",         6, [0.03, 0.02, 0.07]),
    ("eye_r",         6, [-0.03, 0.02, 0.07]),
    ("clavicle_l",    4, [0.06, 0.05, 0]),
    ("upperarm_l",   10, [0.16, 0, 0]),
    ("lowerarm_l",   11, [0.26, 0, 0]),
    ("hand_l",       12, [0.24, 0, 0]),
    ("index_01_l",   13, [0.05, 0, 0.02]),
    ("middle_01_l",  13, [0.05, 0, 0.005]),
    ("ring_01_l",    13, [0.05, 0, -0.01]),
    ("pinky_01_l",   13, [0.04, 0, -0.025]),
    ("thumb_01_l",   13, [0.03, 0.01, 0.03]),
    ("clavicle_r",    4, [-0.06, 0.05, 0]),
    ("upperarm_r",   19, [-0.16, 0, 0]),
    ("lowerarm_r",   20, [-0.26, 0, 0]),
    ("hand_r",       21, [-0.24, 0, 0]),
    ("index_01_r",   22, [-0.05, 0, 0.02]),
    ("middle_01_r",  22, [-0.05, 0, 0.005]),
    ("ring_01_r",    22, [-0.05, 0, -0.01]),
    ("pinky_01_r",   22, [-0.04, 0, -0.025]),
    ("thumb_01_r",   22, [-0.03, 0.01, 0.03]),
    ("thigh_l",       1, [0.10, -0.05, 0]),
    ("calf_l",       28, [0, -0.42, 0]),
    ("foot_l",       29, [0, -0.40, 0.05]),
    ("ball_l",       30, [0, -0.08, 0.08]),
    ("thigh_r",       1, [-0.10, -0.05, 0]),
    ("calf_r",       32, [0, -0.42, 0]),
    ("foot_r",       33, [0, -0.40, 0.05]),
    ("ball_r",       34, [0, -0.08, 0.08]),
    ("ik_foot_l",    -1, [0.10, 0.02, 0]),
    ("ik_foot_r",    -1, [-0.10, 0.02, 0]),
    ("ik_hand_l",    -1, [0.55, 0.92, 0]),
    ("ik_hand_r",    -1, [-0.55, 0.92, 0]),
    ("hair_top",      6, [0, 0.10, -0.01]),
    ("hair_side_l",   6, [0.07, 0.04, 0]),
    ("hair_side_r",   6, [-0.07, 0.04, 0]),
    ("hair_back",     6, [0, 0.02, -0.08]),
    ("hair_fringe",   6, [0, 0.06, 0.07]),
    ("breast_l",      3, [0.10, 0.05, 0.05]),
    ("breast_r",      3, [-0.10, 0.05, 0.05]),
    ("brow_l",        6, [0.04, 0.05, 0.07]),
    ("brow_r",        6, [-0.04, 0.05, 0.07]),
    ("cheek_l",       6, [0.05, -0.01, 0.06]),
    ("cheek_r",       6, [-0.05, -0.01, 0.06]),
    ("lip_upper",     7, [0, 0.01, 0.02]),
    ("lip_lower",     7, [0, -0.01, 0.02]),
    ("lip_corner_l",  7, [0.025, 0, 0.015]),
    ("lip_corner_r",  7, [-0.025, 0, 0.015]),
    ("camera_bone",   6, [0, 0.05, 0.30]),
]

# ── mesh parts: (name, material_idx, generator_fn) ───────────────────────────
# Materials: 0=skin 1=boxer 2=suit_brown 3=shirt_white 4=shoe_brown
#            5=belt_black 6=hair_grey 7=eye_iris 8=eye_white 9=lip

def mesh_torso():       return make_cylinder(0.145, 0.165, 0.40, 14)   # shirt/suit body
def mesh_pelvis():      return make_cylinder(0.155, 0.145, 0.18, 14)   # boxer short area
def mesh_jacket_body(): return make_cylinder(0.150, 0.170, 0.38, 14)   # outer jacket
def mesh_lapel_l():     return make_box(0.06, 0.18, 0.02)
def mesh_lapel_r():     return make_box(0.06, 0.18, 0.02)
def mesh_sleeve_l():    return make_cylinder(0.055, 0.065, 0.28, 10)
def mesh_sleeve_r():    return make_cylinder(0.055, 0.065, 0.28, 10)
def mesh_forearm_l():   return make_cylinder(0.045, 0.055, 0.24, 10)
def mesh_forearm_r():   return make_cylinder(0.045, 0.055, 0.24, 10)
def mesh_hand_l():      return make_box(0.09, 0.10, 0.04)
def mesh_hand_r():      return make_box(0.09, 0.10, 0.04)
def mesh_thigh_l():     return make_cylinder(0.080, 0.090, 0.42, 12)
def mesh_shin_l():      return make_cylinder(0.055, 0.075, 0.40, 12)
def mesh_thigh_r():     return make_cylinder(0.080, 0.090, 0.42, 12)
def mesh_shin_r():      return make_cylinder(0.055, 0.075, 0.40, 12)
def mesh_boot_l():      return make_box(0.12, 0.10, 0.28)
def mesh_boot_r():      return make_box(0.12, 0.10, 0.28)
def mesh_belt():        return make_cylinder(0.170, 0.170, 0.04, 14, cap=False)
def mesh_face():        return make_sphere(0.105, 12)
def mesh_eye_l():       return make_sphere(0.014, 8)
def mesh_eye_r():       return make_sphere(0.014, 8)
def mesh_eye_wl():      return make_sphere(0.013, 8)
def mesh_eye_wr():      return make_sphere(0.013, 8)
def mesh_neck():        return make_cylinder(0.058, 0.065, 0.13, 10)
def mesh_hair_cap():    return make_sphere(0.112, 10)
def mesh_hair_sl():     return make_box(0.04, 0.10, 0.04)
def mesh_hair_sr():     return make_box(0.04, 0.10, 0.04)
def mesh_hair_fr():     return make_box(0.10, 0.03, 0.03)

MESH_PARTS = [
    ("sir_torso_underlayer", 1, mesh_torso),
    ("sir_pelvis_mesh",      1, mesh_pelvis),
    ("sir_jacket_body",      2, mesh_jacket_body),
    ("sir_lapel_l",          2, mesh_lapel_l),
    ("sir_lapel_r",          2, mesh_lapel_r),
    ("sir_jacket_sleeve_l",  2, mesh_sleeve_l),
    ("sir_jacket_sleeve_r",  2, mesh_sleeve_r),
    ("sir_forearm_l",        0, mesh_forearm_l),
    ("sir_forearm_r",        0, mesh_forearm_r),
    ("sir_hand_l",           0, mesh_hand_l),
    ("sir_hand_r",           0, mesh_hand_r),
    ("sir_thigh_l",          2, mesh_thigh_l),
    ("sir_shin_l",           2, mesh_shin_l),
    ("sir_thigh_r",          2, mesh_thigh_r),
    ("sir_shin_r",           2, mesh_shin_r),
    ("sir_boot_l",           4, mesh_boot_l),
    ("sir_boot_r",           4, mesh_boot_r),
    ("sir_belt",             5, mesh_belt),
    ("sir_face_mesh",        0, mesh_face),
    ("sir_eye_l",            7, mesh_eye_l),
    ("sir_eye_r",            7, mesh_eye_r),
    ("sir_eye_white_l",      8, mesh_eye_wl),
    ("sir_eye_white_r",      8, mesh_eye_wr),
    ("sir_neck",             0, mesh_neck),
    ("sir_hair_cap",         6, mesh_hair_cap),
    ("sir_hair_side_l",      6, mesh_hair_sl),
    ("sir_hair_side_r",      6, mesh_hair_sr),
    ("sir_hair_fringe",      6, mesh_hair_fr),
]

# ── GLB builder ───────────────────────────────────────────────────────────────
class GLBBuilder:
    def __init__(self):
        self.gltf = pygltflib.GLTF2()
        self.gltf.asset = pygltflib.Asset(version="2.0", generator="SirPurfluous_v1")
        self.buffer_data = bytearray()
        self.gltf.buffers = [pygltflib.Buffer(byteLength=0)]
        self.acc_idx = 0
        self.bv_idx  = 0

    def add_buffer_view(self, data: bytes, target=None):
        offset = len(self.buffer_data)
        # 4-byte align
        pad = (4 - len(data) % 4) % 4
        self.buffer_data += data + bytes(pad)
        bv = pygltflib.BufferView(buffer=0, byteOffset=offset,
                                  byteLength=len(data), target=target)
        self.gltf.bufferViews.append(bv)
        idx = self.bv_idx; self.bv_idx += 1
        return idx

    def add_accessor(self, bv_idx, comp_type, count, acc_type,
                     min_v=None, max_v=None, byte_offset=0):
        a = pygltflib.Accessor(
            bufferView=bv_idx, byteOffset=byte_offset,
            componentType=comp_type, count=count, type=acc_type,
        )
        if min_v: a.min = min_v
        if max_v: a.max = max_v
        self.gltf.accessors.append(a)
        idx = self.acc_idx; self.acc_idx += 1
        return idx

    def add_mesh(self, name, verts, norms, uvs, tris, mat_idx,
                 joint_idx, weight_idx):
        """Add a skinned mesh primitive."""
        ARRAY_BUFFER      = 34962
        ELEMENT_ARRAY_BUF = 34963

        bv_pos = self.add_buffer_view(verts.tobytes(), ARRAY_BUFFER)
        bv_nor = self.add_buffer_view(norms.tobytes(), ARRAY_BUFFER)
        bv_uv  = self.add_buffer_view(uvs.tobytes(),   ARRAY_BUFFER)
        bv_idx_buf = self.add_buffer_view(tris.tobytes(), ELEMENT_ARRAY_BUF)
        bv_j   = self.add_buffer_view(joint_idx.tobytes(), ARRAY_BUFFER)
        bv_w   = self.add_buffer_view(weight_idx.tobytes(), ARRAY_BUFFER)

        n = len(verts) // 3
        mn = verts.reshape(-1,3).min(0).tolist()
        mx = verts.reshape(-1,3).max(0).tolist()

        a_pos  = self.add_accessor(bv_pos, 5126, n, "VEC3", mn, mx)
        a_nor  = self.add_accessor(bv_nor, 5126, n, "VEC3")
        a_uv   = self.add_accessor(bv_uv,  5126, n, "VEC2")
        a_tri  = self.add_accessor(bv_idx_buf, 5123, len(tris), "SCALAR")
        a_j    = self.add_accessor(bv_j, 5121, n, "VEC4")
        a_w    = self.add_accessor(bv_w, 5126, n, "VEC4")

        prim = pygltflib.Primitive(
            attributes=pygltflib.Attributes(
                POSITION=a_pos, NORMAL=a_nor, TEXCOORD_0=a_uv,
                JOINTS_0=a_j, WEIGHTS_0=a_w),
            indices=a_tri, material=mat_idx)
        mesh = pygltflib.Mesh(name=name, primitives=[prim])
        self.gltf.meshes.append(mesh)
        return len(self.gltf.meshes) - 1

def make_joint_weights(n_verts, primary_bone, n_bones):
    """Assign all verts to one bone (rigid bind — good for base mesh)."""
    joints  = np.zeros((n_verts, 4), np.uint8)
    weights = np.zeros((n_verts, 4), np.float32)
    joints[:, 0]  = primary_bone
    weights[:, 0] = 1.0
    return joints.flatten(), weights.flatten()

# ── primary bone mapping per mesh part ───────────────────────────────────────
# Maps mesh part index → bone index in BONES list
PART_BONE = [
    3,  # torso_underlayer  → spine_02
    1,  # pelvis_mesh       → pelvis
    3,  # jacket_body       → spine_02
    3,  # lapel_l           → spine_02
    3,  # lapel_r           → spine_02
    11, # sleeve_l          → upperarm_l
    20, # sleeve_r          → upperarm_r
    12, # forearm_l         → lowerarm_l
    21, # forearm_r         → lowerarm_r
    13, # hand_l            → hand_l
    22, # hand_r            → hand_r
    28, # thigh_l           → thigh_l
    29, # shin_l            → calf_l
    32, # thigh_r           → thigh_r
    33, # shin_r            → calf_r
    30, # boot_l            → foot_l
    34, # boot_r            → foot_r
    1,  # belt              → pelvis
    6,  # face              → head
    8,  # eye_l             → eye_l  (bone 8)
    9,  # eye_r             → eye_r  (bone 9)
    8,  # eye_white_l       → eye_l
    9,  # eye_white_r       → eye_r
    5,  # neck              → neck_01
    40, # hair_cap          → hair_top
    41, # hair_side_l       → hair_side_l
    42, # hair_side_r       → hair_side_r
    44, # hair_fringe       → hair_fringe
]

def build():
    b = GLBBuilder()
    g = b.gltf

    # ── materials ────────────────────────────────────────────────────────────
    def mat(name, r, gr, gb, metallic=0.0, rough=0.8):
        return pygltflib.Material(
            name=name,
            pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
                baseColorFactor=[r, gr, gb, 1.0],
                metallicFactor=metallic,
                roughnessFactor=rough))

    g.materials = [
        mat("skin",        0.78, 0.60, 0.47),          # 0 aged skin
        mat("boxer",       0.85, 0.82, 0.75),          # 1 off-white
        mat("suit_brown",  0.32, 0.20, 0.10),          # 2 warm brown
        mat("shirt_white", 0.92, 0.90, 0.85),          # 3 cream shirt
        mat("shoe_brown",  0.22, 0.13, 0.07, 0.1),    # 4 dark brown leather
        mat("belt_black",  0.08, 0.07, 0.06, 0.2),    # 5 near-black belt
        mat("hair_grey",   0.55, 0.54, 0.53),          # 6 silver-grey hair
        mat("eye_iris",    0.25, 0.35, 0.55),          # 7 blue-grey iris
        mat("eye_white",   0.95, 0.93, 0.90),          # 8 aged white
        mat("lip",         0.62, 0.38, 0.32),          # 9 lip
    ]

    # ── skeleton nodes ────────────────────────────────────────────────────────
    bone_node_indices = []
    for bone_name, parent_idx, trans in BONES:
        node = pygltflib.Node(name=bone_name, translation=trans)
        g.nodes.append(node)
        bone_node_indices.append(len(g.nodes) - 1)

    # Wire up bone children
    for i, (_, parent_idx, _) in enumerate(BONES):
        if parent_idx >= 0:
            parent_node = g.nodes[bone_node_indices[parent_idx]]
            if parent_node.children is None:
                parent_node.children = []
            parent_node.children.append(bone_node_indices[i])

    n_bones = len(BONES)

    # ── inverse bind matrices accessor ───────────────────────────────────────
    ibm_data = np.tile(np.eye(4, dtype=np.float32).flatten(), n_bones)
    bv_ibm = b.add_buffer_view(ibm_data.tobytes())
    a_ibm = b.add_accessor(bv_ibm, 5126, n_bones, "MAT4")

    # ── skin ─────────────────────────────────────────────────────────────────
    skin = pygltflib.Skin(name="sir_purfluous_rig_56",
                          inverseBindMatrices=a_ibm,
                          joints=list(bone_node_indices))
    g.skins.append(skin)

    # ── meshes ────────────────────────────────────────────────────────────────
    mesh_node_indices = []
    for part_idx, (name, mat_idx, gen_fn) in enumerate(MESH_PARTS):
        verts, norms, uvs, tris = gen_fn()
        n_verts = len(verts) // 3
        primary_bone = PART_BONE[part_idx]
        joints_flat, weights_flat = make_joint_weights(n_verts, primary_bone, n_bones)

        mesh_idx = b.add_mesh(name, verts, norms, uvs, tris, mat_idx,
                              joints_flat.astype(np.uint8),
                              weights_flat.astype(np.float32))
        node = pygltflib.Node(name=f"node_{name}", mesh=mesh_idx, skin=0)
        g.nodes.append(node)
        mesh_node_indices.append(len(g.nodes) - 1)

    # ── IK / orphan bones as root children ───────────────────────────────────
    root_node_idx = bone_node_indices[0]  # "root" bone
    orphan_bones = [36, 37, 38, 39]       # ik_foot_l/r, ik_hand_l/r

    # ── scene ─────────────────────────────────────────────────────────────────
    scene_children = [root_node_idx] + \
                     [bone_node_indices[i] for i in orphan_bones] + \
                     mesh_node_indices
    scene = pygltflib.Scene(name="Sir_Purfluous_T-Pose", nodes=scene_children)
    g.scenes.append(scene)
    g.scene = 0

    # ── finalise buffer ────────────────────────────────────────────────────────
    g.buffers[0].byteLength = len(b.buffer_data)
    g.set_binary_blob(bytes(b.buffer_data))

    out = "/home/claude/sir_purfluous_v1.glb"
    g.save(out)
    print(f"Saved: {out}  ({len(b.buffer_data):,} bytes)")
    return out

build()
