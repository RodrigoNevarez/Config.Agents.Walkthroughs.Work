#!/usr/bin/env python3
"""Generate a read-only Obsidian vault view of index.org's :BLOCKED_BY:
dependency graph, one Markdown file per issue.

index.org stays the single source of truth — this script only ever reads
it. The output directory is a disposable, regenerate-on-demand compiled
view (same "immutable source -> compiled artifact" split this system
already uses for CONTEXT/archive): never hand-edit a generated file,
just rerun this script after index.org changes. Safe to .gitignore.

Each generated <uuid>.md carries:
  - id: the issue's own :ID:, so the file is traceable back to its
    index.org node even though the filename is also the UUID.
  - aliases: the issue's real title, so Obsidian's graph/search/backlinks
    can show something legible instead of the raw UUID filename.
  - state: TODO or DONE.
  - blocked_by: a typed frontmatter list of [[uuid]] wikilinks — kept out
    of the body so a real dependency edge is never confused with a
    casual mention in prose.
  - tags: any Org tags on the heading, plus a synthetic state/todo or
    state/done tag so the core Graph view can group/color by state
    without needing a plugin.
The body is the issue's own description text (and =*End-State:*= line,
if present), verbatim — so clicking a node in Obsidian shows the real
problem, not an empty stub.

Usage: .agents/walkthroughs/SCRIPTS/generate-obsidian-graph.py [output-dir]
       (default output-dir: .agents/walkthroughs/obsidian-graph/)
"""

import re
import sys
from pathlib import Path

WT_DIR = Path(__file__).resolve().parent.parent
INDEX = WT_DIR / "index.org"
DEFAULT_OUTPUT = WT_DIR / "obsidian-graph"

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


def yaml_str(s):
    """Quote a string for safe inclusion as a YAML scalar."""
    escaped = s.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def yaml_list(items):
    if not items:
        return "[]"
    return "[" + ", ".join(yaml_str(i) for i in items) + "]"


def parse_index(text):
    """Returns a list of issue dicts: id, title, state, tags, domain,
    subcategory, blocked_by, body (list of description lines)."""
    lines = text.splitlines()
    heading_idxs = [i for i, l in enumerate(lines) if re.match(r"^\*+\s", l)]

    issues = []
    domain = None
    subcategory = None

    for i, line in enumerate(lines):
        star_m = re.match(r"^(\*+)\s+(.*)$", line)
        if not star_m:
            continue
        level, rest = len(star_m.group(1)), star_m.group(2)

        if level == 1:
            domain = rest.strip()
            subcategory = None
            continue
        if level == 2:
            subcategory = rest.strip()
            continue
        if level != 3:
            continue

        m = re.match(r"^(TODO|DONE)\s+(.*)$", rest)
        if not m:
            continue
        state, title_and_tags = m.group(1), m.group(2)

        tag_m = re.search(r"\s+(:[A-Za-z0-9_@:]+:)\s*$", title_and_tags)
        if tag_m:
            title = title_and_tags[: tag_m.start()].strip()
            tags = [t for t in tag_m.group(1).strip(":").split(":") if t]
        else:
            title = title_and_tags.strip()
            tags = []

        next_idx = next((h for h in heading_idxs if h > i), len(lines))

        in_drawer = False
        drawer_end = None
        issue_id = None
        blocked_by = []
        for j in range(i + 1, next_idx):
            s = lines[j].strip()
            if s == ":PROPERTIES:":
                in_drawer = True
                continue
            if s == ":END:":
                in_drawer = False
                drawer_end = j + 1
                continue
            if in_drawer and re.match(r"^:ID:\s*", s, re.I):
                issue_id = re.sub(r"^:ID:\s*", "", s, flags=re.I).strip()
            if in_drawer and re.match(r"^:BLOCKED_BY:\s*", s, re.I):
                val = re.sub(r"^:BLOCKED_BY:\s*", "", s, flags=re.I).strip()
                blocked_by = val.split() if val else []

        if not issue_id:
            continue  # validate-walkthroughs.py is what enforces this; skip here

        body_start = drawer_end if drawer_end is not None else i + 1
        body = [
            lines[j].strip()
            for j in range(body_start, next_idx)
            if lines[j].strip()
        ]  # de-indented — Org nests body text under the heading, but a
        # 4-space Markdown indent renders as a code block, not prose

        issues.append({
            "id": issue_id,
            "title": title,
            "state": state,
            "tags": tags,
            "domain": domain,
            "subcategory": subcategory,
            "blocked_by": blocked_by,
            "body": body,
        })

    return issues


def render(issue):
    tags = list(issue["tags"]) + [f"state/{issue['state'].lower()}"]
    blocked_by_links = [f"[[{b}]]" for b in issue["blocked_by"]]

    frontmatter = [
        "---",
        f"id: {yaml_str(issue['id'])}",
        f"aliases: {yaml_list([issue['title']])}",
        f"state: {yaml_str(issue['state'])}",
        f"domain: {yaml_str(issue['domain'] or '')}",
        f"subcategory: {yaml_str(issue['subcategory'] or '')}",
        f"tags: {yaml_list(tags)}",
        f"blocked_by: {yaml_list(blocked_by_links)}",
        "---",
        "",
        f"# {issue['title']}",
        "",
    ]
    if issue["body"]:
        frontmatter.extend(issue["body"])
        frontmatter.append("")
    frontmatter.append(
        "*Generated from `index.org` by `generate-obsidian-graph.py` — "
        "never hand-edit; rerun the script after `index.org` changes.*"
    )
    return "\n".join(frontmatter) + "\n"


def main():
    output_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUTPUT

    if not INDEX.exists():
        print(f"ERROR: {INDEX} does not exist", file=sys.stderr)
        sys.exit(1)

    issues = parse_index(INDEX.read_text())
    output_dir.mkdir(parents=True, exist_ok=True)

    current_ids = set()
    for issue in issues:
        if not UUID_RE.match(issue["id"]):
            print(f"WARN: skipping node with invalid :ID: {issue['id']!r}", file=sys.stderr)
            continue
        current_ids.add(issue["id"].lower())
        (output_dir / f"{issue['id']}.md").write_text(render(issue))

    removed = 0
    for p in output_dir.glob("*.md"):
        if p.stem.lower() not in current_ids:
            p.unlink()
            removed += 1

    print(f"Wrote {len(current_ids)} issue file(s) to {output_dir}"
          + (f", removed {removed} stale file(s)" if removed else ""))


if __name__ == "__main__":
    main()
