#!/usr/bin/env python3
"""Validate the flashcards feature (.agents/flashcards/) against the rules
in .agents/walkthroughs/INSTRUCTIONS/06-flashcards-guide.org. Exits non-zero
if any check fails.

Also cross-checks flashcard card UUIDs against every UUID already in use
under .agents/walkthroughs/ and .agents/wikis/, per 00-conventions.org's
"one namespace" rule. This script does not re-validate those trees' own
internal structure — validate-walkthroughs.py already does that; run both
after any change here, since each builds its own UUID registry
independently and neither catches a cross-script collision by reading
alone, only by comparing.

Usage: .agents/flashcards/SCRIPTS/validate-flashcards.py
"""

import re
import sys
from pathlib import Path

FC_DIR = Path(__file__).resolve().parent.parent
ROOT = FC_DIR.parent.parent
WT_DIR = ROOT / ".agents" / "walkthroughs"
WT_INDEX = WT_DIR / "index.org"
WT_ARCHIVE_DIR = WT_DIR / "archive"
FLASHCARDS_INDEX = FC_DIR / "index.org"
WIKIS_DIR = ROOT / ".agents" / "wikis"
SKIP_DIRS = {"SCRIPTS"}

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)
DECK_DIR_RE = UUID_RE
DRAWER_ID_RE = re.compile(r"^:ID:\s*(\S+)", re.I)
CARD_HEADING_RE = re.compile(r"^\* Card: (.*)$")
CLOZE_SPAN_RE = re.compile(r"\{\{c\d+::.+?\}\}")
FILE_LINK_RE = re.compile(r"\[\[file:([^\]]+)\]")
INDEX_NODE_RE = re.compile(r"^\*\*\*\s+(TODO|DONE)\s+.+$")

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


def preload_external_uuids():
    """Register every :ID: already in use under walkthroughs/ and wikis/,
    so a flashcard UUID that collides with one is caught here too — those
    trees' own validator only checks collisions *within* themselves."""
    external_files = []
    if WT_DIR.exists():
        external_files.extend(WT_DIR.rglob("*.org"))
    if WIKIS_DIR.exists():
        external_files.extend(WIKIS_DIR.rglob("*.org"))
    for f in external_files:
        for m in DRAWER_ID_RE.finditer(f.read_text(errors="replace")):
            uuid = m.group(1)
            if UUID_RE.match(uuid):
                # Pre-seed only; a genuine external/external collision is
                # that tree's own validator's problem, not ours to report.
                seen_uuids.setdefault(uuid.lower(), f"(external) {f.relative_to(ROOT)}")


def archived_walkthrough_ids():
    """uuid -> title, for every DONE node in walkthroughs/index.org whose
    package has actually been archived."""
    if not WT_INDEX.exists():
        fail(f"{WT_INDEX.relative_to(ROOT)}: does not exist")
        return {}
    text = WT_INDEX.read_text()
    lines = text.splitlines()
    result = {}
    i = 0
    while i < len(lines):
        m = INDEX_NODE_RE.match(lines[i])
        if m and m.group(1) == "DONE":
            title = re.sub(r"^\*\*\*\s+DONE\s+", "", lines[i])
            title = re.sub(r"\s+:[\w:]+:$", "", title).strip()
            j = i + 1
            node_id = None
            while j < len(lines) and not lines[j].strip().startswith("***"):
                dm = DRAWER_ID_RE.match(lines[j].strip())
                if dm:
                    node_id = dm.group(1)
                j += 1
            if node_id and (WT_ARCHIVE_DIR / f"{node_id}.org").exists():
                result[node_id.lower()] = title
            i = j
        else:
            i += 1
    return result


def parse_deck(path):
    """Yield one dict per '* Card: ...' block in a deck file."""
    text = path.read_text()
    lines = text.splitlines()
    card_starts = [i for i, l in enumerate(lines) if CARD_HEADING_RE.match(l)]
    for idx, start in enumerate(card_starts):
        end = card_starts[idx + 1] if idx + 1 < len(card_starts) else len(lines)
        block = lines[start:end]
        heading = CARD_HEADING_RE.match(block[0]).group(1).strip()
        card_id = None
        card_type = None
        in_drawer = False
        back = None
        source_line = None
        tags_line = None
        for l in block[1:]:
            s = l.strip()
            if s == ":PROPERTIES:":
                in_drawer = True
                continue
            if s == ":END:":
                in_drawer = False
                continue
            if in_drawer:
                idm = DRAWER_ID_RE.match(s)
                if idm:
                    card_id = idm.group(1)
                tm = re.match(r"^:TYPE:\s*(\S+)", s, re.I)
                if tm:
                    card_type = tm.group(1).lower()
            elif s.startswith("*Back:*"):
                back = s[len("*Back:*"):].strip()
            elif s.startswith("*Source:*"):
                source_line = s[len("*Source:*"):].strip()
            elif s.startswith("*Tags:*"):
                tags_line = s[len("*Tags:*"):].strip()
        yield {
            "heading": heading,
            "id": card_id,
            "type": card_type,
            "back": back,
            "source_line": source_line,
            "tags_line": tags_line,
            "line_no": start + 1,
            "path": path,
        }


def validate_card(card, location_prefix, expected_source_id):
    loc = f"{location_prefix} (line {card['line_no']})"

    if not card["id"]:
        fail(f"{loc}: card has no :ID: in a :PROPERTIES: drawer")
    else:
        register_uuid(card["id"], loc)

    if card["type"] not in ("basic", "cloze"):
        fail(f"{loc}: :TYPE: must be 'basic' or 'cloze', got {card['type']!r}")
    elif card["type"] == "basic":
        if not card["back"]:
            fail(f"{loc}: basic card has no non-empty *Back:* line")
    elif card["type"] == "cloze":
        if not CLOZE_SPAN_RE.search(card["heading"]):
            fail(f"{loc}: cloze card heading has no valid {{{{c1::...}}}} span")

    if not card["source_line"]:
        fail(f"{loc}: card has no *Source:* line")
    else:
        links = FILE_LINK_RE.findall(card["source_line"])
        if not links:
            fail(f"{loc}: *Source:* line has no [[file:...]] link")
        for link in links:
            target = (card["path"].parent / link.split("::")[0]).resolve()
            if not target.exists():
                fail(f"{loc}: *Source:* link target does not exist: {link}")
            elif target != (WT_ARCHIVE_DIR / f"{expected_source_id}.org").resolve():
                fail(f"{loc}: *Source:* link does not point at this deck's own "
                     f"source walkthroughs/archive/{expected_source_id}.org: {link}")

    if not card["tags_line"] or not re.match(r"^:[^:\s][^:]*(::[^:\s][^:]*)*:$",
                                              card["tags_line"]):
        warn(f"{loc}: *Tags:* line missing or not in :Domain::Subcategory::slug: form")


def validate_no_dangling_file_links(path, text):
    for link in FILE_LINK_RE.findall(text):
        target_str = link.split("::")[0]
        if target_str.startswith(("http://", "https://", "mailto:")):
            continue
        target = (path.parent / target_str).resolve()
        if not target.exists():
            fail(f"{path.relative_to(ROOT)}: dangling link target: {link}")


def main():
    preload_external_uuids()
    archived = archived_walkthrough_ids()

    if not FLASHCARDS_INDEX.exists():
        fail(f"{FLASHCARDS_INDEX.relative_to(ROOT)}: does not exist")
    index_text = FLASHCARDS_INDEX.read_text() if FLASHCARDS_INDEX.exists() else ""

    deck_dirs = sorted(
        d for d in FC_DIR.iterdir() if d.is_dir() and d.name not in SKIP_DIRS
    ) if FC_DIR.exists() else []
    seen_deck_ids = set()

    for deck_dir in deck_dirs:
        if not DECK_DIR_RE.match(deck_dir.name):
            fail(f"{deck_dir.relative_to(ROOT)}: directory name is not a valid UUID")
            continue
        deck_id = deck_dir.name.lower()
        seen_deck_ids.add(deck_id)
        if deck_id not in archived:
            fail(f"{deck_dir.relative_to(ROOT)}: UUID does not match a DONE, "
                 f"archived walkthrough in walkthroughs/index.org")

        deck_path = deck_dir / "deck.org"
        if not deck_path.exists():
            fail(f"{deck_dir.relative_to(ROOT)}: missing deck.org")
            continue

        rel_link = f"{deck_dir.name}/deck.org"
        if rel_link not in index_text:
            fail(f"{deck_path.relative_to(ROOT)}: not linked from flashcards/index.org")

        deck_text = deck_path.read_text()
        if not re.search(r"^\* For AI Assistants\s*$", deck_text, re.M):
            fail(f"{deck_path.relative_to(ROOT)}: missing required "
                 f"'* For AI Assistants' section — see 06-flashcards-guide.org's "
                 f"Deck Template")

        cards = list(parse_deck(deck_path))
        if not cards:
            warn(f"{deck_path.relative_to(ROOT)}: deck file has no '* Card:' entries")
        for card in cards:
            validate_card(card, str(deck_path.relative_to(ROOT)), deck_dir.name)

        validate_no_dangling_file_links(deck_path, deck_text)

    for uuid, title in sorted(archived.items(), key=lambda kv: kv[1]):
        if uuid not in seen_deck_ids:
            warn(f"no deck yet for archived walkthrough '{title}' ({uuid})")

    if FLASHCARDS_INDEX.exists():
        validate_no_dangling_file_links(FLASHCARDS_INDEX, index_text)

    for w in warnings:
        print(f"WARN: {w}")
    for f in failures:
        print(f"FAIL: {f}")

    print()
    print(f"{len(failures)} failure(s), {len(warnings)} warning(s)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
