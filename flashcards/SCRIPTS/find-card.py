#!/usr/bin/env python3
"""Look up one flashcard by its UUID (full, or the 8-char prefix printed on
the card's own front in Anki) across every .agents/flashcards/<uuid>/deck.org.

For use in a live Study Session (see
.agents/walkthroughs/INSTRUCTIONS/06-flashcards-guide.org): an AI study
partner runs this to pull up a card's full content — front, type, back/cloze
answer, source, tags — from just the short ID the human reads off the card
in Anki, without grepping decks by hand.

Usage: .agents/flashcards/SCRIPTS/find-card.py <card-id-or-8-char-prefix>
"""

import re
import sys
from pathlib import Path

FC_DIR = Path(__file__).resolve().parent.parent

CARD_HEADING_RE = re.compile(r"^\* Card: (.*)$")
DRAWER_ID_RE = re.compile(r"^:ID:\s*(\S+)", re.I)


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
        yield {
            "id": card_id,
            "type": card_type,
            "heading": heading,
            "back": back,
            "source_line": source_line,
            "tags": tags_line,
            "deck": path,
        }


def deck_title(deck_path):
    m = re.search(r"^#\+TITLE:\s*Flashcards\s*—\s*(.+)$", deck_path.read_text(), re.M)
    return m.group(1).strip() if m else deck_path.parent.name


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    query = sys.argv[1].strip().lower()

    matches = []
    for deck_path in sorted(FC_DIR.glob("*/deck.org")):
        for card in parse_deck(deck_path):
            if card["id"] and card["id"].lower().startswith(query):
                matches.append(card)

    if not matches:
        print(f"no card found matching '{sys.argv[1]}'", file=sys.stderr)
        sys.exit(1)
    if len(matches) > 1:
        print(f"ambiguous prefix '{sys.argv[1]}' — {len(matches)} cards match:",
              file=sys.stderr)
        for c in matches:
            print(f"  {c['id']}  {c['heading'][:70]}", file=sys.stderr)
        print("give more characters to disambiguate", file=sys.stderr)
        sys.exit(1)

    card = matches[0]
    print(f"Deck:   {deck_title(card['deck'])}  ({card['deck'].parent.name})")
    print(f"ID:     {card['id']}")
    print(f"Type:   {card['type']}")
    print(f"Front:  {card['heading']}")
    if card["type"] == "basic":
        print(f"Back:   {card['back']}")
    print(f"Source: {card['source_line']}")
    print(f"Tags:   {card['tags']}")


if __name__ == "__main__":
    main()
