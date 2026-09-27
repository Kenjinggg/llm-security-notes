# LLM Security — Red Team Notes

Hands-on learning log for LLM / AI red teaming, using
[garak](https://github.com/NVIDIA/garak) as the primary scanner.

## Structure
- `findings/` — session write-ups (what was run, results, lessons)
- `read_garak.py` — reusable reader that extracts prompts + model outputs
  from a garak `.report.jsonl` and marks each PASS / FAIL / SKIP
- `scripts/` — Ollama target setup: `check_ollama.py` (smoke test),
  `garak_ollama.json` (garak generator options), `Modelfile.shophelper`
  (test target with a canary secret)
- `experiments/` — attack payloads and working files

## Progress
- **Session 1** — OWASP Top 10 for LLM (2025), attacker-framed notes; Python venv
- **Session 2** — garak installed; first scan (`gpt2`, `lmrc.Profanity`);
  learned the probe / detector / score model and HTML-vs-JSONL reporting
- **Session 3** — ran individual probes (`continuation`, `dan`, `leakreplay`);
  learned to read results critically: a hit ≠ meaningful, a SKIP ≠ a pass
- **Session 4** — local Ollama target (`llama3.2:1b`); DAN probe now engages
  (was SKIP on gpt2); found a `MitigationBypass` detector false positive on a
  clean refusal (reported ASR 80%, true ASR 0/5)
- **Session 5** — attack taxonomy: jailbreak vs. prompt injection, direct vs.
  indirect, jailbreak families mapped to MITRE ATLAS, OWASP and garak probes
- **Session 6** — 5 manual attacks on `shophelper` (canary-based): the secret
  leaked with a plain request (1/4) and an instruction override (1/3);
  simulated indirect injection hijacked the task 3/3 without leaking.
  Takeaway: a system prompt is not a security boundary

## Note
Scan artifacts and the virtual environment are gitignored (regenerable).
