"""
translator.py  (backend_test)

Swappable translation layer for cross-lingual retrieval.

The rest of the pipeline calls ONLY these two functions:
    translate_query(text, target_lang)      # English -> target language
    translate_to_english(text, source_lang) # target language -> English

Everything provider-specific (Google, LibreTranslate, DeepL, ...) lives behind
the Translator interface below, so swapping engines is a one-line change here
and never touches main.py or query_builder.py.

Design:
  - No-op identity when target == "en" or translation is disabled, so English
    countries flow through the EXACT same code path (no if/else in the pipeline).
  - Deterministic -> cached invisibly by (text, source, target).
  - Feature-flagged OFF by default: ship English-only V1 now, flip on later.
"""

# ── CROSS-LINGUAL FLOW (this file = steps 2 & 4) ─────────────────
#    headline+body → English entities        (query_builder.py)
# >> → [translate entities EN→country lang]   step 2
#    → GNews (lang+country) → foreign headlines
# >> → [translate headlines back → English]  step 4

# Master switch. While False, translate_* are pure identity (English-only V1).
TRANSLATION_ENABLED = True

# Which provider to use when enabled. Swap this single name to change engines.
ACTIVE_PROVIDER = "deep_google"   # "noop" | "deep_google" | "google" | "libre"


# ---------------------------------------------------------------------------
# Provider interface
# ---------------------------------------------------------------------------
class Translator:
    """Abstract translator. A provider implements translate()."""
    def translate(self, text: str, source: str, target: str) -> str:
        raise NotImplementedError


class NoOpTranslator(Translator):
    """Returns text unchanged. Default until a real provider is wired in."""
    def translate(self, text: str, source: str, target: str) -> str:
        return text


class DeepGoogleTranslator(Translator):
    """Free translation via deep-translator's Google web endpoint.
    No API key, no cost. Requires:  pip install deep-translator
    """
    def translate(self, text: str, source: str, target: str) -> str:
        from deep_translator import GoogleTranslator as _G
        # deep-translator uses ISO codes; it accepts 'he','ar','tr','en'.
        return _G(source=source, target=target).translate(text)


class GoogleTranslator(Translator):
    """TODO: implement with the paid Google Cloud Translation client.
    Left unimplemented on purpose so no key is required for V1.
    """
    def translate(self, text: str, source: str, target: str) -> str:
        raise NotImplementedError(
            "GoogleTranslator (Cloud API) not implemented. Use 'deep_google'."
        )


class LibreTranslator(Translator):
    """TODO: implement with a (self-hosted) LibreTranslate endpoint."""
    def translate(self, text: str, source: str, target: str) -> str:
        raise NotImplementedError(
            "LibreTranslator not implemented. Set ACTIVE_PROVIDER='noop' or "
            "implement this method against your LibreTranslate instance."
        )


_PROVIDERS = {
    "noop": NoOpTranslator,
    "deep_google": DeepGoogleTranslator,
    "google": GoogleTranslator,
    "libre": LibreTranslator,
}


def _get_provider() -> Translator:
    return _PROVIDERS.get(ACTIVE_PROVIDER, NoOpTranslator)()


# ---------------------------------------------------------------------------
# Invisible cache (deterministic input -> deterministic output).
# Swap this dict for Redis later without changing the public functions.
# ---------------------------------------------------------------------------
_cache: dict[tuple[str, str, str], str] = {}


def _translate(text: str, source: str, target: str) -> str:
    if not TRANSLATION_ENABLED:
        return text
    if not text or source == target:
        return text
    key = (text, source, target)
    if key in _cache:
        print(f"[TRANSLATOR] cache hit {source}->{target}: {text[:40]!r}")
        return _cache[key]
    try:
        result = _get_provider().translate(text, source, target)
        print(f"[TRANSLATOR] {source}->{target}: {text[:40]!r} => {result[:40]!r}")
    except NotImplementedError:
        # Provider not wired yet -> fail open to identity so nothing crashes.
        result = text
    except Exception as e:
        # Network/provider error -> fail open to original text so search still runs.
        print(f"[TRANSLATOR] ERROR {source}->{target} ({e}); using original text")
        result = text
    _cache[key] = result
    return result


# ---------------------------------------------------------------------------
# Public API — the only things main.py should import.
# ---------------------------------------------------------------------------
def translate_query(text: str, target_lang: str) -> str:
    """Translate an English query into target_lang. Identity for 'en'."""
    return _translate(text, "en", target_lang)


def build_translated_query(entities, target_lang: str) -> str:
    """Build a GNews AND-query in target_lang from English entities.

    IMPORTANT: only the ENTITIES are translated; the AND operator and quotes
    are literal so GNews still parses the boolean query. (Translating the whole
    '"X" AND "Y"' string turns AND into e.g. Arabic 'و' / Turkish 'VE', which
    GNews rejects with a 400.)
    """
    if not entities:
        return ""
    if target_lang == "en":
        parts = list(entities)
    else:
        parts = [_translate(e, "en", target_lang) for e in entities]
    quoted = [f'"{p}"' for p in parts]
    return " AND ".join(quoted)


def translate_to_english(text: str, source_lang: str) -> str:
    """Translate a foreign headline back into English. Identity for 'en'."""
    return _translate(text, source_lang, "en")
