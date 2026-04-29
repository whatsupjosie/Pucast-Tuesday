# Re-Pete — Asset Handoff
**Date:** April 25, 2026 | **Status:** v1 GLB — audit PASSED (0 errors, 0 warnings)

## What's in this zip
| File | Description |
|------|-------------|
| `repete_v1.glb` | Rigged character — 58 bones, 33 mesh parts, T-pose |
| `build_repete.py` | Source script to rebuild from scratch |

## Character Specs (from reference sheet)
- Age 22, slim build, 5'7" canon height (~1.70m in rig)
- Auburn/copper curly hair (4 overlapping mesh volumes)
- Beard on jaw bone (separate mesh, animates with jaw)
- Black cat t-shirt, blue jeans, tall brown boots (lifted)
- Props rigged: messenger bag (bag_strap bone), Nikon camera (camera_prop bone), watch

## Rig — 58 bones
Standard 56 + 2 extras: `bag_strap`, `camera_prop`  
UE5/Mixamo compatible. IK targets: ik_foot_l/r, ik_hand_l/r  
Facial: brow L/R, cheek L/R, jaw, lip upper/lower/corners, eye L/R

## Materials (12)
skin_warm, hair_auburn, beard_auburn, tshirt_black, jeans_blue,  
boot_brown, eye_green, eye_white, lip, watch_tan, bag_leather, camera_black

## Audit Results
- ✓ Buffer integrity (82,652 bytes, exact match)
- ✓ Triangle indices all in range
- ✓ Skin weights sum to 1.0
- ✓ All 58 joints reachable from scene root
- ✓ All 33 mesh nodes reference skin 0
- ✓ No duplicate bone names
- ✓ All material indices in range

## Next Steps
1. Run through Blender script (adapt sir_purfluous_blender.py — change INPUT_GLB, update reshape values for slim build)
2. Sculpt shape key expressions on face mesh
3. Retarget Pete's animations directly (same rig structure)
