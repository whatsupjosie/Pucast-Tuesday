# PubCast Tuesday Handoff - Ollama and Local Model Setup

Created: 2026-04-29

## User Boundaries

- Non-destructive work only.
- Do not delete or move user files.
- Work from copies when changing important files.
- Keep Alex Little One / care research intact unless explicitly asked to sanitize a specific public build.
- User is stressed by terminal literalness. Give only commands when asking them to paste commands. Do not mix example output with commands.

## Current Repo

Repo path:

```text
C:\Users\hardc\OneDrive\Documents\Playground\Pubcast Tuesday
```

Important snapshot already created:

```text
C:\Users\hardc\OneDrive\Documents\Playground\Pubcast Tuesday\snapshots\PUBCAST_SNAPSHOT_20260429_083521.md
```

Backup before planned Mistral install:

```text
C:\Users\hardc\OneDrive\Documents\Playground\Pubcast Tuesday\backup_pre_ministral_pubcast_install_20260429
```

No final PubCast model wiring was completed after that backup because the user pivoted to testing Gemma 4.

## Ollama Findings

Ollama itself works, but CPU gets overloaded when multiple large models are loaded at once.

Most important discovery:

- `qwen2.5-coder:7b` loaded at context `16384` makes the system sluggish.
- Raw `ministral-3:3b` may load with context `16384`, also heavy.
- Raw `gemma4:e4b` loaded at context `16384`, used about `10 GB`, and wedged/slowed the system.
- One model at a time is the rule for this machine.

## Working Mistral Setup

The user successfully created a small-context PubCast wrapper:

```text
ministral-pubcast:3b
```

Created from:

```text
FROM ministral-3:3b
PARAMETER num_ctx 2048
PARAMETER num_predict 160
PARAMETER temperature 0.7
```

It responded successfully to:

```powershell
ollama run ministral-pubcast:3b "ready"
```

It gave a chatty answer rather than only `ready`, but the important result is that it ran.

Recommendation:

- Use `ministral-pubcast:3b` as PubCast's main conversational brain for now.
- Keep `qwen2.5-coder:7b` unloaded unless explicitly coding.
- Do not use raw `ministral-3:3b` for PubCast if it loads with `CONTEXT 16384`.

## Gemma Findings

Installed Ollama Gemma models:

```text
gemma4:e4b                            8.95 GB  gemma4  8.0B     Q4_K_M
gemma4:e2b                            6.67 GB  gemma4  5.1B     Q4_K_M
google_gemma-3-1b-it-Q4_K_L:latest    0.75 GB  gemma3  999.89M  Q4_K_M
google_gemma-3-1b-it-Q6_K:latest      0.94 GB  gemma3  999.89M  Q6_K
gemma3:1b                             0.76 GB  gemma3  999.89M  Q4_K_M
jayeshpandit2480/gemma3-UNCENSORED:1b 0.76 GB  gemma3  999.89M  Q4_K_M
gemma3:latest                         3.11 GB  gemma3  4.3B     Q4_K_M
gemma3:4b                             3.11 GB  gemma3  4.3B     Q4_K_M
```

Clarification:

- The uncensored model is Gemma 3 1B, not Gemma 4:

```text
jayeshpandit2480/gemma3-UNCENSORED:1b
```

Gemma 4 tests:

- `gemma4:e2b` answered once, but cold load took about 5 minutes.
- A warm follow-up threw HTTP 500.
- `gemma4:e4b` loaded at 16k context and wedged the machine.

Recommendation:

- Do not make Gemma 4 the PubCast default yet.
- If testing Gemma 4 again, create small-context wrapper first and test one model at a time.

Safe Gemma 4 wrapper command to try later:

```powershell
$mf = @'
FROM gemma4:e2b
PARAMETER num_ctx 2048
PARAMETER num_predict 160
PARAMETER temperature 0.5
'@

$mf | Set-Content "$env:TEMP\Modelfile.gemma4.pubcast" -Encoding UTF8
ollama create gemma4-pubcast:e2b -f "$env:TEMP\Modelfile.gemma4.pubcast"
```

Then test:

```powershell
ollama run gemma4-pubcast:e2b "Say exactly one word: ready"
```

## Broken/Incomplete Local GGUF

File:

```text
C:\Models\Gemma4\Coder\gemma-4-E4b-it.Q4_K_M.gguf
```

Size:

```text
0.72 GB
```

Ollama rejected it:

```text
tensor "per_layer_token_embd.weight" offset+size (2382990656) exceeds file size (767841657)
```

Conclusion:

- The file is truncated or corrupt.
- Do not try to install it again unless replaced with a complete download.

Other local files found:

```text
C:\AI\Models\Gemma4\gemma-4-E2B-it-Q5_K_M.gguf
C:\AI\Models\Gemma4\gemma-4-e2b-Q2_K.gguf
```

These were not fully imported/tested during this handoff.

## Safe Ollama Recovery Commands

Clear loaded models without deleting model files:

```powershell
ollama stop ministral-3:3b
ollama stop ministral-3:3b-instruct-2512-q4_K_M
ollama stop ministral-pubcast:3b
ollama stop qwen2.5-coder:7b
ollama stop gemma4:e2b
ollama stop gemma4:e4b
ollama ps
```

If a model is stuck on `Stopping...`, wait. If PowerShell cursor does not return, press:

```text
Ctrl+C
```

Then:

```powershell
ollama ps
```

If still wedged, quit Ollama from the tray icon and reopen it.

## Important Terminal Guidance

The user accidentally pasted example output as commands several times. Future assistants should avoid output examples unless clearly labeled.

Best style:

```text
Paste only this:
```

Then provide one command block, no nearby fake output.

## Recommended Next Step

1. Make sure `ollama ps` is empty.
2. Run:

```powershell
ollama run ministral-pubcast:3b "ready"
```

3. If it responds, wire PubCast bot configs and default Ollama model to `ministral-pubcast:3b`.
4. Keep Gemma 4 as experimental until it works reliably under a 2048 context wrapper.

## Files Likely To Patch For PubCast Mistral Install

Backups already exist in `backup_pre_ministral_pubcast_install_20260429`.

Likely files:

```text
data\bots\pete.json
data\bots\repeat.json
data\bots\sir_purfluous.json
modules\bots.py
modules\llm_framework.py
modules\llm_orchestrator.py
modules\ollama_provider.py
modules\performance_manager.py
system_policy.json
.env.example
```

Recommended code/config changes:

- Bot JSON model fields: `ministral-pubcast:3b`
- Default `OLLAMA_MODEL`: `ministral-pubcast:3b`
- Studio model default: `ministral-pubcast:3b`
- Ollama request options should include `num_ctx: 2048` where requests are made directly.

Do not patch Alex care/protocol files during this model install.
