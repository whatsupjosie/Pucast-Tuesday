# PubCast AI — GPT Safe Merge Audit
Date: 2026-05-02
Branch: `dinner`

## Safety Position

This is a non-destructive merge/audit note. No source files were deleted, moved, or overwritten by this audit step.

The prior Claude handoff said the correct doctrine was: use v5.5 as the trusted base, layer in newer GitHub-only April 29 files, back up every overwritten file, and do not blindly delete or replace new work. That doctrine is preserved here. The handoff also reported 107/107 tests passing in the v5.5 zip environment, but those zip bytes were not mounted in this GPT sandbox, so I did not claim a completed zip merge without the actual payload. See the pasted handoff transcript for the original context.

## Actual Finding From Current GitHub Inspection

The current `dinner` branch already contains several files that the earlier handoff described as missing or recovered only from v5.5:

- `modules/voxel_asset_manager.py`
- `modules/voxel_llm_adapter.py`
- `modules/voxel_studio_integration.py`
- `modules/studio_websocket.py`
- `modules/pubworld_router.py`
- `modules/unity_bridge.py`
- `bin/ws_renderer`

That means the safe strategy is no longer "replace GitHub with v5.5." The safe strategy is now:

1. Verify the live `dinner` tree.
2. Verify the actual local v5.5 zip payload.
3. Compare donor files by path and hash.
4. Patch only files that are truly missing, corrupt, or older.
5. Preserve all GitHub-only April 29 resurrection/security/cast work.
6. Never force-push until tests and manifest prove the result.

## Known Risk: Renderer Binary

`bin/ws_renderer` exists as a GitHub path/blob, but this audit could not prove its byte size through the connector. Local verification must check that the renderer is not empty or truncated.

Run from `Pubcast Tuesday`:

```powershell
Get-Item ".\bin\ws_renderer*" | Select-Object FullName,Length
```

Prior expected size from Claude handoff was roughly 9.3MB. Anything tiny means the renderer must be restored from the v5.5 zip.

## Known Risk: Design-Pattern / Stub Boundaries

Some current files are useful but not fully finished runtime integration:

- `voxel_asset_manager.py` has real asset catalog and scene/preflight structure, but its preloading/Rust sync still contains TODO/simulated integration behavior.
- `voxel_studio_integration.py` documents an integration pattern and depends on Studio Control extensibility hooks.
- `pubworld_router.py` has real WebSocket broadcasting, but `/pubworld/state` is explicitly a stub snapshot endpoint.

These are not trash. They should be preserved, but not misrepresented as final renderer integration.

## Added Verification Tools

- `tools/Verify-PubCastMerge.ps1`
- `tools/Start-PubCastWithRenderer.ps1`

These are additive only and safe to keep in the repo.
