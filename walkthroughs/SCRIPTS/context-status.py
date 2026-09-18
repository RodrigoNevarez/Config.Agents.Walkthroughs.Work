#!/usr/bin/env python3
"""Report CONTEXT files that still need attention: agent-sourced research
awaiting your review ('proposed'), and anything cleared to mine but not
yet cited by a filed issue ('approved'). See
INSTRUCTIONS/08-context-guide.org's Checking Pending Files section.

CONTEXT is organized as one subdirectory per owning issue
(CONTEXT/<issue-uuid>/), each with its own index.org — this scans every
one of them, not a single flat file.

This is a status report, not a pass/fail gate — run
SCRIPTS/validate-walkthroughs.py for structural validation of each
subdirectory's index.org itself.

Usage: .agents/walkthroughs/SCRIPTS/context-status.py
"""

import re
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
CONTEXT_DIR = WT_DIR / "CONTEXT"

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


def load_entries_from(index_path, issue_uuid):
    lines = index_path.read_text().splitlines()
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
            "file": file_link, "note": note, "issue": issue_uuid,
        })
    return entries


def load_entries():
    if not CONTEXT_DIR.is_dir():
        print(f"No CONTEXT directory found at {CONTEXT_DIR}")
        return []

    entries = []
    for sub in sorted(CONTEXT_DIR.iterdir()):
        if not sub.is_dir():
            continue
        index_path = sub / "index.org"
        if not index_path.exists():
            continue
        entries.extend(load_entries_from(index_path, sub.name))
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
            print(f"  - [{e['issue']}] {e['file']}  {e['note']}")
    else:
        print("AWAITING YOUR REVIEW (0)")

    print()

    if approved:
        print(f"READY TO MINE ({len(approved)}) — approved, no filed issue cites these yet:")
        for e in approved:
            print(f"  - [{e['issue']}] {e['file']}  {e['note']}")
    else:
        print("READY TO MINE (0)")


if __name__ == "__main__":
    main()
