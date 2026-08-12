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

COUNTRIES = ["us", "in", "hk", "au"]  

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

    data = {}
    for country in COUNTRIES:
        # Query Parameters
        params = {
            "q": short_query,
            "max": 3,
            "in": "title,description", # to choose in which attributes keywords are searched
            "sortby": "relevance",
            "country": country,
            "apikey": api_key,
        }

        try:
            # httpx creates a request
            # Ex. https://gnews.io/api/v4/search?q=Air+India+Phuket&max=10&apikey=...
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://gnews.io/api/v4/search",
                    params=params
                )

                # GNews response contains totalArticles and articles[] which in turn contains
                # sources containing country
                response.raise_for_status() # Checks for HTTP errors
                curr_data = response.json() # Converts GNews JSON into a Python dictionary
                data[country] = curr_data 

        except Exception as error:
            print("[BACKEND] GNews error =", error)

            return {
                "searchQueryReceived": search_query,
                "articles": []
            }

        # STEP 4: Convert GNews format into our frontend format
        articles = []

        for country in data:
            for article in data[country].get("articles", []):
                source = article.get("source", {})

                articles.append({
                    "title": article.get("title", ""),
                    "source": source.get("name", "Unknown"),
                    "url": article.get("url", ""),
                    "country": country,
                })

    print("[BACKEND] articles =", articles)

    # Returns search query and article list to sidepanel.js
    # Each element of article is a dict with title, source, url and country keys
    return {
        "searchQueryReceived": search_query,
        "articles": articles
    }