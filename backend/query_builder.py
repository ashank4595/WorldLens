import re

# Hashset with words not useful for requests
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "for",
    "at", "with", "from", "by", "as", "is", "are", "was", "were", "this",
    "that", "it", "its", "be", "been", "being", "after", "before", "over",
    "under", "into", "out", "up", "down", "than", "then", "amid", "while"
}

COMMON_NEWS_WORDS = {
    "says", "said", "say", "new", "report", "reports", "official", "officials",
    "people", "year", "years", "first", "latest", "plan", "plans", "could",
    "would", "will", "may", "might", "world", "country", "city", "state",
    "man", "woman", "group", "team", "announces", "calls", "claims", "reveals",
    "support", "requested", "items", "potential", "gets", "got", "make", "makes",
    "made", "high", "higher", "low", "lower", "big", "major", "top", "near",
    "strong", "weak", "rise", "rises", "falls", "fall", "ahead", "back",
    "returns", "return", "opens", "close", "closes", "press", "set", "sets"
}


def tokenize(headline):
    words = re.findall(
        r"[^\W_]+(?:[.'’\-][^\W_]+)*|\d+(?:\.\d+)?",
        headline,
        flags=re.UNICODE
    )

    return [
        re.sub(r"[’']s$", "", word, flags=re.IGNORECASE)
        for word in words
    ]


def extract_keywords(headline, max_keywords=6):
    words = [
        word for word in tokenize(headline)
        if word.lower() not in STOP_WORDS
    ]

    if not words:
        return []

    # If most words are capitalized, capitalization is probably just Title Case.
    capitalized_count = sum(
        word[0].isupper() and not word.isupper()
        for word in words
    )

    title_case = (
        len(words) >= 4
        and capitalized_count / len(words) >= 0.65
    )

    proper_indexes = set()

    # Acronyms such as US, AI, NATO, FIFA
    for i, word in enumerate(words):
        if (
            word.isupper()
            and any(char.isalpha() for char in word)
            and 2 <= len(word) <= 8
        ):
            proper_indexes.add(i)

    if not title_case:
        # Capitalized words inside the headline
        for i, word in enumerate(words[1:], start=1):
            if (
                word[0].isupper()
                and word.lower() not in COMMON_NEWS_WORDS
            ):
                proper_indexes.add(i)

        # Catch beginning entities such as "Air India"
        if (
            len(words) >= 2
            and words[0][0].isupper()
            and words[1][0].isupper()
            and (
                words[0].lower() not in COMMON_NEWS_WORDS
                or words[1].lower() not in COMMON_NEWS_WORDS
            )
        ):
            proper_indexes.update({0, 1})

    chosen_indexes = []

    # Priority 1: proper nouns
    # Priority 2: story-specific words
    # Priority 3: earliest remaining words
    priority_groups = [
        sorted(proper_indexes),
        [
            i for i, word in enumerate(words)
            if word.lower() not in COMMON_NEWS_WORDS
        ],
        range(len(words))
    ]

    for group in priority_groups:
        for i in group:
            if i not in chosen_indexes:
                chosen_indexes.append(i)

            if len(chosen_indexes) == max_keywords:
                return [words[i] for i in chosen_indexes]

    return [words[i] for i in chosen_indexes]


def build_query(headline):
    return " OR ".join(extract_keywords(headline))