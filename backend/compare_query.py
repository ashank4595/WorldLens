import os, httpx
from datetime import datetime, timedelta, timezone

API_KEY = os.getenv("GNEWS_API_KEY")
now = datetime.now(timezone.utc)
iso = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def g(label, q, country="us", **extra):
    params = {"q": q, "country": country, "max": 10,
              "in": "title,description", "apikey": API_KEY}
    params.update(extra)
    r = httpx.get("https://gnews.io/api/v4/search", params=params, timeout=10)
    d = r.json()
    print(f"\n{label}  [country={country}]")
    print("  query   :", q)
    print("  total   :", d.get("totalArticles"), "| returned:", len(d.get("articles", [])))
    for a in d.get("articles", [])[:6]:
        print("   -", a.get("publishedAt", "")[:10], a.get("title", ""))


print("api key:", bool(API_KEY))

# ---- The story's actual entities are Saudi Arabia / Pakistan / Turkey ----
# (Note: none of these are in the DW headline — we're feeding them manually
#  to test the RETRIEVAL ceiling, separate from headline extraction.)

# Loose OR (what build_query would produce from the headline) — for contrast
g("OR (headline-style):", "Mecca OR country OR defense OR pact OR new OR targeting")

# Two-entity AND — the shape we think build_query SHOULD produce
g("two-entity AND:", '"Saudi Arabia" AND Pakistan')

# Entity + topic
g("entities + topic:", '(Saudi OR Mecca) AND Pakistan AND (defense OR pact)')

# Same two-entity AND, but explicitly inside the servable window
g("two-entity AND, servable window:", '"Saudi Arabia" AND Pakistan',
  **{"from": iso(now - timedelta(days=30)), "to": iso(now - timedelta(hours=12))})

# ---- And check the countries that were dark before ----
g("two-entity AND @ Pakistan:", '"Saudi Arabia" AND Pakistan', country="pk")
g("two-entity AND @ India:", '"Saudi Arabia" AND Pakistan', country="in")
