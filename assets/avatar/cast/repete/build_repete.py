import pygltflib
import numpy as np
import struct

def make_cylinder(r_top, r_bot, height, segs=12, cap=True):
    verts, norms, uvs, tris = [], [], [], []
    for i in range(segs):
        a = 2 * np.pi * i / segs
        ca, sa = np.cos(a), np.sin(a)
        for y_frac, r in ((0.0, r_bot), (1.0, r_top)):
            y = y_frac * height - height / 2
            verts += [r*ca, y, r*sa]; norms += [ca, 0, sa]; uvs += [i/segs, y_frac]
    for i in range(segs):
        n = (i+1)%segs
        b0,b1,t0,t1 = i*2, n*2, i*2+1, n*2+1
        tris += [b0,b1,t0, b1,t1,t0]
    if cap:
        ci = len(verts)//3
        verts += [0, height/2, 0]; norms += [0,1,0]; uvs += [.5,.5]
        for i in range(segs): tris += [ci, i*2+1, ((i+1)%segs)*2+1]
        ci2 = len(verts)//3
        verts += [0,-height/2, 0]; norms += [0,-1,0]; uvs += [.5,.5]
        for i in range(segs): tris += [ci2, ((i+1)%segs)*2, i*2]
    return np.array(verts,np.float32), np.array(norms,np.float32), np.array(uvs,np.float32), np.array(tris,np.uint16)

def make_box(w,h,d):
    hw,hh,hd = w/2,h/2,d/2
    v = np.array([-hw,-hh,-hd, hw,-hh,-hd, hw,hh,-hd, -hw,hh,-hd,
                  -hw,-hh, hd, hw,-hh, hd, hw,hh, hd, -hw,hh, hd], np.float32)
    n = np.array([0,0,-1]*4 + [0,0,1]*4, np.float32)
    uv = np.array([0,0,1,0,1,1,0,1]*2, np.float32)
    t = np.array([0,1,2,0,2,3, 4,5,6,4,6,7], np.uint16)
    return v, n, uv, t

def make_sphere(radius, segs=10):
    verts, norms, uvs, tris = [], [], [], []
    for i in range(segs+1):
        theta = np.pi*i/segs
        for j in range(segs+1):
            phi = 2*np.pi*j/segs
            x = radius*np.sin(theta)*np.cos(phi)
            y = radius*np.cos(theta)
            z = radius*np.sin(theta)*np.sin(phi)
            verts += [x,y,z]; norms += [x/radius,y/radius,z/radius]; uvs += [j/segs,i/segs]
    for i in range(segs):
        for j in range(segs):
            a = i*(segs+1)+j
            tris += [a, a+1, a+segs+1, a+1, a+segs+2, a+segs+1]
    return np.array(verts,np.float32), np.array(norms,np.float32), np.array(uvs,np.float32), np.array(tris,np.uint16)

# Re-Pete: 5'10" (with boots), slim build, age 22
# Canon 5'7" = ~1.70m. Slight forward-lean anxious posture implied.
# Key visual: curly auburn hair, beard, black cat t-shirt, blue jeans,
# brown boots (3" lifted), messenger bag strap, watch, camera around neck

BONES = [
    ("root",         -1, [0, 0, 0]),
    ("pelvis",        0, [0, 0.87, 0]),       # slim hips
    ("spine_01",      1, [0, 0.10, 0]),
    ("spine_02",      2, [0, 0.10, 0]),
    ("spine_03",      3, [0, 0.10, 0]),        # slight slouch built into mesh
    ("neck_01",       4, [0, 0.13, 0]),
    ("head",          5, [0, 0.09, 0]),
    ("jaw",           6, [0, -0.04, 0.04]),
    ("eye_l",         6, [0.032, 0.02, 0.07]),
    ("eye_r",         6, [-0.032, 0.02, 0.07]),
    ("clavicle_l",    4, [0.06, 0.04, 0]),
    ("upperarm_l",   10, [0.15, 0, 0]),
    ("lowerarm_l",   11, [0.25, 0, 0]),
    ("hand_l",       12, [0.22, 0, 0]),
    ("index_01_l",   13, [0.05, 0, 0.02]),
    ("middle_01_l",  13, [0.05, 0, 0.005]),
    ("ring_01_l",    13, [0.05, 0, -0.01]),
    ("pinky_01_l",   13, [0.04, 0, -0.025]),
    ("thumb_01_l",   13, [0.03, 0.01, 0.03]),
    ("clavicle_r",    4, [-0.06, 0.04, 0]),
    ("upperarm_r",   19, [-0.15, 0, 0]),
    ("lowerarm_r",   20, [-0.25, 0, 0]),
    ("hand_r",       21, [-0.22, 0, 0]),
    ("index_01_r",   22, [-0.05, 0, 0.02]),
    ("middle_01_r",  22, [-0.05, 0, 0.005]),
    ("ring_01_r",    22, [-0.05, 0, -0.01]),
    ("pinky_01_r",   22, [-0.04, 0, -0.025]),
    ("thumb_01_r",   22, [-0.03, 0.01, 0.03]),
    ("thigh_l",       1, [0.09, -0.04, 0]),
    ("calf_l",       28, [0, -0.42, 0]),
    ("foot_l",       29, [0, -0.40, 0.05]),
    ("ball_l",       30, [0, -0.09, 0.09]),
    ("thigh_r",       1, [-0.09, -0.04, 0]),
    ("calf_r",       32, [0, -0.42, 0]),
    ("foot_r",       33, [0, -0.40, 0.05]),
    ("ball_r",       34, [0, -0.09, 0.09]),
    ("ik_foot_l",    -1, [0.09, 0.02, 0]),
    ("ik_foot_r",    -1, [-0.09, 0.02, 0]),
    ("ik_hand_l",    -1, [0.52, 0.87, 0]),
    ("ik_hand_r",    -1, [-0.52, 0.87, 0]),
    ("hair_top",      6, [0, 0.11, -0.01]),    # volume for curly hair
    ("hair_side_l",   6, [0.08, 0.04, 0]),
    ("hair_side_r",   6, [-0.08, 0.04, 0]),
    ("hair_back",     6, [0, 0.02, -0.09]),
    ("hair_fringe",   6, [0, 0.07, 0.08]),
    ("breast_l",      3, [0.08, 0.04, 0.04]),
    ("breast_r",      3, [-0.08, 0.04, 0.04]),
    ("brow_l",        6, [0.04, 0.055, 0.07]),
    ("brow_r",        6, [-0.04, 0.055, 0.07]),
    ("cheek_l",       6, [0.05, -0.01, 0.06]),
    ("cheek_r",       6, [-0.05, -0.01, 0.06]),
    ("lip_upper",     7, [0, 0.01, 0.02]),
    ("lip_lower",     7, [0, -0.01, 0.02]),
    ("lip_corner_l",  7, [0.025, 0, 0.015]),
    ("lip_corner_r",  7, [-0.025, 0, 0.015]),
    ("camera_bone",   6, [0, 0.05, 0.30]),
    # Extra: bag strap bone, camera prop bone
    ("bag_strap",     3, [0.12, 0.05, 0.03]),
    ("camera_prop",  12, [0, -0.12, 0.05]),    # hangs from hand_l area
]

# Materials:
# 0=skin(warm freckled) 1=hair_auburn 2=beard_auburn 3=tshirt_black
# 4=jeans_blue 5=boot_brown 6=eye_iris_green 7=eye_white
# 8=lip 9=watch_leather 10=bag_leather_brown 11=camera_black

MESH_PARTS = [
    # name, mat_idx, generator
    ("repete_torso_base",    3, lambda: make_cylinder(0.115, 0.125, 0.38, 14)),  # slim torso, black tshirt
    ("repete_pelvis_base",   4, lambda: make_cylinder(0.118, 0.115, 0.16, 14)),  # jeans hips
    ("repete_sleeve_l",      3, lambda: make_cylinder(0.042, 0.050, 0.26, 10)),  # tshirt sleeve
    ("repete_sleeve_r",      3, lambda: make_cylinder(0.042, 0.050, 0.26, 10)),
    ("repete_forearm_l",     0, lambda: make_cylinder(0.035, 0.042, 0.23, 10)),  # bare arm
    ("repete_forearm_r",     0, lambda: make_cylinder(0.035, 0.042, 0.23, 10)),
    ("repete_hand_l",        0, lambda: make_box(0.082, 0.090, 0.036)),
    ("repete_hand_r",        0, lambda: make_box(0.082, 0.090, 0.036)),
    ("repete_thigh_l",       4, lambda: make_cylinder(0.068, 0.075, 0.42, 12)),  # slim jeans
    ("repete_shin_l",        4, lambda: make_cylinder(0.052, 0.065, 0.40, 12)),
    ("repete_thigh_r",       4, lambda: make_cylinder(0.068, 0.075, 0.42, 12)),
    ("repete_shin_r",        4, lambda: make_cylinder(0.052, 0.065, 0.40, 12)),
    ("repete_boot_l",        5, lambda: make_box(0.11, 0.13, 0.30)),             # tall lifted boots
    ("repete_boot_r",        5, lambda: make_box(0.11, 0.13, 0.30)),
    ("repete_belt",          10, lambda: make_cylinder(0.128, 0.128, 0.03, 14, cap=False)),
    ("repete_face_mesh",     0, lambda: make_sphere(0.098, 12)),
    ("repete_beard",         2, lambda: make_cylinder(0.070, 0.085, 0.08, 12, cap=False)),  # beard volume
    ("repete_eye_l",         6, lambda: make_sphere(0.013, 8)),
    ("repete_eye_r",         6, lambda: make_sphere(0.013, 8)),
    ("repete_eye_white_l",   7, lambda: make_sphere(0.012, 8)),
    ("repete_eye_white_r",   7, lambda: make_sphere(0.012, 8)),
    ("repete_neck",          0, lambda: make_cylinder(0.050, 0.056, 0.12, 10)),
    # Curly hair — multiple overlapping volumes for volume
    ("repete_hair_cap",      1, lambda: make_sphere(0.108, 10)),
    ("repete_hair_vol_top",  1, lambda: make_sphere(0.055, 8)),                  # extra curl volume top
    ("repete_hair_vol_l",    1, lambda: make_sphere(0.045, 8)),                  # side poof L
    ("repete_hair_vol_r",    1, lambda: make_sphere(0.045, 8)),                  # side poof R
    ("repete_hair_fringe",   1, lambda: make_box(0.09, 0.04, 0.04)),
    ("repete_hair_back",     1, lambda: make_box(0.08, 0.09, 0.05)),
    # Accessories
    ("repete_watch",         9, lambda: make_box(0.032, 0.016, 0.032)),
    ("repete_bag_strap",    10, lambda: make_box(0.018, 0.55, 0.012)),           # diagonal strap
    ("repete_bag_body",     10, lambda: make_box(0.22, 0.18, 0.06)),             # messenger bag
    ("repete_camera_body",  11, lambda: make_box(0.11, 0.08, 0.06)),            # Nikon body
    ("repete_camera_lens",  11, lambda: make_cylinder(0.030, 0.030, 0.06, 10)), # lens
]

# Bone index per mesh part
PART_BONE = [
    3,   # torso → spine_02
    1,   # pelvis
    11,  # sleeve_l → upperarm_l
    20,  # sleeve_r → upperarm_r
    12,  # forearm_l → lowerarm_l
    21,  # forearm_r
    13,  # hand_l
    22,  # hand_r
    28,  # thigh_l
    29,  # shin_l → calf_l
    32,  # thigh_r
    33,  # shin_r
    30,  # boot_l → foot_l
    34,  # boot_r
    1,   # belt → pelvis
    6,   # face → head
    7,   # beard → jaw
    8,   # eye_l
    9,   # eye_r
    8,   # eye_white_l
    9,   # eye_white_r
    5,   # neck → neck_01
    40,  # hair_cap → hair_top (bone idx 40)
    40,  # hair_vol_top
    41,  # hair_vol_l → hair_side_l
    42,  # hair_vol_r → hair_side_r
    44,  # hair_fringe
    43,  # hair_back
    13,  # watch → hand_l (wrist area)
    56,  # bag_strap → bag_strap bone
    56,  # bag_body → bag_strap bone
    57,  # camera_body → camera_prop bone
    57,  # camera_lens
]

class GLBBuilder:
    def __init__(self):
        self.gltf = pygltflib.GLTF2()
        self.gltf.asset = pygltflib.Asset(version="2.0", generator="RePete_v1")
        self.buf = bytearray()
        self.gltf.buffers = [pygltflib.Buffer(byteLength=0)]
        self.acc_i = 0; self.bv_i = 0

    def add_bv(self, data, target=None):
        off = len(self.buf)
        pad = (4 - len(data)%4)%4
        self.buf += data + bytes(pad)
        self.gltf.bufferViews.append(pygltflib.BufferView(buffer=0, byteOffset=off, byteLength=len(data), target=target))
        i = self.bv_i; self.bv_i += 1; return i

    def add_acc(self, bv, ct, count, atype, mn=None, mx=None):
        a = pygltflib.Accessor(bufferView=bv, byteOffset=0, componentType=ct, count=count, type=atype)
        if mn: a.min=mn
        if mx: a.max=mx
        self.gltf.accessors.append(a)
        i = self.acc_i; self.acc_i += 1; return i

    def add_mesh(self, name, v, n, uv, tri, mat, joints, weights):
        AB, EAB = 34962, 34963
        bvp=self.add_bv(v.tobytes(),AB); bvn=self.add_bv(n.tobytes(),AB)
        bvu=self.add_bv(uv.tobytes(),AB); bvt=self.add_bv(tri.tobytes(),EAB)
        bvj=self.add_bv(joints.tobytes(),AB); bvw=self.add_bv(weights.tobytes(),AB)
        nv=len(v)//3; mn=v.reshape(-1,3).min(0).tolist(); mx=v.reshape(-1,3).max(0).tolist()
        ap=self.add_acc(bvp,5126,nv,"VEC3",mn,mx); an=self.add_acc(bvn,5126,nv,"VEC3")
        au=self.add_acc(bvu,5126,nv,"VEC2"); at=self.add_acc(bvt,5123,len(tri),"SCALAR")
        aj=self.add_acc(bvj,5121,nv,"VEC4"); aw=self.add_acc(bvw,5126,nv,"VEC4")
        prim=pygltflib.Primitive(attributes=pygltflib.Attributes(POSITION=ap,NORMAL=an,TEXCOORD_0=au,JOINTS_0=aj,WEIGHTS_0=aw),indices=at,material=mat)
        self.gltf.meshes.append(pygltflib.Mesh(name=name,primitives=[prim]))
        return len(self.gltf.meshes)-1

def build():
    b = GLBBuilder(); g = b.gltf

    def mat(name, r, gr, gb, metallic=0.0, rough=0.85):
        return pygltflib.Material(name=name, pbrMetallicRoughness=pygltflib.PbrMetallicRoughness(
            baseColorFactor=[r,gr,gb,1.0], metallicFactor=metallic, roughnessFactor=rough))

    g.materials = [
        mat("skin_warm",    0.82, 0.64, 0.50),           # 0  warm freckled skin
        mat("hair_auburn",  0.55, 0.18, 0.06),           # 1  rich auburn/copper
        mat("beard_auburn", 0.52, 0.17, 0.05),           # 2  slightly darker beard
        mat("tshirt_black", 0.08, 0.08, 0.09),           # 3  near-black tshirt
        mat("jeans_blue",   0.22, 0.35, 0.58),           # 4  medium blue denim
        mat("boot_brown",   0.28, 0.16, 0.07, 0.05, 0.6),# 5  warm brown leather boots
        mat("eye_green",    0.22, 0.42, 0.28),           # 6  hazel-green iris
        mat("eye_white",    0.96, 0.94, 0.92),           # 7
        mat("lip",          0.65, 0.40, 0.35),           # 8
        mat("watch_tan",    0.45, 0.28, 0.12, 0.0, 0.7),# 9  leather watch strap
        mat("bag_leather",  0.32, 0.18, 0.08, 0.05, 0.6),# 10 messenger bag brown
        mat("camera_black", 0.06, 0.06, 0.07, 0.3, 0.4),# 11 matte camera body
    ]

    bone_nodes = []
    for bname, pidx, trans in BONES:
        node = pygltflib.Node(name=bname, translation=trans)
        g.nodes.append(node); bone_nodes.append(len(g.nodes)-1)
    for i,(_, pidx, _) in enumerate(BONES):
        if pidx>=0:
            pn = g.nodes[bone_nodes[pidx]]
            if not pn.children: pn.children=[]
            pn.children.append(bone_nodes[i])

    n_bones = len(BONES)
    ibm = np.tile(np.eye(4,dtype=np.float32).flatten(), n_bones)
    bv_ibm = b.add_bv(ibm.tobytes())
    a_ibm = b.add_acc(bv_ibm, 5126, n_bones, "MAT4")
    g.skins.append(pygltflib.Skin(name="repete_rig_58", inverseBindMatrices=a_ibm, joints=list(bone_nodes)))

    mesh_nodes = []
    for pi,(name,mat_idx,gen) in enumerate(MESH_PARTS):
        v,n,uv,tri = gen()
        nv = len(v)//3
        pb = PART_BONE[pi]
        joints  = np.zeros((nv,4),np.uint8);  joints[:,0]=pb
        weights = np.zeros((nv,4),np.float32); weights[:,0]=1.0
        midx = b.add_mesh(name,v,n,uv,tri,mat_idx,joints.flatten(),weights.flatten())
        node = pygltflib.Node(name=f"node_{name}", mesh=midx, skin=0)
        g.nodes.append(node); mesh_nodes.append(len(g.nodes)-1)

    orphans = [36,37,38,39]
    scene_ch = [bone_nodes[0]] + [bone_nodes[i] for i in orphans] + mesh_nodes
    g.scenes.append(pygltflib.Scene(name="RePete_T-Pose", nodes=scene_ch))
    g.scene = 0
    g.buffers[0].byteLength = len(b.buf)
    g.set_binary_blob(bytes(b.buf))
    out = "/home/claude/repete_v1.glb"
    g.save(out)
    print(f"Saved {out}  ({len(b.buf):,} bytes)")

build()
