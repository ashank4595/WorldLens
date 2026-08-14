# diagnose.py — standalone diagnostic for "why so few articles?"
# Run from the backend folder:  python diagnose.py
# This does NOT touch main.py. It reuses build_query so it tests the real pipeline.

import os
import httpx
from query_builder import build_query, COMMON_NEWS_WORDS

# Swap this for the headline of the article you actually tested the extension on.
HEADLINE = "Which country is the new Mecca defense pact targeting?"

COUNTRIES = ["tr", "pk", "us", "il", "eg", "in", "gb"]
API_KEY = os.getenv("GNEWS_API_KEY")


def gnews(params):
    """One GNews search call. Raises on HTTP error so we can see 403/429 clearly."""
    with httpx.Client(timeout=10.0) as client:
        r = client.get("https://gnews.io/api/v4/search", params=params)
        r.raise_for_status()
        return r.json()


# ----------------------------------------------------------------------
# STAGE 0: is the QUERY itself junk?  (suspect A)
# ----------------------------------------------------------------------
final_query, keywords = build_query(HEADLINE)
strong = [k for k in keywords if k.lower() not in COMMON_NEWS_WORDS]

print("HEADLINE :", HEADLINE)
print("keywords :", keywords)
print("strong   :", strong, "  <- entity words that SHOULD drive relevance")
print("query    :", final_query)
print("api key  :", bool(API_KEY))
print("=" * 70)


# ----------------------------------------------------------------------
# STAGE 1 + 2: retrieval vs filter, per country  (suspects B vs C)
# ----------------------------------------------------------------------
for country in COUNTRIES:
    params = {
        "q": final_query,
        "max": 20,
        "in": "title,description",
        "sortby": "relevance",
        "country": country,
        "apikey": API_KEY,
    }

    try:
        data = gnews(params)
    except Exception as e:
        # 403/429 here means you're rate limited (free tier ~100 requests/day).
        print(f"[{country}] REQUEST FAILED: {e}")
        continue

    raw = data.get("articles", [])
    total = data.get("totalArticles", "?")

    kept = 0
    drops = []
    for a in raw:
        text = (a.get("title", "") + " " + a.get("description", "")).lower()
        mc = sum(k.lower() in text for k in keywords)          # current filter metric
        strong_hit = any(k.lower() in text for k in strong)    # had a real entity word?
        if mc < 2:
            drops.append((mc, strong_hit, a.get("title", "")))
        else:
            kept += 1

    # THE diagnostic line: returned=0 -> retrieval/language (B);
    # returned>>kept -> filter too strict (C).
    print(f"[{country}] totalArticles={total}  returned={len(raw)}  kept={kept}")
    for mc, sh, title in drops:
        # strong=True + dropped = a genuine article you're throwing away.
        print(f"     DROP mc={mc} strong={sh} :: {title}")
    print("-" * 70)


# ----------------------------------------------------------------------
# PROBE 1: prove it's LANGUAGE, not "GNews has nothing" for Israel.
# If English il returned 0 above but this returns lots -> language wall confirmed.
# ----------------------------------------------------------------------
try:
    he = gnews({"q": "הסכם הגנה", "country": "il", "lang": "he",
                "max": 20, "apikey": API_KEY})
    print(f"[PROBE il/he] totalArticles={he.get('totalArticles')} "
          f"returned={len(he.get('articles', []))}")
except Exception as e:
    print(f"[PROBE il/he] FAILED: {e}")


# ----------------------------------------------------------------------
# PROBE 2: retrieval ceiling — how much exists before country/in restrictions?
# High here but low per-country above = your params are the bottleneck, not GNews.
# ----------------------------------------------------------------------
try:
    ceiling = gnews({"q": final_query, "max": 20, "apikey": API_KEY})
    print(f"[PROBE no-country] totalArticles={ceiling.get('totalArticles')} "
          f"returned={len(ceiling.get('articles', []))}")
except Exception as e:
    print(f"[PROBE no-country] FAILED: {e}")

# AND query, US — expect totalArticles to crash from millions to dozens, returned to be ON-topic
print(gnews({"q": 'LG AND Nvidia AND (humanoid OR robot)',
             "country": "us", "max": 10, "apikey": API_KEY}))