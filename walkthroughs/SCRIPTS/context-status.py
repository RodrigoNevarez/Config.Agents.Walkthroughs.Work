#!/usr/bin/env python3
"""Report CONTEXT files that still need attention: agent-sourced research
awaiting your review ('proposed'), and anything cleared to mine but not
yet cited by a filed issue ('approved'). See
INSTRUCTIONS/08-context-guide.org's Checking Pending Files section.

This is a status report, not a pass/fail gate — run
SCRIPTS/validate-walkthroughs.py for structural validation of
context_index.org itself.

Usage: .agents/walkthroughs/SCRIPTS/context-status.py
"""

import re
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WT_DIR / "CONTEXT"
CONTEXT_INDEX = CONTEXT_DIR / "context_index.org"

FILE_LINK_RE = re.compile(r"\[\[file:([^\]]+)\]")


def extract_drawer_field(lines, start, stop, field):
    in_drawer = False
    val = None
    pattern = re.compile(rf"^:{re.escape(field)}:\s*", re.I)
    for line in lines[start:stop]:
        s = line.strip()
        if s == ":PROPERTIES:":
            in_drawer = True
            continue
        if s == ":END:":
            in_drawer = False
            continue
        if in_drawer and pattern.match(s):
            val = pattern.sub("", s).strip()
    return val


def load_entries():
    if not CONTEXT_INDEX.exists():
        print(f"No context_index.org found at {CONTEXT_INDEX}")
        return []

    lines = CONTEXT_INDEX.read_text().splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]
    entries = []

    for i, line in enumerate(lines):
        if not re.match(r"^\*\s+\S", line):
            continue
        next_idx = next((h for h in heading_idxs if h > i), len(lines))
        entry_id = extract_drawer_field(lines, i + 1, next_idx, "ID")
        source = extract_drawer_field(lines, i + 1, next_idx, "SOURCE")
        status = extract_drawer_field(lines, i + 1, next_idx, "STATUS")
        m = FILE_LINK_RE.search("\n".join(lines[i + 1:next_idx]))
        file_link = m.group(1) if m else None
        note = ""
        for l in lines[i + 1:next_idx]:
            s = l.strip()
            if s and not s.startswith((":", "-", "*File:")):
                note = s
                break
        entries.append({
            "id": entry_id, "source": source, "status": status,
            "file": file_link, "note": note,
        })
    return entries


def main():
    entries = load_entries()
    proposed = [e for e in entries if e["status"] == "proposed"]
    approved = [e for e in entries if e["status"] == "approved"]

    if not entries:
        print("CONTEXT is empty — nothing pending.")
        return

    if proposed:
        print(f"AWAITING YOUR REVIEW ({len(proposed)}) — agent-sourced, not yet approved:")
        for e in proposed:
            print(f"  - {e['file']}  {e['note']}")
    else:
        print("AWAITING YOUR REVIEW (0)")

    print()

    if approved:
        print(f"READY TO MINE ({len(approved)}) — approved, no filed issue cites these yet:")
        for e in approved:
            print(f"  - {e['file']}  {e['note']}")
    else:
        print("READY TO MINE (0)")


if __name__ == "__main__":
    main()
