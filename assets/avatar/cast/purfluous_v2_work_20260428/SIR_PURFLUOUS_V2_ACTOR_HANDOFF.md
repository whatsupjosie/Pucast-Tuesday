# Sir Purfluous v2 Actor Avatar Handoff

Date: 2026-04-28

## Non-Destructive Boundary

This folder is a copied work area:

- `assets/avatar/cast/purfluous_v2_work_20260428/`

The original staged Sir Purfluous folder was not edited:

- `assets/avatar/cast/purfluous/`

The build reads `sir_purfluous_v1_sourcecopy.glb` and writes new v2 files in this work folder only.

## New Outputs

- `sir_purfluous_v2_actor.glb`
- `sir_purfluous_v2_actor.blend`
- `build_sir_purfluous_v2_actor.py`
- `run_blender_51_build_v2.bat`
- `inspect_sir_purfluous_v2_actor.py`
- `sir_purfluous_v2_actor_inspection.json`

## Character Direction Used

Reference: `assets/characters/canon/sir_purfluous_reference.png`

V2 pushes the staged v1 body toward the canonical Vincent Holloway / Sir Purfluous read:

- older theatrical actor
- tawny brown suit
- cream shirt
- silver-white hair
- beard and mustache
- expressive brows
- vest buttons
- pocket square
- pocket watch and chain
- warmer aged skin materials

## Rig / Export Audit

Audited with `tools/audit_glb_rigs.mjs`.

Result:

- GLB loads.
- 56 joints preserved.
- 1 skin preserved.
- skin weights normalized.
- 15 morph target names exported.
- no duplicate joints.
- no baked animations.

Note: the audit reports IK controls as unreachable:

- `ik_foot_l`
- `ik_foot_r`
- `ik_hand_l`
- `ik_hand_r`

That appears consistent with the staged rig style and should be reviewed in the next animation/retargeting pass rather than treated as a destructive blocker here.

## Known Limitations

This is a first Blender 5.1 actor pass, not final lock.

- Added beard, mustache, brows, pocket square, watch, chain, buttons, and tie are separate visual meshes.
- Those new detail meshes are not yet skinned/weighted to the head or torso bones.
- Shape keys are named and exported, but they still need sculpted expression deltas.
- Blender 5.1 crashed when attempting an EEVEE preview render on this machine, so the final build script skips rendering and exports only `.blend` and `.glb`.

## Next Avatar Pass

1. Open `sir_purfluous_v2_actor.blend`.
2. Parent/weight the added face details to the head/face bones.
3. Parent/weight pocket details to the chest/spine area.
4. Sculpt the expression shape keys:
   - thoughtful
   - amused
   - angry
   - shocked
   - contemptuous
   - passionate
   - mouth_open
   - visemes
5. Add a small idle animation set:
   - theatrical hand lift
   - doorway host bow
   - thoughtful chin touch
   - pocket-watch check
6. Only after review, copy a final approved GLB into the runtime `purfluous` folder.
