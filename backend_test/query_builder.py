"""
query_builder.py  (backend_test version)

Entity-first query builder for World Lens.

Design (all conclusions proven during debugging):
  - AND the top ~2 ENTITIES, never OR all keywords, and never AND topic words
    (topic words like "defense"/"pact" live in the body, not title/description,
    so ANDing them over-filters to zero).
  - Merge adjacent Capitalized tokens into ONE entity so "Air India" and
    "Saudi Arabia" aren't split into weak single-token picks.
  - Extract over headline + body, because rhetorical headlines (e.g.
    "Which country is the new Mecca defense pact targeting?") name no actors;
    the entities only appear in the body.

build_query(headline, body="") -> (query_string, entities_list)
"""

import re

# Minimal stop/common lists. Kept local to backend_test so this file is
# self-contained and does not import the production query_builder.
STOP_WORDS = {
    "a", "an", "the", "this", "that", "these", "those", "and", "or", "but",
    "as", "at", "by", "for", "from", "in", "into", "of", "off", "on", "onto",
    "to", "with", "is", "are", "was", "were", "be", "been", "being", "will",
    "which", "what", "who", "whom", "whose", "how", "when", "where", "why",
    "its", "it", "they", "them", "their", "he", "she", "his", "her",
}

# Generic words that are Capitalized only because they start a sentence/headline,
# so they must NOT be treated as entities.
COMMON_TITLE_WORDS = {
    "the", "a", "an", "new", "which", "what", "who", "how", "why", "when",
    "where", "says", "say", "said", "report", "reports", "amid", "after",
    "before", "over", "into", "plans", "plan", "us",  # keep US? handled below
}


def _tokens_with_positions(text):
    """Return list of (token, is_capitalized, is_acronym, is_break) in order.

    A 'break' token is punctuation (comma, semicolon, etc.) or a connector word
    ('and'/'&') that must SEPARATE two entities, e.g. "Saudi Arabia, Pakistan"
    -> two entities, not one fused "Saudi Arabia Pakistan".
    """
    # Capture words OR single break characters, in order.
    raw = re.findall(r"[A-Za-z][A-Za-z.'’\-]*|[,;:&/()]", text)
    out = []
    for w in raw:
        if w in ",;:&/()":
            out.append((w, False, False, True))
            continue
        is_acronym = w.isupper() and 2 <= len(w) <= 8
        is_cap = w[0].isupper()
        # 'and'/'or' between capitals also break an entity run.
        is_break = w.lower() in {"and", "or"}
        out.append((w, is_cap, is_acronym, is_break))
    return out


def extract_entities(text):
    """
    Find candidate entities by merging runs of adjacent Capitalized tokens.
    "Saudi Arabia" -> one entity; "Air India" -> one entity; "US"/"AI" -> kept.
    Sentence-initial generic words (New, Which, The...) are dropped so they
    don't anchor a bogus entity.
    Returns entities in order of appearance, de-duplicated.
    """
    tokens = _tokens_with_positions(text)

    entities = []
    current = []

    def flush():
        if current:
            phrase = " ".join(current)
            entities.append(phrase)
            current.clear()

    for w, is_cap, is_acronym, is_break in tokens:
        # Hard separator: comma / "and" / "&" etc. ends the current entity run
        # so adjacent entities across punctuation don't fuse.
        if is_break:
            flush()
            continue

        low = w.lower().rstrip(".")
        looks_entity = (is_cap or is_acronym)

        # Drop a Capitalized token that is really just a generic word
        # (usually sentence-initial): "New", "Which", "The", "Says"...
        if looks_entity and low in COMMON_TITLE_WORDS and not is_acronym:
            flush()
            continue

        if looks_entity and low not in STOP_WORDS:
            current.append(w.rstrip(".'’"))
        else:
            flush()

    flush()

    # De-dupe, preserve order.
    seen = set()
    unique = []
    for e in entities:
        key = e.lower()
        if key not in seen and len(e) > 1:
            seen.add(key)
            unique.append(e)
    return unique


def _is_title_case(headline):
    """True if the headline is mostly Capitalized (Title Case / Headline Case),
    which makes capitalization useless as an entity signal.

    e.g. "Saudi Arabia Sign Defense Pact In Mecca" -> every word capitalized,
    so "Sign"/"Defense"/"Pact" would look like entities. When this is true we
    must NOT trust the headline's casing and should extract from the body
    (which is sentence-case, so caps are reliable) instead.
    """
    words = re.findall(r"[A-Za-z][A-Za-z.'’\-]*", headline)
    if len(words) < 4:
        return False
    capped = sum(1 for w in words if w[0].isupper() and not w.isupper())
    return capped / len(words) >= 0.65


def build_query(headline, body="", max_entities=2):
    """
    Build an entity-AND query from headline (+ optional body text).

    Returns (query_string, entities) where:
      - entities is the list of chosen entities (up to max_entities)
      - query_string ANDs them, each quoted:  "Saudi Arabia" AND "Pakistan"

    Title-case guard: if the headline is mostly capitalized, its casing is
    meaningless for entity detection, so we extract from the BODY only (which
    is sentence-case and therefore reliable). If there's no body, we fall back
    to using the headline anyway.

    Fallbacks:
      - 1 entity  -> just that entity (quoted), no AND
      - 0 entities -> OR of the non-stopword headline tokens (last resort;
                      mirrors the old loose behaviour so we never send empty q)
    """
    if _is_title_case(headline) and body.strip():
        # Headline casing is unreliable -> extract from body only.
        source_text = body.strip()
    else:
        source_text = f"{headline} {body}".strip()

    entities = extract_entities(source_text)

    chosen = entities[:max_entities]

    if len(chosen) >= 2:
        query = " AND ".join(f'"{e}"' for e in chosen)
    elif len(chosen) == 1:
        query = f'"{chosen[0]}"'
    else:
        # No entities found anywhere: fall back to a loose OR of headline words.
        fallback = [w for w in re.findall(r"[A-Za-z]+", headline)
                    if w.lower() not in STOP_WORDS][:6]
        query = " OR ".join(fallback)

    return query, chosen
