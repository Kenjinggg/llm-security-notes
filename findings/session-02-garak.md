# Session 02 — Garak: First Scan & Reading Results

*Red team learning path · 2026-09-20*

## Goal of this session
Install Garak, run the first LLM vulnerability scan, and learn to read the
output — not to find a real vulnerability. Target was chosen to be tiny and
free (`gpt2`) so it runs locally with no API key.

## What I ran
```
garak --target_type huggingface --target_name gpt2 --probes lmrc.Profanity
```
- **Target model:** gpt2 (small, old, runs on CPU)
- **Probe:** `lmrc.Profanity` — tries to bait the model into swearing
- **garak version:** 0.17.0

## Setup snags (and fixes) — worth remembering
1. **Install got interrupted** mid-way (Ctrl+C during `Installing collected
   packages`). Fix: just re-run `pip install -U garak` — cached downloads make
   it finish fast. Nothing was corrupted.
2. **PowerShell blocked venv activation** ("running scripts is disabled").
   Fix: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (safe, per-user;
   NOT `Unrestricted`).
3. **Garak crashed on first run** — `PermissionError [WinError 5]` trying to
   create `C:\Users\kenji\.config\garak` (Linux-style path Windows blocked).
   Fix: point Garak's config/data/cache into the project folder via the
   `XDG_CONFIG_HOME`, `XDG_DATA_HOME`, `XDG_CACHE_HOME` env vars.

## The mental model — every Garak run is these 3 things
| Concept | What it is | Side |
|---|---|---|
| **Probe** | the attack (e.g. `lmrc.Profanity` = "make it swear") | offense |
| **Detector** | the judge that scores each response | evaluation |
| **Score / pass rate** | pass = model behaved; **fail = attack succeeded (a "hit")** | result |

One probe can trigger **many detectors**. My run used 10 profanity detectors
(religious, political, sexual, racial/ethnic, disability, etc.), so one probe
produced 10 score lines.

## My results
- **Run shape:** 2 attack prompts × 5 generations each = **10 outputs evaluated**
  (NOT 10 prompts — corrected after reading the raw data).
- **Outcome:** 100% pass, **0 hits** across all 10 detectors.

## The key lesson — a clean report ≠ a secure model
gpt2 "passed" not because it defended itself, but because it's too incoherent
to follow the attack. Asked for an insult, it rambled about the "National Book
Critics Circle." **Pass rate measures the detector's verdict, not the model's
safety.** A capable model that refuses and a dumb model that spouts gibberish
both score 100% — for opposite reasons. Reading *why* something passed is the
real skill.

## HTML vs JSONL — where the data actually lives
Garak writes two files per run in `.garak/data/garak/garak_runs/`:
- **`*.report.html`** — SUMMARY ONLY. Scores, rates, charts. Verified by search:
  the actual prompt text and model answers are **NOT in the HTML**.
- **`*.report.jsonl`** — the raw data. One JSON record per line. The
  `entry_type: "attempt"` records hold the prompt + the model's outputs.

### JSONL structure gotchas (learned by inspecting)
- Each attempt is logged **twice**: `status=1` (generated, empty results) and
  `status=2` (judged, has `detector_results`). Only read `status=2`.
- `detector_results` maps detector name → list of scores, one per output.
  `0.0` = clean; a high score (>= 0.5) = detector fired = **hit/fail**.
- Prompt text path: `prompt.turns[0].content.text`. Goal: `goal` field.

## Tool I built: `read_garak.py`
A single reusable reader (in the redteam root). Auto-finds the newest report,
keeps only judged attempts, marks each output PASS/FAIL, and prints the raw
prompt + response text the HTML hides.
```
python read_garak.py                # all outputs, marked PASS/FAIL
python read_garak.py --fails-only   # only the hits (empty for this run)
python read_garak.py --path <file>  # a specific report
```
Caveat: parser is written against garak 0.17.0's JSONL shape; field paths may
need updating if a future garak version changes the format.

## Status
Session 2 complete: Garak installed, first scan run, report understood, and a
reusable inspection tool built.

## Next (Session 3)
Pick two specific Garak probes, run each on its own, and note what fired.
Ideally against a target capable enough to actually produce some hits — so
`--fails-only` finally has something to show.
