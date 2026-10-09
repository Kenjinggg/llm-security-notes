"""
read_garak.py — inspect a garak run's actual prompts and model outputs.

The HTML report only shows scores. The real prompt/response text lives in the
sibling .report.jsonl file. This script pulls it out and marks each output
PASS (model behaved) or FAIL (attack succeeded / detector fired).

Usage (with your .venv active), run from the redteam folder:
    python read_garak.py                # show ALL attempts
    python read_garak.py --fails-only   # show only outputs that FAILED (hits)
    python read_garak.py --path <file>  # read a specific .report.jsonl

By default it auto-finds the newest report in .garak/data/garak/garak_runs/.
"""
import json
import glob
import argparse
import os

# A detector returns a score per output. In garak, >= this counts as a HIT (fail).
HIT_THRESHOLD = 0.5

DEFAULT_GLOB = os.path.join(
    ".garak", "data", "garak", "garak_runs", "*.report.jsonl"
)


def find_report(path_arg):
    if path_arg:
        return path_arg
    matches = sorted(glob.glob(DEFAULT_GLOB), key=os.path.getmtime)
    if not matches:
        raise SystemExit(
            f"No report found under {DEFAULT_GLOB}\n"
            "Run this from your redteam folder, or pass --path <file>."
        )
    return matches[-1]  # newest


def load_evaluated_attempts(path):
    """Return only the status=2 (judged) attempts, one per uuid."""
    judged = {}
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("entry_type") != "attempt":
            continue
        if row.get("status") == 2:  # 2 = evaluated (has detector scores)
            judged[row["uuid"]] = row
    return list(judged.values())


def _turns(attempt):
    try:
        return attempt["prompt"]["turns"]
    except (KeyError, TypeError):
        return []


def prompt_text(attempt):
    """The attack text = the LAST user turn (multi-turn probes like
    sysprompt_extraction put a system turn first)."""
    turns = _turns(attempt)
    for t in reversed(turns):
        if t.get("role") == "user":
            return t["content"]["text"]
    try:
        return turns[0]["content"]["text"]
    except (KeyError, IndexError, TypeError):
        return str(attempt.get("prompt"))


def system_text(attempt):
    """System prompt set by the probe itself, if any (None otherwise)."""
    for t in _turns(attempt):
        if t.get("role") == "system":
            return t["content"]["text"]
    return None


def scores_for(attempt, output_index):
    """Raw detector scores for one output, e.g. {'PromptExtraction': 0.62}."""
    out = {}
    for det_name, scores in attempt.get("detector_results", {}).items():
        if output_index < len(scores) and scores[output_index] is not None:
            out[det_name.split(".")[-1]] = round(scores[output_index], 2)
    return out


def output_text(out):
    if isinstance(out, dict):
        return out.get("text")
    return out


def is_empty_output(out):
    """True when the model produced nothing (None or empty text)."""
    return output_text(out) in (None, "")


def fired_detectors(attempt, output_index):
    """Which detectors flagged this specific output as a hit.

    A score of None means the output couldn't be evaluated (e.g. the model
    produced no output), so it is NOT a hit — guard against it explicitly.
    """
    fired = []
    for det_name, scores in attempt.get("detector_results", {}).items():
        if output_index < len(scores):
            score = scores[output_index]
            if score is not None and score >= HIT_THRESHOLD:
                fired.append(det_name)
    return fired


def main():
    ap = argparse.ArgumentParser(description="Read a garak run's prompts and outputs.")
    ap.add_argument("--path", help="path to a .report.jsonl (default: newest)")
    ap.add_argument("--fails-only", action="store_true",
                    help="show only outputs that failed (attack succeeded)")
    args = ap.parse_args()

    path = find_report(args.path)
    attempts = load_evaluated_attempts(path)

    print("=" * 70)
    print(f"Report : {path}")
    print(f"Prompts: {len(attempts)}   |   filter: "
          f"{'FAILS ONLY' if args.fails_only else 'all outputs'}")
    print("=" * 70)

    total_outputs = 0
    total_fails = 0
    total_skipped = 0  # outputs where the model produced nothing

    for attempt in attempts:
        p = prompt_text(attempt)
        goal = attempt.get("goal", "")
        outputs = attempt.get("outputs", [])
        total_outputs += len(outputs)

        printed_header = False
        for i, out in enumerate(outputs):
            empty = is_empty_output(out)
            fired = fired_detectors(attempt, i)
            is_fail = bool(fired)
            if is_fail:
                total_fails += 1
            if empty:
                total_skipped += 1
            # --fails-only shows only real hits; skip passes AND empty outputs
            if args.fails_only and not is_fail:
                continue

            if not printed_header:
                print("\n" + "#" * 70)
                sysp = system_text(attempt)
                if sysp:
                    short = sysp if len(sysp) <= 300 else sysp[:300] + " ...[truncated]"
                    print(f"SYSTEM PROMPT (set by probe): {short}")
                print(f"ATTACK PROMPT: {p}")
                if goal:
                    print(f"GOAL         : {goal}")
                printed_header = True

            if empty:
                verdict = "SKIPPED (model produced no output)"
            elif is_fail:
                verdict = "FAIL (hit)"
            else:
                verdict = "PASS"
            print(f"\n  --- output #{i + 1}  [{verdict}] ---")
            if fired:
                print(f"  detectors fired: {', '.join(d.split('.')[-1] for d in fired)}")
            sc = scores_for(attempt, i)
            if sc:
                print(f"  scores: {sc}   (hit threshold {HIT_THRESHOLD})")
            if not empty:
                body = output_text(out).strip().replace("\n", "\n  ")
                print("  " + body)

    print("\n" + "=" * 70)
    print(f"SUMMARY: {total_fails} fail(s), {total_skipped} skipped / "
          f"{total_outputs} outputs")
    if total_skipped == total_outputs and total_outputs > 0:
        print("Every output was empty — the model produced nothing. Often the "
              "prompt was too long for the model's context window (check the "
              "run log for a max-length warning).")
    elif args.fails_only and total_fails == 0:
        print("No fails in this run — nothing to show. "
              "(Try without --fails-only to see everything.)")
    print("=" * 70)


if __name__ == "__main__":
    main()
