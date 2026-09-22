#!/usr/bin/env python3
"""Validate .agents/walkthroughs/ against the rules in
INSTRUCTIONS/00-conventions.org, 01-index-guide.org, 02-expansion-guide.org,
04-archive-guide.org, and 08-context-guide.org. Exits non-zero if any check
fails.

Usage: .agents/walkthroughs/SCRIPTS/validate-walkthroughs.py
"""

import re
import sys
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
ROOT = WT_DIR.parent.parent
INDEX = WT_DIR / "index.org"
CONVENTIONS = WT_DIR / "INSTRUCTIONS" / "00-conventions.org"
CONTEXT_DIR = WT_DIR / "CONTEXT"
SKIP_DIRS = {"INSTRUCTIONS", "SCRIPTS", "CONTEXT", "inbox", "obsidian-graph"}
CONTEXT_VALID_SOURCES = {"you", "agent"}
CONTEXT_VALID_STATUSES = {"proposed", "approved", "mined"}
OUTCOME_FILENAME = "outcome.org"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
UUID_ANY_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)
SESH_RE = re.compile(r"^\d+-.+-SESH\.\w+$", re.I)
SESH_LOOSE_RE = re.compile(r"sesh", re.I)
DANGLING_SESH_LINK_RE = re.compile(r"\[\[file:[^\]]*\d+-[^\]/]+-SESH\.\w+", re.I)
FILE_LINK_RE = re.compile(r"\[\[file:([^\]]+)\]")
CHECKED_STEP_RE = re.compile(r"^-\s+\[[Xx]\]\s+\S")
RESULT_RE = re.compile(r"^\s*\*Result:\*\s*\S")

failures = []
warnings = []
seen_uuids = {}  # lowercased uuid -> first location string


def fail(msg):
    failures.append(msg)


def warn(msg):
    warnings.append(msg)


def register_uuid(uuid, location):
    if not UUID_RE.match(uuid):
        fail(f"{location}: '{uuid}' is not a valid UUID")
        return
    key = uuid.lower()
    if key in seen_uuids:
        fail(f"{location}: UUID {uuid} collides with {seen_uuids[key]}")
    else:
        seen_uuids[key] = location


def extract_drawer_id(lines, start, stop):
    """First :ID: value inside a :PROPERTIES:...:END: drawer in lines[start:stop]."""
    in_drawer = False
    id_val = None
    for line in lines[start:stop]:
        s = line.strip()
        if s == ":PROPERTIES:":
            in_drawer = True
            continue
        if s == ":END:":
            in_drawer = False
            continue
        if in_drawer and re.match(r"^:ID:\s*", s, re.I):
            id_val = re.sub(r"^:ID:\s*", "", s, flags=re.I).strip()
    return id_val


def extract_drawer_field(lines, start, stop, field):
    """First :<field>: value inside a :PROPERTIES:...:END: drawer in
    lines[start:stop]. Generic version of extract_drawer_id, used for
    index.org's :BLOCKED_BY: and CONTEXT's :SOURCE:/:STATUS: fields."""
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


def current_guide_version():
    if not CONVENTIONS.exists():
        fail(f"{CONVENTIONS.relative_to(ROOT)}: file is missing")
        return None
    text = CONVENTIONS.read_text()
    m = re.search(r"^#\+WALKTHROUGH_GUIDE_VERSION:\s*(\S+)", text, re.M)
    if not m:
        fail(f"{CONVENTIONS.relative_to(ROOT)}: missing #+WALKTHROUGH_GUIDE_VERSION:")
        return None
    return m.group(1)


def validate_index():
    """Returns {uuid: {"state", "title", "has_link", "loc", "blocked_by"}}."""
    node_ids = {}
    if not INDEX.exists():
        fail(f"{INDEX.relative_to(ROOT)}: file is missing")
        return node_ids

    lines = INDEX.read_text().splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    for i, line in enumerate(lines):
        m = re.match(r"^\*\*\*\s+(TODO|DONE)\s+(.*)$", line)
        if not m:
            continue
        state, title = m.group(1), m.group(2).strip()
        loc = f"index.org:{i + 1}"

        if UUID_ANY_RE.search(title):
            fail(f"{loc}: heading text contains a raw UUID: '{title}'")

        next_idx = next((h for h in heading_idxs if h > i), len(lines))
        node_id = extract_drawer_id(lines, i + 1, next_idx)
        if not node_id:
            fail(f"{loc}: node '{title}' has no :ID: drawer")
            continue
        register_uuid(node_id, loc)

        blocked_by_val = extract_drawer_field(lines, i + 1, next_idx, "BLOCKED_BY")
        blocked_by = blocked_by_val.split() if blocked_by_val else []

        has_link = any(
            f"file:{node_id}/walkthrough.org" in l
            or f"file:CONTEXT/{node_id}/{OUTCOME_FILENAME}" in l
            for l in lines[i + 1 : next_idx]
        )
        node_ids[node_id] = {
            "state": state,
            "title": title,
            "has_link": has_link,
            "loc": loc,
            "blocked_by": blocked_by,
        }
        if state == "DONE" and not has_link:
            fail(f"{loc}: DONE node '{title}' has no walkthrough link")
        if state == "TODO" and has_link:
            warn(f"{loc}: TODO node '{title}' has a walkthrough link — should this be DONE?")

    validate_dependency_graph(node_ids)
    return node_ids


def validate_dependency_graph(node_ids):
    """See 01-index-guide.org's 'The Blocked By Property': every
    :BLOCKED_BY: UUID must resolve to a real node, and the graph they
    form must be acyclic. Plain DFS with a 3-color scheme is enough here
    — this graph is small enough that Tarjan's SCC machinery would be
    solving a problem of a scale this system never reaches."""
    by_lower = {k.lower(): k for k in node_ids}

    for node_id, info in node_ids.items():
        for blocker in info["blocked_by"]:
            if blocker.lower() not in by_lower:
                fail(
                    f"{info['loc']}: node '{info['title']}' has "
                    f":BLOCKED_BY: {blocker}, which doesn't match any "
                    f"index.org node"
                )

    WHITE, GRAY, BLACK = 0, 1, 2
    color = {nid: WHITE for nid in node_ids}

    def visit(nid, path):
        color[nid] = GRAY
        for blocker in node_ids[nid]["blocked_by"]:
            key = by_lower.get(blocker.lower())
            if key is None:
                continue  # already reported above
            if color[key] == GRAY:
                cycle = " -> ".join(path + [node_ids[key]["title"]])
                fail(f"circular :BLOCKED_BY: dependency: {cycle}")
            elif color[key] == WHITE:
                visit(key, path + [node_ids[key]["title"]])
        color[nid] = BLACK

    for nid in node_ids:
        if color[nid] == WHITE:
            visit(nid, [node_ids[nid]["title"]])


def find_package_dirs():
    dirs = {}
    if not WT_DIR.is_dir():
        return dirs
    for p in WT_DIR.iterdir():
        if not p.is_dir() or p.name in SKIP_DIRS:
            continue
        if not UUID_RE.match(p.name):
            warn(f"{p.relative_to(ROOT)}: directory name is not a UUID, skipping")
            continue
        dirs[p.name] = p
    return dirs


def find_settled_outcomes():
    """{uuid: path} for CONTEXT/<uuid>/outcome.org files — a settled,
    permanently read-only walkthrough record folded into the same
    directory as the research behind it. See 04-archive-guide.org."""
    files = {}
    if not CONTEXT_DIR.is_dir():
        return files
    for p in CONTEXT_DIR.iterdir():
        if not p.is_dir() or not UUID_RE.match(p.name):
            continue
        outcome = p / OUTCOME_FILENAME
        if outcome.is_file():
            files[p.name] = outcome
    return files


def cross_check(node_ids, package_dirs, settled):
    dupes = set(package_dirs) & set(settled)
    for node_id in dupes:
        fail(
            f"{node_id}: exists both as an active "
            f".agents/walkthroughs/{node_id}/ directory and as "
            f".agents/walkthroughs/CONTEXT/{node_id}/{OUTCOME_FILENAME} — "
            f"archiving is a move, not a copy; delete the active directory"
        )

    for node_id, info in node_ids.items():
        if info["state"] == "DONE" and node_id not in package_dirs and node_id not in settled:
            fail(
                f"{info['loc']}: DONE node '{info['title']}' has no matching "
                f".agents/walkthroughs/{node_id}/ directory or "
                f".agents/walkthroughs/CONTEXT/{node_id}/{OUTCOME_FILENAME} file"
            )
    for dir_id, path in package_dirs.items():
        rel = path.relative_to(ROOT)
        if dir_id not in node_ids:
            fail(f"{rel}: no matching index.org node for this UUID")
        elif node_ids[dir_id]["state"] != "DONE":
            fail(f"{rel}: package exists but index.org node is not DONE")
    for settled_id, path in settled.items():
        rel = path.relative_to(ROOT)
        if settled_id not in node_ids:
            fail(f"{rel}: no matching index.org node for this UUID")
        elif node_ids[settled_id]["state"] != "DONE":
            fail(f"{rel}: settled outcome exists but index.org node is not DONE")


REQUIRED_SECTIONS = ["Notes", "Search Prompts"]
# New required sections go here keyed by the guide version that introduced
# them, so old packages that haven't bumped their own version tag yet are
# only flagged via the version-staleness warning, not a hard failure —
# honoring 00-conventions.org's "not required to retrofit immediately" rule.
REQUIRED_SECTIONS_SINCE = {
    "For AI Assistants": 2,
}
RESULT_BLOCK_REQUIRED_SINCE = 3


FORBIDDEN_WHEN_SETTLED = ["For AI Assistants", "Search Prompts"]


def validate_walkthrough(wt_id, path, current_version, settled=False):
    """settled=True checks a CONTEXT/<uuid>/outcome.org (see
    04-archive-guide.org) instead of an active walkthrough.org: Problem,
    the Guide checklist, and Notes are still required exactly the same
    way, but 'For AI Assistants' and 'Search Prompts' are required to be
    *absent* instead — both brief someone about to work the file, and a
    settled outcome is never worked again."""
    rel = path.relative_to(ROOT)
    text = path.read_text()
    lines = text.splitlines()

    top_headings = [(i, l) for i, l in enumerate(lines) if re.match(r"^\*\s+\S", l)]
    titles = [re.sub(r"^\*\s+", "", l).strip() for _, l in top_headings]

    if "Problem" not in titles:
        fail(f"{rel}: missing '* Problem' section")

    guide_idx = None
    for idx, (_, l) in enumerate(top_headings):
        if re.match(r"^\*\s+(TODO|DONE)\s+.*\[\d+/\d+\]", l):
            guide_idx = idx
            break
    if guide_idx is None:
        fail(f"{rel}: missing Guide checklist heading ('* TODO <title> [x/n]')")

    if settled:
        if "Notes" not in titles:
            fail(f"{rel}: missing '* Notes' section")
        for name in FORBIDDEN_WHEN_SETTLED:
            if name in titles:
                fail(
                    f"{rel}: has a '* {name}' section — settled outcomes "
                    f"must have it stripped (see 04-archive-guide.org "
                    f"Archive Workflow, CRITICAL RULE 5)"
                )
    else:
        for name in REQUIRED_SECTIONS:
            if name not in titles:
                fail(f"{rel}: missing '* {name}' section")

    m = re.search(r"^#\+WALKTHROUGH_GUIDE_VERSION:\s*(\S+)", text, re.M)
    pkg_version = m.group(1) if m else None
    if not m:
        warn(f"{rel}: no #+WALKTHROUGH_GUIDE_VERSION: line")
    elif current_version and pkg_version != current_version:
        warn(
            f"{rel}: guide version {pkg_version} is behind current "
            f"({current_version}) — may be missing newer required sections"
        )

    try:
        pkg_version_int = int(pkg_version) if pkg_version is not None else None
    except ValueError:
        pkg_version_int = None
    if not settled:
        for name, since in REQUIRED_SECTIONS_SINCE.items():
            if (
                pkg_version_int is not None
                and pkg_version_int >= since
                and name not in titles
            ):
                fail(
                    f"{rel}: missing '* {name}' section (required since guide "
                    f"v{since}; this package declares v{pkg_version})"
                )

    for i, l in top_headings:
        if UUID_ANY_RE.search(l):
            fail(f"{rel}:{i + 1}: heading text contains a raw UUID")

    if guide_idx is not None:
        start = top_headings[guide_idx][0] + 1
        end = (
            top_headings[guide_idx + 1][0]
            if guide_idx + 1 < len(top_headings)
            else len(lines)
        )
        step_idxs = [
            i for i in range(start, end) if re.match(r"^-\s+\[[ Xx]\]\s+\S", lines[i])
        ]
        for si, step_i in enumerate(step_idxs):
            step_end = step_idxs[si + 1] if si + 1 < len(step_idxs) else end
            step_loc = f"{rel}:{step_i + 1}"
            if UUID_ANY_RE.search(lines[step_i]):
                fail(f"{step_loc}: step text contains a raw UUID")
            step_id = extract_drawer_id(lines, step_i + 1, step_end)
            if not step_id:
                fail(f"{step_loc}: checklist step has no :ID: drawer")
                continue
            register_uuid(step_id, step_loc)

            if (
                pkg_version_int is not None
                and pkg_version_int >= RESULT_BLOCK_REQUIRED_SINCE
                and CHECKED_STEP_RE.match(lines[step_i])
            ):
                has_result = any(
                    RESULT_RE.match(l) for l in lines[step_i + 1 : step_end]
                )
                if not has_result:
                    fail(
                        f"{step_loc}: step is checked [X] but has no "
                        f"non-empty '*Result:*' block — no step is marked "
                        f"done without its own real, verified output "
                        f"(required since guide v{RESULT_BLOCK_REQUIRED_SINCE}; "
                        f"this package declares v{pkg_version})"
                    )


def validate_supporting_files(dir_path, wt_text):
    """Every NN-<tool>-SESH.<ext> export in a package dir must be linked
    from that package's walkthrough.org (External Session Workflow rule).
    Any extension is fine — the export stays in its native format, never
    converted to .org."""
    for p in dir_path.iterdir():
        if not p.is_file() or p.name == "walkthrough.org":
            continue
        if SESH_RE.match(p.name):
            if f"file:{p.name}" not in wt_text:
                fail(
                    f"{p.relative_to(ROOT)}: session-export file is not linked "
                    f"from walkthrough.org (expected a 'file:{p.name}' link, "
                    f"e.g. in Notes)"
                )
        elif SESH_LOOSE_RE.search(p.name):
            fail(
                f"{p.relative_to(ROOT)}: filename looks like a session export "
                f"but doesn't match the required 'NN-<tool>-SESH.<ext>' pattern "
                f"(e.g. '01-GEMINI-SESH.md') — a name missing the sequence "
                f"number or the tool name is invisible to the linking check "
                f"above, which is exactly what this catches"
            )


def validate_settled_no_dangling_sesh_links(path, text):
    """A SESH export can never legitimately exist next to a settled
    outcome.org (it's deleted during archiving) — so any link to one is
    guaranteed dangling. See 04-archive-guide.org CRITICAL RULE 4."""
    rel = path.relative_to(ROOT)
    for m in DANGLING_SESH_LINK_RE.finditer(text):
        fail(
            f"{rel}: contains a dangling 'file:' link to a SESH export "
            f"({m.group(0)}...) — SESH files are deleted on archiving; "
            f"rewrite this as plain text (see 04-archive-guide.org "
            f"CRITICAL RULE 4)"
        )


def validate_no_dangling_file_links(path, text):
    """Every [[file:...]] link in a file this system actively maintains
    must resolve to a real file, relative to that file's own directory —
    a wrong number of '../' is exactly the kind of mistake that's easy to
    make and easy to miss by reading, since it looks correct until
    something actually tries to follow it."""
    rel = path.relative_to(ROOT)
    for m in FILE_LINK_RE.finditer(text):
        target = m.group(1).split("::", 1)[0]
        if not target or target.startswith(("http:", "https:", "mailto:")):
            continue
        target_path = (
            (ROOT / target.lstrip("/")) if target.startswith("/")
            else (path.parent / target)
        ).resolve()
        if not target_path.exists():
            fail(f"{rel}: dangling 'file:' link, target does not exist: "
                 f"{target}")


def validate_context(node_ids):
    """See INSTRUCTIONS/08-context-guide.org.

    CONTEXT is organized as one subdirectory per owning issue
    (CONTEXT/<issue-uuid>/), each with its own index.org — mirroring how
    walkthrough packages are one directory per issue UUID. This checks:
    every direct child of CONTEXT/ is a directory (nothing flat at the
    top level any more); each subdirectory's name is a valid UUID
    matching some real index.org node (any state — CONTEXT research
    routinely predates an issue's own expansion, so DONE is not
    required, unlike a walkthrough package); each subdirectory has an
    index.org; and each index.org is validated the same way the old
    single flat file was, scoped to just that subdirectory's files.
    """
    if not CONTEXT_DIR.is_dir():
        return

    for p in CONTEXT_DIR.iterdir():
        if not p.is_dir():
            fail(f"{p.relative_to(ROOT)}: CONTEXT/ must contain only "
                 f"per-issue subdirectories — no loose files at this level")
            continue
        validate_context_subdir(p, node_ids)


def validate_context_subdir(sub_dir, node_ids):
    rel_dir = sub_dir.relative_to(ROOT)
    if not UUID_RE.match(sub_dir.name):
        fail(f"{rel_dir}: subdirectory name is not a UUID")
        return
    if sub_dir.name not in node_ids:
        fail(f"{rel_dir}: no matching index.org node for this UUID")

    index_path = sub_dir / "index.org"
    if not index_path.exists():
        other_files = [
            p for p in sub_dir.iterdir()
            if p.is_file() and p.name != OUTCOME_FILENAME
        ]
        if other_files:
            fail(f"{rel_dir}: missing index.org")
        # Else: this subdirectory holds only a settled outcome.org (see
        # 04-archive-guide.org) or is otherwise empty — nothing to index.
        return

    text = index_path.read_text()
    lines = text.splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    indexed_files = set()
    for i, line in enumerate(lines):
        if not re.match(r"^\*\s+\S", line):
            continue
        loc = f"{rel_dir / 'index.org'}:{i + 1}"
        next_idx = next((h for h in heading_idxs if h > i), len(lines))

        if UUID_ANY_RE.search(line):
            fail(f"{loc}: heading text contains a raw UUID: '{line.strip()}'")

        entry_id = extract_drawer_id(lines, i + 1, next_idx)
        if not entry_id:
            fail(f"{loc}: entry has no :ID: drawer")
            continue
        register_uuid(entry_id, loc)

        source_val = extract_drawer_field(lines, i + 1, next_idx, "SOURCE")
        if source_val not in CONTEXT_VALID_SOURCES:
            fail(f"{loc}: ':SOURCE:' value '{source_val}' must be one of "
                 f"{sorted(CONTEXT_VALID_SOURCES)}")

        status_val = extract_drawer_field(lines, i + 1, next_idx, "STATUS")
        if status_val not in CONTEXT_VALID_STATUSES:
            fail(f"{loc}: ':STATUS:' value '{status_val}' must be one of "
                 f"{sorted(CONTEXT_VALID_STATUSES)}")
        if source_val == "you" and status_val == "proposed":
            fail(f"{loc}: 'SOURCE: you' entries are auto-approved and can "
                 f"never be 'STATUS: proposed'")

        m = FILE_LINK_RE.search("\n".join(lines[i + 1:next_idx]))
        if not m:
            fail(f"{loc}: entry has no 'file:' link to its actual CONTEXT file")
        else:
            target = (sub_dir / m.group(1).split("::", 1)[0]).resolve()
            if not target.exists():
                fail(f"{loc}: 'file:' link target does not exist: {m.group(1)}")
            else:
                indexed_files.add(target)

    for p in sub_dir.iterdir():
        if (
            not p.is_file()
            or p.name in ("index.org", OUTCOME_FILENAME)
            or p.resolve() in indexed_files
        ):
            continue
        fail(f"{p.relative_to(ROOT)}: file is not listed in {rel_dir / 'index.org'}")

    validate_no_dangling_file_links(index_path, text)


def main():
    current_version = current_guide_version()
    node_ids = validate_index()
    package_dirs = find_package_dirs()
    settled = find_settled_outcomes()
    cross_check(node_ids, package_dirs, settled)

    if INDEX.exists():
        validate_no_dangling_file_links(INDEX, INDEX.read_text())

    for wt_id, dir_path in sorted(package_dirs.items()):
        wt_file = dir_path / "walkthrough.org"
        if not wt_file.exists():
            fail(f"{dir_path.relative_to(ROOT)}: missing walkthrough.org")
            continue
        validate_walkthrough(wt_id, wt_file, current_version)
        validate_supporting_files(dir_path, wt_file.read_text())
        validate_no_dangling_file_links(wt_file, wt_file.read_text())

    for settled_id, outcome_file in sorted(settled.items()):
        # A settled outcome carries the same content requirements as an
        # active walkthrough.org minus 'For AI Assistants'/'Search
        # Prompts' (settled=True flips that check). No
        # validate_supporting_files call: archiving means there's nothing
        # left to check (SESH exports are deleted, not moved).
        validate_walkthrough(settled_id, outcome_file, current_version, settled=True)
        validate_settled_no_dangling_sesh_links(outcome_file, outcome_file.read_text())
        validate_no_dangling_file_links(outcome_file, outcome_file.read_text())

    validate_context(node_ids)

    for w in warnings:
        print(f"WARN: {w}")
    for f in failures:
        print(f"FAIL: {f}")

    print()
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
