#!/usr/bin/env python3
"""Validate .agents/walkthroughs/ (and .agents/wikis/) against the rules in
INSTRUCTIONS/00-conventions.org, 01-index-guide.org, 02-expansion-guide.org,
04-archive-guide.org, 05-wiki-guide.org, and 08-context-guide.org. Exits
non-zero if any check fails.

Usage: .agents/walkthroughs/SCRIPTS/validate-walkthroughs.py
"""

import re
import sys
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
ROOT = WT_DIR.parent.parent
INDEX = WT_DIR / "index.org"
CONVENTIONS = WT_DIR / "INSTRUCTIONS" / "00-conventions.org"
ARCHIVE_DIR = WT_DIR / "archive"
WIKIS_DIR = WT_DIR.parent / "wikis"
WIKI_META_FILES = {"index.org", "CHANGELOG.org"}
CONTEXT_DIR = WT_DIR / "CONTEXT"
CONTEXT_INDEX = CONTEXT_DIR / "context_index.org"
SKIP_DIRS = {"INSTRUCTIONS", "SCRIPTS", "archive", "CONTEXT"}
CONTEXT_VALID_SOURCES = {"you", "agent"}
CONTEXT_VALID_STATUSES = {"proposed", "approved", "mined"}

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
UUID_ANY_RE = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}", re.I
)
ARCHIVE_FILE_RE = re.compile(
    r"^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})\.org$", re.I
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


def extract_drawer_step(lines, start, stop):
    """First :STEP: value inside a :PROPERTIES:...:END: drawer in lines[start:stop]."""
    in_drawer = False
    step_val = None
    for line in lines[start:stop]:
        s = line.strip()
        if s == ":PROPERTIES:":
            in_drawer = True
            continue
        if s == ":END:":
            in_drawer = False
            continue
        if in_drawer and re.match(r"^:STEP:\s*", s, re.I):
            step_val = re.sub(r"^:STEP:\s*", "", s, flags=re.I).strip()
    return step_val


def extract_drawer_field(lines, start, stop, field):
    """First :<field>: value inside a :PROPERTIES:...:END: drawer in
    lines[start:stop]. Generic version of extract_drawer_id/_step, used
    for context_index.org's :SOURCE:/:STATUS: fields."""
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


seen_steps = {}  # int -> first location string, index.org's own :STEP: sequence


def register_step(step_val, location):
    if not re.match(r"^\d+$", step_val or ""):
        fail(f"{location}: ':STEP:' value '{step_val}' is not a positive integer")
        return
    key = int(step_val)
    if key in seen_steps:
        fail(f"{location}: ':STEP:' {key} collides with {seen_steps[key]}")
    else:
        seen_steps[key] = location


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
    """Returns {uuid: {"state", "title", "has_link", "loc"}}."""
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

        step_val = extract_drawer_step(lines, i + 1, next_idx)
        if not step_val:
            fail(f"{loc}: node '{title}' has no :STEP: property")
        else:
            register_step(step_val, loc)

        has_link = any(
            f"file:{node_id}/walkthrough.org" in l or f"file:archive/{node_id}.org" in l
            for l in lines[i + 1 : next_idx]
        )
        node_ids[node_id] = {
            "state": state,
            "title": title,
            "has_link": has_link,
            "loc": loc,
        }
        if state == "DONE" and not has_link:
            fail(f"{loc}: DONE node '{title}' has no walkthrough link")
        if state == "TODO" and has_link:
            warn(f"{loc}: TODO node '{title}' has a walkthrough link — should this be DONE?")

    return node_ids


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


def find_archived_packages():
    """{uuid: path} for archive/<uuid>.org files."""
    files = {}
    if not ARCHIVE_DIR.is_dir():
        return files
    for p in ARCHIVE_DIR.iterdir():
        if not p.is_file():
            continue
        m = ARCHIVE_FILE_RE.match(p.name)
        if not m:
            warn(f"{p.relative_to(ROOT)}: filename is not '<uuid>.org', skipping")
            continue
        files[m.group(1)] = p
    return files


def cross_check(node_ids, package_dirs, archived):
    dupes = set(package_dirs) & set(archived)
    for node_id in dupes:
        fail(
            f"{node_id}: exists both as an active "
            f".agents/walkthroughs/{node_id}/ directory and as "
            f".agents/walkthroughs/archive/{node_id}.org — archiving is a "
            f"move, not a copy; delete the active directory"
        )

    for node_id, info in node_ids.items():
        if info["state"] == "DONE" and node_id not in package_dirs and node_id not in archived:
            fail(
                f"{info['loc']}: DONE node '{info['title']}' has no matching "
                f".agents/walkthroughs/{node_id}/ directory or "
                f".agents/walkthroughs/archive/{node_id}.org file"
            )
    for dir_id, path in package_dirs.items():
        rel = path.relative_to(ROOT)
        if dir_id not in node_ids:
            fail(f"{rel}: no matching index.org node for this UUID")
        elif node_ids[dir_id]["state"] != "DONE":
            fail(f"{rel}: package exists but index.org node is not DONE")
    for arc_id, path in archived.items():
        rel = path.relative_to(ROOT)
        if arc_id not in node_ids:
            fail(f"{rel}: no matching index.org node for this UUID")
        elif node_ids[arc_id]["state"] != "DONE":
            fail(f"{rel}: archived package exists but index.org node is not DONE")


REQUIRED_SECTIONS = ["Notes", "Search Prompts"]
# New required sections go here keyed by the guide version that introduced
# them, so old packages that haven't bumped their own version tag yet are
# only flagged via the version-staleness warning, not a hard failure —
# honoring 00-conventions.org's "not required to retrofit immediately" rule.
REQUIRED_SECTIONS_SINCE = {
    "For AI Assistants": 2,
}
RESULT_BLOCK_REQUIRED_SINCE = 3


def validate_walkthrough(wt_id, path, current_version):
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
    converted to .org (see 00-conventions.org's Changelog, v6)."""
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


def validate_archived_no_dangling_sesh_links(path, text):
    """A SESH export can never legitimately exist next to an archived
    <uuid>.org file (it's deleted during archiving) — so any link to one
    is guaranteed dangling. See 04-archive-guide.org CRITICAL RULE 4."""
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
    something actually tries to follow it. Hit twice in practice while
    writing cross-links from an active package directory to .agents/wikis/
    before this check existed."""
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


def validate_wikis():
    """See INSTRUCTIONS/05-wiki-guide.org's 'What the Validator Checks'."""
    if not WIKIS_DIR.is_dir():
        return
    index_file = WIKIS_DIR / "index.org"
    if not index_file.exists():
        fail(f"{WIKIS_DIR.relative_to(ROOT)}: missing index.org")
        return
    index_text = index_file.read_text()

    for p in WIKIS_DIR.iterdir():
        if not p.is_file() or p.name in WIKI_META_FILES:
            continue
        rel = p.relative_to(ROOT)
        if p.suffix != ".org":
            fail(f"{rel}: every file in .agents/wikis/ must be .org "
                 f"(readable in Emacs like everything else in this system)")
            continue
        if f"file:{p.name}" not in index_text:
            fail(f"{rel}: page is not linked from wikis/index.org — an "
                 f"orphaned page defeats the point of a single entry point")

        text = p.read_text()
        lines = text.splitlines()
        page_id = extract_drawer_id(lines, 0, len(lines))
        if not page_id:
            fail(f"{rel}: no ':PROPERTIES:'/':ID:' drawer found")
        else:
            register_uuid(page_id, str(rel))

        jb_links = re.findall(r"\[\[file:(\.\./walkthroughs/archive/[^\]]+\.org)\]", text)
        if not jb_links:
            fail(f"{rel}: no '* Justified By' link to an archived "
                 f"walkthrough found")
        for link in jb_links:
            target = (WIKIS_DIR / link).resolve()
            if not target.exists():
                fail(f"{rel}: 'Justified By' link target does not exist: {link}")

        validate_no_dangling_file_links(p, text)

    for meta in WIKI_META_FILES:
        meta_path = WIKIS_DIR / meta
        if meta_path.exists():
            validate_no_dangling_file_links(meta_path, meta_path.read_text())


def validate_context():
    """See INSTRUCTIONS/08-context-guide.org."""
    if not CONTEXT_DIR.is_dir():
        return
    if not CONTEXT_INDEX.exists():
        fail(f"{CONTEXT_DIR.relative_to(ROOT)}: missing context_index.org")
        return

    text = CONTEXT_INDEX.read_text()
    lines = text.splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    indexed_files = set()
    for i, line in enumerate(lines):
        if not re.match(r"^\*\s+\S", line):
            continue
        loc = f"{CONTEXT_INDEX.relative_to(ROOT)}:{i + 1}"
        next_idx = next((h for h in heading_idxs if h > i), len(lines))

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
            target = (CONTEXT_DIR / m.group(1).split("::", 1)[0]).resolve()
            if not target.exists():
                fail(f"{loc}: 'file:' link target does not exist: {m.group(1)}")
            else:
                indexed_files.add(target)

    for p in CONTEXT_DIR.iterdir():
        if not p.is_file() or p.name == "context_index.org" or p.resolve() in indexed_files:
            continue
        fail(f"{p.relative_to(ROOT)}: file is not listed in context_index.org")

    validate_no_dangling_file_links(CONTEXT_INDEX, text)


def main():
    current_version = current_guide_version()
    node_ids = validate_index()
    package_dirs = find_package_dirs()
    archived = find_archived_packages()
    cross_check(node_ids, package_dirs, archived)

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

    for arc_id, arc_file in sorted(archived.items()):
        # Archived files carry identical content requirements to an active
        # walkthrough.org — only their location and filename differ. No
        # validate_supporting_files call: archiving means there's nothing
        # left to check (SESH exports are deleted, not moved).
        validate_walkthrough(arc_id, arc_file, current_version)
        validate_archived_no_dangling_sesh_links(arc_file, arc_file.read_text())
        validate_no_dangling_file_links(arc_file, arc_file.read_text())

    validate_wikis()
    validate_context()

    for w in warnings:
        print(f"WARN: {w}")
    for f in failures:
        print(f"FAIL: {f}")

    print()
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
