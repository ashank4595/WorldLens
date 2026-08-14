from fastapi import FastAPI

# CORS allows the extension to make requests to the backend which has different origin
from fastapi.middleware.cors import CORSMiddleware 
import os
import httpx # Library to send http requests from Fast API to GNEWS

# query to be sent to GNews built in query_builder.py
from query_builder import build_query


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COUNTRIES = ["tr", "pk", "us", "il", "eg", "in", "gb"]

# Endpoint called by sidepanel.js, request is dict with pageUrl, searchQuery/headline etc.
@app.post("/api/search") 
async def search(request: dict): 

    print("[BACKEND] request body =", request) 

    # Get headline from frontend
    search_query = request.get("searchQuery", "")

    final_query, keywords = build_query(search_query)

    print("[BACKEND] headline =", search_query)
    print("[BACKEND] final query =", final_query)

    # Call GNews
    api_key = os.getenv("GNEWS_API_KEY") # Read API key from terminal
    print("[BACKEND] api key exists =", bool(api_key))

    data = {}

    for country in COUNTRIES:
        # Query Parameters
        params = {
            "q": final_query,
            "max": 20,
            "in": "title,description", # to choose in which attributes keywords are searched
            "sortby": "relevance",
            "country": country,
            "apikey": api_key,
        }

        try:
            # httpx creates a request
            # Ex. https://gnews.io/api/v4/search?q=Air+India+Phuket&max=10&apikey=...
            # Allows FastAPI to wait for GNEWS without blocking the server
            # while one request is waiting on GNews, FastAPI can  handle other requests.
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    "https://gnews.io/api/v4/search",
                    params=params
                )

                # GNews response contains totalArticles and articles[]
                response.raise_for_status() # Checks for HTTP errors
                curr_data = response.json() # Converts GNews JSON into a Python dictionary
                data[country] = curr_data 

        except Exception as error:
            print("[BACKEND] GNews error =", error)

            continue

    # Convert GNews format into frontend format
    articles = []

    for country in data:
        for article in data[country].get("articles", []):
            source = article.get("source", {})

            # Do not append any_articles that have less than 3 query keywords
            article_text = (
                article.get("title", "")
                + " "
                + article.get("description", "")
            ).lower()

            match_count = 0

            for keyword in keywords:
                if keyword.lower() in article_text:
                    match_count += 1

            if match_count < 2:
                continue

            articles.append({
                "title": article.get("title", ""),
                "source": source.get("name", "Unknown"),
                "url": article.get("url", ""),
                "country": source.get("country", "Unknown"),
            })

    print("[BACKEND] articles =", articles)

    # Returns search query and article list to sidepanel.js
    # Each element of article is a dict with title, source, url and country keys
    return {
        "searchQueryReceived": search_query,
        "articles": articles
    }
