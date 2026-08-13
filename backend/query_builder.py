import re

# Hashset with words not useful for requests
STOP_WORDS = {
    # Articles / determiners
    "a", "an", "the", "this", "that", "these", "those",

    # Conjunctions
    "and", "or", "but", "nor", "so", "yet",

    # Prepositions / structural words
    "about", "above", "across", "after", "against", "ahead", "along",
    "amid", "amidst", "among", "around", "as", "at", "before", "behind",
    "below", "beneath", "beside", "between", "beyond", "by", "despite",
    "during", "except", "for", "from", "in", "inside", "into", "near",
    "of", "off", "on", "onto", "outside", "over", "past", "per", "since",
    "through", "throughout", "to", "toward", "towards", "under",
    "underneath", "until", "up", "upon", "via", "with", "within",

    # Question words
    "how", "what", "when", "where", "which", "who", "whom", "whose",
    "why", "whether",

    # Pronouns
    # NOTE: do NOT add "us" because we want to preserve US = United States
    "i", "me", "my", "mine", "myself",
    "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself",
    "she", "her", "hers", "herself",
    "it", "its", "itself",
    "we", "our", "ours", "ourselves",
    "they", "them", "their", "theirs", "themselves",

    # Auxiliary / modal verbs
    "am", "are", "be", "been", "being", "can", "cannot", "could",
    "did", "do", "does", "doing", "had", "has", "have", "having",
    "is", "might", "must", "shall", "should", "was", "were", "will",
    "would",

    # Quantifiers / generic structure
    "all", "any", "both", "each", "either", "enough", "every", "few",
    "many", "more", "most", "much", "neither", "no", "none", "not",
    "other", "others", "several", "some", "such", "than", "then",
    "there", "too", "very",

    # Misc filler
    "again", "already", "also", "away", "else", "ever", "here", "just",
    "never", "now", "perhaps", "rather", "still",

    # Contractions
    "aren't", "can't", "couldn't", "didn't", "doesn't", "don't",
    "hadn't", "hasn't", "haven't", "isn't", "mustn't", "shouldn't",
    "wasn't", "weren't", "won't", "wouldn't",
    "he's", "she's", "it's", "they're", "we're", "you're",
    "i'm", "i've", "we've", "they've", "you've",
}


COMMON_NEWS_WORDS = {
    # Attribution / reporting
    "say", "says", "said",
    "report", "reports", "reported", "reporting", "reportedly",
    "source", "sources",
    "official", "officials",
    "spokesman", "spokeswoman", "spokesperson",
    "statement", "according", "reuters",

    # Announcing / intentions
    "announce", "announces", "announced", "announcement",
    "plan", "plans", "planned", "planning",
    "expect", "expects", "expected", "expecting",
    "seek", "seeks", "seeking", "sought",
    "aim", "aims", "aimed",
    "target", "targets", "targeting",
    "want", "wants", "wanted",
    "hope", "hopes",
    "urge", "urges", "urged",
    "call", "calls", "called",
    "ask", "asks", "asked", "asking",

    # Reporting / opinion verbs
    "claim", "claims", "claimed",
    "reveal", "reveals", "revealed",
    "confirm", "confirms", "confirmed",
    "deny", "denies", "denied",
    "tell", "tells", "told",
    "suggest", "suggests", "suggested",
    "indicate", "indicates", "indicated",

    # Generic action verbs
    "move", "moves", "moved", "moving",
    "take", "takes", "taken", "taking",
    "make", "makes", "made", "making",
    "get", "gets", "got", "getting",
    "give", "gives", "gave", "given",
    "keep", "keeps", "kept", "keeping",
    "set", "sets", "setting",
    "show", "shows", "showed", "shown", "showing",
    "see", "sees", "seen", "seeing",
    "find", "finds", "found", "finding",
    "look", "looks", "looking",
    "turn", "turns", "turned",
    "come", "comes", "came", "coming",
    "go", "goes", "went", "going",
    "help", "helps", "helped",

    # Common headline movement words
    "rise", "rises", "rose", "rising",
    "fall", "falls", "fell", "falling",
    "raise", "raises", "raised", "raising",
    "drop", "drops", "dropped", "dropping",
    "jump", "jumps", "jumped",
    "gain", "gains", "gained",
    "boost", "boosts", "boosted",
    "edge", "edges", "edged",
    "soar", "soars", "soared",

    # Generic timing / descriptions
    "new", "latest", "first", "second", "third", "next", "last", "former",
    "early", "late", "current", "recent", "longtime",
    "annual", "quarterly",
    "global", "major", "strong", "weak",
    "higher", "lower", "big",
    "likely", "unlikely", "possible", "possibly",
    "potential", "potentially", "allegedly", "successfully",

    # Generic people / organizations
    "people", "person",
    "group", "groups",
    "leader", "leaders",
    "chief",
    "member", "members",
    "team",
    "company", "firm", "firms",
    "government", "administration", "authorities",

    # Research boilerplate
    "study", "studies",
    "survey", "surveys",
    "poll", "polls",
    "researcher", "researchers",
    "scientist", "scientists",
    "expert", "experts",
    "analyst", "analysts",

    # Business boilerplate
    "market", "markets",
    "sector", "industry",
    "profit", "profits",
    "revenue", "revenues",
    "earnings", "sales",
    "forecast", "forecasts", "forecasting",
    "outlook",
    "estimate", "estimates",
    "demand",
    "share", "shares",
    "stock", "stocks",
    "investor", "investors",
    "price", "prices",
    "trading",
    "quarter", "quarters",

    # Generic time / quantity
    "day", "days",
    "week", "weeks",
    "month", "months",
    "year", "years",
    "million", "millions",
    "billion", "billions",

    # Generic headline framing
    "face", "faces", "faced", "facing",
    "back", "backs", "backed", "backing",
    "support", "supports", "supported", "supporting",
    "reject", "rejects", "rejected",
    "warn", "warns", "warned",
    "push", "pushes", "pushed",
    "lead", "leads", "leading",
    "leave", "leaves", "left",
    "return", "returns", "returned",
    "open", "opens", "opened",
    "close", "closes", "closed",
    "start", "starts", "started",
    "end", "ends", "ended",
    "prepare", "prepares", "prepared",
    "ready",
    "loom", "looms", "looming",
    "focus", "focused", "focusing",
    "worth",

    # Common sports framing
    "win", "wins", "won", "winning",
    "lose", "loses", "lost",
    "beat", "beats", "beaten",
    "debut", "debuted",
    "final", "season", "title",
    "coach", "player", "players",
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
    keywords = extract_keywords(headline)

    return " OR ".join(extract_keywords(headline)), keywords