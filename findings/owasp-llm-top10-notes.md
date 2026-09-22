
_Quick reference. Each entry: what the vulnerability is, then how you'd attack it. Source: OWASP Top 10 for LLM Applications 2025 (genai.owasp.org)._

---

**LLM01 — Prompt Injection** Attacker-supplied text overrides the model's intended instructions. Attack: inject commands directly into the prompt, or plant them in content the model later ingests (web page, PDF, email, RAG doc) so it obeys them _indirectly_.

**LLM02 — Sensitive Information Disclosure** The model itself leaks data it shouldn't — memorized training data, PII, secrets, or another user's context. Attack: craft prompts that coax the model into spilling what's held in its memory or its context window.

**LLM03 — Supply Chain** Untrusted components in the LLM pipeline — backdoored pretrained models, poisoned datasets, vulnerable packages, tampered adapters, deprecated models. Attack: slip a malicious component into something they download and deploy.

**LLM04 — Data and Model Poisoning** Corrupting training/fine-tuning data or the model itself to embed biases or backdoors. Attack: seed poisoned data (or a tampered model) early, so the finished model misbehaves on a trigger only you know.

**LLM05 — Improper Output Handling** Downstream systems execute the model's raw output without validating it first. Attack: get the model to emit a payload (script, SQL, shell command, URL) that the surrounding app blindly runs — XSS, SQLi, SSRF, RCE.

**LLM06 — Excessive Agency** The model has more tools, permissions, or autonomy than its task actually needs. Attack: hijack the model to invoke those capabilities — act, delete, transact, escalate — beyond what it should be allowed to do.

**LLM07 — System Prompt Leakage** Developers hide instructions, access rules, or even secrets in the system prompt, assuming users can't see it. Attack: extract the prompt, then use the exposed secrets or the revealed security controls to bypass its defenses.

**LLM08 — Vector and Embedding Weaknesses** Flaws in how a RAG system generates, stores, or retrieves embeddings. Attack: plant a document containing hidden text/instructions so retrieval feeds your payload into the model — or leaks data it shouldn't return.

**LLM09 — Misinformation** The model confidently produces false or fabricated output that users over-trust. Attack: exploit predictable hallucinations — e.g. register a package/repo name the model habitually invents (_slopsquatting_) and wait for it to recommend yours.

**LLM10 — Unbounded Consumption** No limits on resource or query consumption. Attack: flood it with expensive or looping requests to exhaust compute, crash the service, or run up crippling cost (denial of wallet).