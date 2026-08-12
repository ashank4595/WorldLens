# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Run search() when someone sends POST request to /api/search
# @app.post("/api/search")
# async def search(request: dict):
# #     const requestBody = {                 
# #       pageUrl: "https://example.com/article",
# #       pageTitle: "Some browser title",...
# #     }; Converted to python dict, request
#     print("[BACKEND] request body =", request)

#     search_query = request.get("searchQuery", "")

#     return {
#         "searchQueryReceived": search_query,
#         "articles": [
#             {
#                 "title": "Fake backend article from India",
#                 "source": "HT",
#                 "url": "https://example.com/india",
#                 "country": "India",
#             },
#             {
#                 "title": "Fake backend article from Japan",
#                 "source": "Nikkei",
#                 "url": "https://example.com/japan",
#                 "country": "Japan",
#             },
#         ],
#     }

from fastapi import FastAPI

# CORS allows the extension to make requests to the backend which has different origin
from fastapi.middleware.cors import CORSMiddleware 
import os
import re
import httpx # Library to send http requests from Fast API to GNEWS


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Hashset with words not useful for requests
STOP_WORDS = {
    "the", "a", "an", "and", "or", "but",
    "of", "to", "in", "on", "for", "at",
    "with", "from", "by", "as", "is", "are",
    "was", "were", "this", "that"
}


def shorten_query(text): # text = full headline
    # Puts words of the headline in a list, removing punctuation
    words = re.findall(r"[A-Za-z0-9]+", text)

    important_words = []

    for word in words:
        if word.lower() not in STOP_WORDS:
            important_words.append(word.lower())

    important_words = [
        word for word in words
        if word.lower() not in STOP_WORDS
    ]

    return " ".join(important_words[:5]) # String of first 5 words

# Endpoint called by sidepanel.js, request is dict with pageUrl, searchQuery etc.
@app.post("/api/search") 
async def search(request: dict): 

    print("[BACKEND] request body =", request) 

    # STEP 1: Get headline from frontend
    search_query = request.get("searchQuery", "")

    # STEP 2: Shorten headline
    short_query = "Air India Phuket" #shorten_query(search_query)

    print("[BACKEND] original query =", search_query)
    print("[BACKEND] short query =", short_query)

    # STEP 3: Call GNews
    api_key = os.getenv("GNEWS_API_KEY") # Read API key from terminal
    print("[BACKEND] api key exists =", bool(api_key))

    # settings sent to GNews
    params = {
        "q": short_query,
        "max": 10,
        "in": "title,description",
        "sortby": "relevance",
        "apikey": api_key,
    }

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://gnews.io/api/v4/search",
                params=params
            )
            
            # GNews response contains totalArticles and articles[] which in turn contains
            # sources containing country
            response.raise_for_status() # Checks for HTTP errors
            data = response.json() # Converts GNews JSON into a Python dictionary

    except Exception as error:
        print("[BACKEND] GNews error =", error)

        return {
            "searchQueryReceived": search_query,
            "articles": []
        }

    # STEP 4: Convert GNews format into our frontend format
    articles = []

    for article in data.get("articles", []):

        source = article.get("source", {})

        articles.append({
            "title": article.get("title", ""),
            "source": source.get("name", "Unknown"),
            "url": article.get("url", ""),
            "country": source.get("country", "Unknown"),
        })

    print("[BACKEND] articles =", articles)

    # Returns results to sidepanel.js
    return {
        "searchQueryReceived": search_query,
        "articles": articles
    }