"""Generate inventory of _handle_error context usages from quality_gui_main_app.py.

Non-intrusive audit helper:
- Scans only active main file (excludes backups path heuristic)
- Extracts context arguments passed to _handle_error(... context="...") or self._handle_error(...
- Normalizes, de-duplicates, sorts and writes JSON to error_context_inventory.json
- Prints summary counts grouped by top-level namespace (e.g. files., upload., project.)

Design rules:
- Read-only: does not modify target file
- Safe fallbacks: tries multiple regex patterns
- No external deps

Usage: python generate_error_context_inventory.py
"""
from __future__ import annotations
import json, re, os, collections, sys

TARGET_FILE = "quality_gui_main_app.py"
OUTPUT_JSON = "error_context_inventory.json"

# Regex patterns capturing context parameter (allow single/double quotes, optional whitespace)
PATTERNS = [
    re.compile(r"_handle_error\s*\(.*?context\s*=\s*['\"]([^'\"]+)['\"]", re.DOTALL),
]

def extract_contexts(text: str) -> list[str]:
    contexts: set[str] = set()
    for pat in PATTERNS:
        for m in pat.finditer(text):
            ctx = m.group(1).strip()
            if ctx:
                contexts.add(ctx)
    return sorted(contexts)

def group_by_namespace(contexts: list[str]) -> dict:
    groups = collections.defaultdict(list)
    for c in contexts:
        top = c.split('.', 1)[0]
        groups[top].append(c)
    return {k: sorted(v) for k, v in sorted(groups.items())}

def main():
    if not os.path.exists(TARGET_FILE):
        print(f"Target file not found: {TARGET_FILE}")
        sys.exit(1)
    with open(TARGET_FILE, 'r', encoding='utf-8') as f:
        text = f.read()
    contexts = extract_contexts(text)
    data = {
        "total_contexts": len(contexts),
        "namespaces": group_by_namespace(contexts),
        "all_contexts": contexts,
    }
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    # Console summary
    print(f"Extracted {len(contexts)} unique _handle_error contexts")
    for ns, items in data["namespaces"].items():
        print(f"  {ns}: {len(items)}")
    print(f"Inventory written to {OUTPUT_JSON}")

if __name__ == "__main__":
    main()
