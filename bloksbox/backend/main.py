from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pytrends.request import TrendReq
import pandas as pd

app = FastAPI()

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Category to keywords mapping
CATEGORY_KEYWORDS = {
    "Mobiles": ["iPhone", "Samsung Galaxy", "OnePlus", "Nothing Phone"],
    "Cars": ["Tata Nexon", "Hyundai Creta", "Maruti Brezza"],
    "AI Tools": ["ChatGPT", "Midjourney", "Claude AI"],
    "Movies": ["Latest Bollywood Movies", "Upcoming Movies"],
    "TV Series": ["Trending TV Shows", "Web Series"],
    "Travel Destinations": ["Goa", "Manali", "Bali"],
    "Fashion & Apparels": ["Streetwear", "Summer Fashion"],
    "Celebrities": ["Bollywood Actors", "Indian Celebrities"],
    "Sports": ["Cricket", "Football"],
    "Internet Trends": ["Viral Videos", "Trending Topics"],
    "Social Media Trends": ["Instagram Trends", "YouTube Trends"],
    "Technology Trends": ["AI Technology", "Future Tech"],
    "Gaming Trends": ["Mobile Gaming", "PC Gaming"],
    "Mobile Apps": ["Trending Apps"],
    "Streaming Content": ["Netflix Shows", "Prime Video"],
    "Web Series": ["Trending Web Series"],
    "Music": ["Trending Songs"],
    "Podcasts": ["Popular Podcasts"],
    "Influencers": ["Instagram Influencers"],
    "Memes": ["Trending Memes"],
    "Viral News": ["Trending News"],
    "Live Events": ["Concerts", "Sports Events"],
    "Festivals": ["Indian Festivals"],
    "Esports": ["Esports Tournaments"],
    "Global Culture": ["Global Trends"],
    "Pop Culture": ["Pop Culture"],
    "Digital Creators": ["Content Creators"],
    "Online Communities": ["Online Forums"],
    "Science & Space": ["Space News"],
    "Future Tech": ["Emerging Technology"],
}

@app.get("/")
async def root():
    return {"status": "API running"}

@app.get("/api/trends")
async def get_trends(category: str):
    if category not in CATEGORY_KEYWORDS:
        raise HTTPException(status_code=400, detail=f"Category '{category}' not found")
    
    try:
        pytrends = TrendReq(hl='en-US', tz=360)
        keywords = CATEGORY_KEYWORDS[category]
        
        # Fetch related queries
        pytrends.build_payload(keywords, geo='IN', timeframe='now 7-d')
        related_queries = pytrends.related_queries()
        
        # Extract rising and top queries
        search_queries = []
        for keyword in keywords:
            if keyword in related_queries and related_queries[keyword] is not None:
                rising = related_queries[keyword].get('rising', pd.DataFrame())
                top = related_queries[keyword].get('top', pd.DataFrame())
                
                if not rising.empty:
                    search_queries.extend(rising['query'].tolist())
                if not top.empty:
                    search_queries.extend(top['query'].tolist())
        
        # Remove duplicates
        search_queries = list(set(search_queries))
        
        # Generate interest distribution
        interest_dist = {}
        for i, query in enumerate(search_queries[:5]):
            interest_dist[query] = max(10, 30 - (i * 5))
        
        # Generate features with change
        features = [
            {"name": f"Trend {i+1}", "change": max(5, 25 - (i * 5))}
            for i in range(min(5, len(search_queries)))
        ]
        
        return {
            "trendingTopics": keywords,
            "interestDistribution": interest_dist,
            "searchQueries": search_queries[:10],
            "features": features
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trends: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
