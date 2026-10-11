# LLM Security Notes — Hands-on LLM Red Teaming

Practical LLM / AI red-teaming work by **Kenji** ([@Kenjinggg](https://github.com/Kenjinggg)),
a final-year Cybersecurity student. I build small, deliberately vulnerable LLM applications,
attack them with manual techniques and automated tools, measure how often the attacks succeed,
and write the results up as security findings with root cause, fix and retest.

> **Responsible scope.** Every target in this repo is a local lab I built and ran on my own
> machine: fictional store ("Kopi Kita"), fake customer records, canary strings instead of real
> secrets. No real system, service or person was tested. Techniques are documented to explain
> defences, and each finding ends with a verified or planned fix.

## Findings

| # | Finding | Severity | Class | Fix status |
|---|---|---|---|---|
| 02 | [Cross-customer data disclosure via indirect prompt injection](findings/finding-02-indirect-injection-data-disclosure.md) | **High** | OWASP LLM01 (indirect) + LLM06; BOLA via an LLM agent | Fixed in lab; verified (9/9 attempts denied) |
| 01 | [Staff discount code disclosed through the system prompt](findings/finding-01-shophelper-secret-disclosure.md) | **Medium** | OWASP LLM07 via LLM01 | Open (fix + retest plan written) |

**Headline results**
- A hidden instruction in a customer review made a support agent fetch **another customer's
  record in 7/10 runs** and repeat her name in 6/10. Moving the authorization check into the
  tool stopped it completely, even though the model was still fooled 9/10 times.
- A "secret" protected only by the system prompt leaked to a **plain request (~8%)** and to an
  automated **multi-turn attack (30%, ~4×)**.
- Automated scanners needed checking by hand: garak's detectors misreported results in both
  directions (a reported 80% attack success rate was really 0/5; a reported 5/30 was really
  ~13/30), and my own harness once scored broken model output as a pass.

## What I worked with
- **Targets:** `llama3.2:1b` via [Ollama](https://ollama.com), wrapped as a support chatbot
  (canary secret in the system prompt) and as a ReAct-style agent with an order-lookup tool.
- **Tools:** [garak](https://github.com/NVIDIA/garak) (scanner), [PyRIT](https://github.com/Azure/PyRIT)
  (multi-turn attacker), plus my own Python harnesses and report readers.
- **Frameworks:** OWASP Top 10 for LLM Applications 2025, MITRE ATLAS, OWASP API Security
  (BOLA), a simplified OWASP risk rating for severity.

## Session notes
Learning log, in order. Each session records what I ran, the raw results and what I learned.

| Session | Topic | Key lesson |
|---|---|---|
| [01](findings/owasp-llm-top10-notes.md) | OWASP Top 10 for LLM (2025), attacker-framed | — |
| [02](findings/session-02-garak.md) | garak install, first scan | Probe / detector / score; HTML = summary, JSONL = raw |
| [03](findings/session-03-garak-probes.md) | Individual garak probes | A SKIP is not a pass; a hit is not automatically severe |
| [04](findings/session-04-ollama-dan.md) | Local Ollama target, DAN jailbreak | Detector false positive: reported 80% success, actually 0/5 |
| [05](findings/session-05-attack-taxonomy.md) | Attack taxonomy | Jailbreak ≠ prompt injection; a system prompt is not a security boundary |
| [06](findings/session-06-shophelper-manual.md) | Manual attacks on the chatbot | Secret leaked with no technique at all |
| [07](findings/session-07-garak-vs-manual.md) | garak vs manual testing | Hand-grading changed the numbers; no stock probe tests *your* app's secret |
| [08](findings/session-08-indirect-injection-lab.md) | Indirect injection against an agent with a tool | Defences belong in the backend, not in the prompt |
| [09](findings/session-09-pyrit-multiturn.md) | PyRIT multi-turn attack | Conversation beats a cold ask (~4×); a rate only means something next to a baseline |

## Repository layout
```
findings/                 formal findings (finding-NN-*.md) and session notes (session-NN-*.md)
experiments/lab-indirect/ ShopHelper v2 agent lab: harness, fake customers, clean/poisoned reviews, retest logs
experiments/pyrit-lab/    PyRIT multi-turn attack harness
experiments/*.txt         raw evidence logs
scripts/                  Ollama targets (Modelfiles), garak configs, smoke test
read_garak.py             reads a garak .report.jsonl and marks each attempt PASS / FAIL / SKIP
```

## Reproducing
Developed on Windows (PowerShell) with Python virtual environments. Everything runs locally.

1. Install [Ollama](https://ollama.com) and pull the models:
   ```powershell
   ollama pull llama3.2:1b
   ollama pull llama3.2:3b   # only needed as the PyRIT attacker
   ```
2. Build the lab targets:
   ```powershell
   ollama create shophelper -f scripts\Modelfile.shophelper
   ollama create shophelper-agent -f experiments\lab-indirect\Modelfile.shophelper-agent
   ```
3. **Finding 02 (agent lab)** needs only the Python standard library:
   ```powershell
   python experiments\lab-indirect\shophelper_app.py --review review_poisoned.txt                  # vulnerable
   python experiments\lab-indirect\shophelper_app.py --review review_poisoned.txt --enforce-authz  # fixed
   ```
4. **Finding 01** steps are in the finding itself. The scanners need separate virtual
   environments because garak and PyRIT require incompatible `datasets` versions:
   ```powershell
   python -m venv .venv-garak; .\.venv-garak\Scripts\Activate.ps1; pip install garak      # garak
   python -m venv .venv;       .\.venv\Scripts\Activate.ps1;       pip install pyrit      # PyRIT
   ```

Results vary between runs (temperature 0.7), so findings report rates over batches rather than
single outputs. Virtual environments and garak scan output are gitignored.

## Contact
Open an issue on this repository, or reach me via my GitHub profile.
