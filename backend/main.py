from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Run search() when someone sends POST request to /api/search
@app.post("/api/search")
async def search(request: dict):
#     const requestBody = {                 
#       pageUrl: "https://example.com/article",
#       pageTitle: "Some browser title",...
#     }; Converted to python dict, request
    print("[BACKEND] request body =", request)

    search_query = request.get("searchQuery", "")

    return {
        "searchQueryReceived": search_query,
        "articles": [
            {
                "title": "Fake backend article from India",
                "source": "HT",
                "url": "https://example.com/india",
                "country": "India",
            },
            {
                "title": "Fake backend article from Japan",
                "source": "Nikkei",
                "url": "https://example.com/japan",
                "country": "Japan",
            },
        ],
    }