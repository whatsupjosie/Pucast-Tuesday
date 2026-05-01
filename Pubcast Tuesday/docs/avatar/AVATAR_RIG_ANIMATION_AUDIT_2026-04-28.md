# Avatar Rig Animation Audit - 2026-04-28

This audit covers the staged Pete, RePete, and Sir Purfluous GLBs currently in `assets/avatar/cast`.

## Primary Best-Practice Notes

- glTF supports real-time delivery of meshes, materials, skinning, morph targets, and animation clips. For animation, keep the exported data inside glTF-supported channels: object transforms, pose bones, and shape-key values.
- Blender glTF export should use actions/NLA tracks deliberately, reset pose bones between actions when actions do not key every bone, and sample animations when needed for reliable export.
- Keep skinning to four influences per vertex for broad runtime compatibility. Blender's glTF exporter warns that allowing more than four influences may display incorrectly in many viewers.
- Three.js expects skinned meshes to have valid `skinIndex` and `skinWeight` attributes, and `AnimationMixer` can play glTF animation clips when clips are present.

Reference sources:

- Blender glTF exporter manual: https://docs.blender.org/manual/en/latest/addons/import_export/scene_gltf2.html
- Three.js `SkinnedMesh`: https://threejs.org/docs/pages/SkinnedMesh.html
- Khronos glTF 2.0 specification: https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html

## Current GLB Audit

Command:

```powershell
node tools/audit_glb_rigs.mjs `
  "assets/avatar/cast/pete/pete_avatar_pubcast_v56.glb" `
  "assets/avatar/cast/repete/repete_v1.glb" `
  "assets/avatar/cast/purfluous/sir_purfluous_v1.glb"
```

### Pete

- File: `assets/avatar/cast/pete/pete_avatar_pubcast_v56.glb`
- Joints: 56
- Vertices: 4,259
- Animations: 0
- Morph targets: 28 on one primitive
- Skin weights: normalized; no bad rows found
- Scene shape: clean single root, `pete_armature`
- Skeleton root: `root`

Pete is the strongest animation asset today. She has the shared body rig and facial morph targets for lipsync and expressions.

### RePete

- File: `assets/avatar/cast/repete/repete_v1.glb`
- Joints: 58
- Vertices: 1,285
- Animations: 0
- Morph targets: 0
- Skin weights: normalized; no bad rows found
- Scene shape: many scene roots, including mesh roots and IK controls
- Skeleton root: missing from skin metadata
- Extra bones: `bag_strap`, `camera_prop`

RePete shares Pete's first 56 ordered joints exactly, then adds two prop bones. That is good for body retargeting, but he needs a cleaner export and face morph targets before he can match Pete's expressiveness.

### Sir Purfluous

- File: `assets/avatar/cast/purfluous/sir_purfluous_v1.glb`
- Joints: 56
- Vertices: 1,018
- Animations: 0
- Morph targets: 0
- Skin weights: normalized; no bad rows found
- Scene shape: many scene roots, including mesh roots and IK controls
- Skeleton root: missing from skin metadata

Sir Purfluous shares Pete's 56 ordered joints exactly. Body animation retargeting should be straightforward after export cleanup. His face needs morph targets and/or pose bones wired for performance.

## Key Findings

The shared skeleton is real and usable. Pete and Sir Purfluous match exactly by ordered joint name. RePete matches those same 56 joints and adds two useful prop bones.

The skin weights are healthy. All tested vertices sum to 1.0 and use only `JOINTS_0`/`WEIGHTS_0`, keeping the assets within the common four-influence limit.

The cast GLBs do not contain baked animation clips yet. `static/avatar_glow.js` already has `AnimationMixer` support, but there is nothing for it to play on these files until we add idle/walk/gesture clips or stream poses into the skeleton.

Pete has morph targets. RePete and Sir Purfluous do not yet. That means Pete can support face/lipsync much sooner; the other two will look rigid above the neck until morph targets or facial bone driving are added.

RePete and Sir Purfluous need export cleanup. Their meshes and IK controls are separate scene roots, and their skins do not declare `skin.skeleton`. Many viewers tolerate this, but a clean single armature/root export will reduce retargeting weirdness.

## Recommended Next Build Order

1. Make Pete the animation reference character.
   - Keep her 56-joint rig as the body standard.
   - Use her 28 morph targets as the starting face/lipsync standard.
   - Create or import short `idle`, `walk`, `turn`, `sit_idle`, `talk`, and `gesture_open` clips.

2. Clean RePete and Sir Purfluous exports.
   - Ensure one clean scene root.
   - Set `skin.skeleton` to `root`.
   - Keep IK controls available in Blender source but do not export them as loose runtime scene roots unless needed.
   - Add face morph targets matching Pete's names where possible.

3. Use a shared animation contract.
   - Body clip names: `idle`, `walk`, `turn`, `sit_idle`, `talk`, `gesture_open`, `gesture_think`.
   - Face target names should match Pete's current `vis_*` and `expr_*` set.
   - Runtime should fall back gracefully when a clip or morph target is missing.

4. Keep performance constraints simple.
   - Prefer one skinned mesh hierarchy per character.
   - Keep <= 4 bone influences per vertex.
   - Keep clip count small and reusable.
   - Use morph targets for faces, not full mesh swaps.
   - Avoid physics-driven animation until the core clips are stable.

## Current Tooling Blocker

Blender was not found on PATH or in common install locations during this audit. Python was also unavailable in the current PowerShell environment. Blender is needed for the next real export pass.

When Blender is available, run the Sir Purfluous automation first, then use that path as the template for RePete and Pete polish exports.
