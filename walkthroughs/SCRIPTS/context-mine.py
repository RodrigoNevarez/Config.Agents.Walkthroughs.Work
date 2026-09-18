#!/usr/bin/env python3
"""Mine an approved CONTEXT file into a citing issue/walkthrough: verifies
the citing file already links to it, flips its owning subdirectory's
index.org's :STATUS: to 'mined', and re-runs the full validator. See
INSTRUCTIONS/08-context-guide.org.

CONTEXT is organized as one subdirectory per owning issue
(CONTEXT/<issue-uuid>/), each with its own index.org — this searches all
of them for the entry matching <context-uuid>, rather than assuming a
single flat file.

This script deliberately does NOT write the citation or any mined content
for you — add the actual [[file:...]] link (and whatever prose draws on
the research) to the citing file yourself first. This only verifies that
happened and updates the bookkeeping; it refuses to flip STATUS on a claim
alone, same evidentiary standard as everywhere else in this system.

Usage: .agents/walkthroughs/SCRIPTS/context-mine.py <context-uuid> <citing-file>
"""

import re
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
WT_DIR = SCRIPT_DIR.parent
ROOT = WT_DIR.parent.parent
CONTEXT_DIR = WT_DIR / "CONTEXT"
VALIDATOR = SCRIPT_DIR / "validate-walkthroughs.py"

UUID_RE = r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"


def fail(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def find_owning_index(context_uuid):
    """Search every CONTEXT/<issue-uuid>/index.org for an entry with
    :ID: context_uuid. Returns the index.org Path, or None."""
    if not CONTEXT_DIR.is_dir():
        return None
    for sub in sorted(CONTEXT_DIR.iterdir()):
        if not sub.is_dir():
            continue
        index_path = sub / "index.org"
        if not index_path.exists():
            continue
        text = index_path.read_text()
        if re.search(rf"^\s*:ID:\s+{re.escape(context_uuid)}\s*$", text, re.I | re.M):
            return index_path
    return None


def main():
    if len(sys.argv) != 3:
        fail("usage: context-mine.py <context-uuid> <citing-file>")

    context_uuid, citing_file_arg = sys.argv[1], sys.argv[2]
    if not re.fullmatch(UUID_RE, context_uuid, re.I):
        fail(f"'{context_uuid}' doesn't look like a UUID")

    citing_path = Path(citing_file_arg)
    citing_file = citing_path if citing_path.is_absolute() else (ROOT / citing_path)
    citing_file = citing_file.resolve()

    if not citing_file.exists():
        fail(f"citing file does not exist: {citing_file}")

    citing_text = citing_file.read_text()
    if not re.search(rf"\[\[file:[^\]]*{re.escape(context_uuid)}[^\]]*\]", citing_text):
        fail(
            f"{citing_file} has no [[file:...]] link to CONTEXT uuid "
            f"{context_uuid} yet. Add the actual citation — and whatever "
            f"content the research actually justifies — to the citing file "
            f"first. This script only verifies that happened; it doesn't "
            f"write the citation or the content for you."
        )

    context_index = find_owning_index(context_uuid)
    if context_index is None:
        fail(f"no CONTEXT/<issue-uuid>/index.org entry found with :ID: {context_uuid}")

    lines = context_index.read_text().splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    entry_start = None
    entry_end = None
    for i, line in enumerate(lines):
        if not re.match(r"^\*\s+\S", line):
            continue
        next_idx = next((h for h in heading_idxs if h > i), len(lines))
        for l in lines[i + 1:next_idx]:
            if re.match(rf"^\s*:ID:\s+{re.escape(context_uuid)}\s*$", l, re.I):
                entry_start, entry_end = i, next_idx
                break
        if entry_start is not None:
            break

    if entry_start is None:
        fail(f"no entry found with :ID: {context_uuid} in {context_index}")

    status_line_idx = None
    for j in range(entry_start + 1, entry_end):
        if re.match(r"^\s*:STATUS:\s+", lines[j], re.I):
            status_line_idx = j
            break
    if status_line_idx is None:
        fail(f"entry for {context_uuid} has no :STATUS: line")

    current = re.sub(r"^\s*:STATUS:\s+", "", lines[status_line_idx], flags=re.I).strip()
    indent = lines[status_line_idx][: len(lines[status_line_idx]) - len(lines[status_line_idx].lstrip())]
    lines[status_line_idx] = f"{indent}:STATUS:   mined"
    context_index.write_text("\n".join(lines) + "\n")
    print(f"{context_uuid}: {current} -> mined ({context_index.relative_to(ROOT)}, "
          f"cited from {citing_file.relative_to(ROOT)})", flush=True)

    result = subprocess.run([sys.executable, str(VALIDATOR)])
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
