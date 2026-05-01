# Pubcast Tuesday

This repo is the Tuesday rehearsal-week formalization of the current PubCast
5.6 working copy, prepared on 2026-04-28.

## Source

- Copied from `pubcast_v5_6_baby_role_work_2026-04-28`.
- Created non-destructively; the source working copy was not moved or deleted.

## Default Shape

- FastAPI/Python production hub with `main.py` as the boot and wiring entry.
- Local Ollama is the default AI path.
- Current bot defaults:
  - Pete: `ollama` / `gemma3:1b`
  - RePete: `ollama` / `gemma3:1b`
  - Sir Purfluous: `ollama` / `gemma4:e2b`
- Optional GGUF Architect path remains configurable with
  `PUBCAST_ARCHITECT_MODEL`.
- Rust animation bridge source and `bin/ws_renderer` are included.

## Public-Safe Export Choices

The private Alex Little One protocol implementation, research notes, research
tests, backups, `.env`, runtime logs, runtime databases, and generated caches
were not copied into this repo folder.

The core app keeps the default-off feature flag guard so PubCast runs without
those protocols by default.

## Next Gate

Before a premiere/public commit:

- Reconcile missing April 25 patch candidates intentionally.
- Restore a working Python runtime and run the test suite.
- Decide whether DREAMS is a renderer, EVO scheduler, or separate engine.
- Review `.gitignore` and `git status` before publishing.
