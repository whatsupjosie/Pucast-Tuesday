# PubCast 6.0 Current Handoff

Created: 2026-04-29

## Status

This snapshot represents the current PubCast working state after the local brain change.
For practical purposes this is the PubCast 6.0 working line, pending the later Gemma 4 E2B Q4/Q5 compute-brain work.

## Primary Local Brain

PubCast is currently wired to use:

```text
ministral-pubcast:3b
```

This is a small-context Ollama wrapper around the installed Ministral 3B model.

Observed behavior:

- Cold load is still slow, about 45 seconds.
- Warm response is usable, about 5 seconds in the latest check.
- Ollama reports the wrapper loads with `context_length: 2048`.

## Important Runtime Fixes Applied

The app was patched so cold Ministral startup does not block PubCast boot:

- Studio warmup now runs in the background.
- PubCast requests include `keep_alive: "1h"`.
- PubCast requests keep `num_ctx: 2048`.
- Default reply budget is reduced to `num_predict: 160`.
- Ollama timeout is now `180` seconds.

Files touched for model/runtime behavior include:

```text
.env.example
data/bots/pete.json
data/bots/repeat.json
data/bots/sir_purfluous.json
modules/bots.py
modules/llm_framework.py
modules/llm_orchestrator.py
modules/ollama_provider.py
modules/performance_manager.py
modules/byok_routes.py
static/byok.html
system_policy.json
```

## PubCast Memory / Identity Work

The session resurrection layer is now wired into PubCast entry paths.

Session entry now attempts `SessionResurrector` first, then falls back to the previous Alex/Jeremy bridge packet if resurrection fails.

Affected routes:

- `POST /api/session/register`
- `POST /api/dressing-room/resolve`

Those responses now include:

```text
alex_bridge
jeremy_whisper
session_resurrection
```

The verified core test showed:

```text
memory_count=1
resumed=True
summary=1 memories loaded, offline 0min, mood=guide, battery=medium
whisper_has_memory=True
```

Files touched for resurrection wiring:

```text
main.py
modules/session_resurrector.py
modules/alex_jeremy_bridge.py
```

`modules/session_resurrector.py` already existed; this work connected it into live entry flow.

## Validation Notes

Normal `python` is still not visible in the Codex shell.

Usable validation Python found at:

```text
C:\Program Files\Blender Foundation\Blender 5.1\5.1\python\bin\python.exe
```

Syntax checks passed with Blender Python for the edited core files.

`pytest` is not installed in Blender Python, so the focused test suite could not be run through pytest.
The core resurrection flow was executed directly and passed.

## Backups Created During This Work

```text
backup_pre_ministral_pubcast_wiring_20260429_codex
backup_pre_ministral_runtime_tuning_20260429_codex
backup_pre_ministral_boot_fix_20260429_codex
backup_pre_pubcast_resurrection_wiring_20260429_codex
```

An earlier important snapshot also exists:

```text
snapshots/PUBCAST_SNAPSHOT_20260429_083521.md
```

## Ollama Safety Notes

Use one loaded model at a time on this machine.

Avoid making these defaults right now:

```text
gemma4:e2b
gemma4:e4b
qwen2.5-coder:7b
raw ministral-3:3b
```

Gemma 4 E2B should be tested later as a small-context compute wrapper before being wired into PubCast.

## Portable Identity Filter Seed

A separate seed folder was created outside this PubCast repo:

```text
C:\Users\hardc\OneDrive\Documents\Playground\Portable Identity Filter
```

That is not yet the priority. PubCast is the proving ground first.

## Recommended Next Step

Before adding Gemma 4 compute-brain wiring, verify the current PubCast flow:

1. Start Ollama.
2. Wake `ministral-pubcast:3b`.
3. Start PubCast.
4. Register/resolve a session user.
5. Confirm the response includes `session_resurrection`.
6. Confirm the first character response uses the warmed Ministral path.

After that, create a dedicated Gemma 4 E2B compute wrapper with `num_ctx 2048`, test it alone, and only then wire it as a secondary compute role.

