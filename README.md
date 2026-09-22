# LLM Security — Red Team Notes

Hands-on learning log for LLM / AI red teaming, using
[garak](https://github.com/NVIDIA/garak) as the primary scanner.

## Structure
- `findings/` — session write-ups (what was run, results, lessons)
- `read_garak.py` — reusable reader that extracts prompts + model outputs
  from a garak `.report.jsonl` and marks each PASS / FAIL / SKIP
- `experiments/`, `scripts/` — working space

## Progress
- **Session 1** — OWASP Top 10 for LLM (2025), attacker-framed notes; Python venv
- **Session 2** — garak installed; first scan (`gpt2`, `lmrc.Profanity`);
  learned the probe / detector / score model and HTML-vs-JSONL reporting
- **Session 3** — ran individual probes (`continuation`, `dan`, `leakreplay`);
  learned to read results critically: a hit ≠ meaningful, a SKIP ≠ a pass

## Note
Scan artifacts and the virtual environment are gitignored (regenerable).
