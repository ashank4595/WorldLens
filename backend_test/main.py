"""
main.py  (backend_test version)

Cross-lingual search test harness — TRANSLATION-ONLY countries (il/eg/tr).

Flow per request:
  1. build entity-AND query from headline + body (query_builder.py)
  2. for each country: translate the ENTITIES into that country's language and
     assemble a valid AND-query (operators stay literal), call GNews with
     lang+country, then translate returned headlines back to English
  3. dedup + return

Two code systems, kept separate on purpose:
  - TRANSLATOR_LANG: code deep-translator wants (Hebrew = 'iw')
  - GNEWS_LANG:      code GNews wants           (Hebrew = 'he')

Run:  uvicorn main:app --reload --port 8001
"""

# ── CROSS-LINGUAL FLOW (this file orchestrates) ──────────────────────
#   headline+body → query_builder: English entities
#                 → translator:    entities → country language
#                 → GNews (lang+country) → foreign headlines
#                 → translator:    headlines → English → dedup → return

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import asyncio
import httpx

from query_builder import build_query
from translator import build_translated_query, translate_to_english

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Translation-only countries (non-English). Each maps to TWO language codes
# because deep-translator and GNews disagree on some (Hebrew especially).
#   TRANSLATOR_LANG -> passed to deep-translator
#   GNEWS_LANG      -> passed to GNews `lang` param
# Any country missing from a map falls back to "en" (no crash); add an entry
# to both maps when you want real translation for that country.
TRANSLATOR_LANG = {
    "kp": "ko", "kr": "ko", "us": "en", "jp": "ja", "cn": "zh-CN",
    "ru": "ru", "au": "en", "gb": "en", "fr": "fr", "de": "de",
}
GNEWS_LANG = {
    "kp": "ko", "kr": "ko", "us": "en", "jp": "ja", "cn": "zh",
    "ru": "ru", "au": "en", "gb": "en", "fr": "fr", "de": "de",
}

COUNTRIES = ["kp", "kr", "us", "jp", "cn", "ru", "au", "gb", "fr", "de"]

REQUEST_DELAY_SECONDS = 1.1


@app.post("/api/search")
async def search(request: dict):
    print("\n" + "=" * 60)
    print("[FLOW] 1. request received. keys =", list(request.keys()))

    search_query = request.get("searchQuery", "")
    body_text = request.get("pageTextPreview", "")

    print(f"[FLOW] 2. headline = {search_query!r}")
    print(f"[FLOW]    body chars = {len(body_text)}")

    # We use the ENTITIES (not the pre-joined query) so we can translate each
    # entity and rebuild the AND-query per language.
    english_query, entities = build_query(search_query, body_text)
    print(f"[FLOW] 3. entities = {entities}")
    print(f"[FLOW]    english query = {english_query!r}")

    api_key = os.getenv("GNEWS_API_KEY")
    print(f"[FLOW] 4. api key present = {bool(api_key)}")

    data = {}
    for i, country in enumerate(COUNTRIES):
        tlang = TRANSLATOR_LANG.get(country, "en")   # for deep-translator
        glang = GNEWS_LANG.get(country, "en")        # for GNews

        # translate ENTITIES only; operators/quotes stay literal
        country_query = build_translated_query(entities, tlang)
        print(f"[FLOW] 5.[{country}] translator_lang={tlang} gnews_lang={glang}")
        print(f"[FLOW]    query sent = {country_query!r}")

        params = {
            "q": country_query,
            "max": 10,
            "in": "title,description",
            "sortby": "relevance",   # OR publishedAt
            "country": country,
            "lang": glang,
            "apikey": api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    "https://gnews.io/api/v4/search", params=params
                )
                response.raise_for_status()
                curr = response.json()
                data[country] = curr
                print(f"[FLOW] 6.[{country}] GNews pulled "
                      f"{len(curr.get('articles', []))} "
                      f"(totalArticles={curr.get('totalArticles')})")
        except Exception as error:
            print(f"[FLOW] 6.[{country}] GNews ERROR = {error}")
            data[country] = {"articles": []}

        if i < len(COUNTRIES) - 1:
            await asyncio.sleep(REQUEST_DELAY_SECONDS)

    # ---- build response: dedup + translate headlines back to English ----
    print("[FLOW] 7. translating headlines back to English + deduping")
    articles = []
    seen = set()

    for country in COUNTRIES:
        slang = TRANSLATOR_LANG.get(country, "en")   # source lang for back-translation
        raw = data.get(country, {}).get("articles", [])
        kept = 0
        for article in raw:
            title = article.get("title", "")
            norm = "".join(c for c in title.lower() if c.isalnum() or c == " ").strip()
            if norm in seen:
                continue
            seen.add(norm)

            title_en = translate_to_english(title, slang)

            source = article.get("source", {})
            articles.append({
                "title": title,          # original-language headline
                "title_en": title_en,    # English rendering
                "source": source.get("name", "Unknown"),
                "url": article.get("url", ""),
                "country": source.get("country", country),
                "lang": GNEWS_LANG.get(country, "en"),
            })
            kept += 1
        print(f"[FLOW]    [{country}] kept {kept} after dedup")

    print(f"[FLOW] 8. done. total articles = {len(articles)}")
    print("=" * 60)

    return {
        "searchQueryReceived": search_query,
        "finalQuery": english_query,
        "entities": entities,
        "articles": articles,
    }
