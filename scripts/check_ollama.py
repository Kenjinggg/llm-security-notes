"""Smoke-test the local Ollama server before pointing garak at it.

Usage (venv active):
    python scripts\check_ollama.py                 # checks llama3.2:1b
    python scripts\check_ollama.py shophelper      # checks another local model

Uses the `ollama` Python package, which garak already installed as a dependency.
"""
import sys
import time

import ollama

MODEL = sys.argv[1] if len(sys.argv) > 1 else "llama3.2:1b"
if ":" not in MODEL:
    MODEL += ":latest"  # Ollama lists untagged models as name:latest


def main() -> None:
    # 1. Is the server up?
    try:
        models = [m.model for m in ollama.list().models]
    except Exception as e:
        print(f"[X] Can't reach Ollama at 127.0.0.1:11434 ({e})")
        print("    Is the Ollama app running (llama icon in the system tray)?")
        print("    If not, start it from the Start menu, or run:  ollama serve")
        sys.exit(1)
    print(f"[OK] Ollama server is up. Local models: {', '.join(models) or '(none)'}")

    # 2. Is the model pulled?
    if MODEL not in models:
        print(f"[X] {MODEL} isn't pulled yet. Run:  ollama pull {MODEL}")
        sys.exit(1)

    # 3. Cold call (loads the model into RAM), then warm call (real speed)
    for label in ("cold", "warm"):
        t = time.perf_counter()
        r = ollama.chat(
            model=MODEL,
            messages=[{"role": "user", "content": "Reply with exactly one word: pong"}],
        )
        dt = time.perf_counter() - t
        print(f"[OK] {label} call: {dt:5.1f}s -> {r['message']['content'].strip()!r}")

    print("\nIf the warm call is over ~20s, raise 'timeout' in scripts\\garak_ollama.json.")


if __name__ == "__main__":
    main()
