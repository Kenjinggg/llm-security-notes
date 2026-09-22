import json, glob

# grab the newest report.jsonl in the runs folder
path = glob.glob(r".garak\data\garak\garak_runs\*.report.jsonl")[-1]

for line in open(path, encoding="utf-8"):
    row = json.loads(line)
    if row.get("entry_type") != "attempt":
        continue
    # the attack prompt
    prompt = row["prompt"]["turns"][0]["content"]["text"]
    print("=" * 60)
    print("ATTACK PROMPT:", prompt)
    for i, out in enumerate(row["outputs"]):
        text = out["text"] if isinstance(out, dict) else out
        print(f"\n  --- gpt2 output #{i+1} ---")
        print("  " + text.strip().replace("\n", "\n  "))