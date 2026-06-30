import json
from deep_translator import GoogleTranslator
from pathlib import Path

ROOTS_PATH = Path(r"C:\Users\salek\word-roots-tutor\data\roots.json")

with open(ROOTS_PATH, "r", encoding="utf-8") as f:
    roots = json.load(f)

updated = 0
for i, r in enumerate(roots):
    ex = r.get("example_sentence", "")
    if ex and not r.get("example_zh"):
        try:
            r["example_zh"] = GoogleTranslator(source="auto", target="zh-TW").translate(ex)
            updated += 1
        except Exception as e:
            print(f"translate error {i} example: {e}")
            r["example_zh"] = ex
    tip = r.get("mnemonic", "")
    if tip and not r.get("mnemonic_zh"):
        try:
            r["mnemonic_zh"] = GoogleTranslator(source="auto", target="zh-TW").translate(tip)
            updated += 1
        except Exception as e:
            print(f"translate error {i} mnemonic: {e}")
            r["mnemonic_zh"] = tip

with open(ROOTS_PATH, "w", encoding="utf-8") as f:
    json.dump(roots, f, ensure_ascii=False, indent=2)

print(f"updated {updated} fields")
