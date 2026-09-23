#!/usr/bin/env python3
"""Bring every mechanical, derived value in the walkthrough system up to
date in one pass, and report only what changed. See
INSTRUCTIONS/01-index-guide.org's 'The Blocked Property' and
02-expansion-guide.org's 'Finishing a Walkthrough'.

What it derives, in order:
  1. Checklist counts. For each *active* walkthrough.org, count the real
     `- [X]` / `- [ ]` steps in its Guide section and fix the heading's
     `[x/n]` count and its TODO/DONE keyword (DONE exactly at [n/n]).
     Archived outcomes (CONTEXT/<uuid>/outcome.org) are read-only and never
     edited; a mismatch there is only reported.
  2. Index state, ACTIVE <-> DONE. An ACTIVE node whose checklist is
     complete becomes DONE (closed), and a DONE node whose active checklist
     is no longer complete goes back to ACTIVE.
  3. :BLOCKED: for every node, from its :BLOCKED_BY: edges and the states
     computed in step 2. DONE -> false; TODO/ACTIVE -> true if any blocker
     isn't DONE (an unknown UUID counts as blocking). Blockers are resolved
     across index.org *and* CONTEXT/closed.org.
  4. Moving settled issues out of index.org. A DONE node whose walkthrough
     is archived (CONTEXT/<uuid>/outcome.org exists) moves verbatim to
     CONTEXT/closed.org, under the same "* Domain / ** Subcategory"
     headings (created there if missing), with its file: links rebased
     for the new directory. Any subcategory or domain in index.org that
     the move leaves empty is removed. index.org then holds only open work
     plus closed-but-not-yet-archived issues.

What it never does, because each is a deliberate act and not bookkeeping:
TODO -> ACTIVE (expanding an issue), archiving (step 4 only follows an
archive that already happened), or checking a box. A box
is checked only with its own verified *Result:*, which validate-walkthroughs.py
enforces, and that is the real gate this script's DONE flip relies on.

Output is one line per change (CHECKLIST, CLOSED, REOPENED, NEWLY READY,
NOW BLOCKED, BLOCKED SET, MOVED TO CLOSED) and nothing at all when
everything is current.

Usage: .agents/walkthroughs/SCRIPTS/sync-index.py [--check] [--list]
  --check  write nothing; print what would change; exit 1 if anything would
           (validate-walkthroughs.py fails on the same inconsistencies)
  --list   also print every open (TODO/ACTIVE) issue as READY or BLOCKED
"""

import os
import re
import sys
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
INDEX = WT_DIR / "index.org"
CONTEXT_DIR = WT_DIR / "CONTEXT"
CLOSED = CONTEXT_DIR / "closed.org"
CLOSED_HEADER = """#+TITLE: Closed Issues
#+DESCRIPTION: Archived (DONE, fully worked) issues moved out of index.org by SCRIPTS/sync-index.py; same node format. See INSTRUCTIONS/01-index-guide.org.
#+OPTIONS: toc:nil num:nil
#+TODO: TODO ACTIVE | DONE
"""
LINK_RE = re.compile(r"\[\[file:([^\]]+)\]")

NODE_RE = re.compile(r"^(\*\*\*\s+)(TODO|ACTIVE|DONE)(\s+)(.*?)(\s+:[A-Za-z0-9_@#%:]+:)?\s*$")
FIELD_RE = re.compile(r"^(\s*):([A-Z_]+):(\s*)(.*)$")
GUIDE_RE = re.compile(r"^\*\s+(TODO|DONE)\s+(.*?)\s*\[(\d+)/(\d+)\]\s*$")
STEP_RE = re.compile(r"^-\s+\[([ Xx])\]\s+\S")


def parse_index(lines):
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]
    nodes = []
    for i, line in enumerate(lines):
        m = NODE_RE.match(line)
        if not m:
            continue
        end = next((h for h in heading_idxs if h > i), len(lines))
        node = {"state": m.group(2), "title": m.group(4), "line": i,
                "id": None, "blocked_by": [], "fields": {}}
        in_drawer = False
        for j in range(i + 1, end):
            s = lines[j].strip()
            if s == ":PROPERTIES:":
                in_drawer = True
                continue
            if s == ":END:":
                break
            fm = FIELD_RE.match(lines[j]) if in_drawer else None
            if fm:
                name, value = fm.group(2), fm.group(4).strip()
                node["fields"][name] = j
                if name == "ID":
                    node["id"] = value
                elif name == "BLOCKED_BY":
                    node["blocked_by"] = value.split()
        if node["id"]:
            nodes.append(node)
    return nodes


def sections(lines):
    """[(level, start, end)] for every heading; end is the next heading of
    the same or higher level (exclusive)."""
    heads = [(i, len(m.group(1))) for i, l in enumerate(lines)
             if (m := re.match(r"^(\*+)\s", l))]
    out = []
    for k, (i, lvl) in enumerate(heads):
        end = next((j for j, l2 in heads[k + 1:] if l2 <= lvl), len(lines))
        out.append((lvl, i, end))
    return out


def rebase(text, from_dir, to_dir):
    def fix(m):
        path, sep, rest = m.group(1).partition("::")
        dest = os.path.normpath(os.path.join(from_dir, path))
        return f"[[file:{os.path.relpath(dest, to_dir)}{sep}{rest}]"
    return LINK_RE.sub(fix, text)


def move_to_closed(lines, node_lines, check_only):
    """Moves the Level 3 subtrees starting at node_lines out of index.org
    lines into CLOSED, preserving their "* / **" parents. Returns the new
    index.org lines."""
    secs = sections(lines)
    by_start = {s: (lvl, e) for lvl, s, e in secs}
    moves = []  # (l1_block_head, l2_head, node_block)
    for nl in node_lines:
        l1 = max((s for lvl, s, e in secs if lvl == 1 and s < nl < e), default=None)
        l2 = max((s for lvl, s, e in secs if lvl == 2 and s < nl < e), default=None)
        l1_intro_end = next((s for lvl, s, e in secs if s > l1 and lvl > 1), by_start[l1][1]) if l1 is not None else None
        l1_head = lines[l1:l1_intro_end] if l1 is not None else ["* Uncategorized"]
        l2_head = lines[l2] if l2 is not None else "** Uncategorized"
        block = lines[nl:by_start[nl][1]]
        moves.append((l1_head, l2_head, block))

    # remove moved blocks, then any "**" / "*" left without a "***" under it
    drop = {i for nl in node_lines for i in range(nl, by_start[nl][1])}
    kept = [l for i, l in enumerate(lines) if i not in drop]
    while True:
        secs2 = sections(kept)
        empty = [(s, e) for lvl, s, e in secs2 if lvl in (1, 2)
                 and not any(l2 == 3 and s < s2 < e for l2, s2, _ in secs2)]
        if not empty:
            break
        s, e = empty[0]
        kept = kept[:s] + kept[e:]

    if check_only:
        return kept
    closed = CLOSED.read_text().splitlines() if CLOSED.exists() else CLOSED_HEADER.splitlines() + [""]
    for l1_head, l2_head, block in moves:
        block = rebase("\n".join(block), WT_DIR, CONTEXT_DIR).splitlines()
        while block and not block[-1].strip():
            block.pop()
        secs_c = sections(closed)
        c1 = next((s for lvl, s, e in secs_c if lvl == 1 and closed[s] == l1_head[0]), None)
        if c1 is None:
            while closed and not closed[-1].strip():
                closed.pop()
            closed += [""] + [l for l in l1_head if l.strip()] + [""]
            secs_c = sections(closed)
            c1 = next(s for lvl, s, e in secs_c if lvl == 1 and closed[s] == l1_head[0])
        c1_end = next(e for lvl, s, e in secs_c if s == c1)
        c2 = next((s for lvl, s, e in secs_c if lvl == 2 and c1 < s < c1_end and closed[s] == l2_head), None)
        if c2 is None:
            ins = c1_end
            while ins > c1 + 1 and not closed[ins - 1].strip():
                ins -= 1
            closed[ins:ins] = ["", l2_head]
            secs_c = sections(closed)
            c2 = next(s for lvl, s, e in secs_c if lvl == 2 and closed[s] == l2_head and s > c1)
        c2_end = next(e for lvl, s, e in secs_c if s == c2)
        ins = c2_end
        while ins > c2 + 1 and not closed[ins - 1].strip():
            ins -= 1
        # match index.org's layout: "**" heading directly followed by its
        # first "***", and one blank line between sibling issues
        closed[ins:ins] = ([] if ins - 1 == c2 else [""]) + block
    CLOSED.write_text("\n".join(closed).rstrip("\n") + "\n")
    return kept


def checklist(path, fix):
    """Returns (done, total, change_or_None). With fix=True, rewrites the
    Guide heading's [x/n] and TODO/DONE keyword to match the real steps."""
    lines = path.read_text().splitlines()
    top = [i for i, l in enumerate(lines) if re.match(r"^\*\s+\S", l)]
    g = next((i for i in top if GUIDE_RE.match(lines[i])), None)
    if g is None:
        return None, None, None  # the validator reports a missing checklist
    end = next((i for i in top if i > g), len(lines))
    marks = [STEP_RE.match(lines[i]).group(1) for i in range(g + 1, end)
             if STEP_RE.match(lines[i])]
    done, total = sum(m in "Xx" for m in marks), len(marks)
    gm = GUIDE_RE.match(lines[g])
    want_kw = "DONE" if total and done == total else "TODO"
    have = (gm.group(1), int(gm.group(3)), int(gm.group(4)))
    change = None
    if have != (want_kw, done, total):
        change = f"{have[0]} [{have[1]}/{have[2]}] -> {want_kw} [{done}/{total}]"
        if fix:
            lines[g] = f"* {want_kw} {gm.group(2)} [{done}/{total}]"
            path.write_text("\n".join(lines) + "\n")
    return done, total, change


def main():
    args = sys.argv[1:]
    check_only, want_list = "--check" in args, "--list" in args
    lines = INDEX.read_text().splitlines()
    nodes = parse_index(lines)
    closed_nodes = parse_index(CLOSED.read_text().splitlines()) if CLOSED.exists() else []
    out = []

    # 1-2. checklist counts, then ACTIVE <-> DONE
    for n in nodes:
        if n["state"] == "TODO":
            continue
        active = WT_DIR / n["id"] / "walkthrough.org"
        settled = CONTEXT_DIR / n["id"] / "outcome.org"
        path = active if active.exists() else settled if settled.exists() else None
        if path is None:
            continue  # the validator reports an ACTIVE/DONE node with no file
        is_active = path == active
        done, total, change = checklist(path, fix=is_active and not check_only)
        if total is None:
            continue
        if change:
            where = "" if is_active else " (archived, NOT edited — fix by hand)"
            out.append(f"CHECKLIST: {n['title']}: {change}{where}")
        complete = total > 0 and done == total
        if not is_active:
            continue  # archived: must already be DONE; the validator checks
        want = "DONE" if complete else "ACTIVE"
        if n["state"] != want:
            out.append(f"{'CLOSED' if want == 'DONE' else 'REOPENED'}: {n['title']} "
                       f"({n['state']} -> {want}, checklist [{done}/{total}])")
            m = NODE_RE.match(lines[n["line"]])
            lines[n["line"]] = (f"{m.group(1)}{want}{m.group(3)}{m.group(4)}"
                                f"{m.group(5) or ''}")
            n["state"] = want

    # 3. :BLOCKED: from the (possibly updated) states
    state_by_id = {n["id"].lower(): n["state"] for n in closed_nodes + nodes}

    def blocked(n):
        return n["state"] != "DONE" and any(
            state_by_id.get(b.lower(), "TODO") != "DONE" for b in n["blocked_by"])

    inserts = []
    for n in nodes:
        want = "true" if blocked(n) else "false"
        f = n["fields"]
        if "BLOCKED" in f:
            fm = FIELD_RE.match(lines[f["BLOCKED"]])
            have = fm.group(4).strip()
            if have != want:
                if have == "true" and want == "false" and n["state"] != "DONE":
                    out.append(f"NEWLY READY: {n['title']}")
                elif have == "false" and want == "true":
                    out.append(f"NOW BLOCKED: {n['title']}")
                elif have not in ("true", "false"):
                    out.append(f"BLOCKED SET: {n['title']}: '{have}' -> {want}")
                lines[f["BLOCKED"]] = f"{fm.group(1)}:BLOCKED:{fm.group(3)}{want}"
        else:
            out.append(f"BLOCKED SET: {n['title']}: (missing) -> {want}")
            indent = FIELD_RE.match(lines[f["ID"]]).group(1)
            inserts.append((f.get("BLOCKED_BY", f["ID"]), f"{indent}:BLOCKED:     {want}"))
    for anchor, text in sorted(inserts, reverse=True):
        lines.insert(anchor + 1, text)

    # 4. settled issues leave index.org (after inserts, so line numbers are final)
    to_move = []
    for n in parse_index(lines):
        if n["state"] == "DONE" and (CONTEXT_DIR / n["id"] / "outcome.org").exists():
            to_move.append(n["line"])
            out.append(f"MOVED TO CLOSED: {n['title']}")
    if to_move:
        lines = move_to_closed(lines, to_move, check_only)

    index_changed = any(not o.startswith("CHECKLIST") for o in out)
    if index_changed and not check_only:
        INDEX.write_text("\n".join(lines).rstrip("\n") + "\n")

    for o in out:
        print(("WOULD " if check_only else "") + o)
    if want_list:
        for n in parse_index(lines):
            if n["state"] != "DONE":
                print(f"{'BLOCKED' if blocked(n) else 'READY':<8} {n['state']:<6}  {n['title']}")
    if check_only and out:
        print(f"{len(out)} derived value(s) out of date — run SCRIPTS/sync-index.py",
              file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
