# Sir Purfluous — Asset Handoff
**Date:** April 25, 2026 | **Status:** v1 GLB — audit PASSED (0 errors, 0 warnings)

## What's in this zip
| File | Description |
|------|-------------|
| `sir_purfluous_v1.glb` | Rigged character — 56 bones, 28 mesh parts, T-pose |
| `build_sir_purfluous.py` | Source script to rebuild from scratch |
| `sir_purfluous_blender.py` | Blender automation — reshapes, materials, shape keys, exports v2 |
| `run_blender.bat` | Double-click to run Blender headlessly. No Blender knowledge needed. |

## Character Specs
- Older gentleman, stocky build, dignified but slightly disheveled
- Warm brown suit, cream shirt, silver-grey hair, aged skin
- Dark brown leather boots, near-black belt

## Rig — 56 bones
UE5/Mixamo compatible. IK targets: ik_foot_l/r, ik_hand_l/r  
Facial: brow L/R, cheek L/R, jaw, lip upper/lower/corners, eye L/R  
Hair: top, side L/R, back, fringe | camera_bone for face cam

## Materials (10)
skin, boxer, suit_brown, shirt_white, shoe_brown,  
belt_black, hair_grey, eye_iris, eye_white, lip

## Blender Automation (run_blender.bat)
1. Reshapes to stocky older proportions (torso +18%, hips +20%)
2. Applies Too Much to Bear stylized cel-edge materials
3. Catmull-Clark subdivision on face (level 2 viewport / 3 render)
4. Adds 23 named shape keys: brow, eyes, cheeks, mouth, jaw, lips, 6 visemes
5. Exports sir_purfluous_v2.glb

## Audit Results
- ✓ Buffer integrity (66,264 bytes, exact match)
- ✓ Triangle indices all in range
- ✓ Skin weights sum to 1.0
- ✓ All 56 joints reachable from scene root
- ✓ All 28 mesh nodes reference skin 0
- ✓ No duplicate bone names
- ✓ All material indices in range

## Next Steps
1. Double-click run_blender.bat → get sir_purfluous_v2.glb
2. Open v2 in Blender, sculpt the 23 shape key expressions
3. Mocap retarget: same 56-bone structure as Pete rig
