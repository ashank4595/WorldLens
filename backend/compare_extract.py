# compare_extract.py — standalone probe: compare entity-selection methods.
# Tests METHOD 1 (two proper nouns) vs METHOD 2 (two rarest / wordfreq).
# Does NOT touch main.py or query_builder.py — it only imports (reads) from them.
#
# Setup (once):  pip install wordfreq --break-system-packages
# Run:           python compare_extract.py

from query_builder import tokenize, STOP_WORDS, COMMON_NEWS_WORDS

try:
    from wordfreq import zipf_frequency
    HAVE_WORDFREQ = True
except ImportError:
    HAVE_WORDFREQ = False


# ----------------------------------------------------------------------
# Shared: turn text into candidate tokens (reusing your real tokenizer).
# Drops stop words. Keeps original casing so METHOD 1 can see capitals.
# ----------------------------------------------------------------------
def candidates(text):
    return [w for w in tokenize(text) if w.lower() not in STOP_WORDS]


# ----------------------------------------------------------------------
# METHOD 1 — two proper nouns.
# Pick the first two Capitalized, non-common tokens (a simple version of
# what extract_keywords already does). Acronyms (US, AI, NATO) count.
# ----------------------------------------------------------------------
def method_proper_nouns(text):
    picks = []
    for w in candidates(text):
        is_acronym = w.isupper() and any(c.isalpha() for c in w) and 2 <= len(w) <= 8
        is_capitalized = w[0].isupper()
        if (is_acronym or is_capitalized) and w.lower() not in COMMON_NEWS_WORDS:
            if w not in picks:
                picks.append(w)
        if len(picks) == 2:
            break
    return picks


# ----------------------------------------------------------------------
# METHOD 2 — two rarest (wordfreq zipf).
# Lower zipf = rarer in English = more likely a specific entity.
# Score every candidate, drop common-news words, take the two rarest.
# ----------------------------------------------------------------------
def method_rarest(text):
    if not HAVE_WORDFREQ:
        return ["<install wordfreq>"]
    scored = []
    seen = set()
    for w in candidates(text):
        if w.lower() in COMMON_NEWS_WORDS or w.lower() in seen:
            continue
        seen.add(w.lower())
        # zipf_frequency: higher = more common, ~0 = not in list (unknown word).
        # Unknown words are usually proper nouns (Nvidia, Uzmetkombinat) -> we
        # want those treated as RAREST, so give them the smallest sort key.
        z = zipf_frequency(w.lower(), "en")
        sort_key = -1.0 if z == 0 else z   # rarer -> smaller -> sorted first
        scored.append((sort_key, w))
    scored.sort(key=lambda t: t[0])        # rarest first
    return [w for _, w in scored[:2]]


# ----------------------------------------------------------------------
# Test fixtures: (headline, first_paragraph). The pact one is the hard case
# because the headline names NO actors — only the body does.
# ----------------------------------------------------------------------
CASES = [
    (
        "LG, Nvidia to jointly develop humanoid robot for 2027 unveiling",
        "LG will unveil Nvidia-powered bipedal humanoids by the first quarter "
        "of 2027 as part of a larger deal to collaborate across AI factories "
        "and autonomous driving technologies.",
    ),
    (
        "Which country is the new Mecca defense pact targeting?",
        "The mutual defence agreement signed in Mecca between Saudi Arabia, "
        "Pakistan and Turkey brings together three of the most powerful states "
        "of the Sunni Muslim world, in what some call an emerging Islamic NATO.",
    ),
    (
        "Air India flight investigated after sudden altitude loss",
        "Authorities are investigating an Air India flight from Phuket after "
        "the aircraft experienced a sudden loss of altitude over the Bay of Bengal.",
    ),
]


def show(label, text):
    print(f"  {label}")
    print(f"    METHOD 1 (proper nouns): {method_proper_nouns(text)}")
    print(f"    METHOD 2 (two rarest)  : {method_rarest(text)}")


print("wordfreq available:", HAVE_WORDFREQ)
print("=" * 70)
for headline, para in CASES:
    print(f"\nHEADLINE: {headline}")
    show("[headline only]", headline)
    show("[headline + first paragraph]", headline + " " + para)
    print("-" * 70)
