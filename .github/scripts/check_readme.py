"""Profile README check: every link answers 200 and every table row has as many columns as its header."""
import re
import sys
import time
import urllib.error
import urllib.request

text = open(sys.argv[1] if len(sys.argv) > 1 else "README.md", encoding="utf-8").read()
failed = []

columns = None
for n, line in enumerate(text.splitlines(), 1):
    if line.startswith("|"):
        k = len(re.findall(r"(?<!\\)\|", line))
        columns = columns or k
        if k != columns:
            failed.append(f"line {n}: {k - 1} columns, header has {columns - 1}: {line[:80]}")
    else:
        columns = None

for url in sorted(set(re.findall(r"\]\((https?://[^)\s]+)\)", text))):
    target = re.sub(r"^https://www\.npmjs\.com/package/", "https://registry.npmjs.org/", url)  # npmjs.com answers 403 to bots; the registry is the same source
    for attempt in range(3):
        try:
            req = urllib.request.Request(target, headers={"User-Agent": "profile-readme-check"})
            code = urllib.request.urlopen(req, timeout=20).status
        except urllib.error.HTTPError as e:
            code = e.code
        except OSError as e:
            code = type(e).__name__
        if code == 200 or code == 404:
            break
        time.sleep(3)
    print(code, url)
    if code != 200:
        failed.append(f"{url} → {code}")

print("\n".join(f"✗ {g}" for g in failed) or "✓ all links answer and all tables are well-formed")
sys.exit(1 if failed else 0)
