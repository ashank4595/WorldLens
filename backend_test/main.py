"""
main.py  (backend_test version)

Test harness for the entity-AND query builder. Mirrors the production
/api/search endpoint but:
  - uses backend_test/query_builder.py (entity-AND + merge + body text)
  - reads pageTextPreview from the request and feeds it into build_query
  - DROPS the old match_count<2 filter (proven not to be the bottleneck and
    it fights the tighter AND query)
  - sorts by publishedAt and prints per-country returned counts

Run:  uvicorn main:app --reload --port 8001
      (port 8001 so it can run alongside the real backend on 8000)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx

from query_builder import build_query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# English-publishing countries only for now (il/eg/tr need translated queries;
# that's a separate change, deliberately not done here).
COUNTRIES = ["us", "gb", "in", "pk", "il", "hk", "au"]


@app.post("/api/search")
async def search(request: dict):
    print("\n[TEST BACKEND] request keys =", list(request.keys()))

    search_query = request.get("searchQuery", "")
    body_text = request.get("pageTextPreview", "")   # frontend already sends this

    final_query, entities = build_query(search_query, body_text)

    print("[TEST BACKEND] headline =", search_query)
    print("[TEST BACKEND] body chars =", len(body_text))
    print("[TEST BACKEND] entities =", entities)
    print("[TEST BACKEND] final query =", final_query)

    api_key = os.getenv("GNEWS_API_KEY")
    print("[TEST BACKEND] api key exists =", bool(api_key))

    data = {}
    for country in COUNTRIES:
        params = {
            "q": final_query,
            "max": 10,                       # free tier serves up to 10
            "in": "title,description",
            "sortby": "publishedAt",         # recent first; better for in-window stories
            "country": country,
            "apikey": api_key,
        }
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://gnews.io/api/v4/search", params=params
                )
                response.raise_for_status()
                data[country] = response.json()
        except Exception as error:
            print(f"[TEST BACKEND] GNews error [{country}] =", error)
            data[country] = {"articles": []}
            continue

    # No keyword post-filter: the entity-AND query does the relevance work.
    # We still dedup syndicated wire copy by normalized title.
    articles = []
    seen = set()

    for country in COUNTRIES:
        raw = data.get(country, {}).get("articles", [])
        kept = 0
        for article in raw:
            title = article.get("title", "")
            norm = "".join(ch for ch in title.lower() if ch.isalnum() or ch == " ").strip()
            if norm in seen:
                continue
            seen.add(norm)

            source = article.get("source", {})
            articles.append({
                "title": title,
                "source": source.get("name", "Unknown"),
                "url": article.get("url", ""),
                "country": source.get("country", country),
            })
            kept += 1
        print(f"[TEST BACKEND] {country}: returned {len(raw)}, kept {kept}")

    print(f"[TEST BACKEND] total articles = {len(articles)}")

    return {
        "searchQueryReceived": search_query,
        "finalQuery": final_query,
        "entities": entities,
        "articles": articles,
    }
