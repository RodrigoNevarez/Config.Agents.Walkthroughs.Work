#!/usr/bin/env python3
"""Export each .agents/flashcards/<uuid>/deck.org to that same directory's
own anki-export.txt, per
.agents/walkthroughs/INSTRUCTIONS/06-flashcards-guide.org's Export
Workflow — one artifact per deck, not one combined file.

Each output is a build artifact — regenerate it any time, never commit it
(see the guide's CRITICAL RULE on this). Re-importing after mining more of a
deck updates that deck's existing notes in place, because each row's GUID is
the card's own stable :ID:.

Usage: .agents/flashcards/SCRIPTS/export-anki.py [deck-uuid ...]
       (no args: export every deck under .agents/flashcards/)
"""

import re
import sys
from pathlib import Path

FC_DIR = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"SCRIPTS"}

CARD_HEADING_RE = re.compile(r"^\* Card: (.*)$")
DRAWER_ID_RE = re.compile(r"^:ID:\s*(\S+)", re.I)
ORG_LINK_WITH_DESC_RE = re.compile(r"\[\[file:[^\]]+\]\[([^\]]+)\]\]")
ORG_LINK_BARE_RE = re.compile(r"\[\[file:([^\]]+)\]\]")


def plain_text(s):
    """Strip Org [[file:...][desc]] link syntax down to readable text —
    Anki doesn't understand Org markup, so a raw org link would show up as
    dead bracket syntax instead of a citation a human can actually read."""
    s = ORG_LINK_WITH_DESC_RE.sub(r"\1", s)
    s = ORG_LINK_BARE_RE.sub(r"\1", s)
    return s

HEADER = [
    "#separator:Tab",
    "#html:true",
    "#guid column:1",
    "#notetype column:2",
    "#tags column:5",
]


def parse_deck(path):
    lines = path.read_text().splitlines()
    starts = [i for i, l in enumerate(lines) if CARD_HEADING_RE.match(l)]
    for idx, start in enumerate(starts):
        end = starts[idx + 1] if idx + 1 < len(starts) else len(lines)
        block = lines[start:end]
        heading = CARD_HEADING_RE.match(block[0]).group(1).strip()
        card_id = card_type = back = source_line = tags_line = None
        in_drawer = False
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
        if not (card_id and card_type):
            print(f"skipping malformed card at {path.name}:{start + 1} "
                  f"(missing :ID: or :TYPE:)", file=sys.stderr)
            continue
        yield {
            "id": card_id,
            "type": card_type,
            "heading": heading,
            "back": back or "",
            "source_line": plain_text(source_line or ""),
            "tags": (tags_line or "").strip(":").replace(":", " "),
        }


def to_row(card):
    notetype = {"basic": "Basic", "cloze": "Cloze"}.get(card["type"])
    if notetype is None:
        return None
    # Anki's import GUID (column 1) is an internal field, not something a
    # reviewer can casually read off the card mid-session — but a Study
    # Session (see the guide) needs the ID visible on the *front*, before
    # the card is flipped, so a short prefix is printed directly into the
    # question text itself.
    short_id = card["id"][:8]
    tag = f'<span style="opacity:0.5;font-size:0.8em">[{short_id}]</span> '
    if card["type"] == "basic":
        field1 = tag + card["heading"]
        field2 = f"{card['back']}<br><br>{card['source_line']}"
    else:  # cloze: field1 is the clozed text itself, field2 is "Back Extra"
        field1 = tag + card["heading"]
        field2 = card["source_line"]
    fields = [card["id"], notetype, field1, field2, card["tags"]]
    return "\t".join(f.replace("\t", " ").replace("\n", "<br>") for f in fields)


def export_deck(deck_dir):
    deck_path = deck_dir / "deck.org"
    if not deck_path.exists():
        print(f"skipping {deck_dir.name}: no deck.org", file=sys.stderr)
        return
    rows = [to_row(card) for card in parse_deck(deck_path)]
    rows = [r for r in rows if r]
    out_path = deck_dir / "anki-export.txt"
    out_path.write_text("\n".join(HEADER + rows) + "\n")
    print(f"wrote {len(rows)} card(s) to {out_path}")


def main():
    if not FC_DIR.exists():
        print(f"{FC_DIR} does not exist yet — nothing to export", file=sys.stderr)
        sys.exit(1)

    wanted = set(sys.argv[1:])
    deck_dirs = sorted(
        d for d in FC_DIR.iterdir() if d.is_dir() and d.name not in SKIP_DIRS
    )
    if wanted:
        deck_dirs = [d for d in deck_dirs if d.name in wanted]

    for deck_dir in deck_dirs:
        export_deck(deck_dir)


if __name__ == "__main__":
    main()
