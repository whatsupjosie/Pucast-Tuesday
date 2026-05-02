# PubCast AI — GPT Safe Merge Audit
Date: 2026-05-02
Branch: `gpt-safe-merge-staging-2026-05-02`
Base branch/commit source: current GitHub `dinner` snapshot commit `0c1f74756ec6a208727f51822748ffec22a3370b`

## Safety Position

This branch is intentionally non-destructive.

No source files were deleted.
No runtime data was moved.
No zip files were overwritten.
No `dinner` branch files were directly changed.

This branch exists to stage merge/audit tooling and document the verified current state before any real replacement or force-push operation.

## What Was Actually Verified

The current GitHub `dinner` branch already contains several files that the earlier Claude transcript described as missing from GitHub:

- `Pubcast Tuesday/modules/voxel_asset_manager.py`
- `Pubcast Tuesday/modules/voxel_llm_adapter.py`
- `Pubcast Tuesday/modules/voxel_studio_integration.py`
- `Pubcast Tuesday/modules/studio_websocket.py`
- `Pubcast Tuesday/modules/pubworld_router.py`
- `Pubcast Tuesday/modules/unity_bridge.py`
- `Pubcast Tuesday/bin/ws_renderer`

That means the previous handoff claim, "GitHub dinner is missing all of these," is no longer safe to treat as current truth without re-running a full local checkout/test. The branch may have advanced, or the earlier session may have been looking at a different/incomplete snapshot.

## Known Risk: Binary Renderer Verification

`bin/ws_renderer` exists in GitHub, but the GitHub connector returned an empty base64 content body for the binary fetch while still providing a blob SHA. That verifies a path/blob record exists, but it does **not** prove the binary is usable or has the expected 9.3MB payload.

Required local check on Windows:

```powershell
Get-Item ".\bin\ws_renderer*" | Select-Object FullName,Length
```

Expected from prior Claude handoff: approximately 9.3MB. Anything empty or very small means the renderer binary was not actually preserved correctly.

## Known Risk: Stub / Design-Pattern Code Still Present

The following files are useful, but not all are production-complete:

- `voxel_asset_manager.py` contains real catalog/scene/preflight structure, but its `preload_scene_assets` and Rust sync areas still contain TODO/simulated integration behavior.
- `voxel_studio_integration.py` states that actual preflight hook registration depends on Studio Control extensibility; it is partly an integration pattern, not a fully wired runtime hook.
- `pubworld_router.py` has a real WebSocket broadcaster, but `/pubworld/state` is explicitly a stub convenience endpoint.

These should not be deleted, but they should not be represented as finished renderer/runtime integration either.

## Merge Doctrine Going Forward

1. Use the current `dinner` repo as the live GitHub baseline.
2. Use `PubCast_AI_v5.5_AIS_READY.zip` only as a donor source, not as a blind replacement.
3. For every donor file:
   - compare path exists / missing,
   - compare hashes,
   - compare import surface,
   - backup overwritten GitHub version,
   - prefer newer GitHub code where it contains April 29 resurrection/security/cast work,
   - preserve v5.5-only renderer/Rust/assets if GitHub lacks or corrupts them.
4. Never delete GitHub-only files merely because the v5.5 zip lacks them.
5. Do not force-push until tests and manifest confirm the merged result.

## Files Added By This Staging Branch

- `docs/merge/GPT_SAFE_MERGE_AUDIT_2026-05-02.md`
- `tools/Start-PubCastWithRenderer.ps1`
- `tools/Verify-PubCastMerge.ps1`

## Required Local Inputs Still Needed For Full Merge

The actual zip bytes were not mounted in the GPT sandbox during this run. A real final merge still needs local access to:

- `PubCast_AI_v5.5_AIS_READY.zip`
- `pubcast_mined_old_files_package.zip`
- optionally `PUBCAST_OLD_FILES_CAPTURE_NONDESTRUCTIVE_2026-04-30.zip`

Until those zip contents are physically available to the runner, any claim of a completed v5.5-vs-GitHub merge would be false.
