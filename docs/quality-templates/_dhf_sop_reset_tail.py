"""Replace the corrupt out-of-scope bullet (from its start to EOF) with the contents of dhf_tail.md."""
from pathlib import Path

HERE = Path(__file__).parent
P = HERE / "SOP-Design-History-File-ISO13485.md"
T = HERE / "dhf_tail.md"
text = P.read_text(encoding="utf-8")
needle = "- The full **(DM)****(R)****(/)**"
if needle not in text:
    raise SystemExit("needle not found: file may already be fixed")
tail = T.read_text(encoding="utf-8")
if not tail.endswith("\n"):
    tail += "\n"
P.write_text(text[: text.index(needle)] + tail, encoding="utf-8")
print("OK", P)
